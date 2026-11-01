#!/usr/bin/env python3
"""Validate clinical trial visual outputs & enforce strict CONSORT participant count closure."""

from __future__ import annotations

import argparse
import json
import pathlib
from PIL import Image
Image.MAX_IMAGE_PIXELS = 250_000_000
from pypdf import PdfReader


def validate_trial(out_dir: pathlib.Path, spec_path: pathlib.Path) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    checks = []
    req = ["clinical_trial_visual.svg", "clinical_trial_visual.pdf", "clinical_trial_visual.png", "clinical_trial_visual.pptx"]
    missing = [f for f in req if not (out_dir / f).exists() or (out_dir / f).stat().st_size == 0]
    checks.append({"id": "OUTPUT_FILES", "status": "PASS" if not missing else "FAIL", "msg": "All SVG/PDF/PNG/PPTX files verified." if not missing else f"Missing {missing}"})

    # Strict CONSORT participant conservation audit
    cf = spec["consort"]
    assessed = int(cf["assessed"])
    excl = sum(int(r["n"]) for r in cf["excluded_reasons"])
    rand = int(cf["randomized"])
    alloc_sum = sum(int(a["allocated"]) for a in cf["arms"])

    arith_errors = []
    if assessed - excl != rand:
        arith_errors.append(f"Enrollment mismatch: {assessed} - {excl} != {rand}")
    if alloc_sum != rand:
        arith_errors.append(f"Allocation mismatch: sum(arms)={alloc_sum} != randomized={rand}")
    for a in cf["arms"]:
        pop = a.get("population", "ITT").upper()
        if pop == "ITT" and int(a["analyzed"]) > int(a["allocated"]):
            arith_errors.append(f"{a['name']}: analyzed > allocated")
        elif pop != "ITT" and int(a["allocated"]) - int(a["lost_to_followup"]) - int(a["discontinued"]) != int(a["analyzed"]):
            arith_errors.append(f"{a['name']} PP mismatch")

    checks.append({
        "id": "CONSORT_COUNT_CLOSURE",
        "status": "PASS" if not arith_errors else "FAIL",
        "msg": f"CONSORT arithmetic exact: {assessed} assessed - {excl} excluded = {rand} randomized = {alloc_sum} allocated." if not arith_errors else "; ".join(arith_errors),
    })

    reader = PdfReader(str(out_dir / "clinical_trial_visual.pdf"))
    w_in = round(float(reader.pages[0].mediabox.width) / 72.0, 2)
    with Image.open(out_dir / "clinical_trial_visual.png") as im:
        pw, ph = im.size
    dpi = round(pw / max(0.1, w_in))
    checks.append({"id": "PRINT_RESOLUTION", "status": "PASS" if dpi >= 280 else "FAIL", "msg": f"PNG {pw}×{ph} px ({dpi} DPI)."})

    overall = "FAIL" if any(c["status"] == "FAIL" for c in checks) else "PASS"
    rep = {"overall_status": overall, "checks": checks}
    (out_dir / "validation_report.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    (out_dir / "validation_report.md").write_text("# Clinical Trial Visual Validation\n\n" + "\n".join(f"- **{c['status']}** (`{c['id']}`): {c['msg']}" for c in checks) + "\n", encoding="utf-8")
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--spec", required=True)
    args = ap.parse_args()
    rep = validate_trial(pathlib.Path(args.output_dir), pathlib.Path(args.spec))
    print(json.dumps(rep, indent=2))
    return 0 if rep["overall_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
