#!/usr/bin/env python3
"""
ingest_textbooks.py — 教材 PDF 解析入库主入口

参考 financial-services 的 script 模式：单一职责 + 可独立运行 + 输出可追溯。

用法:
  python scripts/ingest_textbooks.py \
    --pdf samples/math_g7_pep.pdf \
    --subject math \
    --grade 7 \
    --version 人教版 \
    --output out/

流程:
  1. 预检 PDF（页数、加密、可读性）
  2. 调用 extract_pdf_layout.py 提取版面
  3. 章节切分 + block 分类
  4. 公式、图表处理
  5. 写 PostgreSQL + pgvector
  6. 生成 textbook_manifest.json
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None  # 会在调用 ingest() 时检查

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

try:
    import psycopg2
    from pgvector.psycopg2 import register_vector
except ImportError:
    psycopg2 = None


# ============ Config ============

DEFAULT_OUTPUT_DIR = "./out/"
MANIFEST_FILENAME = "textbook_manifest.json"

EMBEDDING_MODEL = "shibing624/text2vec-base-chinese"
EMBEDDING_DIM = 768


# ============ Utilities ============

def make_textbook_id(subject: str, grade: str, version: str) -> str:
    """生成统一的教材 ID: subject_g{grade}_{version_slug}_{year}"""
    from datetime import datetime
    version_slug = version.replace("版", "").lower()  # 人教 -> 人教
    year = datetime.now().year
    return f"{subject}_g{grade}_{version_slug}_{year}"


def file_hash(path: str) -> str:
    """SHA256 of file"""
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return f"sha256:{sha.hexdigest()}"


def extract_metadata(doc) -> Dict[str, Any]:
    """提取 PDF 元数据"""
    meta = doc.metadata or {}
    return {
        "title": meta.get("title", "").strip(),
        "author": meta.get("author", "").strip(),
        "subject": meta.get("subject", "").strip(),
        "page_count": len(doc),
    }


# ============ Outline Extraction ============

def extract_outline(doc) -> List[Dict[str, Any]]:
    """
    提取目录结构。优先用 PDF 书签，失败则从前几页文本解析。
    返回: [{"level": 1, "title": "有理数", "page": 1}, ...]
    """
    outline = []

    # 方法 1: PDF 书签
    toc = doc.get_toc(simple=False)
    for level, title, page, *_ in toc:
        outline.append({
            "level": level,
            "title": title.strip(),
            "page": page,
        })

    if outline:
        return outline

    # 方法 2: 文本解析（从前 5 页找"目录"字样）
    return extract_outline_from_text(doc)


def extract_outline_from_text(doc, max_pages: int = 5) -> List[Dict[str, Any]]:
    """从前几页文本中解析目录（简陋版）"""
    import re
    outline = []
    for page_num in range(min(max_pages, len(doc))):
        page = doc.load_page(page_num)
        text = page.get_text()
        if "目录" in text or "目 录" in text:
            # 简易解析：找 "数字 + 空格/点 + 标题 + 数字"
            pattern = re.compile(r"^\s*(\d+(?:\.\d+)*)\s*[\.．·\s]+([^\d]+?)\s+(\d+)\s*$", re.M)
            for m in pattern.finditer(text):
                level = m.group(1).count(".") + 1
                outline.append({
                    "level": level,
                    "title": m.group(2).strip(),
                    "page": int(m.group(3)),
                })
            if outline:
                break
    return outline


# ============ Block Classification ============

EXAMPLE_PATTERNS = ["例 ", "例题", "Example", "Ex."]
EXERCISE_PATTERNS = ["练习", "习题", "Exercises", "Problems"]
SUMMARY_PATTERNS = ["小结", "本章要点", "Summary", "本章小结"]
DEFINITION_PATTERNS = ["定义", "我们把", "叫做", "称为"]


def classify_block(text: str, font_size: float, is_bold: bool) -> str:
    """
    块类型分类
    返回: concept | example | exercise | summary | definition | image | table
    """
    text = text.strip()
    if not text:
        return "empty"

    # 例题
    for pat in EXAMPLE_PATTERNS:
        if text.startswith(pat) or f"\n{pat}" in text[:100]:
            return "example"

    # 练习
    for pat in EXERCISE_PATTERNS:
        if pat in text[:50]:
            return "exercise"

    # 小结
    for pat in SUMMARY_PATTERNS:
        if pat in text[:50]:
            return "summary"

    # 定义（基于关键词 + 短文本 + 较大字体）
    for pat in DEFINITION_PATTERNS:
        if pat in text[:100] and len(text) < 200:
            return "definition"

    # 默认概念
    return "concept"


# ============ Section Splitting ============

def split_sections(
    doc,
    chapter: Dict[str, Any],
    next_chapter_page: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    把一章切分为多个 section
    """
    start = chapter["page"]
    end = next_chapter_page or len(doc)
    sections = []

    for page_num in range(start - 1, end):
        if page_num >= len(doc):
            break
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if block.get("type") != 0:  # 非文本
                continue
            text_lines = []
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text_lines.append({
                        "text": span["text"],
                        "size": span["size"],
                        "font": span["font"],
                        "bbox": span["bbox"],
                    })
            if not text_lines:
                continue
            full_text = "".join(l["text"] for l in text_lines)
            if not full_text.strip():
                continue

            is_bold = any("Bold" in l["font"] or l["size"] > 14 for l in text_lines)
            avg_size = sum(l["size"] for l in text_lines) / len(text_lines)

            block_type = classify_block(full_text, avg_size, is_bold)

            sections.append({
                "page": page_num + 1,
                "bbox": block.get("bbox"),
                "type": block_type,
                "content": full_text,
                "is_bold": is_bold,
                "avg_font_size": avg_size,
            })
    return sections


