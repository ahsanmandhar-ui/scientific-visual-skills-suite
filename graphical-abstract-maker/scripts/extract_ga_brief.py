#!/usr/bin/env python3
"""Extract concise study design, population, intervention, and quantitative findings for a graphical abstract."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
from typing import Any, Dict, List


def extract_brief(path: pathlib.Path) -> Dict[str, Any]:
    suf = path.suffix.lower()
    if suf == ".docx":
        import docx
        doc = docx.Document(str(path))
        text = "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
    elif suf == ".pdf":
        from pypdf import PdfReader
        text = "\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)
    else:
        text = path.read_text(encoding="utf-8", errors="replace")

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    title = re.sub(r"^#+\s*|^Title:\s*", "", lines[0], flags=re.I) if lines else ""
    stats = list(dict.fromkeys(re.findall(
        r"(?:(?:OR|RR|HR|aHR|AUC|MD|Δ)\s*[=:]?\s*−?-?\d+(?:\.\d+)?%?|"
        r"95%\s*CI[,:\s]*\[?−?-?\d+(?:\.\d+)?[–\-−,\sto]+\d+(?:\.\d+)?\]?|"
        r"\bp\s*[=<≤]\s*0?\.\d+|\b[Nn]\s*=\s*\d[\d,]*)",
        text,
    )))

    missing: List[str] = []
    if not title:
        missing.append("title")
    if not stats:
        missing.append("quantitative_outcomes")

    return {
        "source_file": str(path),
        "title": title,
        "word_count": len(text.split()),
        "verbatim_statistics": stats[:30],
        "missing_essential": missing,
        "excerpt": text[:4000],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract graphical abstract brief from manuscript.")
    ap.add_argument("input", help="Manuscript file (.md, .txt, .docx, .pdf)")
    ap.add_argument("--output", required=True, help="Output JSON path")
    args = ap.parse_args()
    out = pathlib.Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    brief = extract_brief(pathlib.Path(args.input))
    out.write_text(json.dumps(brief, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Extracted GA brief ({len(brief['verbatim_statistics'])} statistical tokens) -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
