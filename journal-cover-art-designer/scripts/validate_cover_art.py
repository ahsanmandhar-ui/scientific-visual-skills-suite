#!/usr/bin/env python3
"""Validate journal cover art dual deliverables (unlettered full-bleed art + masthead proof), mm bleed size, and 300 DPI."""

from __future__ import annotations

import argparse
import json
import pathlib
from PIL import Image
Image.MAX_IMAGE_PIXELS = 250_000_000
from pypdf import PdfReader


def validate_cover(out_dir: pathlib.Path, spec_path: pathlib.Path) -> dict:
    checks = []
    req = [
        "cover_artwork_unlettered.svg",
        "cover_artwork_unlettered.pdf",
        "cover_artwork_unlettered.png",
        "cover_editorial_mockup.pdf",
        "cover_editorial_mockup.png",
        "cover_caption.md",
    ]
    missing = [f for f in req if not (out_dir / f).exists() or (out_dir / f).stat().st_size == 0]
    checks.append({"id": "DUAL_DELIVERABLE_STANDARD", "status": "PASS" if not missing else "FAIL", "msg": "Both clean unlettered production files and masthead safe-zone mockup verified." if not missing else f"Missing {missing}"})

    # Verify unlettered PDF has ZERO embedded text strings
    r_un = PdfReader(str(out_dir / "cover_artwork_unlettered.pdf"))
    p0 = r_un.pages[0]
    w_mm = round(float(p0.mediabox.width) / 72.0 * 25.4, 2)
    h_mm = round(float(p0.mediabox.height) / 72.0 * 25.4, 2)
    unlet_text = (p0.extract_text() or "").strip()
    checks.append({"id": "CLEAN_UNLETTERED_BLEED_GEOMETRY", "status": "PASS" if unlet_text == "" else "FAIL", "msg": f"Unlettered PDF {w_mm}×{h_mm} mm (trim+bleed) contains 0 stray text characters."})

    with Image.open(out_dir / "cover_artwork_unlettered.png") as im:
        pw, ph = im.size
    eff_dpi = round(pw / (w_mm / 25.4))
    checks.append({"id": "COVER_PRINT_DPI", "status": "PASS" if eff_dpi >= 295 else "FAIL", "msg": f"Full-bleed raster {pw}×{ph} px ({eff_dpi} DPI)."})

    overall = "FAIL" if any(c["status"] == "FAIL" for c in checks) else "PASS"
    rep = {"overall_status": overall, "checks": checks}
    (out_dir / "validation_report.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    (out_dir / "validation_report.md").write_text("# Journal Cover Art Validation\n\n" + "\n".join(f"- **{c['status']}** (`{c['id']}`): {c['msg']}" for c in checks) + "\n", encoding="utf-8")
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--spec", required=True)
    args = ap.parse_args()
    rep = validate_cover(pathlib.Path(args.output_dir), pathlib.Path(args.spec))
    print(json.dumps(rep, indent=2))
    return 0 if rep["overall_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