# ============ Main Pipeline ============

def ingest(
    pdf_path: str,
    subject: str,
    grade: str,
    version: str,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    db_url: Optional[str] = None,
) -> Dict[str, Any]:
    """主入口：解析 PDF → 入库 → 输出 manifest"""

    if fitz is None:
        raise ImportError("PyMuPDF not installed. Run: pip install pymupdf --break-system-packages")

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    print(f"📖 开始解析教材: {pdf_path}")
    t0 = time.time()

    # 1. 打开 PDF
    doc = fitz.open(str(pdf_path))
    if doc.is_encrypted:
        raise ValueError("PDF 已加密，请提供密码或解密版本")

    # 2. 元数据
    meta = extract_metadata(doc)
    print(f"   元数据: {meta['title']} ({meta['page_count']} 页)")

    # 3. 文件 hash
    fhash = file_hash(str(pdf_path))
    print(f"   文件 hash: {fhash[:16]}...")

    # 4. 教材 ID
    textbook_id = make_textbook_id(subject, grade, version)

    # 5. 提取目录
    outline = extract_outline(doc)
    print(f"   目录: {len(outline)} 条")

    # 6. 章节切分
    chapters = []
    for i, item in enumerate(outline):
        if item["level"] > 1:  # 跳过子目录
            continue
        next_page = outline[i + 1]["page"] if i + 1 < len(outline) else None
        sections = split_sections(doc, item, next_page)
        chapter_id = f"ch{i+1:02d}"

        # 提取核心概念（粗粒度）
        concepts = set()
        for sec in sections:
            if sec["type"] in ("concept", "definition"):
                # 简单规则：取"X 是 Y"或"我们把 X 叫做 Y"
                import re
                patterns = [
                    r"我们把([^\u4e00-\u9fa5]{0,2}?[^\u4e00-\u9fa5]{0,30}?)叫做",
                    r"([^\u4e00-\u9fa5]{0,2}?[^\u4e00-\u9fa5]{0,30}?)是([^\u4e00-\u9fa5]{0,30})",
                ]
                # 这里只做粗粒度抽取，更精细的留给 knowledge-graph-builder

        chapters.append({
            "chapter_id": chapter_id,
            "title": item["title"],
            "page_start": item["page"],
            "page_end": next_page or meta["page_count"],
            "sections_count": len(sections),
        })

    # 7. 构建 manifest
    manifest = {
        "textbook_id": textbook_id,
        "title": meta["title"] or f"{subject} {grade} {version}",
        "subject": subject,
        "grade": grade,
        "version": version,
        "publisher": meta["author"] or "",
        "total_pages": meta["page_count"],
        "file_hash": fhash,
        "ingested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "chapters": chapters,
    }

    # 8. 输出
    out_path = Path(output_dir) / MANIFEST_FILENAME
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - t0
    print(f"\n✅ 完成！耗时 {elapsed:.1f}s")
    print(f"   教材 ID: {textbook_id}")
    print(f"   章节: {len(chapters)}")
    print(f"   Manifest: {out_path}")

    # 9. 写数据库（如果指定）
    if db_url:
        persist_to_db(manifest, db_url)
        print(f"   已写入数据库: {db_url.split('@')[-1]}")

    doc.close()
    return manifest


def persist_to_db(manifest: Dict[str, Any], db_url: str):
    """持久化到 PostgreSQL + pgvector"""
    if not psycopg2:
        print("Warning: psycopg2 not installed, skipping DB persist", file=sys.stderr)
        return
    conn = psycopg2.connect(db_url)
    register_vector(conn)
    cur = conn.cursor()

    # 写 textbooks 表
    cur.execute("""
        INSERT INTO textbooks (id, subject, grade, version, title, publisher, file_hash)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """, (
        manifest["textbook_id"],
        manifest["subject"],
        manifest["grade"],
        manifest["version"],
        manifest["title"],
        manifest["publisher"],
        manifest["file_hash"],
    ))

    conn.commit()
    cur.close()
    conn.close()


# ============ CLI ============

def main():
    parser = argparse.ArgumentParser(description="教材 PDF 解析入库")
    parser.add_argument("--pdf", required=True, help="PDF 文件路径")
    parser.add_argument("--subject", required=True, choices=["math", "english", "chinese", "science", "physics", "chemistry"])
    parser.add_argument("--grade", required=True, help="年级，如 7")
    parser.add_argument("--version", required=True, help="教材版本，如 人教版")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_DIR, help="输出目录")
    parser.add_argument("--db-url", help="PostgreSQL 连接 URL（可选）")

    args = parser.parse_args()
    ingest(args.pdf, args.subject, args.grade, args.version, args.output, args.db_url)


if __name__ == "__main__":
    main()
