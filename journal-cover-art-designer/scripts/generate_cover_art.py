#!/usr/bin/env python3
"""
Journal Cover Art Generator (Unlettered Full-Bleed Artwork + Masthead Editorial Mockup + Cover Caption).
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import textwrap
from typing import Any, Dict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
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


def _draw_cover_artwork(ax: plt.Axes, style: str, pal: Dict[str, str], focal_y0: float, focal_y1: float, seed: int = 42) -> None:
    """Render full-bleed background + focal scientific geometric artwork strictly centered in [focal_y0, focal_y1]."""
    rng = np.random.default_rng(seed)
    grad = np.linspace(0, 1, 512)[:, None] * np.ones((1, 256))
    cmap_bg = LinearSegmentedColormap.from_list("cover_bg", [pal["bg_top"], pal["bg_bot"]])
    ax.imshow(grad, extent=[0, 100, 0, 100], origin="upper", cmap=cmap_bg, aspect="auto", zorder=0)

    # Subtle full-bleed phase contours (safe behind masthead because low-contrast)
    xg = np.linspace(0, 100, 220)
    for k in range(14):
        yk = 8.0 + k * 6.6 + 2.8 * np.sin(xg * 0.085 + k * 0.55)
        ax.plot(xg, yk, color=pal["field"], alpha=0.22, lw=0.85, zorder=1)

    yc_mid = 0.5 * (focal_y0 + focal_y1)
    y_span = (focal_y1 - focal_y0) * 0.86

    if style == "molecular_lattice":
        # 3D-projected icosahedral / coordination molecular cage + orbital rings inside focal window
        for r_orb, ang in [(25.0, 18), (31.0, -24), (19.0, 52)]:
            ell = mpatches.Ellipse((50.0, yc_mid), r_orb * 2.1, r_orb * 0.85, angle=ang, facecolor="none", edgecolor=pal["strand_a"], alpha=0.35, lw=1.3, zorder=2)
            ax.add_patch(ell)
        n_pts = 26
        phis = np.linspace(0, np.pi * (3 - np.sqrt(5)) * n_pts, n_pts)
        zs = np.linspace(-0.92, 0.92, n_pts)
        rs = np.sqrt(np.maximum(0.0, 1.0 - zs ** 2))
        pts = [(50.0 + 22.0 * r * math.cos(p), yc_mid + (y_span * 0.42) * z, z) for r, p, z in zip(rs, phis, zs)]
        pts.sort(key=lambda t: t[2])
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                if math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]) < 16.5:
                    ax.plot([pts[i][0], pts[j][0]], [pts[i][1], pts[j][1]], color=pal["strand_a"], alpha=0.42, lw=1.2, zorder=3)
        for px, py, pz in pts:
            rad = 1.15 + 0.65 * (pz + 1.0)
            col = pal["strand_b"] if pz > 0.25 else pal["strand_a"]
            ax.add_patch(mpatches.Circle((px, py), rad * 1.65, facecolor=col, alpha=0.18, zorder=4))
            ax.add_patch(mpatches.Circle((px, py), rad, facecolor=col, edgecolor=pal["node_hi"], lw=0.7, zorder=5))

    elif style == "neural_connectome":
        # Bundled neural/vascular Bézier-like harmonic filaments converging through focal hub
        t = np.linspace(0, 1, 160)
        for k in range(28):
            y_start = focal_y0 + (k / 27.0) * y_span
            y_end = focal_y0 + ((27 - k) / 27.0) * y_span
            xs = 12.0 + 76.0 * t
            ys = (1 - t) ** 2 * y_start + 2 * (1 - t) * t * (yc_mid + rng.uniform(-6, 6)) + t ** 2 * y_end
            col = pal["strand_a"] if k % 3 != 0 else pal["strand_b"]
            ax.plot(xs, ys, color=col, alpha=0.38, lw=1.35, zorder=3)
        for _ in range(22):
            nx = rng.uniform(22.0, 78.0)
            ny = rng.uniform(focal_y0 + 4.0, focal_y1 - 4.0)
            ax.add_patch(mpatches.Circle((nx, ny), 1.9, facecolor=pal["strand_b"], alpha=0.22, zorder=4))
            ax.add_patch(mpatches.Circle((nx, ny), 0.95, facecolor=pal["node_hi"], zorder=5))

    else:  # Default: helical_chromatin (3D-projected double helix + base-pair rungs + epigenetic glow nodes)
        t = np.linspace(0, 3.2 * np.pi, 260)
        ys = np.linspace(focal_y0 + 2.0, focal_y1 - 2.0, 260)
        amp = 19.5
        x1 = 50.0 + amp * np.sin(t)
        x2 = 50.0 + amp * np.sin(t + np.pi)
        z1 = np.cos(t)

        # Base-pair rungs sampled every 9 steps
        for idx in range(4, len(t) - 4, 9):
            c_rung = pal["strand_b"] if (idx // 9) % 3 == 0 else pal["strand_a"]
            ax.plot([x1[idx], x2[idx]], [ys[idx], ys[idx]], color=c_rung, alpha=0.58, lw=1.7, zorder=3)
            mx = 0.5 * (x1[idx] + x2[idx])
            if (idx // 9) % 3 == 0:
                ax.add_patch(mpatches.Circle((mx, ys[idx]), 1.85, facecolor=pal["strand_b"], alpha=0.28, zorder=4))
                ax.add_patch(mpatches.Circle((mx, ys[idx]), 0.95, facecolor=pal["node_hi"], zorder=5))

        # Depth-modulated helical ribbons
        for idx in range(len(t) - 1):
            lw1 = 2.6 + 1.6 * (z1[idx] + 1.0) * 0.5
            lw2 = 2.6 + 1.6 * (-z1[idx] + 1.0) * 0.5
            ax.plot(x1[idx : idx + 2], ys[idx : idx + 2], color=pal["strand_a"], lw=lw1, solid_capstyle="round", zorder=5 if z1[idx] >= 0 else 2)
            ax.plot(x2[idx : idx + 2], ys[idx : idx + 2], color=pal["strand_b"], lw=lw2, solid_capstyle="round", zorder=5 if z1[idx] < 0 else 2)


def generate_cover(spec: Dict[str, Any], out_dir: pathlib.Path) -> Dict[str, Any]:
    db = json.loads((SKILL_ROOT / "templates" / "journal_cover_specs.json").read_text(encoding="utf-8"))
    prof_id = spec.get("journal_profile", "cell-press")
    prof = db["profiles"].get(prof_id, db["profiles"]["cell-press"])
    pal = db["palettes"].get(spec.get("palette", "obsidian_gold_teal"), db["palettes"]["obsidian_gold_teal"])
    style = spec.get("motif_style", "helical_chromatin")

    trim_w, trim_h, bleed = float(prof["trim_w_mm"]), float(prof["trim_h_mm"]), float(prof["bleed_mm"])
    full_w_mm = trim_w + 2.0 * bleed
    full_h_mm = trim_h + 2.0 * bleed
    w_in, h_in = full_w_mm / 25.4, full_h_mm / 25.4
    dpi = int(spec.get("dpi", prof["dpi"]))

    # Compute normalized [0..100] safe focal window
    bot_pct = ((bleed + float(prof["bottom_safe_mm"])) / full_h_mm) * 100.0
    top_pct = 100.0 - ((bleed + float(prof["masthead_mm"])) / full_h_mm) * 100.0

    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Source Serif 4", "DejaVu Serif"],
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "path",
    })

    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. UNLETTERED FULL-BLEED PRODUCTION ARTWORK
    fig1 = plt.figure(figsize=(w_in, h_in))
    ax1 = fig1.add_axes([0, 0, 1, 1])
    ax1.set_xlim(0, 100); ax1.set_ylim(0, 100); ax1.axis("off")
    _draw_cover_artwork(ax1, style, pal, bot_pct + 2.0, top_pct - 2.0, seed=int(spec.get("seed", 42)))
    unlet_svg = out_dir / "cover_artwork_unlettered.svg"
    unlet_pdf = out_dir / "cover_artwork_unlettered.pdf"
    unlet_png = out_dir / "cover_artwork_unlettered.png"
    fig1.savefig(unlet_svg, format="svg")
    fig1.savefig(unlet_pdf, format="pdf")
    fig1.savefig(unlet_png, format="png", dpi=dpi)
    plt.close(fig1)

    # 2. EDITORIAL MASTHEAD & TRIM SAFE-ZONE MOCKUP PROOF
    fig2 = plt.figure(figsize=(w_in, h_in))
    ax2 = fig2.add_axes([0, 0, 1, 1])
    ax2.set_xlim(0, 100); ax2.set_ylim(0, 100); ax2.axis("off")
    _draw_cover_artwork(ax2, style, pal, bot_pct + 2.0, top_pct - 2.0, seed=int(spec.get("seed", 42)))

    bx_pct = (bleed / full_w_mm) * 100.0
    by_pct = (bleed / full_h_mm) * 100.0
    # Trim crop rectangle (subtle dashed editorial proof guide)
    ax2.add_patch(mpatches.Rectangle((bx_pct, by_pct), 100.0 - 2 * bx_pct, 100.0 - 2 * by_pct, facecolor="none", edgecolor="#FFFFFF", lw=0.6, ls="--", alpha=0.45, zorder=10))
    # Masthead placeholder typography
    j_title = spec.get("mockup_masthead_title", "JOURNAL COVER PROOF")
    ax2.text(50.0, 90.5, j_title, color="#FFFFFF", fontsize=34.0, fontweight="bold", ha="center", va="center", zorder=11)
    ax2.text(50.0, 82.8, spec.get("issue_line", "VOLUME · ISSUE · EDITORIAL SAFE-ZONE PROOF"), color="#CBD5E1", fontsize=8.5, family="sans-serif", fontweight="bold", ha="center", va="center", zorder=11)
    # Cover teaser headline & barcode safe box
    ax2.text(8.5, bot_pct - 1.5, "\n".join(textwrap.wrap(spec["cover_teaser"], width=34)), color="#FFFFFF", fontsize=12.0, family="sans-serif", fontweight="bold", va="top", linespacing=1.2, zorder=11)
    ax2.add_patch(mpatches.Rectangle((73.0, by_pct + 2.2), 19.0, 7.2, facecolor="#FFFFFF", alpha=0.88, zorder=11))
    ax2.text(82.5, by_pct + 5.8, "ISSN / BARCODE\nSAFE ZONE", color="#0F172A", fontsize=6.2, family="sans-serif", fontweight="bold", ha="center", va="center", zorder=12)

    mock_pdf = out_dir / "cover_editorial_mockup.pdf"
    mock_png = out_dir / "cover_editorial_mockup.png"
    fig2.savefig(mock_pdf, format="pdf")
    fig2.savefig(mock_png, format="png", dpi=dpi)
    plt.close(fig2)

    # 3. 'On the Cover' submission statement + honest color-space disclosure
    caption_md = "\n".join([
        "# On the Cover — Editorial Submission Package",
        "",
        f"**Target Profile:** `{prof_id}` (`{trim_w} × {trim_h} mm` trim + `{bleed} mm` bleed = `{full_w_mm:.2f} × {full_h_mm:.2f} mm` full-bleed)",
        "",
        "## Cover Caption ('On the Cover')",
        spec.get("on_the_cover_caption", "Algorithmic vector representation of the study's central mechanism."),
        "",
        "## Production & Color-Space Notes",
        "- Submit `cover_artwork_unlettered.pdf` or `cover_artwork_unlettered.png` (`300 DPI`, zero text overlays) to the journal production portal.",
        "- Retain `cover_editorial_mockup.png` for internal art-direction review verifying zero masthead/barcode collision.",
        "- **Color Profile Note:** Exported files use high-precision sRGB/RGB color space. If the print vendor requires ICC-profiled CMYK (`ISO Coated v2` / `SWOP`), perform profile conversion during prepress soft-proofing.",
        "",
    ])
    (out_dir / "cover_caption.md").write_text(caption_md, encoding="utf-8")

    return {
        "profile": prof_id,
        "full_bleed_mm": [round(full_w_mm, 2), round(full_h_mm, 2)],
        "dpi": dpi,
        "files": {
            "unlettered_pdf": str(unlet_pdf),
            "unlettered_svg": str(unlet_svg),
            "unlettered_png": str(unlet_png),
            "mockup_pdf": str(mock_pdf),
            "mockup_png": str(mock_png),
            "caption_md": str(out_dir / "cover_caption.md"),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    spec = json.loads(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    print(json.dumps(generate_cover(spec, pathlib.Path(args.output_dir)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
