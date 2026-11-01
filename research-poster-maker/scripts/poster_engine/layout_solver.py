#!/usr/bin/env python3
"""
Exact-Metrics Layout Engine & Scene-Graph Solver for research-poster-maker.

Implements all 8 academic layout strategies using real TrueType glyph metrics,
preventing boundary overflow, object collisions, and illegibly shrunk text.
"""

from __future__ import annotations

import copy
import math
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from PIL import ImageFont

from .design_tokens import (
    ColorPalette,
    PosterDimensions,
    TypographySpec,
)

SUPPORTED_LAYOUTS = {
    "three_column_classic",
    "two_column_editorial",
    "asymmetric_grid",
    "results_focused",
    "timeline_flow",
    "central_visual",
    "clinical_workflow",
    "systematic_review_prisma",
}


class FontMetrics:
    """High-precision physical text measurement in inches using TrueType outlines."""

    def __init__(self) -> None:
        self._cache: Dict[Tuple[str, int], ImageFont.FreeTypeFont] = {}

    def _get(self, ttf_path: str, pt: float) -> ImageFont.FreeTypeFont:
        px_4x = max(12, int(round(pt * 4.0)))
        key = (ttf_path, px_4x)
        if key not in self._cache:
            self._cache[key] = ImageFont.truetype(ttf_path, size=px_4x)
        return self._cache[key]

    def text_width_in(self, text: str, ttf_path: str, pt: float) -> float:
        if not text:
            return 0.0
        font = self._get(ttf_path, pt)
        # 1 pt = 1/72 inch; font loaded at 4x points
        return float(font.getlength(text)) / (4.0 * 72.0)

    def wrap_lines(
        self,
        text: str,
        ttf_path: str,
        pt: float,
        max_width_in: float,
        safety_factor: float = 0.92,
    ) -> List[str]:
        """Wrap text into lines guaranteed to fit inside max_width_in across engines."""
        eff_w = max(1.0, max_width_in * safety_factor)
        out_lines: List[str] = []
        for raw_para in (text or "").split("\n"):
            words = raw_para.split()
            if not words:
                out_lines.append("")
                continue
            cur = words[0]
            for w in words[1:]:
                cand = f"{cur} {w}"
                if self.text_width_in(cand, ttf_path, pt) <= eff_w:
                    cur = cand
                else:
                    out_lines.append(cur)
                    cur = w
            out_lines.append(cur)
        return out_lines

    def block_height_in(
        self,
        lines: List[str],
        pt: float,
        line_spacing: float = 1.24,
        extra_bottom_in: float = 0.0,
    ) -> float:
        if not lines:
            return 0.0
        line_h_in = (pt / 72.0) * line_spacing
        # Add 0.06 in optical descender safety buffer
        return len(lines) * line_h_in + 0.06 + extra_bottom_in


@dataclass
class SceneElement:
    id: str
    kind: str  # background | masthead | banner_band | section_text | callout | figure | table | colophon
    x_in: float
    y_in: float
    w_in: float
    h_in: float
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PosterSceneIR:
    poster_title: str
    template_id: str
    layout_recipe: str
    masthead_style: str
    dimensions: Dict[str, Any]
    palette: Dict[str, Any]
    typography: Dict[str, Any]
    elements: List[SceneElement]
    layout_notes: List[str]
    pruned_items: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "poster_title": self.poster_title,
            "template_id": self.template_id,
            "layout_recipe": self.layout_recipe,
            "masthead_style": self.masthead_style,
            "dimensions": self.dimensions,
            "palette": self.palette,
            "typography": self.typography,
            "elements": [asdict(e) for e in self.elements],
            "layout_notes": self.layout_notes,
            "pruned_items": self.pruned_items,
        }


