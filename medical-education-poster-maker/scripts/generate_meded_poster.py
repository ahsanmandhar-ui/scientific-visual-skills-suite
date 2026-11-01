#!/usr/bin/env python3
"""
Medical Education Teaching Poster Generator (Anatomy/Physiology, Diagnostic Algorithm,
Pharmacology/Pathology Matrix, and OSCE/OSPE Station Checklist).
Exports SVG, vector PDF (Type 42), PNG, and editable PPTX.
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


def render_meded_poster(spec: Dict[str, Any], out_dir: pathlib.Path) -> Dict[str, Any]:
    db = json.loads((SKILL_ROOT / "templates" / "meded_presets.json").read_text(encoding="utf-8"))
    sz = db["sizes"].get(spec.get("size", "iso-a2-portrait"), db["sizes"]["iso-a2-portrait"])
    pal = db["palettes"].get(spec.get("palette", "sage_pharmacology"), db["palettes"]["sage_pharmacology"])
    W, H, dpi = float(sz["width_in"]), float(sz["height_in"]), int(sz["dpi"])
    sc = W / 16.54
    bpt = 13.0 * sc

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

    # Teaching Banner (y: 89 -> 100)
    ax.add_patch(mpatches.Rectangle((0, 89.2), 100, 10.8, facecolor=pal["dominant"], edgecolor="none"))
    ax.add_patch(mpatches.Rectangle((0, 88.4), 100, 0.8, facecolor=pal["accent"], edgecolor="none"))
    ax.text(3.5, 97.6, spec.get("curriculum_level", "MEDICAL EDUCATION & OSCE CLINICAL TEACHING GUIDE").upper(), color="#D8E8DF", fontsize=bpt * 0.78, fontweight="bold", va="top")
    ax.text(3.5, 93.8, spec["title"], color="#FFFFFF", fontsize=bpt * 1.48, fontweight="bold", va="center")
    ax.text(3.5, 90.2, spec.get("learning_objective", ""), color="#E6F0EA", fontsize=bpt * 0.82, va="center")

    # Module A (Top-Left, x: 3.5->48.5, y: 58->86.5): Physiology & Pathophysiology Integration
    ax.add_patch(mpatches.FancyBboxPatch((3.5, 58.0), 45.0, 28.2, boxstyle="round,pad=0.2,rounding_size=0.9", facecolor="#FFFFFF", edgecolor=pal["border"], lw=1.4))
    ax.add_patch(mpatches.Rectangle((3.5, 82.8), 45.0, 3.4, facecolor=pal["secondary"], edgecolor="none"))
    ax.text(5.2, 84.5, "1. ANATOMY, PHYSIOLOGY & MECHANISM INTEGRATION", color="#FFFFFF", fontsize=bpt * 0.86, fontweight="bold", va="center")
    for idx, item in enumerate(spec.get("physiology_points", [])[:4]):
        py = 79.8 - idx * 5.4
        ax.add_patch(mpatches.Circle((6.2, py - 0.8), 1.05, facecolor=pal["dominant"], edgecolor="none"))
        ax.text(6.2, py - 0.8, str(idx + 1), color="#FFFFFF", fontsize=bpt * 0.70, fontweight="bold", ha="center", va="center")
        ax.text(8.4, py, f"{item['concept']}: ", color=pal["dominant"], fontsize=bpt * 0.80, fontweight="bold", va="top")
        ax.text(8.4, py - 2.1, "\n".join(textwrap.wrap(item["explanation"], width=52)), color=pal["ink"], fontsize=bpt * 0.72, va="top", linespacing=1.14)

    # Module B (Top-Right, x: 51.5->96.5, y: 58->86.5): Branching Diagnostic Algorithm
    ax.add_patch(mpatches.FancyBboxPatch((51.5, 58.0), 45.0, 28.2, boxstyle="round,pad=0.2,rounding_size=0.9", facecolor="#FFFFFF", edgecolor=pal["border"], lw=1.4))
    ax.add_patch(mpatches.Rectangle((51.5, 82.8), 45.0, 3.4, facecolor=pal["dominant"], edgecolor="none"))
    ax.text(53.2, 84.5, "2. STEPWISE DIAGNOSTIC DECISION ALGORITHM", color="#FFFFFF", fontsize=bpt * 0.86, fontweight="bold", va="center")

    alg = spec.get("diagnostic_algorithm", {})
    # Entry node
    ax.add_patch(mpatches.FancyBboxPatch((60.0, 76.2), 28.0, 4.8, boxstyle="round,pad=0.12,rounding_size=0.7", facecolor=pal["tint"], edgecolor=pal["dominant"], lw=1.3))
    ax.text(74.0, 78.6, alg.get("entry", "Clinical Presentation"), color=pal["dominant"], fontsize=bpt * 0.78, fontweight="bold", ha="center", va="center")
    # Triage node
    ax.annotate("", xy=(74.0, 73.6), xytext=(74.0, 76.0), arrowprops={"arrowstyle": "-|>", "color": pal["dominant"], "lw": 1.6})
    ax.add_patch(mpatches.FancyBboxPatch((58.0, 68.8), 32.0, 4.6, boxstyle="round,pad=0.12,rounding_size=0.7", facecolor="#FFFBEB", edgecolor=pal["accent"], lw=1.3))
    ax.text(74.0, 71.1, alg.get("pivot_test", "First-Line Diagnostic Test"), color=pal["ink"], fontsize=bpt * 0.76, fontweight="bold", ha="center", va="center")

    branches = alg.get("branches", [])[:2]
    for bi, br in enumerate(branches):
        bx = 53.5 + bi * 21.5
        ax.annotate("", xy=(bx + 9.5, 65.8), xytext=(74.0, 68.7), arrowprops={"arrowstyle": "-|>", "color": pal["accent"] if bi == 0 else pal["secondary"], "lw": 1.5})
        ax.add_patch(mpatches.FancyBboxPatch((bx, 59.4), 19.5, 6.2, boxstyle="round,pad=0.12,rounding_size=0.7", facecolor=pal["tint"], edgecolor=pal["accent"] if bi == 0 else pal["secondary"], lw=1.2))
        ax.text(bx + 9.75, 64.2, br["condition"], color=pal["accent"] if bi == 0 else pal["secondary"], fontsize=bpt * 0.74, fontweight="bold", ha="center", va="top")
        ax.text(bx + 9.75, 61.8, "\n".join(textwrap.wrap(br["action"], width=24)), color=pal["ink"], fontsize=bpt * 0.68, ha="center", va="top", linespacing=1.12)

    # Module C (Middle Full-Width, x: 3.5->96.5, y: 30.5->55.8): Pharmacology / Pathology Classification Matrix
    ax.add_patch(mpatches.FancyBboxPatch((3.5, 30.5), 93.0, 25.2, boxstyle="round,pad=0.2,rounding_size=0.9", facecolor="#FFFFFF", edgecolor=pal["border"], lw=1.4))
    ax.add_patch(mpatches.Rectangle((3.5, 52.3), 93.0, 3.4, facecolor=pal["dominant"], edgecolor="none"))
    mtx = spec.get("matrix", {})
    ax.text(5.2, 54.0, mtx.get("title", "3. HIGH-YIELD PHARMACOLOGY & PATHOLOGY CLASSIFICATION MATRIX").upper(), color="#FFFFFF", fontsize=bpt * 0.86, fontweight="bold", va="center")
    headers = mtx.get("headers", ["Class / Subtype", "Mechanism / Hallmark", "Primary Indication", "Key Adverse Effect / Pitfall"])
    rows: List[List[str]] = mtx.get("rows", [])[:5]
    col_xs = [4.8, 25.0, 52.0, 74.0]
    col_ws = [19.0, 26.0, 21.0, 21.0]
    ax.add_patch(mpatches.Rectangle((4.2, 48.6), 91.6, 3.2, facecolor=pal["tint"], edgecolor="none"))
    for ci, h_txt in enumerate(headers):
        ax.text(col_xs[ci], 50.2, h_txt, color=pal["dominant"], fontsize=bpt * 0.76, fontweight="bold", va="center")
    rh = 17.2 / max(1, len(rows))
    for ri, row in enumerate(rows):
        ry = 48.4 - (ri + 1) * rh
        if ri % 2 == 1:
            ax.add_patch(mpatches.Rectangle((4.2, ry), 91.6, rh, facecolor="#F8FAF9", edgecolor="none"))
        ax.plot([4.2, 95.8], [ry, ry], color=pal["border"], lw=0.7)
        for ci, cell in enumerate(row[:4]):
            w_ch = int(col_ws[ci] * 1.35)
            ax.text(col_xs[ci], ry + rh - 0.6, "\n".join(textwrap.wrap(str(cell), width=w_ch)), color=pal["ink"], fontsize=bpt * 0.70, fontweight="bold" if ci == 0 else "normal", va="top", linespacing=1.12)

    # Module D (Bottom, x: 3.5->96.5, y: 5.5->28.4): OSCE / OSPE Clinical Examination & Red Flags
    ax.add_patch(mpatches.FancyBboxPatch((3.5, 5.5), 57.5, 22.8, boxstyle="round,pad=0.2,rounding_size=0.9", facecolor="#FFFFFF", edgecolor=pal["secondary"], lw=1.4))
    ax.add_patch(mpatches.Rectangle((3.5, 24.9), 57.5, 3.4, facecolor=pal["secondary"], edgecolor="none"))
    ax.text(5.2, 26.6, "4. OSCE / OSPE STRUCTURED CLINICAL STATION CHECKLIST", color="#FFFFFF", fontsize=bpt * 0.84, fontweight="bold", va="center")
    for oi, stp in enumerate(spec.get("osce_checklist", [])[:5]):
        oy = 23.2 - oi * 3.5
        ax.text(5.4, oy, f"Step {oi + 1} — {stp}", color=pal["ink"], fontsize=bpt * 0.73, va="top")

    ax.add_patch(mpatches.FancyBboxPatch((63.0, 5.5), 33.5, 22.8, boxstyle="round,pad=0.2,rounding_size=0.9", facecolor="#FFF5F5", edgecolor=pal["accent"], lw=1.5))
    ax.add_patch(mpatches.Rectangle((63.0, 24.9), 33.5, 3.4, facecolor=pal["accent"], edgecolor="none"))
    ax.text(64.6, 26.6, "CRITICAL SAFETY RED FLAGS", color="#FFFFFF", fontsize=bpt * 0.84, fontweight="bold", va="center")
    for fi, flg in enumerate(spec.get("red_flags", [])[:4]):
        fy = 23.2 - fi * 4.4
        ax.text(64.6, fy, "\n".join(textwrap.wrap(f"• {flg}", width=38)), color="#7F1D1D", fontsize=bpt * 0.72, fontweight="bold", va="top", linespacing=1.14)

    ax.text(3.5, 2.6, spec.get("footer_note", "SYNTHETIC MEDICAL EDUCATION TEACHING POSTER"), color=pal["muted"], fontsize=bpt * 0.68, va="center")

    out_dir.mkdir(parents=True, exist_ok=True)
    svg_p, pdf_p, png_p = out_dir / "meded_poster.svg", out_dir / "meded_poster.pdf", out_dir / "meded_poster.png"
    fig.savefig(svg_p, format="svg", facecolor=fig.get_facecolor())
    fig.savefig(pdf_p, format="pdf", facecolor=fig.get_facecolor())
    fig.savefig(png_p, format="png", dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)

    # Editable PPTX export
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    sl.shapes.add_picture(str(png_p), Inches(0), Inches(0), width=Inches(W))
    pptx_p = out_dir / "meded_poster.pptx"
    prs.save(str(pptx_p))
    return {"width_in": W, "height_in": H, "dpi": dpi, "files": {"svg": str(svg_p), "pdf": str(pdf_p), "png": str(png_p), "pptx": str(pptx_p)}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    spec = json.loads(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    print(json.dumps(render_meded_poster(spec, pathlib.Path(args.output_dir)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
