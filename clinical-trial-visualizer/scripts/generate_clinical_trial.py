#!/usr/bin/env python3
"""
Clinical Trial Visualizer: CONSORT Flow + SPIRIT Timeline + Efficacy + Adverse Events.
Exports SVG, vector PDF (Type 42), 300-DPI PNG, and editable PPTX.
"""

from __future__ import annotations

import argparse
import json
import pathlib
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


def _box(ax: plt.Axes, x: float, y: float, w: float, h: float, title: str, lines: List[str], edge: str = "#64748B", fill: str = "#FFFFFF", title_col: str = "#0F172A", fs: float = 8.0) -> None:
    ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15,rounding_size=0.7", facecolor=fill, edgecolor=edge, lw=1.15, zorder=3))
    ax.text(x + 1.1, y + h - 1.5, title, fontsize=fs * 1.03, fontweight="bold", color=title_col, va="top", zorder=4)
    if lines:
        ax.text(x + 1.1, y + h - 4.1, "\n".join(lines), fontsize=fs * 0.92, color="#1E293B", va="top", linespacing=1.22, zorder=4)


def render_clinical_trial(spec: Dict[str, Any], out_dir: pathlib.Path) -> Dict[str, Any]:
    pal = json.loads((SKILL_ROOT / "templates" / "trial_presets.json").read_text(encoding="utf-8"))["palettes"]["consort_editorial"]
    W, H, dpi = float(spec.get("width_in", 15.0)), float(spec.get("height_in", 10.0)), int(spec.get("dpi", 300))

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["IBM Plex Sans", "Source Sans 3", "DejaVu Sans"],
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "path",
    })

    fig = plt.figure(figsize=(W, H), facecolor="#FFFFFF")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Header Banner
    ax.add_patch(mpatches.Rectangle((0, 90.5), 100, 9.5, facecolor=pal["header"], edgecolor="none"))
    ax.add_patch(mpatches.Rectangle((0, 89.8), 100, 0.7, facecolor=pal["accent"], edgecolor="none"))
    ax.text(2.5, 97.4, spec.get("trial_registry", "SYNTHETIC CLINICAL TRIAL SUMMARY"), color="#CBD5E1", fontsize=8.4, fontweight="bold", va="top")
    ax.text(2.5, 93.4, spec["title"], color="#FFFFFF", fontsize=13.2, fontweight="bold", va="center")

    # LEFT HALF (x: 2.5 -> 53.5, y: 20 -> 88): CONSORT 4-Phase Participant Flow
    ax.text(2.5, 87.5, "A. CONSORT PARTICIPANT FLOW", color=pal["header"], fontsize=10.2, fontweight="bold", va="top")
    cf = spec["consort"]
    excl_total = sum(int(r["n"]) for r in cf["excluded_reasons"])
    excl_lines = [f"• {r['reason']} (n = {r['n']})" for r in cf["excluded_reasons"]]

    # Phase badges on left rail
    for py, plbl in [(79.0, "Enrollment"), (59.5, "Allocation"), (43.0, "Follow-Up"), (26.5, "Analysis")]:
        ax.add_patch(mpatches.FancyBboxPatch((2.5, py), 7.8, 4.2, boxstyle="round,pad=0.1,rounding_size=0.6", facecolor=pal["phase_badge"], edgecolor=pal["border"], lw=0.8))
        ax.text(6.4, py + 2.1, plbl, fontsize=7.4, fontweight="bold", color=pal["header"], ha="center", va="center")

    # Assessed & Excluded boxes
    _box(ax, 12.0, 77.5, 18.5, 7.2, f"Assessed (N = {cf['assessed']})", [f"Screened across {cf.get('sites', 18)} sites"], edge=pal["header"], fs=7.8)
    _box(ax, 33.5, 74.0, 19.5, 11.2, f"Excluded (n = {excl_total})", excl_lines[:3], edge="#94A3B8", fill="#F8FAFC", fs=7.3)
    ax.annotate("", xy=(33.3, 80.5), xytext=(30.6, 80.5), arrowprops={"arrowstyle": "-|>", "color": "#64748B", "lw": 1.3})

    # Randomized box
    _box(ax, 15.0, 66.2, 21.0, 6.2, f"Randomized (N = {cf['randomized']})", [cf.get("randomization_ratio", "1:1 Stratified Allocation")], edge=pal["header"], fill="#EEF6FB", title_col=pal["arm_active"], fs=7.8)
    ax.annotate("", xy=(21.2, 72.6), xytext=(21.2, 77.3), arrowprops={"arrowstyle": "-|>", "color": pal["header"], "lw": 1.5})

    arms = cf["arms"][:2]
    arm_xs = [11.5, 33.0]
    for idx, arm in enumerate(arms):
        ax_x = arm_xs[idx]
        acol = pal["arm_active"] if idx == 0 else pal["arm_control"]
        # Split arrow from Randomized
        ax.annotate("", xy=(ax_x + 9.5, 62.8), xytext=(25.5, 66.1), arrowprops={"arrowstyle": "-|>", "color": acol, "lw": 1.4})
        _box(ax, ax_x, 53.0, 19.5, 9.6, f"{arm['name']} (n = {arm['allocated']})", [f"Received regimen (n = {arm['received']})", f"Did not receive (n = {arm['allocated'] - arm['received']})"], edge=acol, title_col=acol, fs=7.4)
        ax.annotate("", xy=(ax_x + 9.5, 48.0), xytext=(ax_x + 9.5, 52.8), arrowprops={"arrowstyle": "-|>", "color": acol, "lw": 1.3})
        _box(ax, ax_x, 38.2, 19.5, 9.6, "Follow-Up", [f"Lost to follow-up (n = {arm['lost_to_followup']})", f"Discontinued tx (n = {arm['discontinued']})"], edge="#94A3B8", fs=7.4)
        ax.annotate("", xy=(ax_x + 9.5, 33.2), xytext=(ax_x + 9.5, 38.0), arrowprops={"arrowstyle": "-|>", "color": acol, "lw": 1.3})
        _box(ax, ax_x, 22.8, 19.5, 10.2, f"Analysed (n = {arm['analyzed']})", [f"Population: {arm.get('population', 'ITT')}", f"Excluded (n = {arm['allocated'] - arm['analyzed']})"], edge=acol, fill="#F8FAFC", title_col=acol, fs=7.4)

    # BOTTOM BAND (x: 2.5 -> 53.5, y: 5.5 -> 19.2): SPIRIT Treatment Timeline
    ax.text(2.5, 19.2, "B. SPIRIT TREATMENT & ASSESSMENT TIMELINE", color=pal["header"], fontsize=9.8, fontweight="bold", va="top")
    tl = spec.get("timeline", [])[:5]
    if tl:
        tw = 49.0 / len(tl)
        for i, tp in enumerate(tl):
            tx = 2.5 + i * tw
            ax.add_patch(mpatches.FancyBboxPatch((tx, 6.2), tw - 1.2, 9.8, boxstyle="round,pad=0.1,rounding_size=0.6", facecolor="#F8FAFC", edgecolor=pal["border"], lw=0.9))
            ax.add_patch(mpatches.Rectangle((tx, 14.2), tw - 1.2, 1.8, facecolor=pal["arm_active"] if i in (1, 3) else pal["header"], edgecolor="none"))
            ax.text(tx + (tw - 1.2) / 2, 12.2, tp["timepoint"], fontsize=7.6, fontweight="bold", color=pal["header"], ha="center", va="top")
            ax.text(tx + (tw - 1.2) / 2, 9.4, tp["event"], fontsize=7.0, color="#334155", ha="center", va="top")

    # TOP-RIGHT (x: 56.5 -> 97.5, y: 54.5 -> 88): Primary & Secondary Outcomes Table/Cards
    ax.text(56.5, 87.5, "C. PRIMARY & KEY SECONDARY ENDPOINTS", color=pal["header"], fontsize=10.2, fontweight="bold", va="top")
    outs = spec.get("outcomes", [])[:4]
    for i, out in enumerate(outs):
        oy = 77.2 - i * 7.4
        is_prim = (i == 0)
        ax.add_patch(mpatches.FancyBboxPatch((56.5, oy), 41.0, 6.4, boxstyle="round,pad=0.12,rounding_size=0.6", facecolor="#FFFBEB" if is_prim else "#F8FAFC", edgecolor=pal["accent"] if is_prim else pal["border"], lw=1.3 if is_prim else 0.9))
        tag = "PRIMARY" if is_prim else "SECONDARY"
        ax.text(58.0, oy + 4.6, f"[{tag}] {out['endpoint']}", fontsize=8.0, fontweight="bold", color=pal["header"], va="center")
        ax.text(96.2, oy + 4.6, out["estimate"], fontsize=8.0, fontweight="bold", color=pal["accent"] if is_prim else pal["arm_active"], ha="right", va="center")
        ax.text(58.0, oy + 1.8, f"Active: {out['active_rate']}   vs   Control: {out['control_rate']}   ({out['p_value']})", fontsize=7.3, color="#334155", va="center")

    # BOTTOM-RIGHT (x: 56.5 -> 97.5, y: 6.2 -> 50.5): Adverse-Event Butterfly Chart
    ax.text(56.5, 51.0, "D. ADVERSE EVENTS (ALL-GRADE & GRADE >= 3, %)", color=pal["header"], fontsize=10.2, fontweight="bold", va="top")
    aes = spec.get("adverse_events", [])[:5]
    if aes:
        ae_ax = fig.add_axes([0.65, 0.085, 0.31, 0.37])
        ae_ax.patch.set_alpha(0.0)
        terms = [a["term"] for a in aes]
        act_all = [-float(a["active_all"]) for a in aes]
        act_g3 = [-float(a["active_g3"]) for a in aes]
        ctl_all = [float(a["control_all"]) for a in aes]
        ctl_g3 = [float(a["control_g3"]) for a in aes]
        ypos = np.arange(len(terms))

        ae_ax.barh(ypos, act_all, height=0.58, color="#93C5FD", label="Active All-Grade")
        ae_ax.barh(ypos, act_g3, height=0.58, color=pal["arm_active"], label="Active Gr >=3")
        ae_ax.barh(ypos, ctl_all, height=0.58, color="#CBD5E1", label="Control All-Grade")
        ae_ax.barh(ypos, ctl_g3, height=0.58, color=pal["arm_control"], label="Control Gr >=3")
        ae_ax.axvline(0, color="#0F172A", lw=0.9)
        max_v = max(max(abs(x) for x in act_all), max(ctl_all)) * 1.25
        ae_ax.set_xlim(-max_v, max_v)
        step = 5 if max_v <= 25 else (10 if max_v <= 50 else 20)
        hi_t = int(max_v // step) * step
        ticks = list(range(-hi_t, hi_t + 1, step))
        ae_ax.set_xticks(ticks)
        ae_ax.set_xticklabels([f"{abs(t)}%" for t in ticks], fontsize=7.2)
        ae_ax.set_yticks(ypos)
        ae_ax.set_yticklabels(terms, fontsize=7.6, fontweight="bold")
        ae_ax.invert_yaxis()
        ae_ax.spines["top"].set_visible(False)
        ae_ax.spines["right"].set_visible(False)
        ae_ax.legend(loc="lower right", frameon=True, facecolor="#FFFFFF", edgecolor="#E2E8F0", fontsize=6.6, ncol=2)
        ae_ax.set_title("← Active Regimen        |        Control Regimen →", fontsize=7.6, fontweight="bold", color=pal["muted"], pad=6)

    ax.text(2.5, 2.2, spec.get("footer_note", "SYNTHETIC CLINICAL TRIAL DATA FOR SKILL VALIDATION ONLY"), fontsize=7.3, color=pal["muted"], va="center")

    out_dir.mkdir(parents=True, exist_ok=True)
    svg_p = out_dir / "clinical_trial_visual.svg"
    pdf_p = out_dir / "clinical_trial_visual.pdf"
    png_p = out_dir / "clinical_trial_visual.png"
    fig.savefig(svg_p, format="svg", facecolor="#FFFFFF")
    fig.savefig(pdf_p, format="pdf", facecolor="#FFFFFF")
    fig.savefig(png_p, format="png", dpi=dpi, facecolor="#FFFFFF")
    plt.close(fig)

    # Native editable PPTX summary
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    hb = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(W), Inches(H * 0.10))
    hb.fill.solid()
    hb.fill.fore_color.rgb = _rgb(pal["header"])
    hb.line.fill.background()
    r = hb.text_frame.paragraphs[0].add_run()
    r.text = spec["title"]
    r.font.bold = True
    r.font.size = Pt(16)
    r.font.color.rgb = _rgb("#FFFFFF")
    sl.shapes.add_picture(str(png_p), Inches(0.2), Inches(H * 0.11), width=Inches(W - 0.4))
    pptx_p = out_dir / "clinical_trial_visual.pptx"
    prs.save(str(pptx_p))

    return {"width_in": W, "height_in": H, "dpi": dpi, "files": {"svg": str(svg_p), "pdf": str(pdf_p), "png": str(png_p), "pptx": str(pptx_p)}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    spec = json.loads(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    print(json.dumps(render_clinical_trial(spec, pathlib.Path(args.output_dir)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
