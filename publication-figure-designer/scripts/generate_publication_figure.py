#!/usr/bin/env python3
"""
Multi-Panel & Single-Panel Publication Figure Generator.

Supports exact journal column widths (mm), Nature/Cell/NEJM panel labeling,
Forest plots, Funnel plots, Kaplan-Meier survival curves, ROC curves,
Replicate-overlaid Box/Strip plots, Zero-baseline CI Bar plots, and Scatter fits.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
from typing import Any, Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
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

LINE_STYLES = ["-", "--", "-.", ":"]
MARKERS = ["o", "s", "^", "D"]


def _despine(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _draw_panel(ax: plt.Axes, p: Dict[str, Any], colors: List[str], tick_pt: float) -> None:
    ptype = p["type"]
    d = p["data"]

    if ptype == "forest":
        studies = d["studies"]
        pooled = d.get("pooled")
        is_log = bool(d.get("log_scale", True))
        null_v = float(d.get("null_value", 1.0 if is_log else 0.0))
        tx = (lambda v: math.log(max(v, 1e-4))) if is_log else (lambda v: float(v))

        n = len(studies) + (1 if pooled else 0)
        ys = list(range(n, 0, -1))
        ax.axvline(tx(null_v), color="#64748B", linestyle="--", lw=0.8, zorder=1)

        labels = []
        for idx, st in enumerate(studies):
            y = ys[idx]
            lo, eff, hi = tx(st["ci_low"]), tx(st["effect"]), tx(st["ci_high"])
            ax.plot([lo, hi], [y, y], color="#1E293B", lw=1.0, zorder=3)
            ms = 3.5 + 3.5 * math.sqrt(float(st.get("weight", 15.0)) / 25.0)
            ax.plot(eff, y, marker="s", markersize=ms, color=colors[0], zorder=4)
            labels.append(f"{st['study']} ({st['effect']:.2f} [{st['ci_low']:.2f}–{st['ci_high']:.2f}])")

        if pooled:
            yp = ys[-1]
            lo, eff, hi = tx(pooled["ci_low"]), tx(pooled["effect"]), tx(pooled["ci_high"])
            ax.fill([lo, eff, hi, eff], [yp, yp + 0.28, yp, yp - 0.28], color=colors[1], zorder=5)
            labels.append(f"{pooled.get('label', 'Pooled')} ({pooled['effect']:.2f} [{pooled['ci_low']:.2f}–{pooled['ci_high']:.2f}])")

        ax.set_yticks(ys)
        ax.set_yticklabels(labels, fontsize=tick_pt * 0.94)
        if is_log:
            ticks = d.get("ticks", [0.5, 0.75, 1.0, 1.5, 2.0])
            ax.set_xticks([tx(t) for t in ticks])
            ax.set_xticklabels([f"{t:g}" for t in ticks])
        ax.set_xlabel(p.get("x_label", "Effect Size (95% CI)"))
        if d.get("heterogeneity_note"):
            ax.set_title(d["heterogeneity_note"], loc="right", fontsize=tick_pt * 0.92, fontweight="normal", color="#475569")
        _despine(ax)

    elif ptype == "funnel":
        studies = d["studies"]
        is_log = bool(d.get("log_scale", True))
        theta = math.log(float(d["pooled_effect"])) if is_log else float(d["pooled_effect"])
        xs = [math.log(float(s["effect"])) if is_log else float(s["effect"]) for s in studies]
        ses = [float(s["se"]) for s in studies]
        max_se = max(ses) * 1.18
        grid = np.linspace(0, max_se, 60)
        ax.fill_betweenx(grid, theta - 1.96 * grid, theta + 1.96 * grid, color="#F1F5F9", zorder=1)
        ax.plot(theta - 1.96 * grid, grid, "--", color="#94A3B8", lw=0.8)
        ax.plot(theta + 1.96 * grid, grid, "--", color="#94A3B8", lw=0.8)
        ax.axvline(theta, color=colors[1], lw=0.9)
        ax.scatter(xs, ses, s=22, color=colors[0], edgecolor="#FFFFFF", linewidth=0.4, zorder=4)
        ax.set_ylim(max_se, 0)
        ax.set_xlabel(p.get("x_label", "Log Effect Estimate"))
        ax.set_ylabel(p.get("y_label", "Standard Error"))
        _despine(ax)

    elif ptype == "kaplan_meier":
        for i, grp in enumerate(d["groups"]):
            c = colors[i % len(colors)]
            ax.step(grp["times"], grp["survival"], where="post", color=c, linestyle=LINE_STYLES[i % 4], lw=1.35, label=grp["name"])
            if grp.get("ci_low") and grp.get("ci_high"):
                ax.fill_between(grp["times"], grp["ci_low"], grp["ci_high"], step="post", color=c, alpha=0.14)
        ax.set_ylim(float(d.get("y_min", 0.0)), 1.03)
        ax.set_xlabel(p.get("x_label", "Time (Months)"))
        ax.set_ylabel(p.get("y_label", "Survival Probability"))
        ax.legend(frameon=False, fontsize=tick_pt * 0.92, loc="lower left")
        if d.get("annotation"):
            ax.text(0.97, 0.95, d["annotation"], transform=ax.transAxes, ha="right", va="top", fontsize=tick_pt * 0.92, fontweight="bold")
        _despine(ax)

    elif ptype == "roc":
        ax.plot([0, 1], [0, 1], "--", color="#94A3B8", lw=0.8)
        for i, cv in enumerate(d["curves"]):
            c = colors[i % len(colors)]
            ax.plot(cv["fpr"], cv["tpr"], color=c, linestyle=LINE_STYLES[i % 4], lw=1.35, label=f"{cv['name']} (AUC {cv['auc']:.2f})")
        ax.set_xlim(-0.01, 1.01)
        ax.set_ylim(-0.01, 1.02)
        ax.set_xlabel(p.get("x_label", "1 − Specificity"))
        ax.set_ylabel(p.get("y_label", "Sensitivity"))
        ax.legend(frameon=False, fontsize=tick_pt * 0.90, loc="lower right")
        _despine(ax)

    elif ptype == "box_strip":
        groups = d["groups"]
        arrays = [[float(v) for v in g["values"]] for g in groups]
        pos = np.arange(1, len(groups) + 1)
        bp = ax.boxplot(arrays, positions=pos, widths=0.45, patch_artist=True, showfliers=False)
        rng = np.random.default_rng(7)
        for i, (box, arr) in enumerate(zip(bp["boxes"], arrays)):
            c = colors[i % len(colors)]
            box.set(facecolor=c, alpha=0.25, edgecolor=c, linewidth=1.0)
            bp["medians"][i].set(color="#111827", linewidth=1.3)
            jit = rng.uniform(-0.10, 0.10, size=len(arr))
            ax.scatter(np.full(len(arr), pos[i]) + jit, arr, s=11, color=c, alpha=0.80, edgecolor="#FFFFFF", linewidth=0.3, zorder=4)
        ax.set_xticks(pos)
        ax.set_xticklabels([g["name"] for g in groups])
        ax.set_ylabel(p.get("y_label", "Value"))
        _despine(ax)

    elif ptype == "bar_ci":
        cats = d["categories"]
        vals = [float(v) for v in d["values"]]
        idx = np.arange(len(cats))
        err = None
        if d.get("ci_low") and d.get("ci_high"):
            err = np.array([[v - float(lo) for v, lo in zip(vals, d["ci_low"])], [float(hi) - v for v, hi in zip(vals, d["ci_high"])]])
        ax.bar(idx, vals, width=0.55, color=[colors[i % len(colors)] for i in range(len(cats))], yerr=err, capsize=3, error_kw={"lw": 0.9, "ecolor": "#1E293B"})
        ax.set_ylim(0, max(d.get("ci_high", vals)) * 1.18)  # Mandatory zero baseline
        ax.set_xticks(idx)
        ax.set_xticklabels(cats)
        ax.set_ylabel(p.get("y_label", "Outcome"))
        _despine(ax)

    elif ptype == "scatter_fit":
        for i, grp in enumerate(d["groups"]):
            c = colors[i % len(colors)]
            ax.scatter(grp["x"], grp["y"], s=18, color=c, marker=MARKERS[i % 4], alpha=0.82, label=grp["name"])
        if d.get("fit"):
            ax.plot(d["fit"]["x"], d["fit"]["y"], "--", color=colors[1], lw=1.1, label=d["fit"].get("label", "Fit"))
        ax.set_xlabel(p.get("x_label", "X"))
        ax.set_ylabel(p.get("y_label", "Y"))
        ax.legend(frameon=False, fontsize=tick_pt * 0.90)
        _despine(ax)

    if p.get("title"):
        ax.set_title(p["title"], loc="left", pad=5)


def build_publication_figure(spec: Dict[str, Any], out_dir: pathlib.Path) -> Dict[str, Any]:
    db = json.loads((SKILL_ROOT / "templates" / "journal_figure_specs.json").read_text(encoding="utf-8"))
    prof_id = spec.get("journal_profile", "nature-portfolio")
    prof = db["profiles"].get(prof_id, db["profiles"]["nature-portfolio"])
    colors = spec.get("palette", db["okabe_ito"])

    col_span = spec.get("column_span", "double")
    width_mm = float(spec.get("width_mm", prof["widths_mm"].get(col_span, 183.0)))
    height_mm = min(float(prof["max_height_mm"]), float(spec.get("height_mm", width_mm * 0.68)))
    w_in, h_in = width_mm / 25.4, height_mm / 25.4
    dpi = int(spec.get("dpi", prof["dpi"]))

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Source Sans 3", "IBM Plex Sans", "DejaVu Sans"],
        "font.size": prof["label_pt"],
        "axes.titlesize": prof["label_pt"] * 1.05,
        "axes.titleweight": "bold",
        "axes.labelsize": prof["label_pt"],
        "axes.labelweight": "bold",
        "xtick.labelsize": prof["tick_pt"],
        "ytick.labelsize": prof["tick_pt"],
        "axes.linewidth": 0.75,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "path",
    })

    grid = spec.get("grid", {"rows": 1, "cols": len(spec["panels"])})
    nrows, ncols = int(grid["rows"]), int(grid["cols"])

    fig = plt.figure(figsize=(w_in, h_in), facecolor="#FFFFFF")
    gs = fig.add_gridspec(
        nrows, ncols,
        wspace=float(grid.get("wspace", 0.36)),
        hspace=float(grid.get("hspace", 0.42)),
        left=float(grid.get("left", 0.11)),
        right=float(grid.get("right", 0.97)),
        top=float(grid.get("top", 0.92)),
        bottom=float(grid.get("bottom", 0.11)),
    )

    panels = spec["panels"]
    for idx, p in enumerate(panels):
        r = int(p.get("row", idx // ncols))
        c = int(p.get("col", idx % ncols))
        rspan = int(p.get("rowspan", 1))
        cspan = int(p.get("colspan", 1))
        ax = fig.add_subplot(gs[r : r + rspan, c : c + cspan])
        _draw_panel(ax, p, colors, float(prof["tick_pt"]))

        if len(panels) > 1 or spec.get("force_panel_label"):
            letter = chr(ord("a") + idx)
            lbl = letter.upper() if prof["panel_case"] == "upper" else letter
            ax.text(
                float(p.get("label_x", -0.14)), float(p.get("label_y", 1.10)),
                lbl, transform=ax.transAxes,
                fontsize=prof["panel_pt"], fontweight="bold", va="top", ha="right", color="#111827",
            )

    out_dir.mkdir(parents=True, exist_ok=True)
    svg_p = out_dir / "figure.svg"
    pdf_p = out_dir / "figure.pdf"
    png_p = out_dir / "figure.png"
    fig.savefig(svg_p, format="svg", facecolor="#FFFFFF")
    fig.savefig(pdf_p, format="pdf", facecolor="#FFFFFF")
    fig.savefig(png_p, format="png", dpi=dpi, facecolor="#FFFFFF")
    plt.close(fig)

    # Write structured journal figure legend
    legend_lines = [
        f"# {spec.get('figure_number', 'Figure 1')}. {spec.get('figure_title', 'Composite Scientific Figure')}",
        "",
    ]
    for idx, p in enumerate(panels):
        letter = chr(ord("a") + idx)
        lbl = letter.upper() if prof["panel_case"] == "upper" else letter
        legend_lines.append(f"- **({lbl})** {p.get('caption', p.get('title', p['type']))}")
    if spec.get("statistical_note"):
        legend_lines.extend(["", f"*{spec['statistical_note']}*"])
    (out_dir / "figure_legend.md").write_text("\n".join(legend_lines) + "\n", encoding="utf-8")

    return {
        "journal_profile": prof_id,
        "width_mm": round(width_mm, 1),
        "height_mm": round(height_mm, 1),
        "dpi": dpi,
        "panel_count": len(panels),
        "files": {"svg": str(svg_p), "pdf": str(pdf_p), "png": str(png_p), "legend_md": str(out_dir / "figure_legend.md")},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate journal-formatted single or multi-panel publication figure.")
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    spec = json.loads(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    res = build_publication_figure(spec, pathlib.Path(args.output_dir))
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
