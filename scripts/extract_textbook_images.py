#!/usr/bin/env python3
"""
extract_textbook_images.py — 提取教材中的图片（插图、示意图、表格）

用法:
  python scripts/extract_textbook_images.py --pdf samples/math_g7_pep.pdf --output out/images/
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


def extract_images(
    pdf_path: str,
    output_dir: str,
    min_width: int = 100,
    min_height: int = 100,
    page_range: tuple = None,
) -> Dict[str, Any]:
    """
    提取 PDF 中的所有图片

    Args:
        pdf_path: PDF 路径
        output_dir: 输出目录
        min_width: 最小宽度（过滤小图标）
        min_height: 最小高度
        page_range: (start, end) 1-indexed
    """
    pdf_path = Path(pdf_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"🖼️  提取图片: {pdf_path}")
    print(f"   输出: {output_path}")
    print(f"   最小尺寸: {min_width} x {min_height}")

    doc = fitz.open(str(pdf_path))

    if page_range:
        start, end = page_range
        pages = range(start - 1, min(end, len(doc)))
    else:
        pages = range(len(doc))

    image_index = []
    img_count = 0

    for page_num in pages:
        page = doc.load_page(page_num)
        image_list = page.get_images(full=True)

        for img_idx, img in enumerate(image_list):
            xref = img[0]
            try:
                pix = fitz.Pixmap(doc, xref)

                # 过滤太小的图
                if pix.width < min_width or pix.height < min_height:
                    pix = None
                    continue

                # 转换 CMYK 为 RGB
                if pix.colorspace and pix.colorspace.name == "DeviceCMYK":
                    pix = fitz.Pixmap(fitz.csRGB, pix)

                # 保存
                img_filename = f"page{page_num+1:03d}_img{img_idx:03d}_xref{xref}.png"
                img_path = output_path / img_filename
                pix.save(str(img_path))

                image_index.append({
                    "filename": img_filename,
                    "page": page_num + 1,
                    "xref": xref,
                    "width": pix.width,
                    "height": pix.height,
                    "colorspace": pix.colorspace.name if pix.colorspace else None,
                })

                img_count += 1
                pix = None

            except Exception as e:
                print(f"   跳过第 {page_num+1} 页图片 {img_idx}: {e}", file=sys.stderr)

    # 写索引
    index_file = output_path / "image_index.json"
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump({
            "pdf_path": str(pdf_path),
            "total_images": img_count,
            "images": image_index,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 提取完成：{img_count} 张图片")
    print(f"   索引: {index_file}")

    doc.close()
    return {"total": img_count, "index_file": str(index_file)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--min-width", type=int, default=100)
    parser.add_argument("--min-height", type=int, default=100)
    parser.add_argument("--start-page", type=int)
    parser.add_argument("--end-page", type=int)
    args = parser.parse_args()

    page_range = None
    if args.start_page and args.end_page:
        page_range = (args.start_page, args.end_page)

    extract_images(
        args.pdf, args.output,
        min_width=args.min_width,
        min_height=args.min_height,
        page_range=page_range,
    )


if __name__ == "__main__":
    main()
