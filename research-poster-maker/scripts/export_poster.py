#!/usr/bin/env python3
"""
Phase 7 — Print-Ready PDF & Optional High-Res TIFF Export Engine.

Exports a poster to print-ready PDF using:
  1. LibreOffice Impress headless ('libreoffice'), when available and requested.
  2. Native ReportLab + svglib Vector Scene Engine ('reportlab_vector'),
     preserving exact physical MediaBox dimensions, embedded TrueType font
     subsets, and vector SVG plots on systems without LibreOffice.

Verifies resulting PDF physical dimensions, orientation, and embedded font
resources via pypdf.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List, Optional

from pypdf import PdfReader

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from poster_engine.pdf_renderer import (
    export_pptx_with_libreoffice,
    render_scene_to_vector_pdf,
)


def inspect_pdf_print_readiness(pdf_path: pathlib.Path, expected_w_in: Optional[float] = None, expected_h_in: Optional[float] = None) -> Dict[str, Any]:
    reader = PdfReader(str(pdf_path))
    n_pages = len(reader.pages)
    page = reader.pages[0]
    mb = page.mediabox
    w_pt = float(mb.width)
    h_pt = float(mb.height)
    w_in = round(w_pt / 72.0, 3)
    h_in = round(h_pt / 72.0, 3)
    orientation = "landscape" if w_in > h_in else ("portrait" if h_in > w_in else "square")

    # Inspect embedded /Font dictionary entries
    fonts_found: List[str] = []
    resources = page.get("/Resources") or {}
    font_dict = resources.get("/Font") or {}
    for _, f_ref in font_dict.items():
        try:
            f_obj = f_ref.get_object()
            base_font = str(f_obj.get("/BaseFont", ""))
            fonts_found.append(base_font)
        except Exception:
            pass

    dim_ok = True
    if expected_w_in is not None and expected_h_in is not None:
        dim_ok = (abs(w_in - expected_w_in) <= 0.08 and abs(h_in - expected_h_in) <= 0.08)

    return {
        "page_count": n_pages,
        "width_pt": round(w_pt, 2),
        "height_pt": round(h_pt, 2),
        "width_in": w_in,
        "height_in": h_in,
        "width_mm": round(w_in * 25.4, 1),
        "height_mm": round(h_in * 25.4, 1),
        "orientation": orientation,
        "embedded_fonts": fonts_found,
        "dimensions_match_target": dim_ok,
    }


def export_poster_pdf(
    pptx_path: Optional[pathlib.Path],
    scene_ir_path: Optional[pathlib.Path],
    out_pdf: pathlib.Path,
    backend: str = "auto",
    out_tiff: Optional[pathlib.Path] = None,
    tiff_dpi: int = 300,
) -> Dict[str, Any]:
    scene_dict: Optional[Dict[str, Any]] = None
    if scene_ir_path and scene_ir_path.exists():
        scene_dict = json.loads(scene_ir_path.read_text(encoding="utf-8"))

    export_info: Optional[Dict[str, Any]] = None
    notes: List[str] = []

    if backend in ("auto", "libreoffice") and pptx_path and pptx_path.exists():
        # Note: if poster exceeds 56 in, PPTX is at 50% scale whereas vector scene IR renders 100% full scale
        pptx_scale = float(scene_dict["dimensions"]["pptx_scale_factor"]) if scene_dict else 1.0
        if pptx_scale == 1.0 or backend == "libreoffice":
            lo_res = export_pptx_with_libreoffice(pptx_path, out_pdf)
            if lo_res:
                export_info = lo_res
            elif backend == "libreoffice":
                raise RuntimeError(
                    "LibreOffice ('soffice' / 'libreoffice') was explicitly requested but is not installed on this machine."
                )
            else:
                notes.append(
                    "LibreOffice headless binary not detected; used native ReportLab + svglib vector scene renderer "
                    "to produce true-scale PDF with embedded TrueType subsets and vector SVG charts."
                )
        else:
            notes.append(
                "Poster exceeds PowerPoint's 56-inch canvas limit; used ReportLab vector renderer to emit 1:1 full-size PDF "
                "(while .pptx is saved at exact 50% scale for 200% print enlargement)."
            )

    if export_info is None:
        if scene_dict is None:
            raise RuntimeError(
                "Cannot export PDF: LibreOffice is not installed and no poster_scene_ir.json was provided for ReportLab vector export."
            )
        export_info = render_scene_to_vector_pdf(scene_dict, out_pdf)

    exp_w = float(scene_dict["dimensions"]["width_in"]) if scene_dict else None
    exp_h = float(scene_dict["dimensions"]["height_in"]) if scene_dict else None
    pdf_audit = inspect_pdf_print_readiness(out_pdf, exp_w, exp_h)

    tiff_status: Optional[str] = None
    if out_tiff is not None:
        try:
            import pymupdf
            from PIL import Image

            doc = pymupdf.open(str(out_pdf))
            zoom = tiff_dpi / 72.0
            pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
            im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            out_tiff.parent.mkdir(parents=True, exist_ok=True)
            im.save(str(out_tiff), format="TIFF", dpi=(tiff_dpi, tiff_dpi), compression="tiff_lzw")
            tiff_status = str(out_tiff)
        except Exception as exc:
            notes.append(f"Optional TIFF export skipped/failed: {exc}")

    return {
        **export_info,
        "pdf_audit": pdf_audit,
        "tiff_path": tiff_status,
        "notes": notes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export research poster to verified print-ready PDF (and optional TIFF).")
    parser.add_argument("--pptx", help="Path to generated poster .pptx")
    parser.add_argument("--scene-ir", help="Path to poster_scene_ir.json")
    parser.add_argument("--output", required=True, help="Output PDF path")
    parser.add_argument("--backend", choices=["auto", "libreoffice", "reportlab"], default="auto")
    parser.add_argument("--tiff", help="Optional high-resolution TIFF output path")
    parser.add_argument("--tiff-dpi", type=int, default=300, help="Target DPI for optional TIFF export")
    args = parser.parse_args()

    res = export_poster_pdf(
        pptx_path=pathlib.Path(args.pptx) if args.pptx else None,
        scene_ir_path=pathlib.Path(args.scene_ir) if args.scene_ir else None,
        out_pdf=pathlib.Path(args.output),
        backend="reportlab_vector" if args.backend == "reportlab" else args.backend,
        out_tiff=pathlib.Path(args.tiff) if args.tiff else None,
        tiff_dpi=args.tiff_dpi,
    )
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
