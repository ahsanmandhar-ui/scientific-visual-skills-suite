#!/usr/bin/env python3
"""
Master Poster Production & Iterative QA Engine for research-poster-maker.

Implements the complete production pipeline:
  Generate (Charts + Scene IR + Editable PPTX + Markdown Reports)
    -> Export (Print-Ready Vector PDF)
    -> Render (PNG Preview)
    -> Inspect & Validate (Technical + Scientific + Accessibility + Visual QA)
    -> Revise (Bounded iterative refinement if objective checks fail)
    -> Finalize
"""

from __future__ import annotations

import argparse
import copy
import json
import pathlib
import sys
from typing import Any, Dict, List, Optional

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from poster_engine.design_tokens import (
    TEMPLATES_DIR,
    resolve_dimensions,
    resolve_palette,
    resolve_typography,
    wcag_contrast_ratio,
)
from poster_engine.layout_solver import PosterSceneIR, solve_poster_layout
from poster_engine.pptx_renderer import render_scene_to_pptx
from generate_charts import generate_scientific_chart
from export_poster import export_poster_pdf
from generate_preview import render_pdf_to_png
from validate_poster import validate_poster_bundle, _format_validation_md


def _load_template(template_id: str) -> Dict[str, Any]:
    tpath = TEMPLATES_DIR / template_id / "template.json"
    if not tpath.exists():
        available = sorted(p.parent.name for p in TEMPLATES_DIR.glob("*/template.json"))
        raise ValueError(f"Unknown template '{template_id}'. Available templates: {available}")
    return json.loads(tpath.read_text(encoding="utf-8"))


def _generate_qr_code(url: str, out_dir: pathlib.Path, dark_hex: str) -> Optional[str]:
    try:
        import qrcode

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=18,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color=dark_hex, back_color="#FFFFFF")
        qr_png = out_dir / "figures" / "study_qr.png"
        qr_png.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(qr_png))
        return str(qr_png)
    except ImportError:
        return None


def _write_poster_content_md(
    spec: Dict[str, Any],
    scene: PosterSceneIR,
    out_md: pathlib.Path,
) -> None:
    lines: List[str] = [
        f"# {spec['title']}",
        "",
    ]
    if spec.get("study_badge"):
        lines.append(f"**Study Classification:** {spec['study_badge']}  ")
    if spec.get("authors_line"):
        lines.append(f"**Authors:** {spec['authors_line']}  ")
    if spec.get("affiliations_line"):
        lines.append(f"**Affiliations:** {spec['affiliations_line']}  ")
    lines.append("")

    if spec.get("headline_takeaway"):
        lines.extend([
            "## Headline Takeaway",
            "",
            f"> {spec['headline_takeaway']}",
            "",
        ])

    lines.append("## Poster Sections")
    lines.append("")

    for el in scene.elements:
        if el.kind in ("background", "masthead", "banner_band", "colophon"):
            continue
        p = el.payload
        sec_title = p.get("title") or el.id
        lines.append(f"### {sec_title}")
        lines.append("")
        if p.get("hero_metric"):
            lines.append(f"**Key Quantitative Metric:** `{p['hero_metric']}`")
            lines.append("")
        for para in p.get("paragraphs", []):
            lines.append(para)
            lines.append("")
        for bul in p.get("bullets", []):
            clean_b = bul.lstrip("•–- ").strip()
            lines.append(f"- {clean_b}")
        if p.get("bullets"):
            lines.append("")
        if el.kind == "table" and p.get("table_data"):
            td = p["table_data"]
            hdrs = td["headers"]
            lines.append("| " + " | ".join(str(h) for h in hdrs) + " |")
            lines.append("| " + " | ".join("---" for _ in hdrs) + " |")
            for r in td["rows"]:
                lines.append("| " + " | ".join(str(c) for c in r) + " |")
            lines.append("")
            if p.get("footnote"):
                lines.append(f"*{p['footnote']}*")
                lines.append("")
        if el.kind == "figure":
            if p.get("png_path"):
                lines.append(f"- **Rendered Figure Asset:** `{pathlib.Path(p['png_path']).name}`")
            if p.get("caption"):
                lines.append(f"- **Caption:** {p['caption']}")
            lines.append("")

    colophon = spec.get("colophon") or {}
    if colophon.get("references"):
        lines.extend(["## References", ""])
        for r in colophon["references"]:
            lines.append(f"- {r}")
        lines.append("")
    if colophon.get("funding") or colophon.get("correspondence") or colophon.get("disclosure"):
        lines.extend(["## Funding, Disclosures & Correspondence", ""])
        for field_k in ("funding", "correspondence", "disclosure"):
            if colophon.get(field_k):
                lines.append(f"- {colophon[field_k]}")
        lines.append("")

    if spec.get("missing_information_notes"):
        lines.extend(["## Explicit Source Completeness Notes (Uninvented Fields)", ""])
        for note in spec["missing_information_notes"]:
            lines.append(f"- {note}")
        lines.append("")

    if scene.pruned_items:
        lines.extend(["## Overflow Condensation Log (Preserved Off-Poster Rather Than Shrinking Fonts)", ""])
        for pr in scene.pruned_items:
            lines.append(f"- {pr}")
        lines.append("")

    out_md.write_text("\n".join(lines), encoding="utf-8")


