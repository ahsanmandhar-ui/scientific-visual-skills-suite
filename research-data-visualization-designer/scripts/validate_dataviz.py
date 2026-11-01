#!/usr/bin/env python3
"""Validate statistical data visualization outputs, SHA-256 provenance manifest, and executable reproduce_figure.py."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = 250_000_000


def validate_dataviz(out_dir: pathlib.Path, spec_path: pathlib.Path) -> dict:
    checks = []
    req = ["dataviz_figure.svg", "dataviz_figure.pdf", "dataviz_figure.png", "reproduce_figure.py", "reproducibility_manifest.json"]
    missing = [f for f in req if not (out_dir / f).exists() or (out_dir / f).stat().st_size == 0]
    checks.append({"id": "OUTPUT_ARTIFACTS", "status": "PASS" if not missing else "FAIL", "msg": "Vector/raster figures, reproduce_figure.py, and SHA-256 manifest present." if not missing else f"Missing {missing}"})

    manifest = json.loads((out_dir / "reproducibility_manifest.json").read_text(encoding="utf-8"))
    has_sha = len(manifest.get("dataset_sha256", "")) == 64
    checks.append({"id": "SHA256_DATA_PROVENANCE", "status": "PASS" if has_sha else "FAIL", "msg": f"Dataset SHA-256 checksum recorded ({manifest.get('dataset_sha256', '')[:16]}...)."})

    rc = subprocess.call([sys.executable, str(out_dir / "reproduce_figure.py"), "--verify-only"])
    checks.append({"id": "REPRODUCIBLE_CODE_EXECUTION", "status": "PASS" if rc == 0 else "FAIL", "msg": "reproduce_figure.py executed cleanly (exit code 0)."})

    with Image.open(out_dir / "dataviz_figure.png") as im:
        pw, ph = im.size
    checks.append({"id": "HIGH_DPI_RASTER", "status": "PASS" if pw >= 2400 else "WARN", "msg": f"PNG dimensions {pw}×{ph} px."})

    overall = "FAIL" if any(c["status"] == "FAIL" for c in checks) else "PASS"
    rep = {"overall_status": overall, "checks": checks}
    (out_dir / "validation_report.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    (out_dir / "validation_report.md").write_text("# Research Data Visualization Validation\n\n" + "\n".join(f"- **{c['status']}** (`{c['id']}`): {c['msg']}" for c in checks) + "\n", encoding="utf-8")
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--spec", required=True)
    args = ap.parse_args()
    rep = validate_dataviz(pathlib.Path(args.output_dir), pathlib.Path(args.spec))
    print(json.dumps(rep, indent=2))
    return 0 if rep["overall_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
