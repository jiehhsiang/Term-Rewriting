#!/usr/bin/env python3
"""Render one or more pages of a PDF to PNG so they can be viewed with the Read tool.

Usage:
    python3 debate/tools/pdf_page.py <input.pdf> <page>[-<page>] [--dpi 150] [--out DIR]

Pages are 1-based physical PDF pages. Output files: <DIR>/<pdf-stem>-p<page>.png
(default DIR: debate/bibliography/local/pages/). Prints the output paths.
Needs only PyMuPDF (pip install pymupdf); no poppler required.
"""
import argparse, os, sys
import pymupdf

ap = argparse.ArgumentParser()
ap.add_argument("pdf")
ap.add_argument("pages", help="e.g. 144 or 144-146")
ap.add_argument("--dpi", type=int, default=150)
ap.add_argument("--out", default="debate/bibliography/local/pages")
a = ap.parse_args()
lo, _, hi = a.pages.partition("-")
lo = int(lo); hi = int(hi) if hi else lo
os.makedirs(a.out, exist_ok=True)
doc = pymupdf.open(a.pdf)
stem = os.path.splitext(os.path.basename(a.pdf))[0]
for p in range(lo, min(hi, doc.page_count) + 1):
    path = os.path.join(a.out, f"{stem}-p{p}.png")
    doc[p - 1].get_pixmap(dpi=a.dpi).save(path)
    print(path)
