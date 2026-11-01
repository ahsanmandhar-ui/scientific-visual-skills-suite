#!/usr/bin/env python3
"""
Graphical Abstract & Visual Abstract Generator.

Generates publication-ready SVG, PDF (embedded TrueType Type 42), 300-DPI PNG,
and editable PowerPoint (.pptx) from structured study specifications.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import textwrap
from typing import Any, Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
import numpy as np
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

SKILL_ROOT = pathlib.Path(__file__).resolve().parents[1]
SHARED_FONTS = SKILL_ROOT.parent / "research-poster-maker" / "assets" / "fonts"
if SHARED_FONTS.exists():
    for _ttf in SHARED_FONTS.glob("*.ttf"):
        try:
            font_manager.fontManager.addfont(str(_ttf))
        except Exception:
            pass


def _hex_rgb(h: str) -> RGBColor:
    s = h.lstrip("#")
    return RGBColor(int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def _draw_vector_icon(ax: plt.Axes, kind: str, cx: float, cy: float, r: float, color: str) -> None:
    """Draw clean geometric vector emblem (cohort, molecule/rx, chart) without emoji fonts."""
    circ = mpatches.Circle((cx, cy), r, facecolor="#FFFFFF", edgecolor=color, linewidth=1.6, zorder=4)
    ax.add_patch(circ)
    if kind == "cohort":
        # Stylized person silhouette
        ax.add_patch(mpatches.Circle((cx, cy + r * 0.24), r * 0.24, facecolor=color, zorder=5))
        wedge = mpatches.Wedge((cx, cy - r * 0.52), r * 0.48, 25, 155, facecolor=color, zorder=5)
        ax.add_patch(wedge)
    elif kind == "intervention":
        # Stylized capsule / molecular cross
        ax.add_patch(mpatches.Rectangle((cx - r * 0.14, cy - r * 0.46), r * 0.28, r * 0.92, facecolor=color, zorder=5))
        ax.add_patch(mpatches.Rectangle((cx - r * 0.46, cy - r * 0.14), r * 0.92, r * 0.28, facecolor=color, zorder=5))
    else:
        # Stylized ascending bars
        for bi, bh in enumerate([0.35, 0.62, 0.90]):
            bx = cx - r * 0.44 + bi * r * 0.32
            ax.add_patch(mpatches.Rectangle((bx, cy - r * 0.42), r * 0.20, r * bh, facecolor=color, zorder=5))


def render_graphical_abstract(spec: Dict[str, Any], out_dir: pathlib.Path) -> Dict[str, Any]:
    presets_db = json.loads((SKILL_ROOT / "templates" / "journal_presets.json").read_text(encoding="utf-8"))
    preset_id = spec.get("preset", "bmj-visual-abstract")
    preset = presets_db["presets"].get(preset_id, presets_db["presets"]["bmj-visual-abstract"])
    pal = presets_db["palettes"].get(spec.get("palette", "oxford_clinical"), presets_db["palettes"]["oxford_clinical"])

    W = float(spec.get("width_in", preset["width_in"]))
    H = float(spec.get("height_in", preset["height_in"]))
    dpi = int(spec.get("dpi", preset["dpi"]))
    layout_mode = spec.get("orientation", preset["orientation"])
    show_header = bool(spec.get("show_header", preset["show_header"]))

    scale = min(W / 12.5, H / 5.0) if layout_mode == "horizontal_3panel" else (W / 10.0)
    scale = max(0.62, min(1.35, scale))
    base_pt = 11.5 * scale

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["IBM Plex Sans", "Source Sans 3", "DejaVu Sans"],
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "path",
    })

    fig = plt.figure(figsize=(W, H), facecolor=pal["canvas"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    ax.add_patch(mpatches.Rectangle((0, 0), 100, 100, facecolor=pal["canvas"], edgecolor="none"))

    # Header & Footer bands
    top_y = 96.5
    if show_header and spec.get("headline"):
        ax.add_patch(mpatches.Rectangle((0, 84.5), 100, 15.5, facecolor=pal["dominant"], edgecolor="none"))
        ax.add_patch(mpatches.Rectangle((0, 83.7), 100, 0.8, facecolor=pal["accent"], edgecolor="none"))
        if spec.get("study_badge"):
            ax.text(2.8, 96.4, spec["study_badge"].upper(), color="#DCE6F2", fontsize=base_pt * 0.82, fontweight="bold", va="top")
        ax.text(2.8, 91.5, spec["headline"], color="#FFFFFF", fontsize=base_pt * 1.30, fontweight="bold", va="center")
        top_y = 80.5

    bot_y = 4.0
    if spec.get("citation_footer"):
        ax.plot([2.5, 97.5], [7.2, 7.2], color=pal["border"], lw=1.0)
        ax.text(2.8, 3.6, spec["citation_footer"], color=pal["muted"], fontsize=base_pt * 0.80, va="center")
        bot_y = 9.2

    stages: List[Dict[str, Any]] = spec["stages"][:3]  # 3 canonical panels: Population/Design, Intervention/Mechanism, Outcomes

    if layout_mode == "horizontal_3panel":
        panel_w = 29.2
        xs = [2.5, 35.4, 68.3]
        panel_h = top_y - bot_y
        icons = ["cohort", "intervention", "outcome"]
        cols = [pal["dominant"], pal["secondary"], pal["accent"]]

        for i, st in enumerate(stages):
            px = xs[i]
            card = mpatches.FancyBboxPatch(
                (px, bot_y), panel_w, panel_h,
                boxstyle="round,pad=0.3,rounding_size=1.2",
                facecolor=pal["panel_tint"] if i < 2 else "#FFFFFF",
                edgecolor=cols[i] if i == 2 else pal["border"],
                linewidth=1.8 if i == 2 else 1.1,
            )
            ax.add_patch(card)
            # Top stage strip
            ax.add_patch(mpatches.Rectangle((px, bot_y + panel_h - 8.5), panel_w, 8.5, facecolor=cols[i], edgecolor="none"))
            _draw_vector_icon(ax, icons[i], px + 3.2, bot_y + panel_h - 4.25, 2.5, cols[i])
            ax.text(px + 6.8, bot_y + panel_h - 4.25, st["title"].upper(), color="#FFFFFF", fontsize=base_pt * 0.94, fontweight="bold", va="center")

            cur_y = bot_y + panel_h - 12.5
            if st.get("hero_stat"):
                ax.text(px + 2.0, cur_y, st["hero_stat"], color=cols[i], fontsize=base_pt * 1.32, fontweight="bold", va="top")
                cur_y -= 9.5

            wrap_chars = max(24, int(33 / max(0.75, scale * 0.85)))
            for bul in st.get("bullets", []):
                wrapped = "\n".join(textwrap.wrap(f"• {bul}", width=wrap_chars))
                n_ln = wrapped.count("\n") + 1
                ax.text(px + 2.0, cur_y, wrapped, color=pal["ink"], fontsize=base_pt * 0.92, va="top", linespacing=1.25)
                cur_y -= (n_ln * 5.6 + 2.6)

            # Optional embedded mini bar chart in Outcome panel
            if st.get("mini_bars"):
                mb = st["mini_bars"]  # [{"label": ..., "value": ..., "display": ...}]
                chart_ax = fig.add_axes([(px + 8.6) / 100.0, (bot_y + 4.2) / 100.0, (panel_w - 10.6) / 100.0, min(0.30, (cur_y - bot_y - 5.5) / 100.0)])
                chart_ax.patch.set_alpha(0.0)
                labels_b = [b["label"] for b in mb]
                vals_b = [float(b["value"]) for b in mb]
                b_cols = [pal["accent"], pal["dominant"], pal["positive"]][: len(vals_b)]
                y_pos = np.arange(len(vals_b))
                bars = chart_ax.barh(y_pos, vals_b, color=b_cols, height=0.52)
                chart_ax.set_yticks(y_pos)
                chart_ax.set_yticklabels(labels_b, fontsize=base_pt * 0.78, fontweight="bold")
                chart_ax.invert_yaxis()
                chart_ax.set_xlim(0, max(vals_b) * 1.42)
                for b_obj, b_item in zip(bars, mb):
                    disp = b_item.get("display", f"{b_item['value']}")
                    chart_ax.text(b_obj.get_width() + max(vals_b) * 0.03, b_obj.get_y() + b_obj.get_height() / 2, disp, va="center", fontsize=base_pt * 0.78, fontweight="bold", color=pal["ink"])
                chart_ax.spines["top"].set_visible(False)
                chart_ax.spines["right"].set_visible(False)
                chart_ax.spines["bottom"].set_visible(False)
                chart_ax.set_xticks([])

            # Directional connector arrow to next panel
            if i < 2:
                mid_y = bot_y + panel_h / 2.0
                ax.annotate(
                    "", xy=(xs[i + 1] - 0.5, mid_y), xytext=(px + panel_w + 0.5, mid_y),
                    arrowprops={"arrowstyle": "-|>", "color": pal["dominant"], "lw": 2.2, "mutation_scale": 16},
                )
    else:
        # Vertical 3-tier square architecture (Cell Press style)
        tier_h = (top_y - bot_y - 7.0) / 3.0
        cols = [pal["dominant"], pal["secondary"], pal["accent"]]
        for i, st in enumerate(stages):
            ty = top_y - (i + 1) * tier_h - i * 3.5
            card = mpatches.FancyBboxPatch(
                (4.0, ty), 92.0, tier_h,
                boxstyle="round,pad=0.3,rounding_size=1.2",
                facecolor=pal["panel_tint"] if i < 2 else "#FFFFFF",
                edgecolor=cols[i] if i == 2 else pal["border"],
                linewidth=1.6,
            )
            ax.add_patch(card)
            ax.add_patch(mpatches.Rectangle((4.0, ty), 2.2, tier_h, facecolor=cols[i], edgecolor="none"))
            ax.text(8.0, ty + tier_h - 3.2, st["title"].upper(), color=cols[i], fontsize=base_pt * 1.0, fontweight="bold", va="top")
            if st.get("hero_stat"):
                ax.text(94.0, ty + tier_h - 3.2, st["hero_stat"], color=pal["accent"], fontsize=base_pt * 1.08, fontweight="bold", va="top", ha="right")
            cy_b = ty + tier_h - 9.0
            for bul in st.get("bullets", []):
                ax.text(8.0, cy_b, f"•  {bul}", color=pal["ink"], fontsize=base_pt * 0.90, va="top")
                cy_b -= 5.2
            if i < 2:
                ax.annotate("", xy=(50, ty - 3.1), xytext=(50, ty - 0.4), arrowprops={"arrowstyle": "-|>", "color": pal["dominant"], "lw": 2.0, "mutation_scale": 15})

    out_dir.mkdir(parents=True, exist_ok=True)
    svg_p = out_dir / "graphical_abstract.svg"
    pdf_p = out_dir / "graphical_abstract.pdf"
    png_p = out_dir / "graphical_abstract.png"
    fig.savefig(svg_p, format="svg", facecolor=fig.get_facecolor())
    fig.savefig(pdf_p, format="pdf", facecolor=fig.get_facecolor())
    fig.savefig(png_p, format="png", dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)

    # Also build native editable PowerPoint (.pptx)
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    sl.background.fill.solid()
    sl.background.fill.fore_color.rgb = _hex_rgb(pal["canvas"])

    if show_header and spec.get("headline"):
        hb = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(W), Inches(H * 0.16))
        hb.fill.solid()
        hb.fill.fore_color.rgb = _hex_rgb(pal["dominant"])
        hb.line.fill.background()
        tf = hb.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        r0 = p0.add_run()
        r0.text = spec["headline"]
        r0.font.size = Pt(base_pt * 1.35)
        r0.font.bold = True
        r0.font.color.rgb = _hex_rgb("#FFFFFF")

    for i, st in enumerate(stages):
        bx = Inches(W * (0.03 + i * 0.325)) if layout_mode == "horizontal_3panel" else Inches(W * 0.04)
        by = Inches(H * 0.20) if layout_mode == "horizontal_3panel" else Inches(H * (0.06 + i * 0.31))
        bw = Inches(W * 0.29) if layout_mode == "horizontal_3panel" else Inches(W * 0.92)
        bh = Inches(H * 0.70) if layout_mode == "horizontal_3panel" else Inches(H * 0.27)
        box = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, by, bw, bh)
        box.fill.solid()
        box.fill.fore_color.rgb = _hex_rgb(pal["panel_tint"] if i < 2 else "#FFFFFF")
        box.line.color.rgb = _hex_rgb(pal["accent"] if i == 2 else pal["border"])
        btf = box.text_frame
        btf.word_wrap = True
        tp = btf.paragraphs[0]
        tr = tp.add_run()
        tr.text = st["title"]
        tr.font.bold = True
        tr.font.size = Pt(base_pt * 1.05)
        tr.font.color.rgb = _hex_rgb(pal["dominant"])
        if st.get("hero_stat"):
            sp = btf.add_paragraph()
            sr = sp.add_run()
            sr.text = st["hero_stat"]
            sr.font.bold = True
            sr.font.size = Pt(base_pt * 1.25)
            sr.font.color.rgb = _hex_rgb(pal["accent"])
        for bul in st.get("bullets", []):
            bp = btf.add_paragraph()
            br = bp.add_run()
            br.text = f"• {bul}"
            br.font.size = Pt(base_pt * 0.92)
            br.font.color.rgb = _hex_rgb(pal["ink"])

    pptx_p = out_dir / "graphical_abstract.pptx"
    prs.save(str(pptx_p))
    return {
        "preset": preset_id,
        "width_in": W,
        "height_in": H,
        "dpi": dpi,
        "files": {"svg": str(svg_p), "pdf": str(pdf_p), "png": str(png_p), "pptx": str(pptx_p)},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate journal-ready graphical abstract.")
    ap.add_argument("--spec", required=True, help="Path to ga_spec.json")
    ap.add_argument("--output-dir", required=True, help="Output directory")
    args = ap.parse_args()
    spec = json.loads(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    res = render_graphical_abstract(spec, pathlib.Path(args.output_dir))
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
