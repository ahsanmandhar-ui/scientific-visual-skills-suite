#!/usr/bin/env python3
"""
Vector Scientific Illustration & Mechanism Diagram Generator.
Supports: cellular_signaling, molecular_pathway, organ_pathophysiology, medical_device.
Exports editable SVG, vector PDF (Type 42), and 300/600-DPI PNG.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import textwrap
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
import numpy as np

SKILL_ROOT = pathlib.Path(__file__).resolve().parents[1]
SHARED_FONTS = SKILL_ROOT.parent / "research-poster-maker" / "assets" / "fonts"
if SHARED_FONTS.exists():
    for _ttf in SHARED_FONTS.glob("*.ttf"):
        try:
            font_manager.fontManager.addfont(str(_ttf))
        except Exception:
            pass


def _draw_bilayer(ax: plt.Axes, y_center: float, x0: float, x1: float, head_col: str, tail_col: str, skip_ranges: List[Tuple[float, float]]) -> None:
    """Draw authentic double-leaflet phospholipid bilayer with receptor transmembrane gaps."""
    xs = np.arange(x0, x1, 1.35)
    for x in xs:
        if any(a <= x <= b for a, b in skip_ranges):
            continue
        # Upper and lower leaflets
        ax.plot([x - 0.18, x - 0.18], [y_center + 0.25, y_center + 1.45], color=tail_col, lw=0.9, zorder=2)
        ax.plot([x + 0.18, x + 0.18], [y_center + 0.25, y_center + 1.45], color=tail_col, lw=0.9, zorder=2)
        ax.plot([x - 0.18, x - 0.18], [y_center - 1.45, y_center - 0.25], color=tail_col, lw=0.9, zorder=2)
        ax.plot([x + 0.18, x + 0.18], [y_center - 1.45, y_center - 0.25], color=tail_col, lw=0.9, zorder=2)
        ax.add_patch(mpatches.Circle((x, y_center + 1.75), 0.45, facecolor=head_col, edgecolor="#FFFFFF", lw=0.35, zorder=3))
        ax.add_patch(mpatches.Circle((x, y_center - 1.75), 0.45, facecolor=head_col, edgecolor="#FFFFFF", lw=0.35, zorder=3))


def _rect_offset(ux: float, uy: float, w: float, h: float, pad: float = 0.9) -> float:
    tx = (w / 2.0 + pad) / max(1e-4, abs(ux)) if abs(ux) > 1e-4 else 1e6
    ty = (h / 2.0 + pad) / max(1e-4, abs(uy)) if abs(uy) > 1e-4 else 1e6
    return min(tx, ty)


def _draw_edge(ax: plt.Axes, n1: Dict[str, Any], n2: Dict[str, Any], kind: str, label: str = "") -> None:
    """Draw SBGN-style activation arrow, flat T-bar inhibition, or dashed regulation."""
    x1, y1 = float(n1["x"]), float(n1["y"])
    x2, y2 = float(n2["x"]), float(n2["y"])
    w1, h1 = float(n1.get("w", 14.5)), float(n1.get("h", 6.8))
    w2, h2 = float(n2.get("w", 14.5)), float(n2.get("h", 6.8))
    dx, dy = x2 - x1, y2 - y1
    dist = max(1e-3, math.hypot(dx, dy))
    ux, uy = dx / dist, dy / dist
    d1 = _rect_offset(ux, uy, w1, h1, 0.7)
    d2 = _rect_offset(ux, uy, w2, h2, 1.0)
    sx, sy = x1 + ux * d1, y1 + uy * d1
    ex, ey = x2 - ux * d2, y2 - uy * d2

    if kind == "inhibit":
        col = "#B8332A"
        ax.plot([sx, ex], [sy, ey], color=col, lw=2.0, zorder=5)
        # Perpendicular flat T-bar at target end
        px, py = -uy * 1.6, ux * 1.6
        ax.plot([ex - px, ex + px], [ey - py, ey + py], color=col, lw=2.6, zorder=6)
    elif kind == "transcribe":
        col = "#4A3578"
        ax.annotate("", xy=(ex, ey), xytext=(sx, sy), arrowprops={"arrowstyle": "-|>", "color": col, "lw": 1.7, "ls": "--", "mutation_scale": 14}, zorder=5)
    else:
        col = "#1E3A5F"
        ax.annotate("", xy=(ex, ey), xytext=(sx, sy), arrowprops={"arrowstyle": "-|>", "color": col, "lw": 1.9, "mutation_scale": 15}, zorder=5)

    if label:
        mx, my = (sx + ex) / 2.0, (sy + ey) / 2.0
        ax.text(mx, my + 1.8, label, fontsize=8.0, fontweight="bold", color=col, ha="center", va="bottom", bbox={"boxstyle": "round,pad=0.18", "facecolor": "#FFFFFF", "edgecolor": "none", "alpha": 0.88}, zorder=7)


def render_illustration(spec: Dict[str, Any], out_dir: pathlib.Path) -> Dict[str, Any]:
    pal = json.loads((SKILL_ROOT / "templates" / "illustration_palettes.json").read_text(encoding="utf-8"))["palettes"]["cell_editorial"]
    mode = spec.get("mode", "cellular_signaling")
    W = float(spec.get("width_in", 11.0))
    H = float(spec.get("height_in", 7.5))
    dpi = int(spec.get("dpi", 400))

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Source Sans 3", "IBM Plex Sans", "DejaVu Sans"],
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",  # Editable SVG text elements for Illustrator/Inkscape
    })

    fig = plt.figure(figsize=(W, H), facecolor="#FFFFFF")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Title bar
    ax.text(3.5, 96.2, spec["title"], fontsize=13.5, fontweight="bold", color=pal["ink"], va="top")
    if spec.get("subtitle"):
        ax.text(3.5, 92.2, spec["subtitle"], fontsize=9.2, color=pal["muted"], va="top")

    if mode in ("cellular_signaling", "molecular_pathway"):
        if mode == "cellular_signaling":
            # Extracellular compartment
            ax.add_patch(mpatches.Rectangle((3.0, 72.5), 94.0, 16.5, facecolor=pal["extracellular"], edgecolor="none", zorder=0))
            ax.text(4.5, 87.2, "EXTRACELLULAR MICROENVIRONMENT", fontsize=8.2, fontweight="bold", color=pal["muted"], va="top")
            # Cytoplasm
            ax.add_patch(mpatches.Rectangle((3.0, 29.0), 94.0, 41.0, facecolor=pal["cytoplasm"], edgecolor="none", zorder=0))
            ax.text(4.5, 64.2, "CYTOPLASM / INTRACELLULAR SIGNALING", fontsize=8.2, fontweight="bold", color=pal["muted"], va="top")
            # Nucleus with dashed nuclear pore envelope
            nuc = mpatches.FancyBboxPatch((12.0, 9.5), 76.0, 17.5, boxstyle="round,pad=0.3,rounding_size=4.0", facecolor=pal["nucleus"], edgecolor=pal["tf"], linewidth=1.6, linestyle="--", zorder=1)
            ax.add_patch(nuc)
            ax.text(14.5, 25.0, "NUCLEUS & TRANSCRIPTIONAL LOCUS", fontsize=8.2, fontweight="bold", color=pal["tf"], va="top")
            # Stylized DNA double-strand wave at y=13.5
            xs_dna = np.linspace(38.0, 82.0, 120)
            ax.plot(xs_dna, 13.5 + 1.1 * np.sin((xs_dna - 38.0) * 0.48), color=pal["tf"], lw=1.5, zorder=2)
            ax.plot(xs_dna, 13.5 - 1.1 * np.sin((xs_dna - 38.0) * 0.48), color="#8A70B8", lw=1.5, zorder=2)

            # Determine receptor gaps along plasma membrane y=71.2
            rec_xs = [(float(n["x"]) - 4.8, float(n["x"]) + 4.8) for n in spec.get("nodes", []) if n.get("role") == "receptor"]
            _draw_bilayer(ax, 71.2, 4.0, 96.0, pal["membrane_head"], pal["membrane_tail"], rec_xs)
            ax.text(95.5, 74.2, "Phospholipid Bilayer", fontsize=7.6, color=pal["membrane_head"], fontweight="bold", ha="right")

        nodes = {n["id"]: n for n in spec.get("nodes", [])}
        role_colors = {"ligand": "#0F766E", "receptor": pal["receptor"], "kinase": pal["kinase"], "drug": pal["inhibitor"], "tf": pal["tf"]}
        for nid, n in nodes.items():
            nx, ny = float(n["x"]), float(n["y"])
            role = n.get("role", "kinase")
            col = n.get("color", role_colors.get(role, pal["kinase"]))
            w_n = float(n.get("w", 14.5))
            h_n = float(n.get("h", 6.8 if role != "receptor" else 9.5))
            patch = mpatches.FancyBboxPatch((nx - w_n / 2, ny - h_n / 2), w_n, h_n, boxstyle="round,pad=0.2,rounding_size=1.8", facecolor=col, edgecolor="#FFFFFF", linewidth=1.4, zorder=4)
            ax.add_patch(patch)
            ax.text(nx, ny, n["label"], color="#FFFFFF", fontsize=8.8, fontweight="bold", ha="center", va="center", zorder=6)
            if n.get("phospho"):
                ax.add_patch(mpatches.Circle((nx + w_n / 2 - 0.4, ny + h_n / 2 - 0.4), 1.65, facecolor="#F59E0B", edgecolor="#FFFFFF", lw=1.0, zorder=7))
                ax.text(nx + w_n / 2 - 0.4, ny + h_n / 2 - 0.4, "P", color="#111827", fontsize=7.2, fontweight="bold", ha="center", va="center", zorder=8)

        for e in spec.get("edges", []):
            n1, n2 = nodes[e["from"]], nodes[e["to"]]
            _draw_edge(ax, n1, n2, e.get("type", "activate"), e.get("label", ""))

    elif mode == "medical_device":
        # Layered cross-section schematic + numbered callout pins
        layers = spec.get("layers", [])
        n_l = max(1, len(layers))
        lh = min(10.0, 52.0 / n_l)
        top_l = 78.0
        for idx, lyr in enumerate(layers):
            ly = top_l - (idx + 1) * (lh + 1.4)
            col = lyr.get("color", ["#1E3A5F", "#0F766E", "#C26D2D", "#5B3E8C", "#475569"][idx % 5])
            ax.add_patch(mpatches.FancyBboxPatch((8.0, ly), 44.0, lh, boxstyle="round,pad=0.1,rounding_size=0.8", facecolor=col, edgecolor="#FFFFFF", lw=1.2))
            ax.text(30.0, ly + lh / 2, lyr["name"], color="#FFFFFF", fontsize=9.2, fontweight="bold", ha="center", va="center")
            # Callout pin + leader line to right-hand engineering table
            pin_x, pin_y = 58.0, ly + lh / 2
            ax.plot([52.2, pin_x - 1.6], [pin_y, pin_y], color=col, lw=1.4)
            ax.add_patch(mpatches.Circle((pin_x, pin_y), 1.6, facecolor=col, edgecolor="none"))
            ax.text(pin_x, pin_y, str(idx + 1), color="#FFFFFF", fontsize=8.2, fontweight="bold", ha="center", va="center")
            ax.text(61.0, pin_y, f"{lyr['name']}: {lyr['function']}", color=pal["ink"], fontsize=8.4, va="center")

    else:  # organ_pathophysiology
        for idx, side_key in enumerate(["homeostasis", "pathophysiology"]):
            panel = spec.get(side_key, {})
            px = 4.0 + idx * 47.0
            col = "#0F766E" if idx == 0 else "#B8332A"
            ax.add_patch(mpatches.FancyBboxPatch((px, 12.0), 45.0, 74.0, boxstyle="round,pad=0.2,rounding_size=1.4", facecolor="#FAFBFD", edgecolor=col, lw=1.6))
            ax.add_patch(mpatches.Rectangle((px, 79.0), 45.0, 7.0, facecolor=col, edgecolor="none"))
            ax.text(px + 22.5, 82.5, panel.get("heading", side_key.upper()), color="#FFFFFF", fontsize=10.0, fontweight="bold", ha="center", va="center")
            for bi, item in enumerate(panel.get("features", [])):
                by = 70.0 - bi * 14.5
                ax.add_patch(mpatches.FancyBboxPatch((px + 3.0, by - 4.5), 39.0, 10.5, boxstyle="round,pad=0.15,rounding_size=0.9", facecolor="#FFFFFF", edgecolor="#CBD5E1", lw=1.0))
                ax.text(px + 5.0, by + 3.5, item["structure"], color=col, fontsize=9.0, fontweight="bold", va="top")
                ax.text(px + 5.0, by + 0.2, "\n".join(textwrap.wrap(item["state"], width=42)), color=pal["ink"], fontsize=8.2, va="top")

    # Legend bar at bottom
    ax.plot([3.5, 96.5], [6.8, 6.8], color="#CBD5E1", lw=0.9)
    legend_text = spec.get("legend_footer", "KEY: Solid arrow (→) = direct activation/translocation   |   Flat T-bar [-|] = inhibition/blockade   |   Dashed arrow = transcriptional upregulation   |   (P) = phosphorylation")
    ax.text(3.5, 3.6, legend_text, fontsize=7.8, color=pal["muted"], va="center")

    out_dir.mkdir(parents=True, exist_ok=True)
    svg_p, pdf_p, png_p = out_dir / "illustration.svg", out_dir / "illustration.pdf", out_dir / "illustration.png"
    fig.savefig(svg_p, format="svg", facecolor="#FFFFFF")
    fig.savefig(pdf_p, format="pdf", facecolor="#FFFFFF")
    fig.savefig(png_p, format="png", dpi=dpi, facecolor="#FFFFFF")
    plt.close(fig)
    return {"mode": mode, "width_in": W, "height_in": H, "dpi": dpi, "files": {"svg": str(svg_p), "pdf": str(pdf_p), "png": str(png_p)}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    spec = json.loads(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    print(json.dumps(render_illustration(spec, pathlib.Path(args.output_dir)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
