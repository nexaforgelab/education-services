#!/usr/bin/env python3
"""
extract_pdf_layout.py — 提取 PDF 版面信息：文本块、字体、坐标、图片、表格

用法:
  python scripts/extract_pdf_layout.py --pdf samples/math_g7_pep.pdf --output out/layout.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

try:
    import fitz
except ImportError:
    print("Error: pip install pymupdf --break-system-packages", file=sys.stderr)
    sys.exit(1)


def extract_layout(pdf_path: str) -> Dict[str, Any]:
    """提取 PDF 完整版面信息"""
    doc = fitz.open(pdf_path)
    pages_data = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_dict = page.get_text("dict")

        # 文本块
        text_blocks = []
        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:
                continue
            lines = []
            for line in block.get("lines", []):
                spans = []
                for span in line.get("spans", []):
                    spans.append({
                        "text": span["text"],
                        "font": span["font"],
                        "size": round(span["size"], 2),
                        "color": span["color"],
                        "bbox": [round(c, 2) for c in span["bbox"]],
                    })
                lines.append({
                    "bbox": [round(c, 2) for c in line["bbox"]],
                    "spans": spans,
                })
            text_blocks.append({
                "bbox": [round(c, 2) for c in block["bbox"]],
                "lines": lines,
            })

        # 图片
        images = []
        for img in page.get_images(full=True):
            xref = img[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                images.append({
                    "xref": xref,
                    "width": pix.width,
                    "height": pix.height,
                    "colorspace": pix.colorspace.name if pix.colorspace else None,
                })
                pix = None
            except Exception as e:
                images.append({"xref": xref, "error": str(e)})

        # 表格（基于布局的简单检测）
        tables = detect_tables_simple(page)

        pages_data.append({
            "page_number": page_num + 1,
            "page_size": [round(page.rect.width, 2), round(page.rect.height, 2)],
            "text_blocks": text_blocks,
            "images": images,
            "tables": tables,
            "rotation": page.rotation,
        })

    result = {
        "pdf_path": pdf_path,
        "page_count": len(doc),
        "metadata": doc.metadata,
        "pages": pages_data,
    }
    doc.close()
    return result


def detect_tables_simple(page) -> List[Dict[str, Any]]:
    """简单的表格检测：寻找具有规则线段的区域"""
    # 实际项目里用 pdfplumber 的 table finder 更准
    drawings = page.get_drawings()
    tables = []
    # 简化：检测水平线多于 3 条的区域
    horizontal_lines = []
    for d in drawings:
        for item in d.get("items", []):
            if item[0] == "l":  # line
                p1, p2 = item[1], item[2]
                if abs(p1.y - p2.y) < 1:  # 水平
                    horizontal_lines.append((p1.y, p1.x, p2.x))
    if len(horizontal_lines) >= 3:
        tables.append({
            "horizontal_line_count": len(horizontal_lines),
            "approx_bbox": [0, min(l[0] for l in horizontal_lines),
                          page.rect.width, max(l[0] for l in horizontal_lines)],
        })
    return tables


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--output", required=True, help="输出 JSON 路径")
    args = parser.parse_args()

    layout = extract_layout(args.pdf)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(layout, f, ensure_ascii=False, indent=2)
    print(f"✅ Layout extracted to {out_path}")
    print(f"   Pages: {layout['page_count']}")
    print(f"   Total text blocks: {sum(len(p['text_blocks']) for p in layout['pages'])}")
    print(f"   Total images: {sum(len(p['images']) for p in layout['pages'])}")


if __name__ == "__main__":
    main()
