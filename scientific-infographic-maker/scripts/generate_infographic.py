#!/usr/bin/env python3
"""
Scientific & Medical Editorial Infographic Generator.
Exports SVG, vector PDF (Type 42 TrueType), 300-DPI PNG, and editable PPTX.
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


def _rgb(h: str) -> RGBColor:
    s = h.lstrip("#")
    return RGBColor(int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def render_infographic(spec: Dict[str, Any], out_dir: pathlib.Path) -> Dict[str, Any]:
    db = json.loads((SKILL_ROOT / "templates" / "infographic_presets.json").read_text(encoding="utf-8"))
    preset_id = spec.get("preset", "editorial-legal")
    pr = db["presets"].get(preset_id, db["presets"]["editorial-legal"])
    pal = db["palettes"].get(spec.get("palette", "emerald_public_health"), db["palettes"]["emerald_public_health"])

    W, H, dpi = float(pr["width_in"]), float(pr["height_in"]), int(pr["dpi"])
    sc = W / 8.5
    base_pt = 9.5 * sc

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

    # Masthead Banner (y: 89 -> 100)
    ax.add_patch(mpatches.Rectangle((0, 89.2), 100, 10.8, facecolor=pal["dominant"], edgecolor="none"))
    ax.add_patch(mpatches.Rectangle((0, 88.5), 100, 0.7, facecolor=pal["accent"], edgecolor="none"))
    ax.text(4.0, 97.6, spec.get("category_tag", "SCIENTIFIC & CLINICAL EVIDENCE BRIEF").upper(), color="#E2ECE9", fontsize=base_pt * 0.80, fontweight="bold", va="top")
    title_wrapped = "\n".join(textwrap.wrap(spec["title"], width=52))
    ax.text(4.0, 94.0, title_wrapped, color="#FFFFFF", fontsize=base_pt * 1.48, fontweight="bold", va="center", linespacing=1.15)
    if spec.get("subtitle"):
        ax.text(4.0, 90.1, spec["subtitle"], color="#DCE7E3", fontsize=base_pt * 0.86, va="center")

    # Band 1: Epidemiology & Disease Burden KPIs (y: 75.5 -> 86.8)
    ax.text(4.0, 86.8, "1. EPIDEMIOLOGY & DISEASE BURDEN", color=pal["dominant"], fontsize=base_pt * 0.96, fontweight="bold", va="top")
    kpis: List[Dict[str, str]] = spec.get("epidemiology_kpis", [])[:4]
    if kpis:
        kw = (92.0 - 2.2 * (len(kpis) - 1)) / len(kpis)
        for i, k in enumerate(kpis):
            kx = 4.0 + i * (kw + 2.2)
            ax.add_patch(mpatches.FancyBboxPatch((kx, 74.8), kw, 9.8, boxstyle="round,pad=0.2,rounding_size=0.9", facecolor=pal["card"], edgecolor=pal["border"], linewidth=1.1))
            ax.add_patch(mpatches.Rectangle((kx, 83.8), kw, 0.8, facecolor=pal["accent"] if i == 0 else pal["secondary"], edgecolor="none"))
            ax.text(kx + kw / 2, 81.0, k["metric"], color=pal["accent"] if i == 0 else pal["dominant"], fontsize=base_pt * 1.38, fontweight="bold", ha="center", va="center")
            lbl_w = "\n".join(textwrap.wrap(k["label"], width=20))
            ax.text(kx + kw / 2, 77.2, lbl_w, color=pal["muted"], fontsize=base_pt * 0.78, ha="center", va="center", linespacing=1.15)

    # Band 2: Mechanism of Disease Cascade (y: 56.5 -> 72.5)
    ax.text(4.0, 72.4, "2. MECHANISM OF DISEASE & PATHOPHYSIOLOGY", color=pal["dominant"], fontsize=base_pt * 0.96, fontweight="bold", va="top")
    mechs: List[Dict[str, str]] = spec.get("mechanism_steps", [])[:4]
    if mechs:
        mw = (92.0 - 3.0 * (len(mechs) - 1)) / len(mechs)
        for i, m in enumerate(mechs):
            mx = 4.0 + i * (mw + 3.0)
            ax.add_patch(mpatches.FancyBboxPatch((mx, 56.2), mw, 13.8, boxstyle="round,pad=0.2,rounding_size=0.9", facecolor=pal["tint"], edgecolor=pal["secondary"], linewidth=1.1))
            ax.add_patch(mpatches.Circle((mx + 2.6, 67.6), 1.4, facecolor=pal["dominant"], edgecolor="none"))
            ax.text(mx + 2.6, 67.6, str(i + 1), color="#FFFFFF", fontsize=base_pt * 0.78, fontweight="bold", ha="center", va="center")
            ax.text(mx + 5.0, 67.6, m["stage"], color=pal["dominant"], fontsize=base_pt * 0.84, fontweight="bold", va="center")
            body_w = "\n".join(textwrap.wrap(m["detail"], width=23))
            ax.text(mx + 1.6, 64.4, body_w, color=pal["ink"], fontsize=base_pt * 0.78, va="top", linespacing=1.22)
            if i < len(mechs) - 1:
                ax.annotate("", xy=(mx + mw + 2.6, 63.0), xytext=(mx + mw + 0.4, 63.0), arrowprops={"arrowstyle": "-|>", "color": pal["accent"], "lw": 1.8, "mutation_scale": 13})

    # Band 3: Left = Clinical Pathway (x: 4->52), Right = Quantitative Evidence Chart (x: 55->96), y: 24.5 -> 53.8
    ax.text(4.0, 53.8, "3. CLINICAL PATHWAY & PROTOCOL", color=pal["dominant"], fontsize=base_pt * 0.96, fontweight="bold", va="top")
    ax.text(55.0, 53.8, "4. QUANTITATIVE EVIDENCE", color=pal["dominant"], fontsize=base_pt * 0.96, fontweight="bold", va="top")

    steps: List[Dict[str, str]] = spec.get("clinical_pathway", [])[:4]
    if steps:
        sh = 25.0 / len(steps)
        for i, stp in enumerate(steps):
            sy = 51.2 - (i + 1) * sh + 0.8
            ax.add_patch(mpatches.FancyBboxPatch((4.0, sy), 47.5, sh - 1.0, boxstyle="round,pad=0.15,rounding_size=0.7", facecolor=pal["card"], edgecolor=pal["border"], linewidth=1.0))
            ax.add_patch(mpatches.Rectangle((4.0, sy), 1.4, sh - 1.0, facecolor=pal["secondary"], edgecolor="none"))
            ax.text(6.6, sy + sh - 2.1, f"{stp['time_or_step']} — {stp['action']}", color=pal["dominant"], fontsize=base_pt * 0.82, fontweight="bold", va="top")
            ax.text(6.6, sy + sh - 4.3, "\n".join(textwrap.wrap(stp["criteria"], width=54)), color=pal["ink"], fontsize=base_pt * 0.74, va="top", linespacing=1.14)

    chart = spec.get("evidence_chart")
    if chart:
        ax.add_patch(mpatches.FancyBboxPatch((55.0, 26.2), 41.0, 25.0, boxstyle="round,pad=0.2,rounding_size=0.9", facecolor=pal["card"], edgecolor=pal["border"], linewidth=1.0))
        ax.text(57.0, 49.4, chart["title"], color=pal["ink"], fontsize=base_pt * 0.84, fontweight="bold", va="top")
        cax = fig.add_axes([0.665, 0.295, 0.275, 0.165])
        cax.patch.set_alpha(0.0)
        labels_c = chart["labels"]
        vals_c = [float(v) for v in chart["values"]]
        pos_c = np.arange(len(vals_c))
        cols_c = [pal["accent"] if i == 0 else pal["secondary"] for i in range(len(vals_c))]
        bars = cax.barh(pos_c, vals_c, color=cols_c, height=0.55)
        cax.set_yticks(pos_c)
        cax.set_yticklabels(labels_c, fontsize=base_pt * 0.74, fontweight="bold")
        cax.invert_yaxis()
        cax.set_xlim(0, max(vals_c) * 1.36)
        unit = chart.get("unit", "%")
        for b, v in zip(bars, vals_c):
            cax.text(v + max(vals_c) * 0.03, b.get_y() + b.get_height() / 2, f"{v:g}{unit}", va="center", fontsize=base_pt * 0.74, fontweight="bold", color=pal["ink"])
        cax.spines["top"].set_visible(False)
        cax.spines["right"].set_visible(False)
        cax.set_xlabel(chart.get("x_label", "Outcome Rate"), fontsize=base_pt * 0.74, fontweight="bold")
        cax.tick_params(axis="x", labelsize=base_pt * 0.70)

    # Band 4: Medical Education Key Pearls & Red Flags (y: 5.8 -> 23.2)
    ax.add_patch(mpatches.FancyBboxPatch((4.0, 6.2), 92.0, 16.8, boxstyle="round,pad=0.2,rounding_size=0.9", facecolor=pal["tint"], edgecolor=pal["dominant"], linewidth=1.2))
    ax.text(6.0, 21.3, "5. MEDICAL EDUCATION PEARLS & RED-FLAG INDICATORS", color=pal["dominant"], fontsize=base_pt * 0.92, fontweight="bold", va="top")
    pearls = spec.get("education_pearls", [])[:4]
    for i, prl in enumerate(pearls):
        col_x = 6.0 if i % 2 == 0 else 51.5
        row_y = 18.0 if i < 2 else 12.0
        wrapped_p = "\n".join(textwrap.wrap(f"• {prl}", width=46))
        ax.text(col_x, row_y, wrapped_p, color=pal["ink"], fontsize=base_pt * 0.78, va="top", linespacing=1.2)

    # Citation footer
    ax.text(4.0, 3.0, spec.get("source_footer", "SYNTHETIC EDUCATIONAL INFOGRAPHIC"), color=pal["muted"], fontsize=base_pt * 0.70, va="center")

    out_dir.mkdir(parents=True, exist_ok=True)
    svg_p, pdf_p, png_p = out_dir / "infographic.svg", out_dir / "infographic.pdf", out_dir / "infographic.png"
    fig.savefig(svg_p, format="svg", facecolor=fig.get_facecolor())
    fig.savefig(pdf_p, format="pdf", facecolor=fig.get_facecolor())
    fig.savefig(png_p, format="png", dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)

    # Editable PPTX export
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    sl.background.fill.solid()
    sl.background.fill.fore_color.rgb = _rgb(pal["canvas"])
    hdr = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(W), Inches(H * 0.11))
    hdr.fill.solid()
    hdr.fill.fore_color.rgb = _rgb(pal["dominant"])
    hdr.line.fill.background()
    r = hdr.text_frame.paragraphs[0].add_run()
    r.text = spec["title"]
    r.font.bold = True
    r.font.size = Pt(base_pt * 1.4)
    r.font.color.rgb = _rgb("#FFFFFF")

    for idx, sec_title in enumerate(["Epidemiology KPIs", "Disease Mechanism", "Clinical Pathway", "Education Pearls"]):
        bx = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(W * 0.04), Inches(H * (0.14 + idx * 0.20)), Inches(W * 0.92), Inches(H * 0.17))
        bx.fill.solid()
        bx.fill.fore_color.rgb = _rgb(pal["card"])
        bx.line.color.rgb = _rgb(pal["border"])
        p = bx.text_frame.paragraphs[0]
        rr = p.add_run()
        rr.text = sec_title
        rr.font.bold = True
        rr.font.size = Pt(base_pt)
        rr.font.color.rgb = _rgb(pal["dominant"])

    pptx_p = out_dir / "infographic.pptx"
    prs.save(str(pptx_p))
    return {"preset": preset_id, "width_in": W, "height_in": H, "files": {"svg": str(svg_p), "pdf": str(pdf_p), "png": str(png_p), "pptx": str(pptx_p)}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    spec = json.loads(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    print(json.dumps(render_infographic(spec, pathlib.Path(args.output_dir)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
