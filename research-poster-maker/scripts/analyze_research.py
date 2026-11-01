#!/usr/bin/env python3
"""
Phase 3 — Research Input Analysis Engine for research-poster-maker.

Accepts research manuscripts (.docx, .pdf, .md, .txt, .json), structured
datasets (.csv, .xlsx), and existing figure/logo images (.png, .jpg, .svg).

Extracts and organizes the 18 canonical scientific poster fields without
fabricating missing values, identifies missing essential vs. optional fields,
profiles tabular datasets and image print PPI, and recommends an appropriate
poster template and layout strategy.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


CANONICAL_18_FIELDS: List[Tuple[str, str, bool]] = [
    ("title", "1. Research title", True),
    ("authors_affiliations", "2. Authors and affiliations", True),
    ("background", "3. Background", True),
    ("research_gap", "4. Research gap", False),
    ("objectives", "5. Objectives", True),
    ("study_design", "6. Study design", True),
    ("methods", "7. Methods", True),
    ("study_population", "8. Study population", True),
    ("sample_size", "9. Sample size", True),
    ("statistical_methods", "10. Statistical methods", False),
    ("primary_outcome", "11. Primary outcome", True),
    ("secondary_outcomes", "12. Secondary outcomes", False),
    ("important_findings", "13. Important findings", True),
    ("tables_and_figures", "14. Tables and figures", False),
    ("limitations", "15. Limitations", False),
    ("conclusion", "16. Conclusion", True),
    ("references", "17. References", False),
    ("funding_acknowledgements", "18. Funding and acknowledgements", False),
]

SECTION_SYNONYMS: Dict[str, List[str]] = {
    "background": ["background", "introduction", "rationale", "context"],
    "research_gap": ["research gap", "knowledge gap", "unmet need", "motivation"],
    "objectives": ["objective", "objectives", "aim", "aims", "purpose", "hypothesis"],
    "study_design": ["study design", "design", "trial design"],
    "methods": ["methods", "methodology", "materials and methods", "patients and methods", "procedures", "search strategy"],
    "study_population": ["study population", "participants", "patients", "cohort", "eligibility", "inclusion criteria"],
    "statistical_methods": ["statistical analysis", "statistical methods", "statistics", "data synthesis", "meta-analysis methods"],
    "primary_outcome": ["primary outcome", "primary endpoint", "main outcome"],
    "secondary_outcomes": ["secondary outcomes", "secondary endpoints", "subgroup analysis", "safety"],
    "important_findings": ["results", "findings", "key findings", "main findings", "synthesis of results"],
    "limitations": ["limitations", "strengths and limitations", "methodological considerations"],
    "conclusion": ["conclusion", "conclusions", "interpretation", "clinical implications", "summary"],
    "references": ["references", "bibliography", "citations", "key references"],
    "funding_acknowledgements": ["funding", "acknowledgements", "acknowledgments", "disclosures", "conflicts of interest", "registration"],
}


def _read_docx(path: pathlib.Path) -> Tuple[str, List[Dict[str, Any]]]:
    try:
        import docx
    except ImportError as exc:
        raise RuntimeError("python-docx is required to parse .docx manuscripts (`pip install python-docx`).") from exc

    doc = docx.Document(str(path))
    lines: List[str] = []
    for p in doc.paragraphs:
        txt = p.text.strip()
        if not txt:
            continue
        style_name = (p.style.name if p.style else "").lower()
        if "title" in style_name:
            lines.append(f"# {txt}")
        elif "heading 1" in style_name or "heading 2" in style_name:
            lines.append(f"## {txt}")
        else:
            lines.append(txt)

    tables_out: List[Dict[str, Any]] = []
    for t_i, tbl in enumerate(doc.tables):
        rows = [[cell.text.strip().replace("\n", " ") for cell in row.cells] for row in tbl.rows]
        if len(rows) >= 2:
            tables_out.append({
                "source": f"{path.name}:table_{t_i+1}",
                "headers": rows[0],
                "rows": rows[1:],
            })
    return "\n\n".join(lines), tables_out


def _read_pdf(path: pathlib.Path) -> Tuple[str, List[Dict[str, Any]]]:
    tables_out: List[Dict[str, Any]] = []
    # Prefer pdfplumber for text + table extraction, fall back to pymupdf or pypdf
    try:
        import pdfplumber

        pages_txt: List[str] = []
        with pdfplumber.open(str(path)) as pdf:
            for p_i, page in enumerate(pdf.pages):
                pages_txt.append(page.extract_text() or "")
                for t_i, raw_tbl in enumerate(page.extract_tables() or []):
                    cleaned = [[(c or "").strip().replace("\n", " ") for c in r] for r in raw_tbl if any(r)]
                    if len(cleaned) >= 2:
                        tables_out.append({
                            "source": f"{path.name}:p{p_i+1}_table_{t_i+1}",
                            "headers": cleaned[0],
                            "rows": cleaned[1:],
                        })
        return "\n\n".join(pages_txt), tables_out
    except ImportError:
        pass

    try:
        import pymupdf

        doc = pymupdf.open(str(path))
        return "\n\n".join(page.get_text("text") for page in doc), tables_out
    except ImportError:
        pass

    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return "\n\n".join((p.extract_text() or "") for p in reader.pages), tables_out
    except ImportError as exc:
        raise RuntimeError("Install pdfplumber, pymupdf, or pypdf to parse PDF manuscripts.") from exc


def _profile_tabular_file(path: pathlib.Path) -> Dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = list(csv.reader(f))
        if not reader:
            return {"file": str(path), "rows": 0, "columns": []}
        headers = reader[0]
        rows = reader[1:]
        return {
            "file": str(path),
            "format": "csv",
            "row_count": len(rows),
            "columns": headers,
            "preview_rows": rows[:8],
        }
    if suffix in (".xlsx", ".xlsm"):
        try:
            import openpyxl
        except ImportError as exc:
            raise RuntimeError("openpyxl is required to parse .xlsx datasets (`pip install openpyxl`).") from exc
        wb = openpyxl.load_workbook(str(path), data_only=True)
        sheets_info = []
        for sname in wb.sheetnames:
            ws = wb[sname]
            vals = [["" if v is None else str(v).strip() for v in row] for row in ws.iter_rows(values_only=True)]
            vals = [r for r in vals if any(r)]
            if vals:
                sheets_info.append({
                    "sheet": sname,
                    "row_count": len(vals) - 1,
                    "columns": vals[0],
                    "preview_rows": vals[1:9],
                })
        return {"file": str(path), "format": "xlsx", "sheets": sheets_info}
    return {"file": str(path), "format": suffix}


def _profile_image_file(path: pathlib.Path) -> Dict[str, Any]:
    if path.suffix.lower() == ".svg":
        return {"file": str(path), "format": "svg", "is_vector": True}
    try:
        from PIL import Image

        with Image.open(path) as im:
            w, h = im.size
            mode = im.mode
        return {
            "file": str(path),
            "format": path.suffix.lower().lstrip("."),
            "is_vector": False,
            "pixel_width": w,
            "pixel_height": h,
            "color_mode": mode,
            "max_300dpi_width_in": round(w / 300.0, 2),
            "max_150dpi_width_in": round(w / 150.0, 2),
        }
    except Exception as exc:
        return {"file": str(path), "error": str(exc)}


def _parse_sections_from_text(raw_text: str) -> Dict[str, Any]:
    """Extract structured sections, sample sizes, statistical tokens, and metadata conservatively."""
    lines = [ln.strip() for ln in raw_text.splitlines()]
    non_empty = [ln for ln in lines if ln]

    extracted: Dict[str, Any] = {k: None for k, _, _ in CANONICAL_18_FIELDS}

    # 1. Detect Title (first markdown H1 or first prominent non-metadata line)
    for ln in non_empty[:8]:
        if ln.startswith("# ") and not ln.startswith("## "):
            extracted["title"] = ln[2:].strip()
            break
    if not extracted["title"] and non_empty:
        first = re.sub(r"^(?:Title|Manuscript Title)\s*:\s*", "", non_empty[0], flags=re.I)
        if 12 <= len(first) <= 280:
            extracted["title"] = first

    # 2. Explicit inline key:value labels (common in structured abstracts)
    current_bucket: Optional[str] = None
    buckets: Dict[str, List[str]] = {k: [] for k in SECTION_SYNONYMS}
    author_candidates: List[str] = []

    for ln in non_empty:
        # Check Authors / Affiliations line
        m_auth = re.match(r"^(?:Authors?|Investigators?)\s*:\s*(.+)$", ln, flags=re.I)
        if m_auth:
            author_candidates.append(m_auth.group(1).strip())
            continue
        m_aff = re.match(r"^(?:Affiliations?|Institutions?|Departments?)\s*:\s*(.+)$", ln, flags=re.I)
        if m_aff:
            author_candidates.append(f"Affiliations: {m_aff.group(1).strip()}")
            continue

        # Check Markdown heading or "Heading: content"
        md_h = re.match(r"^#{2,4}\s+(.+)$", ln)
        if md_h:
            hdr_clean = md_h.group(1).strip().lower().rstrip(":")
            matched_key = None
            for b_key, syns in SECTION_SYNONYMS.items():
                if any(hdr_clean == s or hdr_clean.startswith(s) for s in syns):
                    matched_key = b_key
                    break
            current_bucket = matched_key
            continue

        inline_m = re.match(r"^([A-Za-z][A-Za-z\s/&\-]{2,36}):\s+(.+)$", ln)
        if inline_m:
            lbl = inline_m.group(1).strip().lower()
            rest = inline_m.group(2).strip()
            matched_key = None
            for b_key, syns in SECTION_SYNONYMS.items():
                if any(lbl == s or lbl.startswith(s) for s in syns):
                    matched_key = b_key
                    break
            if matched_key:
                current_bucket = matched_key
                buckets[matched_key].append(rest)
                continue

        if current_bucket:
            buckets[current_bucket].append(ln)

    if author_candidates:
        extracted["authors_affiliations"] = " | ".join(author_candidates)

    for b_key, collected in buckets.items():
        if collected:
            extracted[b_key] = "\n".join(collected).strip()

    # 3. Extract explicit sample size mentions (never guessing!)
    sample_matches = re.findall(
        r"\b(?:[Nn]\s*=\s*\d[\d,]*|\d[\d,]*\s+(?:patients|participants|adults|studies|trials|records|individuals|subjects))\b",
        raw_text,
    )
    if sample_matches:
        seen = []
        for m in sample_matches:
            if m not in seen:
                seen.append(m)
        extracted["sample_size"] = "; ".join(seen[:8])

    # 4. Detect study design phrases explicitly stated in text
    design_patterns = [
        r"(?:prospective|retrospective|multicenter|single-center|population-based|nationwide)?\s*(?:randomized controlled trial|observational cohort|cohort study|case-control study|cross-sectional study|systematic review and meta-analysis|systematic review|network meta-analysis|meta-analysis|diagnostic accuracy study)",
    ]
    if not extracted["study_design"]:
        for pat in design_patterns:
            dm = re.search(pat, raw_text, flags=re.I)
            if dm:
                extracted["study_design"] = dm.group(0).strip()
                break

    # 5. Extract research gap sentences if not in dedicated heading
    if not extracted["research_gap"]:
        gap_m = re.search(
            r"([^.?!]*\b(?:however|remains unclear|remains unknown|limited evidence|few studies|uncertain whether|gap in)\b[^.?!]*\.)",
            raw_text,
            flags=re.I,
        )
        if gap_m:
            extracted["research_gap"] = gap_m.group(1).strip()

    # 6. Extract primary outcome sentence if inside results/methods
    if not extracted["primary_outcome"]:
        po_m = re.search(
            r"([^.?!]*\b(?:primary (?:outcome|endpoint)|pooled (?:odds ratio|risk ratio|hazard ratio|estimate))\b[^.?!]*\.)",
            raw_text,
            flags=re.I,
        )
        if po_m:
            extracted["primary_outcome"] = po_m.group(1).strip()

    # 7. Harvest verbatim numerical/statistical expressions for integrity auditing
    stat_tokens = re.findall(
        r"(?:(?:OR|RR|HR|IRR|aHR|aOR|SMD|MD|AUC|I²|I2)\s*[=:]?\s*−?-?\d+(?:\.\d+)?%?|"
        r"95%\s*CI[,:\s]*\[?−?-?\d+(?:\.\d+)?\s*(?:to|[–\-−,])\s*−?-?\d+(?:\.\d+)?\]?|"
        r"\bp\s*[=<≤]\s*0?\.\d+|\b\d+(?:\.\d+)?%)",
        raw_text,
    )
    extracted["_verbatim_statistics"] = list(dict.fromkeys(stat_tokens))[:60]

    return extracted


def _recommend_archetype(raw_text: str, extracted: Dict[str, Any], tabular_files: List[Dict[str, Any]]) -> Dict[str, str]:
    low = raw_text.lower()
    word_count = len(raw_text.split())

    if "forest plot" in low or "meta-analysis" in low or "pooled" in low and ("i²" in low or "i2" in low or "heterogeneity" in low):
        return {
            "template_id": "meta-analysis",
            "layout_recipe": "systematic_review_prisma",
            "palette": "burgundy_offwhite",
            "font_pairing": "editorial_modern",
            "rationale": "Detected quantitative synthesis / heterogeneity / pooled effect terminology.",
        }
    if "prisma" in low or "systematic review" in low or "databases searched" in low:
        return {
            "template_id": "systematic-review",
            "layout_recipe": "systematic_review_prisma",
            "palette": "deep_teal",
            "font_pairing": "editorial_modern",
            "rationale": "Detected systematic review / PRISMA screening methodology.",
        }
    if any(k in low for k in ("person-years", "incidence rate", "surveillance", "age-standardized", "epidemiolog", "public health")):
        return {
            "template_id": "epidemiology",
            "layout_recipe": "timeline_flow",
            "palette": "forest_cream",
            "font_pairing": "classic_symposium",
            "rationale": "Detected population-level epidemiological / surveillance indicators.",
        }
    if word_count < 360 and not tabular_files:
        return {
            "template_id": "minimalist-editorial",
            "layout_recipe": "two_column_editorial",
            "palette": "monochrome_editorial",
            "font_pairing": "editorial_modern",
            "rationale": "Concise abstract-only input without external datasets; minimalist two-column editorial layout prevents artificial padding.",
        }
    if any(k in low for k in ("patients", "clinical", "hospital", "randomized", "cohort", "kaplan-meier", "hazard ratio")):
        return {
            "template_id": "clinical-research",
            "layout_recipe": "clinical_workflow",
            "palette": "academic_navy",
            "font_pairing": "clinical_precision",
            "rationale": "Detected clinical patient cohort / trial outcome structure.",
        }
    return {
        "template_id": "experimental-research",
        "layout_recipe": "asymmetric_grid",
        "palette": "charcoal_ivory",
        "font_pairing": "swiss_scientific",
        "rationale": "General experimental / scientific manuscript structure.",
    }


def analyze_inputs(input_paths: List[pathlib.Path]) -> Dict[str, Any]:
    text_blobs: List[str] = []
    doc_tables: List[Dict[str, Any]] = []
    tabular_profiles: List[Dict[str, Any]] = []
    image_profiles: List[Dict[str, Any]] = []
    structured_json: Optional[Dict[str, Any]] = None

    expanded: List[pathlib.Path] = []
    for p in input_paths:
        if p.is_dir():
            expanded.extend(sorted(f for f in p.rglob("*") if f.is_file()))
        elif p.exists():
            expanded.append(p)
        else:
            raise FileNotFoundError(f"Input path does not exist: {p}")

    for fpath in expanded:
        suf = fpath.suffix.lower()
        if suf == ".docx":
            txt, tbls = _read_docx(fpath)
            text_blobs.append(txt)
            doc_tables.extend(tbls)
        elif suf == ".pdf":
            txt, tbls = _read_pdf(fpath)
            text_blobs.append(txt)
            doc_tables.extend(tbls)
        elif suf in (".md", ".txt", ".tex", ".rst"):
            text_blobs.append(fpath.read_text(encoding="utf-8", errors="replace"))
        elif suf == ".json":
            loaded = json.loads(fpath.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                structured_json = loaded
                text_blobs.append(json.dumps(loaded, ensure_ascii=False))
        elif suf in (".csv", ".xlsx", ".xlsm"):
            tabular_profiles.append(_profile_tabular_file(fpath))
        elif suf in (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".svg"):
            image_profiles.append(_profile_image_file(fpath))

    combined_text = "\n\n".join(text_blobs).strip()
    extracted = _parse_sections_from_text(combined_text) if combined_text else {k: None for k, _, _ in CANONICAL_18_FIELDS}

    # Merge explicit structured JSON fields if supplied
    if structured_json:
        for k, _, _ in CANONICAL_18_FIELDS:
            if structured_json.get(k) and not extracted.get(k):
                extracted[k] = structured_json[k]

    if doc_tables or tabular_profiles or image_profiles:
        extracted["tables_and_figures"] = {
            "manuscript_tables": doc_tables,
            "datasets": tabular_profiles,
            "images": image_profiles,
        }

    missing_essential: List[str] = []
    missing_optional: List[str] = []
    present_fields: List[str] = []

    for f_key, f_label, is_essential in CANONICAL_18_FIELDS:
        val = extracted.get(f_key)
        if val is None or (isinstance(val, str) and not val.strip()):
            if is_essential:
                missing_essential.append(f_label)
            else:
                missing_optional.append(f_label)
        else:
            present_fields.append(f_label)

    clarification_questions: List[str] = []
    if missing_essential:
        clarification_questions.append(
            "Essential study metadata missing from source files (never fabricated): "
            + ", ".join(missing_essential)
            + ". Please supply these if available or confirm omission."
        )
    clarification_questions.append(
        "Confirm conference poster dimensions & orientation (e.g., 48 × 36 in landscape or ISO A0 portrait) if specified by the venue."
    )

    recommendation = _recommend_archetype(combined_text, extracted, tabular_profiles)

    return {
        "source_files": [str(p) for p in expanded],
        "source_word_count": len(combined_text.split()),
        "extracted_fields": {k: v for k, v in extracted.items() if not k.startswith("_")},
        "verbatim_statistics": extracted.get("_verbatim_statistics", []),
        "completeness": {
            "present_count": len(present_fields),
            "total_canonical_fields": len(CANONICAL_18_FIELDS),
            "present_fields": present_fields,
            "missing_essential": missing_essential,
            "missing_optional": missing_optional,
        },
        "clarification_needed": clarification_questions,
        "design_recommendation": recommendation,
        "raw_corpus_excerpt": combined_text[:12000],
    }


def _format_summary_md(report: Dict[str, Any]) -> str:
    comp = report["completeness"]
    rec = report["design_recommendation"]
    ef = report["extracted_fields"]

    lines = [
        "# Research Input Analysis Report",
        "",
        f"- **Source Files Analyzed:** {len(report['source_files'])}",
        f"- **Source Word Count:** {report['source_word_count']:,} words",
        f"- **Canonical Fields Extracted:** {comp['present_count']} / {comp['total_canonical_fields']}",
        "",
        "## Recommended Poster Direction",
        "",
        f"- **Template:** `{rec['template_id']}`",
        f"- **Layout Recipe:** `{rec['layout_recipe']}`",
        f"- **Color Palette:** `{rec['palette']}`",
        f"- **Typography Pairing:** `{rec['font_pairing']}`",
        f"- **Rationale:** {rec['rationale']}",
        "",
        "## Missing Information Audit (Zero-Fabrication Check)",
        "",
    ]
    if comp["missing_essential"]:
        lines.append("### Essential Fields Not Found in Source (Clarification Recommended)")
        for item in comp["missing_essential"]:
            lines.append(f"- [ ] {item}")
        lines.append("")
    else:
        lines.append("- All essential scientific fields were located in the source material.")
        lines.append("")

    if comp["missing_optional"]:
        lines.append("### Optional / Secondary Fields Not Present (Omit Cleanly Unless Supplied)")
        for item in comp["missing_optional"]:
            lines.append(f"- {item}")
        lines.append("")

    lines.append("## Extracted 18-Field Summary")
    lines.append("")
    for key, label, _ in CANONICAL_18_FIELDS:
        val = ef.get(key)
        lines.append(f"### {label}")
        if val is None:
            lines.append("_Not present in supplied source material._")
        elif isinstance(val, (dict, list)):
            lines.append(f"```json\n{json.dumps(val, indent=2)[:1200]}\n```")
        else:
            lines.append(str(val))
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze scientific manuscripts, datasets, and figures for poster generation.")
    parser.add_argument("inputs", nargs="+", help="Paths to manuscript (.docx/.pdf/.md/.txt), dataset (.csv/.xlsx), or asset files/folders")
    parser.add_argument("--output-dir", default=".", help="Directory to write research_extraction.json and extraction_summary.md")
    args = parser.parse_args()

    out_dir = pathlib.Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = analyze_inputs([pathlib.Path(p) for p in args.inputs])

    json_path = out_dir / "research_extraction.json"
    md_path = out_dir / "extraction_summary.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(_format_summary_md(report), encoding="utf-8")

    print(f"Extracted {report['completeness']['present_count']}/18 canonical fields -> {json_path}")
    if report["completeness"]["missing_essential"]:
        print("Missing essential fields:", ", ".join(report["completeness"]["missing_essential"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
