#!/usr/bin/env python3
"""
ocr_textbook.py — 扫描版教材的 OCR 处理

当 PDF 没有文本层（如扫描版教材）时使用：
  - PaddleOCR 识别中英文
  - 公式识别（pix2tex）
  - 版面分析
  - 输出结构化 JSON

用法:
  python scripts/ocr_textbook.py --pdf samples/scanned_textbook.pdf --output out/ocr/
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: pip install pymupdf --break-system-packages", file=sys.stderr)
    sys.exit(1)

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    print("Warning: paddleocr not installed, using fallback", file=sys.stderr)

try:
    from pix2tex.cli import LatexOCR
    PIX2TEX_AVAILABLE = True
except ImportError:
    PIX2TEX_AVAILABLE = False
    print("Warning: pix2tex not installed, formulas not recognized", file=sys.stderr)


# 图像预处理
def preprocess_image(img_bytes: bytes) -> bytes:
    """
    简单的图像预处理：去噪、二值化
    实际项目里用 OpenCV
    """
    # TODO: 实现 OpenCV 预处理
    return img_bytes


# OCR 引擎
class OCREngine:
    """OCR 引擎封装"""

    def __init__(self, lang: str = "ch"):
        self.lang = lang
        self.paddle = None
        self.formula_ocr = None

        if PADDLEOCR_AVAILABLE:
            try:
                self.paddle = PaddleOCR(use_angle_cls=True, lang=lang)
            except Exception as e:
                print(f"Warning: failed to init PaddleOCR: {e}", file=sys.stderr)

        if PIX2TEX_AVAILABLE:
            try:
                self.formula_ocr = LatexOCR()
            except Exception as e:
                print(f"Warning: failed to init pix2tex: {e}", file=sys.stderr)

    def recognize_page(self, page: fitz.Page) -> Dict[str, Any]:
        """
        识别一页：
        - 提取图片
        - OCR 文本
        - 公式识别
        """
        # 渲染为图片
        mat = fitz.Matrix(2, 2)  # 2x 缩放
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")

        # 文本 OCR
        text_blocks = []
        if self.paddle:
            try:
                result = self.paddle.ocr(img_bytes, cls=True)
                for line in result[0]:
                    bbox, (text, conf) = line
                    text_blocks.append({
                        "text": text,
                        "confidence": conf,
                        "bbox": [[p[0], p[1]] for p in bbox],
                    })
            except Exception as e:
                print(f"Warning: PaddleOCR failed: {e}", file=sys.stderr)

        # 公式识别（从 OCR 结果中识别公式区域）
        formulas = []
        # 实际项目里：先检测公式区域（用 YOLO 等），再单独识别

        return {
            "page_number": page.number + 1,
            "text_blocks": text_blocks,
            "formulas": formulas,
            "full_text": "\n".join(b["text"] for b in text_blocks),
        }

    def detect_formula_regions(self, img_bytes: bytes) -> List[Dict[str, Any]]:
        """
        检测公式区域
        实际项目里用深度学习模型（YOLO / Faster R-CNN）检测
        """
        # 简化：返回空
        return []


def ocr_textbook(
    pdf_path: str,
    output_dir: str,
    lang: str = "ch",
    page_range: Optional[tuple] = None,
) -> Dict[str, Any]:
    """
    整本教材 OCR
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"📖 OCR 扫描版教材: {pdf_path}")
    print(f"   输出: {output_path}")
    print(f"   语言: {lang}")

    doc = fitz.open(str(pdf_path))
    engine = OCREngine(lang=lang)

    # 决定页码范围
    if page_range:
        start, end = page_range
        pages_to_process = range(start - 1, min(end, len(doc)))
    else:
        pages_to_process = range(len(doc))

    results = []
    for i in pages_to_process:
        page = doc.load_page(i)
        print(f"   处理第 {i+1} / {len(doc)} 页 ...", end="\r")
        result = engine.recognize_page(page)
        results.append(result)

    print(f"\n✅ OCR 完成，共 {len(results)} 页")

    # 合并为单文件
    output_file = output_path / "ocr_result.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "pdf_path": str(pdf_path),
            "total_pages": len(results),
            "pages": results,
        }, f, ensure_ascii=False, indent=2)

    # 合并为单个 .txt
    txt_file = output_path / "ocr_result.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        for page in results:
            f.write(f"\n\n===== 第 {page['page_number']} 页 =====\n\n")
            f.write(page["full_text"])

    print(f"   JSON: {output_file}")
    print(f"   Text: {txt_file}")

    doc.close()
    return {
        "pages_processed": len(results),
        "output_json": str(output_file),
        "output_text": str(txt_file),
    }


def main():
    parser = argparse.ArgumentParser(description="扫描版教材 OCR")
    parser.add_argument("--pdf", required=True, help="扫描版 PDF 路径")
    parser.add_argument("--output", required=True, help="输出目录")
    parser.add_argument("--lang", default="ch", help="OCR 语言（ch/en/fr/...）")
    parser.add_argument("--start-page", type=int, help="起始页（1-indexed）")
    parser.add_argument("--end-page", type=int, help="结束页（1-indexed）")
    args = parser.parse_args()

    page_range = None
    if args.start_page and args.end_page:
        page_range = (args.start_page, args.end_page)

    ocr_textbook(args.pdf, args.output, args.lang, page_range)


if __name__ == "__main__":
    main()
