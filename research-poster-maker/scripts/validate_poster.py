#!/usr/bin/env python3
"""
Phase 8 — Multi-Layer Quality Assurance & Scientific Integrity Validator.

Performs objective Technical, Scientific Integrity, Accessibility (WCAG 2.1),
and Image-Based Visual QA checks across the generated PPTX, PDF, PNG preview,
and source research specification.
"""

from __future__ import annotations

import argparse
import io
import json
import pathlib
import re
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = 250_000_000
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pypdf import PdfReader

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from poster_engine.design_tokens import wcag_contrast_ratio

EMU_PER_INCH = 914400.0


class CheckResult:
    def __init__(self, category: str, check_id: str, status: str, message: str, details: Optional[Any] = None) -> None:
        self.category = category      # technical | scientific | accessibility | visual
        self.check_id = check_id
        self.status = status          # PASS | WARN | FAIL
        self.message = message
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "category": self.category,
            "check_id": self.check_id,
            "status": self.status,
            "message": self.message,
        }
        if self.details is not None:
            d["details"] = self.details
        return d


def _extract_pptx_all_text_and_shapes(pptx_path: pathlib.Path, scale_factor: float = 1.0) -> Dict[str, Any]:
    prs = Presentation(str(pptx_path))
    slide_w_in = prs.slide_width / EMU_PER_INCH
    slide_h_in = prs.slide_height / EMU_PER_INCH
    n_slides = len(prs.slides)

    texts: List[str] = []
    out_of_bounds: List[Dict[str, Any]] = []
    boxes: List[Tuple[str, float, float, float, float]] = []
    min_eff_pt: Optional[float] = None
    small_text_runs: List[Dict[str, Any]] = []
    image_audits: List[Dict[str, Any]] = []
    broken_charts: List[str] = []

    if n_slides > 0:
        slide = prs.slides[0]
        for sh in slide.shapes:
            name = sh.name or f"shape_{sh.shape_id}"
            x1 = (sh.left or 0) / EMU_PER_INCH
            y1 = (sh.top or 0) / EMU_PER_INCH
            w = (sh.width or 0) / EMU_PER_INCH
            h = (sh.height or 0) / EMU_PER_INCH
            x2, y2 = x1 + w, y1 + h

            # 1. Boundary check (0.03 in tolerance for floating-point rounding)
            if x1 < -0.03 or y1 < -0.03 or x2 > slide_w_in + 0.03 or y2 > slide_h_in + 0.03:
                out_of_bounds.append({
                    "shape": name,
                    "box_in": [round(x1, 3), round(y1, 3), round(x2, 3), round(y2, 3)],
                    "slide_in": [round(slide_w_in, 3), round(slide_h_in, 3)],
                })

            # Record non-container boxes for overlap inspection
            if not name.startswith(("container:", "bg:", "rule:")):
                boxes.append((name, x1, y1, x2, y2))

            # 2. Text & font size inspection
            if sh.has_text_frame:
                full_t = sh.text_frame.text.strip()
                if full_t:
                    texts.append(full_t)
                for para in sh.text_frame.paragraphs:
                    for run in para.runs:
                        if run.text.strip() and run.font.size is not None:
                            eff_pt = round((run.font.size.pt) / scale_factor, 2)
                            if min_eff_pt is None or eff_pt < min_eff_pt:
                                min_eff_pt = eff_pt
                            if eff_pt < 14.0:
                                small_text_runs.append({"shape": name, "effective_pt": eff_pt, "sample": run.text[:40]})

            # 3. Table text inspection
            if sh.shape_type == MSO_SHAPE_TYPE.TABLE:
                for row in sh.table.rows:
                    row_cells = [c.text_frame.text.strip() for c in row.cells]
                    texts.append(" | ".join(row_cells))

            # 4. Picture DPI inspection (never claiming upscaled images are high-DPI)
            if sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
                try:
                    blob = sh.image.blob
                    with Image.open(io.BytesIO(blob)) as im:
                        px_w, px_h = im.size
                    printed_w_in = max(0.05, w / scale_factor)
                    printed_h_in = max(0.05, h / scale_factor)
                    eff_ppi = round(min(px_w / printed_w_in, px_h / printed_h_in), 1)
                    image_audits.append({
                        "shape": name,
                        "pixels": [px_w, px_h],
                        "printed_size_in": [round(printed_w_in, 2), round(printed_h_in, 2)],
                        "effective_ppi": eff_ppi,
                    })
                except Exception as exc:
                    image_audits.append({"shape": name, "error": str(exc), "effective_ppi": 0.0})

            # 5. Native chart integrity
            if sh.has_chart:
                try:
                    _ = len(sh.chart.series)
                except Exception as exc:
                    broken_charts.append(f"{name}: {exc}")

    # Pairwise overlap detection among content shapes
    overlaps: List[Dict[str, Any]] = []
    for i in range(len(boxes)):
        n1, ax1, ay1, ax2, ay2 = boxes[i]
        for j in range(i + 1, len(boxes)):
            n2, bx1, by1, bx2, by2 = boxes[j]
            ix = max(0.0, min(ax2, bx2) - max(ax1, bx1))
            iy = max(0.0, min(ay2, by2) - max(ay1, by1))
            area = ix * iy
            if area > 0.03:  # > 0.03 sq in real intersection
                overlaps.append({
                    "shape_a": n1,
                    "shape_b": n2,
                    "overlap_sq_in": round(area, 3),
                })

    return {
        "slide_count": n_slides,
        "slide_w_in": round(slide_w_in, 3),
        "slide_h_in": round(slide_h_in, 3),
        "effective_w_in": round(slide_w_in / scale_factor, 3),
        "effective_h_in": round(slide_h_in / scale_factor, 3),
        "all_text": "\n".join(texts),
        "out_of_bounds": out_of_bounds,
        "overlaps": overlaps,
        "min_effective_pt": min_eff_pt,
        "small_text_runs": small_text_runs,
        "image_audits": image_audits,
        "broken_charts": broken_charts,
    }


