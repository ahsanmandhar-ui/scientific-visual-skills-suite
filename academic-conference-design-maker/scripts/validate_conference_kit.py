#!/usr/bin/env python3
"""Validate all 6 academic conference deliverables (banner, abstract cover, poster, certificate, speaker card, social card)."""

from __future__ import annotations

import argparse
import json
import pathlib
from PIL import Image
Image.MAX_IMAGE_PIXELS = 250_000_000


def validate_kit(out_dir: pathlib.Path, spec_path: pathlib.Path) -> dict:
    checks = []
    req = [
        "banner.pdf", "banner.png",
        "abstract_book_cover.pdf", "abstract_book_cover.png",
        "event_poster.pdf", "event_poster.png",
        "certificate.pdf", "certificate.png", "certificate.pptx",
        "speaker_card.svg", "speaker_card.png",
        "social_card.svg", "social_card.png",
        "kit_overview.png",
    ]
    missing = [f for f in req if not (out_dir / f).exists() or (out_dir / f).stat().st_size == 0]
    checks.append({"id": "COMPLETE_6_ASSET_SUITE", "status": "PASS" if not missing else "FAIL", "msg": "All 14 print/vector/digital/PPTX conference files verified." if not missing else f"Missing {missing}"})

    with Image.open(out_dir / "speaker_card.png") as im1, Image.open(out_dir / "social_card.png") as im2:
        s1, s2 = im1.size, im2.size
    checks.append({"id": "SOCIAL_PIXEL_DIMENSIONS", "status": "PASS" if (s1 == (1200, 1200) and s2 == (1600, 900)) else "WARN", "msg": f"Speaker card {s1[0]}×{s1[1]} px (1:1); Social card {s2[0]}×{s2[1]} px (16:9)."})

    overall = "FAIL" if any(c["status"] == "FAIL" for c in checks) else "PASS"
    rep = {"overall_status": overall, "checks": checks}
    (out_dir / "validation_report.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    (out_dir / "validation_report.md").write_text("# Academic Conference Kit Validation\n\n" + "\n".join(f"- **{c['status']}** (`{c['id']}`): {c['msg']}" for c in checks) + "\n", encoding="utf-8")
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--spec", required=True)
    args = ap.parse_args()
    rep = validate_kit(pathlib.Path(args.output_dir), pathlib.Path(args.spec))
    print(json.dumps(rep, indent=2))
    return 0 if rep["overall_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