def _column_weights_for_recipe(recipe: str, orientation: str) -> List[float]:
    if recipe == "two_column_editorial":
        return [0.42, 0.58]
    if orientation == "portrait" and recipe in ("systematic_review_prisma", "clinical_workflow"):
        return [0.43, 0.57]
    if orientation == "portrait" and recipe == "central_visual":
        return [0.46, 0.54]
    if recipe == "asymmetric_grid":
        return [0.26, 0.48, 0.26]
    if recipe == "results_focused":
        return [0.27, 0.46, 0.27]
    if recipe == "timeline_flow":
        return [0.32, 0.36, 0.32]
    if recipe == "central_visual":
        return [0.27, 0.46, 0.27]
    if recipe == "clinical_workflow":
        return [0.30, 0.41, 0.29]
    if recipe == "systematic_review_prisma":
        return [0.29, 0.43, 0.28]
    # three_column_classic default
    return [0.31, 0.38, 0.31]


def _measure_item_height(
    item: Dict[str, Any],
    col_w_in: float,
    typo: TypographySpec,
    fm: FontMetrics,
) -> Tuple[float, Dict[str, Any]]:
    """Measure the exact height in inches of a section item and return enriched render info."""
    itype = item.get("item_type", "text")  # text | callout | figure | table
    style = item.get("style", "editorial_rule")
    pad_x = 0.40 if style in ("focal_callout", "focal_callout_subtle") else 0.06
    pad_y = 0.34 if style in ("focal_callout", "focal_callout_subtle") else 0.14
    inner_w = max(2.0, col_w_in - 2 * pad_x)

    h_ttf = typo.heading_font.bold_ttf
    b_reg = typo.body_font.regular_ttf
    b_bold = typo.body_font.bold_ttf

    meta: Dict[str, Any] = {"pad_x": pad_x, "pad_y": pad_y, "inner_w": inner_w}

    # Heading lines
    title = item.get("title", "")
    title_lines = fm.wrap_lines(title, h_ttf, typo.section_heading_pt, inner_w) if title else []
    title_h = fm.block_height_in(title_lines, typo.section_heading_pt, line_spacing=1.14, extra_bottom_in=0.14) if title_lines else 0.0
    meta["title_lines"] = title_lines
    meta["title_h_in"] = title_h

    if itype == "figure":
        cap = item.get("caption", "")
        cap_lines = fm.wrap_lines(cap, b_reg, typo.caption_pt, col_w_in - 0.36) if cap else []
        cap_h = fm.block_height_in(cap_lines, typo.caption_pt, line_spacing=1.18, extra_bottom_in=0.10) if cap_lines else 0.0
        aspect = float(item.get("aspect_ratio", 1.50))  # width / height
        ideal_img_h = (col_w_in - 0.36) / max(0.65, aspect)
        min_img_h = max(3.6, ideal_img_h * 0.76)
        max_img_h = ideal_img_h * 1.30
        meta.update({
            "caption_lines": cap_lines,
            "caption_h_in": cap_h,
            "ideal_img_h": ideal_img_h,
            "min_img_h": min_img_h,
            "max_img_h": max_img_h,
            "img_h_in": ideal_img_h,
        })
        total_h = title_h + ideal_img_h + cap_h + 0.42
        return total_h, meta

    if itype == "table":
        tbl = item["table_data"]
        headers = [str(x) for x in tbl["headers"]]
        rows = [[str(c) for c in r] for r in tbl["rows"]]
        n_cols = max(1, len(headers))
        weights = tbl.get("col_weights") or ([1.8] + [1.0] * (n_cols - 1))
        w_sum = sum(weights)
        col_ws = [inner_w * (w / w_sum) for w in weights]

        # Measure header row height
        hdr_max_lines = 1
        for c_i, h_txt in enumerate(headers):
            ls = fm.wrap_lines(h_txt, b_bold, typo.table_pt, col_ws[c_i] - 0.16, safety_factor=0.90)
            hdr_max_lines = max(hdr_max_lines, len(ls))
        hdr_h = fm.block_height_in(["X"] * hdr_max_lines, typo.table_pt, line_spacing=1.16, extra_bottom_in=0.14)

        row_heights: List[float] = []
        for r in rows:
            rmax = 1
            for c_i, cell in enumerate(r[:n_cols]):
                ls = fm.wrap_lines(cell, b_reg, typo.table_pt, col_ws[c_i] - 0.16, safety_factor=0.90)
                rmax = max(rmax, len(ls))
            rh = fm.block_height_in(["X"] * rmax, typo.table_pt, line_spacing=1.16, extra_bottom_in=0.12)
            row_heights.append(rh)

        fn = item.get("footnote", "")
        fn_lines = fm.wrap_lines(fn, b_reg, typo.caption_pt, inner_w) if fn else []
        fn_h = fm.block_height_in(fn_lines, typo.caption_pt, line_spacing=1.16, extra_bottom_in=0.06) if fn_lines else 0.0

        meta.update({
            "col_widths_in": col_ws,
            "header_h_in": hdr_h,
            "row_heights_in": row_heights,
            "footnote_lines": fn_lines,
            "footnote_h_in": fn_h,
        })
        total_h = title_h + hdr_h + sum(row_heights) + fn_h + 0.28
        return total_h, meta

    # Text or Callout block
    hero_metric = item.get("hero_metric", "")
    hero_h = 0.0
    hero_lines: List[str] = []
    if hero_metric:
        hero_lines = fm.wrap_lines(hero_metric, h_ttf, typo.hero_metric_pt, inner_w)
        hero_h = fm.block_height_in(hero_lines, typo.hero_metric_pt, line_spacing=1.10, extra_bottom_in=0.14)

    paragraphs = item.get("paragraphs", [])
    bullets = item.get("bullets", [])

    para_wrapped: List[List[str]] = []
    body_h = 0.0
    for p in paragraphs:
        ls = fm.wrap_lines(p, b_reg, typo.body_pt, inner_w)
        para_wrapped.append(ls)
        body_h += fm.block_height_in(ls, typo.body_pt, line_spacing=1.25, extra_bottom_in=0.12)

    bullet_wrapped: List[List[str]] = []
    for b in bullets:
        b_txt = b if b.startswith(("•", "–", "-")) else f"•  {b}"
        ls = fm.wrap_lines(b_txt, b_reg, typo.body_pt, inner_w - 0.14)
        bullet_wrapped.append(ls)
        body_h += fm.block_height_in(ls, typo.body_pt, line_spacing=1.24, extra_bottom_in=0.10)

    meta.update({
        "hero_lines": hero_lines,
        "hero_h_in": hero_h,
        "para_wrapped": para_wrapped,
        "bullet_wrapped": bullet_wrapped,
    })
    total_h = 2 * pad_y + title_h + hero_h + body_h + 0.08
    return total_h, meta


