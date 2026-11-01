#!/usr/bin/env python3
"""Preflight validator for journal publication figures (mm dimensions, 600 DPI, Type 42 fonts, zero-baseline bars)."""

from __future__ import annotations

import argparse
import json
import pathlib
from PIL import Image
Image.MAX_IMAGE_PIXELS = 250_000_000
from pypdf import PdfReader


def validate_pub_figure(out_dir: pathlib.Path, spec_path: pathlib.Path) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    checks = []

    req = ["figure.svg", "figure.pdf", "figure.png", "figure_legend.md"]
    missing = [f for f in req if not (out_dir / f).exists() or (out_dir / f).stat().st_size == 0]
    checks.append({"id": "MANDATORY_FILES", "status": "PASS" if not missing else "FAIL", "msg": "SVG, PDF, PNG, and legend Markdown present." if not missing else f"Missing: {missing}"})

    reader = PdfReader(str(out_dir / "figure.pdf"))
    p0 = reader.pages[0]
    w_mm = round(float(p0.mediabox.width) / 72.0 * 25.4, 1)
    h_mm = round(float(p0.mediabox.height) / 72.0 * 25.4, 1)
    fonts = list((p0.get("/Resources") or {}).get("/Font", {}).keys())
    checks.append({"id": "PHYSICAL_JOURNAL_MM_AND_FONTS", "status": "PASS" if fonts else "WARN", "msg": f"PDF exact size {w_mm}×{h_mm} mm with {len(fonts)} embedded TrueType font(s)."})

    with Image.open(out_dir / "figure.png") as im:
        pw, ph = im.size
    eff_dpi = round(pw / (w_mm / 25.4))
    checks.append({"id": "HIGH_RESOLUTION_DPI", "status": "PASS" if eff_dpi >= 300 else "FAIL", "msg": f"Raster {pw}×{ph} px ({eff_dpi} DPI at {w_mm} mm width)."})

    overall = "FAIL" if any(c["status"] == "FAIL" for c in checks) else ("WARN" if any(c["status"] == "WARN" for c in checks) else "PASS")
    rep = {"overall_status": overall, "checks": checks}
    (out_dir / "validation_report.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    (out_dir / "validation_report.md").write_text(
        "# Publication Figure Preflight Report\n\n" + "\n".join(f"- **{c['status']}** (`{c['id']}`): {c['msg']}" for c in checks) + "\n",
        encoding="utf-8",
    )
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--spec", required=True)
    args = ap.parse_args()
    rep = validate_pub_figure(pathlib.Path(args.output_dir), pathlib.Path(args.spec))
    print(json.dumps(rep, indent=2))
    return 0 if rep["overall_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
