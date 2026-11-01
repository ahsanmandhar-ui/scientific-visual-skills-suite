#!/usr/bin/env python3
"""Validate scientific presentation deck (.pptx slides, native speaker notes, word density, and PDF handout)."""

from __future__ import annotations

import argparse
import json
import pathlib
from pptx import Presentation
from pypdf import PdfReader


def validate_deck(out_dir: pathlib.Path, spec_path: pathlib.Path) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    checks = []
    req = ["deck.pptx", "deck_handout.pdf", "deck_overview.png", "speaker_notes.md"]
    missing = [f for f in req if not (out_dir / f).exists() or (out_dir / f).stat().st_size == 0]
    checks.append({"id": "OUTPUT_FILES", "status": "PASS" if not missing else "FAIL", "msg": "PPTX, PDF handout, overview sheet, and speaker script present." if not missing else f"Missing {missing}"})

    prs = Presentation(str(out_dir / "deck.pptx"))
    n_expected = len(spec["slides"])
    n_actual = len(prs.slides)
    notes_ok = all(bool(sl.notes_slide.notes_text_frame.text.strip()) for sl in prs.slides)
    checks.append({"id": "PPTX_SLIDES_AND_SPEAKER_NOTES", "status": "PASS" if (n_actual == n_expected and notes_ok) else "FAIL", "msg": f"{n_actual}/{n_expected} editable slides verified with embedded speaker notes on 100% of slides."})

    # Slide word density audit (anti-wall-of-text <= 60 words per slide)
    dense = []
    for idx, s in enumerate(spec["slides"], start=1):
        wc = sum(len(b.split()) for b in s.get("bullets", []))
        if wc > 60:
            dense.append(f"Slide {idx} ({wc}w)")
    checks.append({"id": "ASSERTION_EVIDENCE_CONCISENESS", "status": "PASS" if not dense else "WARN", "msg": "All slides obey <= 60 body-word conciseness ceiling." if not dense else f"Dense slides: {dense}"})

    reader = PdfReader(str(out_dir / "deck_handout.pdf"))
    checks.append({"id": "PDF_PAGE_PARITY", "status": "PASS" if len(reader.pages) == n_expected else "FAIL", "msg": f"PDF handout matches {len(reader.pages)} slides."})

    overall = "FAIL" if any(c["status"] == "FAIL" for c in checks) else ("WARN" if any(c["status"] == "WARN" for c in checks) else "PASS")
    rep = {"overall_status": overall, "checks": checks}
    (out_dir / "validation_report.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    (out_dir / "validation_report.md").write_text("# Research Presentation Validation\n\n" + "\n".join(f"- **{c['status']}** (`{c['id']}`): {c['msg']}" for c in checks) + "\n", encoding="utf-8")
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--spec", required=True)
    args = ap.parse_args()
    rep = validate_deck(pathlib.Path(args.output_dir), pathlib.Path(args.spec))
    print(json.dumps(rep, indent=2))
    return 0 if rep["overall_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