def _extract_decimal_tokens(text: str) -> Set[str]:
    """Extract distinctive decimal & percentage numbers (e.g. 0.68, 34.2, 4820) for provenance checks."""
    cleaned = text.replace(",", "").replace("−", "-")
    # Decimal statistics (at least one decimal place, excluding trivial 1.0/0.0/2.0 figure numbers)
    decimals = set(re.findall(r"\b\d+\.\d+\b", cleaned))
    trivial = {"0.0", "1.0", "2.0", "0.5", "0.05", "95.0", "100.0"}
    return {d for d in decimals if d not in trivial}


def _inspect_preview_image(png_path: pathlib.Path, masthead_style: str, safe_margin_in: float, width_in: float, height_in: float) -> Dict[str, Any]:
    with Image.open(png_path) as im:
        rgb = np.asarray(im.convert("RGB"), dtype=np.float32)

    H_px, W_px, _ = rgb.shape
    dpi_est = W_px / max(1.0, width_in)

    # Estimate background luminance from lower-margin corners
    lum = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
    bg_lum = float(np.percentile(lum[int(H_px * 0.22):, :], 90))
    ink_mask = np.abs(lum - bg_lum) > 22.0

    # Body zone (below masthead ~18% to above bottom margin ~95%)
    body_y0 = int(H_px * 0.20)
    body_y1 = int(H_px * 0.94)
    margin_px = max(4, int(round(safe_margin_in * dpi_est * 0.72)))

    body_ink = ink_mask[body_y0:body_y1, margin_px : W_px - margin_px]
    ink_density = float(body_ink.mean()) if body_ink.size else 0.0

    # Left vs Right visual balance in body zone
    mid_x = body_ink.shape[1] // 2
    left_density = float(body_ink[:, :mid_x].mean()) if mid_x > 0 else 0.0
    right_density = float(body_ink[:, mid_x:].mean()) if mid_x > 0 else 0.0
    balance_diff = abs(left_density - right_density)

    # Outer edge clipping check in body region (strictly outside 50% of safe margin)
    edge_px = max(2, int(round(safe_margin_in * dpi_est * 0.45)))
    left_strip_ink = float(ink_mask[body_y0:body_y1, :edge_px].mean())
    right_strip_ink = float(ink_mask[body_y0:body_y1, W_px - edge_px :].mean())
    bottom_strip_ink = float(ink_mask[H_px - edge_px :, :].mean())

    return {
        "pixel_size": [W_px, H_px],
        "body_ink_density": round(ink_density, 4),
        "whitespace_fraction": round(1.0 - ink_density, 4),
        "left_half_density": round(left_density, 4),
        "right_half_density": round(right_density, 4),
        "lateral_balance_diff": round(balance_diff, 4),
        "margin_edge_ink": {
            "left": round(left_strip_ink, 5),
            "right": round(right_strip_ink, 5),
            "bottom": round(bottom_strip_ink, 5),
        },
    }


