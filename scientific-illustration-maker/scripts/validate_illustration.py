#!/usr/bin/env python3
"""Validate vector scientific illustration outputs, editable SVG primitives, node non-overlap, and DPI."""

from __future__ import annotations

import argparse
import json
import math
import pathlib
from PIL import Image
Image.MAX_IMAGE_PIXELS = 250_000_000
from pypdf import PdfReader


def validate_illustration(out_dir: pathlib.Path, spec_path: pathlib.Path) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    checks = []
    req = ["illustration.svg", "illustration.pdf", "illustration.png"]
    missing = [f for f in req if not (out_dir / f).exists() or (out_dir / f).stat().st_size == 0]
    checks.append({"id": "VECTOR_AND_RASTER_FILES", "status": "PASS" if not missing else "FAIL", "msg": "SVG, PDF, and PNG present." if not missing else f"Missing {missing}"})

    svg_txt = (out_dir / "illustration.svg").read_text(encoding="utf-8", errors="ignore")
    has_svg_text = "<text" in svg_txt
    checks.append({"id": "EDITABLE_SVG_TEXT", "status": "PASS" if has_svg_text else "WARN", "msg": "SVG preserves editable <text> elements for Inkscape/Illustrator."})

    # Node collision check
    nodes = spec.get("nodes", [])
    collisions = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            d = math.hypot(float(nodes[i]["x"]) - float(nodes[j]["x"]), float(nodes[i]["y"]) - float(nodes[j]["y"]))
            if d < 10.0:
                collisions.append(f"{nodes[i]['id']}<->{nodes[j]['id']}")
    checks.append({"id": "NODE_SPATIAL_SEPARATION", "status": "PASS" if not collisions else "WARN", "msg": "Zero overlapping pathway nodes." if not collisions else f"Close nodes: {collisions}"})

    reader = PdfReader(str(out_dir / "illustration.pdf"))
    p0 = reader.pages[0]
    w_in = round(float(p0.mediabox.width) / 72.0, 2)
    with Image.open(out_dir / "illustration.png") as im:
        pw, ph = im.size
    dpi = round(pw / max(0.1, w_in))
    checks.append({"id": "RASTER_DPI", "status": "PASS" if dpi >= 300 else "FAIL", "msg": f"PNG {pw}×{ph} px ({dpi} DPI)."})

    overall = "FAIL" if any(c["status"] == "FAIL" for c in checks) else ("WARN" if any(c["status"] == "WARN" for c in checks) else "PASS")
    rep = {"overall_status": overall, "checks": checks}
    (out_dir / "validation_report.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    (out_dir / "validation_report.md").write_text("# Scientific Illustration Validation\n\n" + "\n".join(f"- **{c['status']}** (`{c['id']}`): {c['msg']}" for c in checks) + "\n", encoding="utf-8")
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--spec", required=True)
    args = ap.parse_args()
    rep = validate_illustration(pathlib.Path(args.output_dir), pathlib.Path(args.spec))
    print(json.dumps(rep, indent=2))
    return 0 if rep["overall_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
