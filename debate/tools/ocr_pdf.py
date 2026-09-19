#!/usr/bin/env python3
"""OCR a scanned (image-only) PDF into page-tagged plain text so debate agents can grep it.

Usage:
    python3 debate/tools/ocr_pdf.py <input.pdf> [output.txt] [--pages 1-50] [--dpi 200]

Output format (one block per page, PDF page numbers are 1-based physical pages,
NOT the printed 頁碼 of the book):

    ==== page 123 ====
    <OCR text, one detected line per row, in reading order as RapidOCR returns it>

Notes
- Uses PyMuPDF to rasterise and RapidOCR (PP-OCR models, bundled in the wheel,
  no network needed) to recognise. Install once: pip install pymupdf rapidocr-onnxruntime
- 1930s vertical typesetting is recognised line-by-line; expect errors on rare
  glyphs. Agents must re-check any passage they quote against the page image
  (Read tool with `pages`) before citing it as [A].
- Prints progress to stderr; safe to run in the background and resume with --pages.
"""
import argparse
import sys
import time

import pymupdf
from rapidocr_onnxruntime import RapidOCR


def parse_pages(spec, n):
    if not spec:
        return range(1, n + 1)
    a, _, b = spec.partition("-")
    a = int(a)
    b = int(b) if b else a
    return range(max(1, a), min(n, b) + 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--pages", help="e.g. 1-50 (physical PDF pages, 1-based)")
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--append", action="store_true", help="append to output instead of overwriting")
    args = ap.parse_args()

    out_path = args.out or args.pdf.rsplit(".", 1)[0] + ".txt"
    doc = pymupdf.open(args.pdf)
    ocr = RapidOCR()
    pages = parse_pages(args.pages, doc.page_count)
    mode = "a" if args.append else "w"
    t0 = time.time()
    with open(out_path, mode, encoding="utf-8") as out:
        for i in pages:
            page = doc[i - 1]
            pix = page.get_pixmap(dpi=args.dpi, colorspace=pymupdf.csGRAY)
            img = pix.tobytes("png")
            result, _ = ocr(img)
            out.write(f"==== page {i} ====\n")
            if result:
                # result: list of [box, text, score]; keep RapidOCR's order (top-to-bottom, left-to-right).
                for box, text, score in result:
                    out.write(text + "\n")
            out.write("\n")
            out.flush()
            if i % 10 == 0 or i == pages[-1]:
                print(f"[ocr] page {i}/{doc.page_count}  {time.time() - t0:.0f}s", file=sys.stderr)
    print(f"[ocr] wrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