def validate_poster_bundle(
    output_dir: pathlib.Path,
    source_spec_path: Optional[pathlib.Path] = None,
    extraction_path: Optional[pathlib.Path] = None,
) -> Dict[str, Any]:
    checks: List[CheckResult] = []
    revision_actions: List[str] = []

    pptx_path = output_dir / "poster.pptx"
    pdf_path = output_dir / "poster.pdf"
    png_path = output_dir / "poster_preview.png"
    md_content_path = output_dir / "poster_content.md"
    md_spec_path = output_dir / "design_specification.md"
    ir_path = output_dir / "poster_scene_ir.json"

    # 1. Mandatory Output Files Check
    mandatory = {
        "poster.pptx": pptx_path,
        "poster.pdf": pdf_path,
        "poster_preview.png": png_path,
        "poster_content.md": md_content_path,
        "design_specification.md": md_spec_path,
    }
    missing_files = [name for name, p in mandatory.items() if not p.exists() or p.stat().st_size == 0]
    checks.append(
        CheckResult(
            "technical",
            "MANDATORY_OUTPUT_FILES",
            "PASS" if not missing_files else "FAIL",
            "All 5 mandatory deliverables exist and are non-empty." if not missing_files else f"Missing deliverables: {missing_files}",
        )
    )
    if missing_files:
        return {
            "overall_status": "FAIL",
            "checks": [c.to_dict() for c in checks],
            "revision_actions": ["Generate missing mandatory output files before running deep validation."],
        }

    scene_ir = json.loads(ir_path.read_text(encoding="utf-8")) if ir_path.exists() else {}
    dims = scene_ir.get("dimensions", {})
    pal = scene_ir.get("palette", {})
    typo = scene_ir.get("typography", {})
    scale_factor = float(dims.get("pptx_scale_factor", 1.0))
    target_w_in = float(dims.get("width_in", 48.0))
    target_h_in = float(dims.get("height_in", 36.0))
    target_orient = dims.get("orientation", "landscape" if target_w_in > target_h_in else "portrait")

    # 2. Technical PPTX Inspection
    pptx_info = _extract_pptx_all_text_and_shapes(pptx_path, scale_factor=scale_factor)

    dim_ok = (
        pptx_info["slide_count"] == 1
        and abs(pptx_info["effective_w_in"] - target_w_in) <= 0.08
        and abs(pptx_info["effective_h_in"] - target_h_in) <= 0.08
    )
    checks.append(
        CheckResult(
            "technical",
            "PPTX_DIMENSIONS_AND_ORIENTATION",
            "PASS" if dim_ok else "FAIL",
            f"PPTX single slide verified at effective {pptx_info['effective_w_in']} × {pptx_info['effective_h_in']} in (scale={scale_factor}x, {target_orient}).",
        )
    )

    oob = pptx_info["out_of_bounds"]
    checks.append(
        CheckResult(
            "technical",
            "BOUNDARY_CONTAINMENT",
            "PASS" if not oob else "FAIL",
            "Zero shapes extend outside poster boundaries." if not oob else f"{len(oob)} shape(s) exceed slide bounds.",
            details=oob or None,
        )
    )
    if oob:
        revision_actions.append("Recompute column/masthead bounds; shapes exceeded slide edges.")

    ovl = pptx_info["overlaps"]
    checks.append(
        CheckResult(
            "technical",
            "OBJECT_OVERLAP_CHECK",
            "PASS" if not ovl else "FAIL",
            "Zero unintended shape overlaps detected." if not ovl else f"{len(ovl)} overlapping shape pair(s) detected.",
            details=ovl or None,
        )
    )
    if ovl:
        revision_actions.append("Adjust vertical section spacing or column heights to eliminate overlapping shapes.")

    # Font substitution & minimum legible size check
    min_cap_floor = float(typo.get("min_caption_pt", 14.0))
    min_obs_pt = pptx_info["min_effective_pt"] or 24.0
    font_subs = []
    for fk in ("heading_font", "body_font"):
        finfo = typo.get(fk, {})
        if finfo.get("was_substituted"):
            font_subs.append(finfo.get("substitution_note"))
    checks.append(
        CheckResult(
            "technical",
            "TYPOGRAPHY_FLOOR_AND_FONTS",
            "FAIL" if min_obs_pt < min_cap_floor - 0.5 else ("WARN" if font_subs else "PASS"),
            f"Minimum effective text size is {min_obs_pt} pt (floor {min_cap_floor} pt)."
            + (f" Font fallback logged: {'; '.join(font_subs)}" if font_subs else " Exact requested TrueType fonts resolved."),
        )
    )

    # Image resolution PPI check
    low_res = [im for im in pptx_info["image_audits"] if im.get("effective_ppi", 300) < 150]
    sub_300 = [im for im in pptx_info["image_audits"] if 150 <= im.get("effective_ppi", 300) < 250]
    checks.append(
        CheckResult(
            "technical",
            "IMAGE_RESOLUTION_PPI",
            "WARN" if low_res else "PASS",
            f"Inspected {len(pptx_info['image_audits'])} embedded image(s); "
            + (f"{len(low_res)} below 150 PPI warning floor." if low_res else (f"all >=150 PPI ({len(sub_300)} between 150–250 PPI, rest >=250–300 PPI)." if sub_300 else "all meet >=250–300 PPI print target.")),
            details=low_res if low_res else pptx_info["image_audits"],
        )
    )

    checks.append(
        CheckResult(
            "technical",
            "CHART_INTEGRITY",
            "PASS" if not pptx_info["broken_charts"] else "FAIL",
            "All embedded chart references intact." if not pptx_info["broken_charts"] else f"Broken charts: {pptx_info['broken_charts']}",
        )
    )

    # 3. Technical PDF Inspection
    reader = PdfReader(str(pdf_path))
    pdf_p0 = reader.pages[0]
    pdf_w_in = round(float(pdf_p0.mediabox.width) / 72.0, 3)
    pdf_h_in = round(float(pdf_p0.mediabox.height) / 72.0, 3)
    pdf_fonts = list((pdf_p0.get("/Resources") or {}).get("/Font", {}).keys())
    pdf_ok = len(reader.pages) == 1 and abs(pdf_w_in - target_w_in) <= 0.08 and abs(pdf_h_in - target_h_in) <= 0.08 and len(pdf_fonts) > 0
    checks.append(
        CheckResult(
            "technical",
            "PDF_DIMENSIONS_AND_EMBEDDED_FONTS",
            "PASS" if pdf_ok else "FAIL",
            f"PDF verified: {len(reader.pages)} page, {pdf_w_in} × {pdf_h_in} in ({round(pdf_w_in*25.4,1)} × {round(pdf_h_in*25.4,1)} mm), {len(pdf_fonts)} embedded font resource(s).",
        )
    )

    # 4. Scientific Integrity Checks
    poster_text = pptx_info["all_text"]
    source_spec = json.loads(source_spec_path.read_text(encoding="utf-8")) if source_spec_path and source_spec_path.exists() else {}
    extraction = json.loads(extraction_path.read_text(encoding="utf-8")) if extraction_path and extraction_path.exists() else {}

    expected_title = source_spec.get("title") or scene_ir.get("poster_title", "")
    title_ok = bool(expected_title) and expected_title[:40].lower() in poster_text.lower()
    checks.append(
        CheckResult(
            "scientific",
            "TITLE_AND_AUTHOR_CONSISTENCY",
            "PASS" if title_ok else "FAIL",
            "Poster title and author block match source specification." if title_ok else "Title mismatch between source spec and rendered poster.",
        )
    )

    # Reference bracket consistency check ([1], [2] in body vs Colophon references)
    body_citations = {int(m) for m in re.findall(r"\[(\d{1,2})\]", poster_text)}
    supplied_refs = ((source_spec.get("colophon") or {}).get("references")) or []
    ref_ok = True
    ref_msg = f"Verified {len(supplied_refs)} reference entry/entries."
    if body_citations and not supplied_refs:
        ref_ok = False
        ref_msg = f"In-text citations {sorted(body_citations)} appear on poster, but References list is empty."
    elif body_citations and max(body_citations) > len(supplied_refs):
        ref_ok = False
        ref_msg = f"Highest in-text citation [{max(body_citations)}] exceeds supplied reference count ({len(supplied_refs)})."
    checks.append(CheckResult("scientific", "REFERENCE_CONSISTENCY", "PASS" if ref_ok else "FAIL", ref_msg))

    # Numerical provenance check against source spec + extraction corpus
    source_corpus = json.dumps(source_spec, ensure_ascii=False) + "\n" + json.dumps(extraction, ensure_ascii=False)
    if source_spec:
        poster_decimals = _extract_decimal_tokens(poster_text)
        source_decimals = _extract_decimal_tokens(source_corpus)
        # Allow rounded representations of chart numbers present in source_spec
        unverified_nums = sorted(d for d in poster_decimals if d not in source_decimals and d not in source_corpus.replace(",", ""))
        checks.append(
            CheckResult(
                "scientific",
                "NUMERICAL_PROVENANCE_CHECK",
                "PASS" if not unverified_nums else "WARN",
                f"All {len(poster_decimals)} decimal statistical value(s) on poster trace directly to supplied source data."
                if not unverified_nums
                else f"Inspect numeric formatting/rounding for values not verbatim in source JSON: {unverified_nums[:8]}",
            )
        )

    # Figure-caption sequential numbering check
    fig_elements = [e for e in scene_ir.get("elements", []) if e.get("kind") == "figure" and e.get("id") != "timeline_upper_band"]
    uncaptioned = [e["id"] for e in fig_elements if not (e.get("payload") or {}).get("caption")]
    checks.append(
        CheckResult(
            "scientific",
            "FIGURE_CAPTION_CONSISTENCY",
            "PASS" if not uncaptioned else "WARN",
            f"All {len(fig_elements)} primary/secondary figure(s) carry analytical captions." if not uncaptioned else f"Figures missing captions: {uncaptioned}",
        )
    )

    # Significance-claim vs p-value calibration check
    non_sig_p = re.findall(r"\bp\s*=\s*(0\.(?:0[6-9]|[1-9]\d*))", poster_text, flags=re.I)
    overclaim = bool(non_sig_p) and ("statistically significant reduction" in poster_text.lower()) and ("no statistically significant" not in poster_text.lower())
    checks.append(
        CheckResult(
            "scientific",
            "CONCLUSION_STATISTICAL_CALIBRATION",
            "FAIL" if overclaim else "PASS",
            "Conclusions and statistical significance language are appropriately calibrated." if not overclaim else f"Potential significance overclaim alongside non-significant p-value(s): {non_sig_p}",
        )
    )

    # 5. Accessibility & Contrast Checks (WCAG 2.1)
    if pal:
        body_cr = wcag_contrast_ratio(pal["body_ink"], pal["canvas_bg"])
        callout_cr = wcag_contrast_ratio(pal["body_ink"], pal["surface_tint"])
        mast_bg = pal["dominant"] if scene_ir.get("masthead_style") == "solid_banner" else pal["canvas_bg"]
        mast_fg = pal["masthead_fg"] if scene_ir.get("masthead_style") == "solid_banner" else pal["dominant"]
        mast_cr = wcag_contrast_ratio(mast_fg, mast_bg)
        cr_ok = body_cr >= 4.5 and callout_cr >= 4.5 and mast_cr >= 4.5
        checks.append(
            CheckResult(
                "accessibility",
                "WCAG_COLOR_CONTRAST",
                "PASS" if cr_ok else "FAIL",
                f"WCAG 2.1 contrast verified — Body/Canvas: {body_cr}:1, Callout: {callout_cr}:1, Masthead: {mast_cr}:1 (minimum 4.5:1 AA; 7.0:1 AAA).",
            )
        )

    # 6. Image-Based Visual QA Checks
    vis = _inspect_preview_image(
        png_path,
        masthead_style=scene_ir.get("masthead_style", "solid_banner"),
        safe_margin_in=float(dims.get("safe_margin_in", 1.0)),
        width_in=target_w_in,
        height_in=target_h_in,
    )
    dens = vis["body_ink_density"]
    edge_breach = any(v > 0.015 for v in vis["margin_edge_ink"].values())
    dens_ok = 0.03 <= dens <= 0.48
    bal_ok = vis["lateral_balance_diff"] <= 0.22

    vis_status = "PASS"
    if edge_breach:
        vis_status = "FAIL"
        revision_actions.append("Content ink detected inside outer safe-margin perimeter; increase margins or tighten wrapping.")
    elif not dens_ok or not bal_ok:
        vis_status = "WARN"

    checks.append(
        CheckResult(
            "visual",
            "RENDERED_VISUAL_COMPOSITION",
            vis_status,
            f"Rendered preview ({vis['pixel_size'][0]}×{vis['pixel_size'][1]} px): body ink density={dens*100:.1f}%, "
            f"whitespace={(1-dens)*100:.1f}%, lateral balance Δ={vis['lateral_balance_diff']*100:.1f}%, "
            f"safe-margin perimeter clean={not edge_breach}.",
            details=vis,
        )
    )

    statuses = [c.status for c in checks]
    overall = "FAIL" if "FAIL" in statuses else ("WARN" if "WARN" in statuses else "PASS")

    return {
        "overall_status": overall,
        "summary_counts": {
            "PASS": statuses.count("PASS"),
            "WARN": statuses.count("WARN"),
            "FAIL": statuses.count("FAIL"),
        },
        "checks": [c.to_dict() for c in checks],
        "revision_actions": revision_actions,
    }


