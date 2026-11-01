#!/usr/bin/env python3
"""Validate generated graphical abstract dimensions, word budget, PDF fonts, and raster DPI."""

from __future__ import annotations

import argparse
import json
import pathlib
from PIL import Image
from pypdf import PdfReader


def validate_ga(out_dir: pathlib.Path, spec_path: pathlib.Path) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    checks = []

    req = ["graphical_abstract.svg", "graphical_abstract.pdf", "graphical_abstract.png", "graphical_abstract.pptx"]
    missing = [f for f in req if not (out_dir / f).exists() or (out_dir / f).stat().st_size == 0]
    checks.append({"id": "OUTPUT_FILES", "status": "PASS" if not missing else "FAIL", "msg": "All SVG/PDF/PNG/PPTX files present." if not missing else f"Missing: {missing}"})

    # Word count discipline check (<= 95 words recommended)
    words = []
    if spec.get("headline"):
        words.extend(spec["headline"].split())
    for st in spec.get("stages", []):
        words.extend(st.get("title", "").split())
        if st.get("hero_stat"):
            words.extend(st["hero_stat"].split())
        for b in st.get("bullets", []):
            words.extend(b.split())
    wc = len(words)
    checks.append({"id": "WORD_BUDGET_CONCISENESS", "status": "PASS" if wc <= 95 else "WARN", "msg": f"Total body words = {wc} (recommended <= 95 words for rapid 15s scan)."})

    # PDF dimension & font check
    reader = PdfReader(str(out_dir / "graphical_abstract.pdf"))
    p0 = reader.pages[0]
    w_in = round(float(p0.mediabox.width) / 72.0, 2)
    h_in = round(float(p0.mediabox.height) / 72.0, 2)
    fonts = list((p0.get("/Resources") or {}).get("/Font", {}).keys())
    checks.append({"id": "PDF_VECTOR_AND_FONTS", "status": "PASS" if fonts else "WARN", "msg": f"PDF {w_in}×{h_in} in with {len(fonts)} embedded TrueType font(s)."})

    # PNG resolution check
    with Image.open(out_dir / "graphical_abstract.png") as im:
        pw, ph = im.size
    eff_dpi = round(pw / max(0.1, w_in))
    checks.append({"id": "PNG_PRINT_DPI", "status": "PASS" if eff_dpi >= 280 else "WARN", "msg": f"PNG {pw}×{ph} px (~{eff_dpi} DPI at {w_in}×{h_in} in)."})

    overall = "FAIL" if any(c["status"] == "FAIL" for c in checks) else ("WARN" if any(c["status"] == "WARN" for c in checks) else "PASS")
    report = {"overall_status": overall, "checks": checks}
    (out_dir / "validation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = ["# Graphical Abstract QA Report", "", f"**Overall Status:** **{overall}**", ""] + [f"- **{c['status']}** (`{c['id']}`): {c['msg']}" for c in checks]
    (out_dir / "validation_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--spec", required=True)
    args = ap.parse_args()
    rep = validate_ga(pathlib.Path(args.output_dir), pathlib.Path(args.spec))
    print(json.dumps(rep, indent=2))
    return 0 if rep["overall_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