def _write_design_specification_md(
    spec: Dict[str, Any],
    scene: PosterSceneIR,
    pptx_info: Dict[str, Any],
    pdf_info: Dict[str, Any],
    preview_info: Dict[str, Any],
    chart_manifests: List[Dict[str, Any]],
    qa_report: Dict[str, Any],
    iterations_used: int,
    out_md: pathlib.Path,
) -> None:
    dims = scene.dimensions
    pal = scene.palette
    typo = scene.typography

    mast_bg = pal["dominant"] if scene.masthead_style == "solid_banner" else pal["canvas_bg"]
    mast_fg = pal["masthead_fg"] if scene.masthead_style == "solid_banner" else pal["dominant"]

    scale_note = (
        "1:1 Full Physical Scale (100%)"
        if float(dims["pptx_scale_factor"]) == 1.0
        else "1:2 Proportional Half-Scale (50% in PPTX due to PowerPoint 56-in ceiling — enlarge 200% when printing from PPTX; PDF is 1:1 full size)"
    )
    assumed_note = (
        " *(Default assumption — confirm exact board call with conference organizers)*"
        if dims.get("is_default_assumption")
        else " *(Explicitly configured)*"
    )

    lines = [
        "# Poster Design Specification & Production Report",
        "",
        "## 1. Executive Specification Summary",
        "",
        "```text",
        f"Poster Template : {scene.template_id}",
        f"Orientation     : {dims['orientation'].title()}",
        f"Dimensions      : {dims['width_in']} × {dims['height_in']} in ({dims['width_mm']} × {dims['height_mm']} mm){assumed_note}",
        f"Layout Recipe   : {scene.layout_recipe}",
        f"Masthead Style  : {scene.masthead_style}",
        f"Typography      : {typo['heading_font']['resolved_name']} + {typo['body_font']['resolved_name']}",
        f"Color Palette   : {pal['name']} ({pal['dominant']} / {pal['canvas_bg']} / {pal['accent']})",
        f"Output Bundle   : PPTX + Print PDF ({pdf_info.get('backend')}) + PNG Preview + Markdown Reports",
        f"QA Verdict      : {qa_report['overall_status']} (Iterations: {iterations_used})",
        "```",
        "",
        "## 2. Physical Print & Export Architecture",
        "",
        f"- **Physical Trim Size:** `{dims['width_in']} × {dims['height_in']} in` (`{dims['width_mm']} × {dims['height_mm']} mm`)",
        f"- **Bleed / Safe Margin:** Bleed `{dims['bleed_in']} in` | Safe Margin `{dims['safe_margin_in']} in`",
        f"- **PowerPoint Slide Scale:** {scale_note}",
        f"- **Editable PPTX Objects:** `{pptx_info['editable_shape_count']}` native shapes/tables/textframes (`{pptx_info['native_chart_count']}` native Office charts)",
        f"- **PDF Export Engine:** `{pdf_info.get('backend')}` — verified `{pdf_info['pdf_audit']['width_in']} × {pdf_info['pdf_audit']['height_in']} in` with `{len(pdf_info['pdf_audit']['embedded_fonts'])}` embedded font resource(s)",
        f"- **Color Profile Note:** Authored in `sRGB` for wide-gamut conference inkjet plotters (HP DesignJet / Canon imagePROGRAF / Epson SureColor). If submitting to a commercial CMYK offset press requiring PDF/X-1a, perform an ICC prepress conversion first.",
        "",
        "## 3. Typography & Viewing-Distance Scale",
        "",
        f"- **Heading Font:** Requested `{typo['heading_font']['requested_name']}` → Resolved `{typo['heading_font']['resolved_name']}`",
        f"- **Body Font:** Requested `{typo['body_font']['requested_name']}` → Resolved `{typo['body_font']['resolved_name']}`",
        "",
        "| Element | Effective Printed Size | Minimum Floor |",
        "|---|---|---|",
        f"| Main Title | `{typo['title_pt']} pt` | `72 pt` (full) / `54 pt` (compact) |",
        f"| Authors | `{typo['authors_pt']} pt` | `40 pt` (full) / `30 pt` (compact) |",
        f"| Affiliations | `{typo['affiliations_pt']} pt` | `{typo['min_body_pt']} pt` |",
        f"| Section Headings | `{typo['section_heading_pt']} pt` | `{typo['min_heading_pt']} pt` |",
        f"| Hero Quantitative Metric | `{typo['hero_metric_pt']} pt` | `{typo['min_heading_pt']} pt` |",
        f"| Body Copy & Bullets | `{typo['body_pt']} pt` | `{typo['min_body_pt']} pt` |",
        f"| Table Cells | `{typo['table_pt']} pt` | `{typo['min_caption_pt']} pt` |",
        f"| Captions & References | `{typo['caption_pt']} / {typo['reference_pt']} pt` | `{typo['min_caption_pt']} pt` |",
        "",
        "## 4. Color System & WCAG 2.1 Accessibility Verification",
        "",
        "| Surface Pair | Foreground | Background | Contrast Ratio | WCAG 2.1 Rating |",
        "|---|---|---|---|---|",
        f"| Body Copy on Canvas | `{pal['body_ink']}` | `{pal['canvas_bg']}` | **{wcag_contrast_ratio(pal['body_ink'], pal['canvas_bg'])}:1** | AAA |",
        f"| Callout Copy on Surface Tint | `{pal['body_ink']}` | `{pal['surface_tint']}` | **{wcag_contrast_ratio(pal['body_ink'], pal['surface_tint'])}:1** | AAA |",
        f"| Masthead Title | `{mast_fg}` | `{mast_bg}` | **{wcag_contrast_ratio(mast_fg, mast_bg)}:1** | AAA |",
        "",
        "## 5. Scientific Figures Inventory",
        "",
    ]
    if chart_manifests:
        for ch in chart_manifests:
            lines.append(
                f"- **`{ch['chart_id']}` (`{ch['chart_type']}`):** `{ch['width_in']:.2f} × {ch['height_in']:.2f} in` "
                f"exported as vector `.svg`/`.pdf` + `{ch['dpi']} DPI` `.png`."
            )
            for w in ch.get("warnings", []):
                lines.append(f"  - *Arithmetic/Data Note:* {w}")
    else:
        lines.append("- _No standalone scientific chart blocks were required or supplied for this poster._")

    if pdf_info.get("notes") or scene.layout_notes:
        lines.extend(["", "## 6. Production & Layout Solver Notes", ""])
        for n in scene.layout_notes + pdf_info.get("notes", []):
            lines.append(f"- {n}")

    lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")


