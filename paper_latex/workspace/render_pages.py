#!/usr/bin/env python3
"""Convert every page of paper.pdf to PNG at 150 DPI for visual review."""
import fitz  # PyMuPDF
import os

pdf_path = "/ai-inventor/aii_data/runs/run_q27XJGeAT3TE/4_gen_paper_repo/_4_assemble_paper/paper/workspace/paper.pdf"
output_dir = "/ai-inventor/aii_data/runs/run_q27XJGeAT3TE/4_gen_paper_repo/_4_assemble_paper/paper/workspace/page_images"
os.makedirs(output_dir, exist_ok=True)

doc = fitz.open(pdf_path)
dpi = 150
zoom = dpi / 72  # 72 DPI is the base

print(f"PDF has {len(doc)} pages")

for i, page in enumerate(doc):
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    out_path = os.path.join(output_dir, f"page_{i+1:02d}.png")
    pix.save(out_path)
    print(f"Saved page {i+1}: {out_path} ({pix.width}x{pix.height})")

doc.close()
print(f"Done. {len(os.listdir(output_dir))} images saved to {output_dir}")