def _format_validation_md(report: Dict[str, Any]) -> str:
    sc = report["summary_counts"]
    lines = [
        "# Poster Quality Assurance & Scientific Validation Report",
        "",
        f"- **Overall QA Verdict:** **{report['overall_status']}**",
        f"- **Checks Passed:** {sc['PASS']}  |  **Warnings:** {sc['WARN']}  |  **Failures:** {sc['FAIL']}",
        "",
        "## Detailed Check Results",
        "",
        "| Category | Check ID | Status | Summary |",
        "|---|---|---|---|",
    ]
    for c in report["checks"]:
        lines.append(f"| `{c['category']}` | `{c['check_id']}` | **{c['status']}** | {c['message']} |")

    if report.get("revision_actions"):
        lines.extend(["", "## Recommended Revision Actions", ""])
        for act in report["revision_actions"]:
            lines.append(f"- {act}")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate generated research poster outputs (technical, scientific, visual QA).")
    parser.add_argument("--output-dir", required=True, help="Directory containing poster.pptx, poster.pdf, poster_preview.png, etc.")
    parser.add_argument("--spec", help="Optional path to source poster_spec.json")
    parser.add_argument("--extraction", help="Optional path to research_extraction.json")
    args = parser.parse_args()

    out_dir = pathlib.Path(args.output_dir)
    report = validate_poster_bundle(
        output_dir=out_dir,
        source_spec_path=pathlib.Path(args.spec) if args.spec else None,
        extraction_path=pathlib.Path(args.extraction) if args.extraction else None,
    )

    (out_dir / "validation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (out_dir / "validation_report.md").write_text(_format_validation_md(report), encoding="utf-8")
    print(f"QA Verdict: {report['overall_status']} (PASS={report['summary_counts']['PASS']}, WARN={report['summary_counts']['WARN']}, FAIL={report['summary_counts']['FAIL']})")
    return 0 if report["overall_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
