#!/usr/bin/env python3
"""
recognize_formulas.py — 公式识别（pix2tex / Mathpix）

用法:
  python scripts/recognize_formulas.py --image formulas.jpg --output out/formula.txt
  python scripts/recognize_formulas.py --pdf samples/math_g7_pep.pdf --output out/formulas.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import fitz
except ImportError:
    print("Error: pip install pymupdf --break-system-packages", file=sys.stderr)
    sys.exit(1)

try:
    from pix2tex.cli import LatexOCR as Pix2Tex
    PIX2TEX_AVAILABLE = True
except ImportError:
    PIX2TEX_AVAILABLE = False


class FormulaRecognizer:
    """公式识别器"""

    def __init__(self, engine: str = "pix2tex"):
        self.engine = engine
        self.model = None

        if engine == "pix2tex" and PIX2TEX_AVAILABLE:
            try:
                self.model = Pix2Tex()
            except Exception as e:
                print(f"Warning: failed to init pix2tex: {e}", file=sys.stderr)
        # Mathpix API 也可加

    def recognize_image(self, image_path: str) -> str:
        """识别单张图片"""
        if not self.model:
            return "[Formula recognition not available]"

        try:
            result = self.model(image_path)
            return result
        except Exception as e:
            return f"[Error: {e}]"

    def detect_and_recognize_page(self, page: fitz.Page) -> List[Dict[str, Any]]:
        """
        检测并识别一页中的所有公式
        实际项目里用 YOLO 检测公式区域，再用 pix2tex 识别
        """
        # 简化：暂不实现自动检测
        return []


def recognize_from_pdf(
    pdf_path: str,
    output_path: str,
    engine: str = "pix2tex",
) -> Dict[str, Any]:
    """从 PDF 中识别所有公式"""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(str(pdf_path))
    recognizer = FormulaRecognizer(engine=engine)

    formulas = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_formulas = recognizer.detect_and_recognize_page(page)
        for f in page_formulas:
            f["page"] = page_num + 1
        formulas.extend(page_formulas)

    # 写结果
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "pdf_path": str(pdf_path),
            "engine": engine,
            "total_formulas": len(formulas),
            "formulas": formulas,
        }, f, ensure_ascii=False, indent=2)

    print(f"✅ 识别完成：{len(formulas)} 个公式")
    print(f"   输出: {output_path}")

    doc.close()
    return {"total": len(formulas), "output": str(output_path)}


def recognize_from_image(image_path: str) -> str:
    """从单张图片识别公式"""
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    recognizer = FormulaRecognizer()
    result = recognizer.recognize_image(str(image_path))
    print(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action")

    # 识别单张图
    p_img = sub.add_parser("image", help="识别单张图片")
    p_img.add_argument("--image", required=True)
    p_img.add_argument("--output")
    p_img.add_argument("--engine", default="pix2tex")

    # 识别整本 PDF
    p_pdf = sub.add_parser("pdf", help="识别整本 PDF")
    p_pdf.add_argument("--pdf", required=True)
    p_pdf.add_argument("--output", required=True)
    p_pdf.add_argument("--engine", default="pix2tex")

    args = parser.parse_args()

    if args.action == "image":
        result = recognize_from_image(args.image)
        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
            print(f"已写入: {args.output}")
    elif args.action == "pdf":
        recognize_from_pdf(args.pdf, args.output, args.engine)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
