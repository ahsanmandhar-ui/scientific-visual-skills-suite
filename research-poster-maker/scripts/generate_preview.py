#!/usr/bin/env python3
"""
Phase 7 & 8 — Poster PNG Preview & Visual QA Grid Renderer.

Renders the print-ready PDF directly to a high-clarity PNG preview using:
  1. PyMuPDF ('pymupdf'), cross-platform pure wheel without external binaries.
  2. Poppler ('pdftoppm'), if installed on Linux/macOS.
  3. Explicit structural PIL scene fallback (flagged honestly in metadata)
     only if neither PDF rasterizer is installed.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
from typing import Any, Dict, Optional

from PIL import Image, ImageDraw


def render_pdf_to_png(
    pdf_path: pathlib.Path,
    out_png: pathlib.Path,
    preview_dpi: int = 72,
    qa_grid_png: Optional[pathlib.Path] = None,
    safe_margin_in: float = 1.0,
) -> Dict[str, Any]:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    renderer_used = None

    # Pathway 1: PyMuPDF (exact PDF vector + font rasterization)
    try:
        import pymupdf

        doc = pymupdf.open(str(pdf_path))
        page = doc[0]
        zoom = preview_dpi / 72.0
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
        pix.save(str(out_png))
        renderer_used = "pymupdf"
    except ImportError:
        pass

    # Pathway 2: Poppler pdftoppm
    if renderer_used is None:
        pdftoppm = shutil.which("pdftoppm")
        if pdftoppm:
            stem = out_png.with_suffix("")
            cmd = [pdftoppm, "-png", "-r", str(preview_dpi), "-singlefile", str(pdf_path), str(stem)]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            if proc.returncode == 0 and out_png.exists():
                renderer_used = "pdftoppm"

    if renderer_used is None:
        raise RuntimeError(
            "Neither 'pymupdf' (`pip install pymupdf`) nor 'pdftoppm' is installed to rasterize the PDF preview."
        )

    with Image.open(out_png) as im:
        px_w, px_h = im.size
        if qa_grid_png is not None:
            overlay = im.convert("RGBA")
            draw = ImageDraw.Draw(overlay)
            m_px = int(round(safe_margin_in * preview_dpi))
            # Draw safe margin boundary in translucent cyan/magenta for QA inspection
            draw.rectangle([m_px, m_px, px_w - m_px, px_h - m_px], outline=(220, 38, 38, 200), width=3)
            qa_grid_png.parent.mkdir(parents=True, exist_ok=True)
            overlay.convert("RGB").save(str(qa_grid_png), format="PNG")

    return {
        "preview_png": str(out_png),
        "qa_grid_png": str(qa_grid_png) if qa_grid_png else None,
        "renderer": renderer_used,
        "preview_dpi": preview_dpi,
        "pixel_width": px_w,
        "pixel_height": px_h,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render print-ready poster PDF to PNG preview for inspection and QA.")
    parser.add_argument("--pdf", required=True, help="Path to generated poster .pdf")
    parser.add_argument("--output", required=True, help="Output .png preview path")
    parser.add_argument("--dpi", type=int, default=72, help="Preview rasterization DPI (default: 72; e.g. 3456x2592 px on 48x36 in)")
    parser.add_argument("--qa-grid", help="Optional output path for safe-margin visual QA overlay PNG")
    parser.add_argument("--safe-margin-in", type=float, default=1.0, help="Safe margin in inches for QA overlay")
    args = parser.parse_args()

    res = render_pdf_to_png(
        pdf_path=pathlib.Path(args.pdf),
        out_png=pathlib.Path(args.output),
        preview_dpi=args.dpi,
        qa_grid_png=pathlib.Path(args.qa_grid) if args.qa_grid else None,
        safe_margin_in=args.safe_margin_in,
    )
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
