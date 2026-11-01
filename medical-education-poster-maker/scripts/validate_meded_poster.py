#!/usr/bin/env python3
"""Validate medical education teaching poster outputs, dimensions, PDF fonts, and pedagogical modules."""

from __future__ import annotations

import argparse
import json
import pathlib
from PIL import Image
Image.MAX_IMAGE_PIXELS = 250_000_000
from pypdf import PdfReader


def validate_meded(out_dir: pathlib.Path, spec_path: pathlib.Path) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    checks = []
    req = ["meded_poster.svg", "meded_poster.pdf", "meded_poster.png", "meded_poster.pptx"]
    missing = [f for f in req if not (out_dir / f).exists() or (out_dir / f).stat().st_size == 0]
    checks.append({"id": "OUTPUT_FILES", "status": "PASS" if not missing else "FAIL", "msg": "All SVG/PDF/PNG/PPTX teaching poster files present." if not missing else f"Missing {missing}"})

    reader = PdfReader(str(out_dir / "meded_poster.pdf"))
    p0 = reader.pages[0]
    w_in = round(float(p0.mediabox.width) / 72.0, 2)
    h_in = round(float(p0.mediabox.height) / 72.0, 2)
    fonts = list((p0.get("/Resources") or {}).get("/Font", {}).keys())
    checks.append({"id": "PDF_PRINT_DIMENSIONS_AND_FONTS", "status": "PASS" if fonts else "WARN", "msg": f"PDF {w_in}×{h_in} in with {len(fonts)} embedded TrueType font(s)."})

    with Image.open(out_dir / "meded_poster.png") as im:
        pw, ph = im.size
    dpi = round(pw / max(0.1, w_in))
    checks.append({"id": "RASTER_PRINT_DPI", "status": "PASS" if dpi >= 150 else "FAIL", "msg": f"PNG {pw}×{ph} px ({dpi} DPI)."})

    has_osce = bool(spec.get("osce_checklist") and spec.get("matrix") and spec.get("diagnostic_algorithm"))
    checks.append({"id": "PEDAGOGICAL_COMPLETENESS", "status": "PASS" if has_osce else "WARN", "msg": "Diagnostic algorithm, classification matrix, and OSCE checklist verified."})

    overall = "FAIL" if any(c["status"] == "FAIL" for c in checks) else "PASS"
    rep = {"overall_status": overall, "checks": checks}
    (out_dir / "validation_report.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    (out_dir / "validation_report.md").write_text("# Medical Education Poster Validation\n\n" + "\n".join(f"- **{c['status']}** (`{c['id']}`): {c['msg']}" for c in checks) + "\n", encoding="utf-8")
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--spec", required=True)
    args = ap.parse_args()
    rep = validate_meded(pathlib.Path(args.output_dir), pathlib.Path(args.spec))
    print(json.dumps(rep, indent=2))
    return 0 if rep["overall_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
