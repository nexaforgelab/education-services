#!/usr/bin/env python3
"""
build_textbook_index.py — 把解析后的教材 block 写入 pgvector 索引

用法:
  python scripts/build_textbook_index.py \
    --manifest out/textbook_manifest.json \
    --db-url $DATABASE_URL
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Error: pip install sentence-transformers --break-system-packages", file=sys.stderr)
    sys.exit(1)

try:
    import psycopg2
    from pgvector.psycopg2 import register_vector
except ImportError:
    print("Error: pip install pgvector psycopg2-binary --break-system-packages", file=sys.stderr)
    sys.exit(1)


EMBEDDING_MODEL = "shibing624/text2vec-base-chinese"
BATCH_SIZE = 32


def load_manifest(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_blocks_from_pdf(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    从 PDF 重新提取 block（实际项目里应该 ingest 时就持久化）
    这里 demo 用 fitz 直接读
    """
    import fitz

    # 这里简化处理，假设 PDF 路径在环境变量里
    pdf_path = os.environ.get("TEXTBOOK_PDF_PATH")
    if not pdf_path or not Path(pdf_path).exists():
        print(f"Warning: TEXTBOOK_PDF_PATH not set, skipping block extraction", file=sys.stderr)
        return []

    doc = fitz.open(pdf_path)
    blocks = []

    for chapter in manifest.get("chapters", []):
        for page_num in range(chapter["page_start"] - 1, chapter["page_end"]):
            if page_num >= len(doc):
                break
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                blocks.append({
                    "textbook_id": manifest["textbook_id"],
                    "chapter_id": chapter["chapter_id"],
                    "page_number": page_num + 1,
                    "block_type": "concept",
                    "content": text.strip(),
                    "metadata": {},
                })
    doc.close()
    return blocks


def embed_and_persist(blocks: List[Dict[str, Any]], db_url: str):
    """embedding + 写入 pgvector"""
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print(f"Connecting to DB")
    conn = psycopg2.connect(db_url)
    register_vector(conn)
    cur = conn.cursor()

    # 清空该教材的旧索引
    if blocks:
        textbook_id = blocks[0]["textbook_id"]
        cur.execute(
            "DELETE FROM textbook_blocks WHERE textbook_id = %s",
            (textbook_id,)
        )

    # 分批 embedding
    for i in range(0, len(blocks), BATCH_SIZE):
        batch = blocks[i:i + BATCH_SIZE]
        texts = [b["content"][:2000] for b in batch]  # 截断防止超长
        embeddings = model.encode(texts, show_progress_bar=False)

        for block, emb in zip(batch, embeddings):
            cur.execute("""
                INSERT INTO textbook_blocks
                (textbook_id, chapter_id, page_number, block_type, content, embedding)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                block["textbook_id"],
                block["chapter_id"],
                block["page_number"],
                block["block_type"],
                block["content"],
                emb.tolist(),
            ))
        print(f"  Indexed {i + len(batch)} / {len(blocks)}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Done. Indexed {len(blocks)} blocks.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="textbook_manifest.json 路径")
    parser.add_argument("--db-url", required=True, help="PostgreSQL URL")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    blocks = extract_blocks_from_pdf(manifest)
    if blocks:
        embed_and_persist(blocks, args.db_url)
    else:
        print("No blocks to index.")


if __name__ == "__main__":
    main()