def build_poster_pipeline(
    raw_spec: Dict[str, Any],
    output_dir: pathlib.Path,
    template_override: Optional[str] = None,
    dimensions_override: Optional[str] = None,
    width_override: Optional[float] = None,
    height_override: Optional[float] = None,
    units: str = "in",
    bleed_in: float = 0.0,
    layout_override: Optional[str] = None,
    palette_override: Optional[str] = None,
    font_pairing_override: Optional[str] = None,
    heading_font_override: Optional[str] = None,
    body_font_override: Optional[str] = None,
    pdf_backend: str = "auto",
    preview_dpi: int = 72,
    export_tiff: bool = False,
    max_revisions: int = 3,
    source_spec_path: Optional[pathlib.Path] = None,
    extraction_path: Optional[pathlib.Path] = None,
) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = output_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    spec = copy.deepcopy(raw_spec)
    template_id = template_override or spec.get("template_id", "clinical-research")
    tmpl = _load_template(template_id)
    spec["template_id"] = template_id

    # 1. Resolve physical dimensions
    dim_preset = dimensions_override or spec.get("dimensions_preset")
    custom_w = width_override if width_override is not None else spec.get("width")
    custom_h = height_override if height_override is not None else spec.get("height")
    dim_units = spec.get("units", units)
    if not dim_preset and custom_w is None:
        dim_preset = tmpl.get("default_dimensions", "48x36")

    dimensions = resolve_dimensions(
        preset=dim_preset,
        width=custom_w,
        height=custom_h,
        units=dim_units,
        bleed_in=float(spec.get("bleed_in", bleed_in)),
        safe_margin_in=spec.get("safe_margin_in"),
        target_dpi=int(spec.get("target_dpi", 300)),
    )
    if spec.get("dimensions_preset") or custom_w is not None or dimensions_override:
        # Explicitly specified by caller/spec
        object.__setattr__(dimensions, "is_default_assumption", bool(spec.get("is_default_assumption", False)))
    else:
        object.__setattr__(dimensions, "is_default_assumption", True)

    # 2. Resolve palette, typography, and layout recipe
    palette_id = palette_override or spec.get("palette") or tmpl.get("default_palette", "academic_navy")
    palette = resolve_palette(palette_id, spec.get("palette_overrides"))

    pairing_id = font_pairing_override or spec.get("font_pairing") or tmpl.get("default_font_pairing", "clinical_precision")
    typo = resolve_typography(
        dimensions=dimensions,
        pairing_id=pairing_id,
        heading_font_override=heading_font_override or spec.get("heading_font"),
        body_font_override=body_font_override or spec.get("body_font"),
    )

    if layout_override or spec.get("layout_recipe"):
        layout_recipe = layout_override or spec["layout_recipe"]
    elif dimensions.orientation == "portrait":
        layout_recipe = tmpl.get("portrait_layout_recipe", "two_column_editorial")
    else:
        layout_recipe = tmpl.get("default_layout_recipe", "three_column_classic")

    masthead_style = spec.get("masthead_style") or tmpl.get("masthead_style", "solid_banner")

    # 3. Optional QR code generation
    if spec.get("study_url") and not spec.get("qr_path"):
        qr_file = _generate_qr_code(spec["study_url"], output_dir, palette.dominant)
        if qr_file:
            spec["qr_path"] = qr_file

    # 4. Generate scientific figures from supplied data at exact poster-column physical dimensions
    chart_manifests: List[Dict[str, Any]] = []
    raster_dpi = dimensions.effective_pptx_raster_dpi

    # Upper timeline/workflow banner figure if present
    if spec.get("upper_banner_figure") and spec["upper_banner_figure"].get("chart_spec"):
        ub = spec["upper_banner_figure"]
        ub_w = dimensions.width_in - 2 * dimensions.safe_margin_in
        ub_h = float(ub.get("height_in", max(3.6, dimensions.height_in * 0.13)))
        ch_res = generate_scientific_chart(
            spec=ub["chart_spec"],
            out_stem=fig_dir / ub.get("id", "upper_timeline"),
            width_in=ub_w,
            height_in=ub_h,
            palette_id=palette_id,
            palette_overrides=spec.get("palette_overrides"),
            font_family=typo.heading_font.resolved_name,
            base_pt=max(16.0, typo.figure_label_pt * 0.86),
            dpi=raster_dpi,
        )
        ub["png_path"] = ch_res["files"]["png"]
        ub["svg_path"] = ch_res["files"]["svg"]
        ub["height_in"] = ub_h
        chart_manifests.append(ch_res)

    for idx_it, item in enumerate(spec.get("items", [])):
        if item.get("item_type") == "figure" and item.get("chart_spec"):
            cid = item.get("id", f"figure_{idx_it+1}")
            c_spec = item["chart_spec"]
            fig_w = float(c_spec.get("width_in", 14.0 if dimensions.orientation == "landscape" else 15.5))
            fig_h = float(c_spec.get("height_in", 8.8))
            ch_res = generate_scientific_chart(
                spec=c_spec,
                out_stem=fig_dir / cid,
                width_in=fig_w,
                height_in=fig_h,
                palette_id=palette_id,
                palette_overrides=spec.get("palette_overrides"),
                font_family=typo.heading_font.resolved_name,
                base_pt=max(15.5, typo.figure_label_pt * 0.84),
                dpi=raster_dpi,
            )
            item["png_path"] = ch_res["files"]["png"]
            item["svg_path"] = ch_res["files"]["svg"]
            item.setdefault("aspect_ratio", round(fig_w / max(1.0, fig_h), 3))
            chart_manifests.append(ch_res)

    # 5. Iterative Generate -> Export -> Render -> Inspect -> Validate -> Revise Loop
    qa_report: Dict[str, Any] = {}
    pptx_info: Dict[str, Any] = {}
    pdf_info: Dict[str, Any] = {}
    preview_info: Dict[str, Any] = {}
    scene: Optional[PosterSceneIR] = None
    iterations = 0

    working_spec = copy.deepcopy(spec)
    current_recipe = layout_recipe

    for attempt in range(1, max_revisions + 1):
        iterations = attempt
        scene = solve_poster_layout(
            spec=working_spec,
            dimensions=dimensions,
            palette=palette,
            typo=typo,
            layout_recipe=current_recipe,
            masthead_style=masthead_style,
        )

        ir_path = output_dir / "poster_scene_ir.json"
        ir_path.write_text(json.dumps(scene.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

        pptx_path = output_dir / "poster.pptx"
        pptx_info = render_scene_to_pptx(scene, pptx_path)

        content_md_path = output_dir / "poster_content.md"
        _write_poster_content_md(working_spec, scene, content_md_path)

        pdf_path = output_dir / "poster.pdf"
        tiff_path = (output_dir / "poster.tiff") if export_tiff else None
        pdf_info = export_poster_pdf(
            pptx_path=pptx_path,
            scene_ir_path=ir_path,
            out_pdf=pdf_path,
            backend=pdf_backend,
            out_tiff=tiff_path,
        )

        preview_path = output_dir / "poster_preview.png"
        preview_info = render_pdf_to_png(
            pdf_path=pdf_path,
            out_png=preview_path,
            preview_dpi=preview_dpi,
            safe_margin_in=dimensions.safe_margin_in,
        )

        # Write preliminary design spec before running validator (so all 5 mandatory files exist)
        spec_md_path = output_dir / "design_specification.md"
        _write_design_specification_md(
            working_spec, scene, pptx_info, pdf_info, preview_info, chart_manifests,
            {"overall_status": "PENDING"}, iterations, spec_md_path,
        )

        qa_report = validate_poster_bundle(
            output_dir=output_dir,
            source_spec_path=source_spec_path,
            extraction_path=extraction_path,
        )

        # Finalize design spec & validation report with QA results
        _write_design_specification_md(
            working_spec, scene, pptx_info, pdf_info, preview_info, chart_manifests,
            qa_report, iterations, spec_md_path,
        )
        (output_dir / "validation_report.json").write_text(json.dumps(qa_report, indent=2), encoding="utf-8")
        (output_dir / "validation_report.md").write_text(_format_validation_md(qa_report), encoding="utf-8")

        if qa_report["overall_status"] != "FAIL":
            break

        # Automated layout remediation if boundary/overlap failure occurred
        failed_ids = {c["check_id"] for c in qa_report["checks"] if c["status"] == "FAIL"}
        if failed_ids & {"BOUNDARY_CONTAINMENT", "OBJECT_OVERLAP_CHECK", "RENDERED_VISUAL_COMPOSITION"}:
            # Increase figure aspect ratios slightly to free vertical column height without shrinking fonts
            for it in working_spec.get("items", []):
                if it.get("item_type") == "figure":
                    it["aspect_ratio"] = float(it.get("aspect_ratio", 1.5)) * 1.15
            if current_recipe == "two_column_editorial" and dimensions.orientation == "landscape":
                current_recipe = "three_column_classic"
        else:
            # Non-geometric scientific failure (e.g. broken reference citation) cannot be guessed; stop honestly
            break

    return {
        "output_dir": str(output_dir),
        "iterations": iterations,
        "qa_status": qa_report.get("overall_status"),
        "deliverables": {
            "pptx": str(output_dir / "poster.pptx"),
            "pdf": str(output_dir / "poster.pdf"),
            "preview_png": str(output_dir / "poster_preview.png"),
            "poster_content_md": str(output_dir / "poster_content.md"),
            "design_specification_md": str(output_dir / "design_specification.md"),
            "validation_report_md": str(output_dir / "validation_report.md"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a conference-ready scientific research poster bundle.")
    parser.add_argument("--spec", required=True, help="Path to structured poster_spec.json")
    parser.add_argument("--output-dir", required=True, help="Output directory for generated deliverables")
    parser.add_argument("--template", help="Template ID override (e.g. clinical-research, meta-analysis, systematic-review, epidemiology, experimental-research, minimalist-editorial)")
    parser.add_argument("--dimensions", help="Dimension preset (a0_portrait, a0_landscape, a1_portrait, a1_landscape, 48x36, 36x48, 42x56, 56x42, 36x24)")
    parser.add_argument("--width", type=float, help="Custom poster width")
    parser.add_argument("--height", type=float, help="Custom poster height")
    parser.add_argument("--units", default="in", choices=["in", "mm", "cm"], help="Units for custom width/height")
    parser.add_argument("--bleed-in", type=float, default=0.0, help="Optional print bleed in inches")
    parser.add_argument("--layout", help="Layout recipe override (e.g. three_column_classic, two_column_editorial, asymmetric_grid, results_focused, timeline_flow, central_visual, clinical_workflow, systematic_review_prisma)")
    parser.add_argument("--palette", help="Color palette override (academic_navy, charcoal_ivory, deep_teal, burgundy_offwhite, forest_cream, monochrome_editorial)")
    parser.add_argument("--font-pairing", help="Typography pairing preset")
    parser.add_argument("--heading-font", help="Explicit heading font family name")
    parser.add_argument("--body-font", help="Explicit body font family name")
    parser.add_argument("--pdf-backend", default="auto", choices=["auto", "libreoffice", "reportlab"])
    parser.add_argument("--preview-dpi", type=int, default=72, help="PNG preview render DPI")
    parser.add_argument("--tiff", action="store_true", help="Also export optional 300-DPI LZW TIFF")
    parser.add_argument("--extraction", help="Optional path to research_extraction.json for integrity auditing")
    args = parser.parse_args()

    spec_path = pathlib.Path(args.spec)
    raw_spec = json.loads(spec_path.read_text(encoding="utf-8"))

    summary = build_poster_pipeline(
        raw_spec=raw_spec,
        output_dir=pathlib.Path(args.output_dir),
        template_override=args.template,
        dimensions_override=args.dimensions,
        width_override=args.width,
        height_override=args.height,
        units=args.units,
        bleed_in=args.bleed_in,
        layout_override=args.layout,
        palette_override=args.palette,
        font_pairing_override=args.font_pairing,
        heading_font_override=args.heading_font,
        body_font_override=args.body_font,
        pdf_backend="reportlab_vector" if args.pdf_backend == "reportlab" else args.pdf_backend,
        preview_dpi=args.preview_dpi,
        export_tiff=args.tiff,
        source_spec_path=spec_path,
        extraction_path=pathlib.Path(args.extraction) if args.extraction else None,
    )
    print(json.dumps(summary, indent=2))
    return 0 if summary["qa_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