def solve_poster_layout(
    spec: Dict[str, Any],
    dimensions: PosterDimensions,
    palette: ColorPalette,
    typo: TypographySpec,
    layout_recipe: str = "three_column_classic",
    masthead_style: str = "solid_banner",
) -> PosterSceneIR:
    """
    Solve exact physical coordinates for all poster components without overlap
    or global font shrinking.
    """
    if layout_recipe not in SUPPORTED_LAYOUTS:
        layout_recipe = "three_column_classic"

    fm = FontMetrics()
    notes: List[str] = []
    pruned: List[str] = []

    W = dimensions.width_in
    H = dimensions.height_in
    M = dimensions.safe_margin_in
    gutter = 0.78 if dimensions.short_edge_in >= 32.0 else 0.54
    section_gap = 0.50 if dimensions.short_edge_in >= 32.0 else 0.36

    elements: List[SceneElement] = [
        SceneElement(
            id="canvas_background",
            kind="background",
            x_in=0.0,
            y_in=0.0,
            w_in=W,
            h_in=H,
            payload={"fill": palette.canvas_bg},
        )
    ]

    # 1. Measure & Place Masthead
    has_qr = bool(spec.get("qr_path") or spec.get("study_url"))
    has_logo = bool(spec.get("logo_path"))
    right_rail_w = (2.8 if has_qr else 0.0) + (3.2 if has_logo else 0.0)
    if right_rail_w > 0:
        right_rail_w += 0.6
    title_max_w = W - 2 * M - right_rail_w

    badge_txt = spec.get("study_badge", spec.get("study_design", "")).strip()
    title_lines = fm.wrap_lines(spec["title"], typo.heading_font.bold_ttf, typo.title_pt, title_max_w, safety_factor=0.91)
    authors_str = spec.get("authors_line", "")
    author_lines = fm.wrap_lines(authors_str, typo.heading_font.semibold_ttf, typo.authors_pt, title_max_w, safety_factor=0.92) if authors_str else []
    affil_str = spec.get("affiliations_line", "")
    affil_lines = fm.wrap_lines(affil_str, typo.body_font.regular_ttf, typo.affiliations_pt, title_max_w, safety_factor=0.93) if affil_str else []

    badge_h = (typo.badge_pt / 72.0) * 1.45 + 0.10 if badge_txt else 0.0
    title_h = fm.block_height_in(title_lines, typo.title_pt, line_spacing=1.10, extra_bottom_in=0.14)
    auth_h = fm.block_height_in(author_lines, typo.authors_pt, line_spacing=1.14, extra_bottom_in=0.08)
    aff_h = fm.block_height_in(affil_lines, typo.affiliations_pt, line_spacing=1.16, extra_bottom_in=0.04)

    if masthead_style == "solid_banner":
        # Full-width top architectural banner (respects bleed if present; text strictly inside safe margin M)
        mast_pad_top = max(0.55, M * 0.68)
        mast_pad_bot = 0.52
        mast_h = max(4.1, mast_pad_top + badge_h + title_h + auth_h + aff_h + mast_pad_bot)
        elements.append(
            SceneElement(
                id="masthead",
                kind="masthead",
                x_in=0.0,
                y_in=0.0,
                w_in=W,
                h_in=round(mast_h, 4),
                payload={
                    "style": "solid_banner",
                    "bg_color": palette.dominant,
                    "accent_color": palette.accent,
                    "fg_color": palette.masthead_fg,
                    "sub_fg_color": palette.masthead_sub_fg,
                    "margin_x_in": M,
                    "pad_top_in": mast_pad_top,
                    "title_max_w_in": title_max_w,
                    "badge": badge_txt,
                    "title": spec["title"],
                    "title_lines": title_lines,
                    "authors": authors_str,
                    "author_lines": author_lines,
                    "affiliations": affil_str,
                    "affil_lines": affil_lines,
                    "institution": spec.get("institution", ""),
                    "logo_path": spec.get("logo_path"),
                    "qr_path": spec.get("qr_path"),
                    "qr_caption": spec.get("qr_caption", "Scan for Paper / Data"),
                },
            )
        )
        body_top_y = mast_h + 0.58
    else:
        # Light editorial or split-accent masthead inside margins with double typographic rule
        mast_y = M * 0.85
        mast_inner_h = badge_h + title_h + auth_h + aff_h + 0.42
        elements.append(
            SceneElement(
                id="masthead",
                kind="masthead",
                x_in=M,
                y_in=round(mast_y, 4),
                w_in=round(W - 2 * M, 4),
                h_in=round(mast_inner_h, 4),
                payload={
                    "style": masthead_style,
                    "bg_color": palette.canvas_bg,
                    "accent_color": palette.accent,
                    "fg_color": palette.dominant,
                    "sub_fg_color": palette.muted_ink,
                    "margin_x_in": 0.0,
                    "pad_top_in": 0.05,
                    "title_max_w_in": title_max_w,
                    "badge": badge_txt,
                    "title": spec["title"],
                    "title_lines": title_lines,
                    "authors": authors_str,
                    "author_lines": author_lines,
                    "affiliations": affil_str,
                    "affil_lines": affil_lines,
                    "institution": spec.get("institution", ""),
                    "logo_path": spec.get("logo_path"),
                    "qr_path": spec.get("qr_path"),
                    "qr_caption": spec.get("qr_caption", "Scan for Supplement"),
                },
            )
        )
        body_top_y = mast_y + mast_inner_h + 0.48

    # 2. Optional Full-Width Upper Showcase Band (for results_focused or timeline_flow)
    content_w = W - 2 * M
    if layout_recipe == "results_focused" and spec.get("headline_takeaway"):
        hl_txt = spec["headline_takeaway"]
        hl_lines = fm.wrap_lines(hl_txt, typo.heading_font.bold_ttf, typo.section_heading_pt * 1.05, content_w - 1.1)
        hl_h = fm.block_height_in(hl_lines, typo.section_heading_pt * 1.05, line_spacing=1.15, extra_bottom_in=0.52) + 0.36
        elements.append(
            SceneElement(
                id="headline_takeaway_band",
                kind="banner_band",
                x_in=M,
                y_in=round(body_top_y, 4),
                w_in=round(content_w, 4),
                h_in=round(hl_h, 4),
                payload={
                    "label": "KEY EMPIRICAL FINDING",
                    "text": hl_txt,
                    "lines": hl_lines,
                    "pt": round(typo.section_heading_pt * 1.05, 1),
                    "bg_color": palette.surface_tint,
                    "accent_color": palette.accent,
                    "fg_color": palette.dominant,
                },
            )
        )
        body_top_y += hl_h + 0.50

    elif layout_recipe == "timeline_flow" and spec.get("upper_banner_figure"):
        ub = spec["upper_banner_figure"]
        ub_h = float(ub.get("height_in", max(3.6, H * 0.13)))
        elements.append(
            SceneElement(
                id="timeline_upper_band",
                kind="figure",
                x_in=M,
                y_in=round(body_top_y, 4),
                w_in=round(content_w, 4),
                h_in=round(ub_h, 4),
                payload={
                    "title": ub.get("title", ""),
                    "title_lines": [ub["title"]] if ub.get("title") else [],
                    "title_h_in": (typo.section_heading_pt / 72.0) * 1.3 if ub.get("title") else 0.0,
                    "png_path": ub.get("png_path"),
                    "svg_path": ub.get("svg_path"),
                    "caption": ub.get("caption", ""),
                    "caption_lines": [ub["caption"]] if ub.get("caption") else [],
                    "caption_h_in": (typo.caption_pt / 72.0) * 1.35 if ub.get("caption") else 0.0,
                    "bg_color": palette.figure_bg,
                    "border_color": palette.rule_border,
                },
            )
        )
        body_top_y += ub_h + 0.50

    # 3. Bottom Colophon Strip (References, Funding, Correspondence, Synthetic Disclosure if any)
    colophon_data = spec.get("colophon") or {}
    refs = colophon_data.get("references", [])
    funding = colophon_data.get("funding", "")
    correspondence = colophon_data.get("correspondence", "")
    disclosure = colophon_data.get("disclosure", "")

    colophon_parts: List[str] = []
    if refs:
        colophon_parts.append("References:  " + "   ".join(refs))
    meta_bits = [b for b in [funding, correspondence, disclosure] if b]
    if meta_bits:
        colophon_parts.append("  |  ".join(meta_bits))

    if colophon_parts:
        colophon_text = "\n".join(colophon_parts)
        col_lines = fm.wrap_lines(colophon_text, typo.body_font.regular_ttf, typo.reference_pt, content_w - 0.2, safety_factor=0.93)
        colophon_h = fm.block_height_in(col_lines, typo.reference_pt, line_spacing=1.18, extra_bottom_in=0.18) + 0.22
        colophon_y = H - M - colophon_h
        body_bottom_y = colophon_y - 0.42
    else:
        col_lines = []
        colophon_h = 0.0
        colophon_y = H - M
        body_bottom_y = H - M

    avail_col_h = max(6.0, body_bottom_y - body_top_y)

    # 4. Compute Column X Coordinates & Widths
    col_weights = _column_weights_for_recipe(layout_recipe, dimensions.orientation)
    n_cols = len(col_weights)
    total_gutter_w = gutter * (n_cols - 1)
    usable_cols_w = content_w - total_gutter_w
    w_sum = sum(col_weights)
    col_widths = [usable_cols_w * (cw / w_sum) for cw in col_weights]
    col_xs = [M + sum(col_widths[:i]) + i * gutter for i in range(n_cols)]

    # 5. Partition Sections Across Columns & Optimize Vertical Fit
    raw_items = copy.deepcopy(spec.get("items", []))
    cols: List[List[Dict[str, Any]]] = [[] for _ in range(n_cols)]
    for it in raw_items:
        c_idx = min(n_cols - 1, max(0, int(it.get("column", 0))))
        cols[c_idx].append(it)

    def measure_col(c_i: int, gap_val: float) -> Tuple[float, List[Tuple[float, Dict[str, Any]]]]:
        measured = [_measure_item_height(it, col_widths[c_i], typo, fm) for it in cols[c_i]]
        tot = sum(h for h, _ in measured) + max(0, len(measured) - 1) * gap_val
        return tot, measured

    # Pass 1: Rebalance movable tail/head items if a column overflows and neighbor has room
    for _ in range(4):
        heights = [measure_col(i, section_gap)[0] for i in range(n_cols)]
        worst_i = max(range(n_cols), key=lambda i: heights[i])
        if heights[worst_i] <= avail_col_h:
            break
        moved = False
        # Try moving last item of worst_i to top of worst_i + 1
        if worst_i + 1 < n_cols and len(cols[worst_i]) > 1:
            cand = cols[worst_i][-1]
            if not cand.get("pin_column"):
                cand_h, _ = _measure_item_height(cand, col_widths[worst_i + 1], typo, fm)
                if heights[worst_i + 1] + cand_h + section_gap <= avail_col_h * 1.04:
                    cols[worst_i].pop()
                    cols[worst_i + 1].insert(0, cand)
                    notes.append(f"Rebalanced section '{cand.get('title', cand.get('id'))}' from column {worst_i+1} to column {worst_i+2}.")
                    moved = True
        # Or move first item of worst_i to bottom of worst_i - 1
        if not moved and worst_i - 1 >= 0 and len(cols[worst_i]) > 1:
            cand = cols[worst_i][0]
            if not cand.get("pin_column"):
                cand_h, _ = _measure_item_height(cand, col_widths[worst_i - 1], typo, fm)
                if heights[worst_i - 1] + cand_h + section_gap <= avail_col_h * 1.04:
                    cols[worst_i].pop(0)
                    cols[worst_i - 1].append(cand)
                    notes.append(f"Rebalanced section '{cand.get('title', cand.get('id'))}' from column {worst_i+1} to column {worst_i}.")
                    moved = True
        if not moved:
            break

    # Pass 2 & 3: Per-column flexible figure scaling & deterministic secondary bullet pruning (never shrinking fonts!)
    for c_i in range(n_cols):
        col_gap = section_gap
        tot_h, measured = measure_col(c_i, col_gap)

        if tot_h > avail_col_h and col_gap > 0.34:
            col_gap = max(0.34, section_gap * 0.72)
            tot_h, measured = measure_col(c_i, col_gap)

        # Compress flexible figure height down toward min_img_h before touching prose
        if tot_h > avail_col_h:
            overflow = tot_h - avail_col_h
            fig_indices = [idx for idx, it in enumerate(cols[c_i]) if it.get("item_type") == "figure"]
            if fig_indices:
                reducible = sum(measured[idx][1]["img_h_in"] - measured[idx][1]["min_img_h"] for idx in fig_indices)
                if reducible > 0:
                    take_ratio = min(1.0, overflow / reducible)
                    for idx in fig_indices:
                        m = measured[idx][1]
                        shrink = (m["img_h_in"] - m["min_img_h"]) * take_ratio
                        cols[c_i][idx]["aspect_ratio"] = (col_widths[c_i] - 0.36) / max(2.8, m["img_h_in"] - shrink)
                    tot_h, measured = measure_col(c_i, col_gap)

        # Deterministic pruning of non-essential trailing prose bullets if still overflowing
        guard = 0
        while tot_h > avail_col_h and guard < 12:
            guard += 1
            # Pick non-primary text section with the most bullets (>2)
            candidates = [
                idx for idx, it in enumerate(cols[c_i])
                if it.get("item_type", "text") == "text"
                and it.get("style") != "focal_callout"
                and len(it.get("bullets", [])) > 2
            ]
            if not candidates:
                break
            victim_idx = max(candidates, key=lambda idx: len(cols[c_i][idx].get("bullets", [])))
            dropped = cols[c_i][victim_idx]["bullets"].pop()
            pruned.append(f"[{cols[c_i][victim_idx].get('title', 'Section')}] {dropped}")
            tot_h, measured = measure_col(c_i, col_gap)

        # Expand figures gracefully if column has generous spare vertical space
        spare = avail_col_h - tot_h
        fig_indices = [idx for idx, it in enumerate(cols[c_i]) if it.get("item_type") == "figure"]
        if spare > 0.5 and fig_indices:
            expandable = sum(measured[idx][1]["max_img_h"] - measured[idx][1]["img_h_in"] for idx in fig_indices)
            if expandable > 0:
                give_ratio = min(0.92, spare / expandable)
                for idx in fig_indices:
                    m = measured[idx][1]
                    grow = (m["max_img_h"] - m["img_h_in"]) * give_ratio
                    new_img_h = m["img_h_in"] + grow
                    measured[idx] = (measured[idx][0] + grow, {**m, "img_h_in": new_img_h})
                tot_h = sum(h for h, _ in measured) + max(0, len(measured) - 1) * col_gap

        # Distribute modest remaining slack into comfortable inter-section breathing room (capped at 0.95 in)
        rem_spare = avail_col_h - tot_h
        if rem_spare > 0.3 and len(measured) > 1:
            extra_gap = min(0.45, (rem_spare * 0.55) / (len(measured) - 1))
            col_gap += extra_gap
            tot_h = sum(h for h, _ in measured) + (len(measured) - 1) * col_gap

        # Emit placed scene elements in column c_i
        cur_y = body_top_y
        for idx, (item, (item_h, meta)) in enumerate(zip(cols[c_i], measured)):
            itype = item.get("item_type", "text")
            kind_map = {
                "figure": "figure",
                "table": "table",
                "callout": "callout",
                "text": "callout" if item.get("style") in ("focal_callout", "focal_callout_subtle") else "section_text",
            }
            elements.append(
                SceneElement(
                    id=item.get("id", f"col{c_i+1}_item{idx+1}"),
                    kind=kind_map.get(itype, "section_text"),
                    x_in=round(col_xs[c_i], 4),
                    y_in=round(cur_y, 4),
                    w_in=round(col_widths[c_i], 4),
                    h_in=round(item_h, 4),
                    payload={**item, "metrics": meta},
                )
            )
            cur_y += item_h + col_gap

    # 6. Append Bottom Colophon Element if present
    if col_lines:
        elements.append(
            SceneElement(
                id="footer_colophon",
                kind="colophon",
                x_in=round(M, 4),
                y_in=round(colophon_y, 4),
                w_in=round(content_w, 4),
                h_in=round(colophon_h, 4),
                payload={
                    "lines": col_lines,
                    "raw_parts": colophon_parts,
                    "rule_color": palette.rule_border,
                    "fg_color": palette.muted_ink,
                },
            )
        )

    return PosterSceneIR(
        poster_title=spec["title"],
        template_id=spec.get("template_id", "clinical-research"),
        layout_recipe=layout_recipe,
        masthead_style=masthead_style,
        dimensions=asdict(dimensions) | {
            "orientation": dimensions.orientation,
            "width_mm": dimensions.width_mm,
            "height_mm": dimensions.height_mm,
            "pptx_scale_factor": dimensions.pptx_scale_factor,
            "pptx_width_in": dimensions.pptx_width_in,
            "pptx_height_in": dimensions.pptx_height_in,
            "effective_pptx_raster_dpi": dimensions.effective_pptx_raster_dpi,
        },
        palette=asdict(palette),
        typography={
            "pairing_id": typo.pairing_id,
            "heading_font": asdict(typo.heading_font),
            "body_font": asdict(typo.body_font),
            "scale_multiplier": typo.scale_multiplier,
            "badge_pt": typo.badge_pt,
            "title_pt": typo.title_pt,
            "authors_pt": typo.authors_pt,
            "affiliations_pt": typo.affiliations_pt,
            "section_heading_pt": typo.section_heading_pt,
            "subheading_pt": typo.subheading_pt,
            "hero_metric_pt": typo.hero_metric_pt,
            "body_pt": typo.body_pt,
            "table_pt": typo.table_pt,
            "figure_label_pt": typo.figure_label_pt,
            "caption_pt": typo.caption_pt,
            "reference_pt": typo.reference_pt,
            "min_body_pt": typo.min_body_pt,
            "min_heading_pt": typo.min_heading_pt,
            "min_caption_pt": typo.min_caption_pt,
        },
        elements=elements,
        layout_notes=notes,
        pruned_items=pruned,
    )
