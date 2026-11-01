#!/usr/bin/env python3
"""
Scientific Visualization Engine for research-poster-maker.

Generates publication-grade, colorblind-safe vector (.svg, .pdf) and high-DPI
raster (.png) scientific figures directly from verified study data.

Supported chart types (15):
  1. bar_chart
  2. forest_plot
  3. funnel_plot
  4. kaplan_meier
  5. roc_curve
  6. confusion_matrix
  7. scatter_plot
  8. box_plot
  9. violin_plot
  10. prisma_diagram
  11. consort_diagram
  12. flow_diagram
  13. workflow_diagram
  14. characteristics_table
  15. statistical_table
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
import textwrap
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
import numpy as np

# Ensure sibling package import works from any cwd
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from poster_engine.design_tokens import (
    BUNDLED_FONT_DIR,
    OKABE_ITO_SERIES,
    ColorPalette,
    resolve_palette,
    wcag_contrast_ratio,
)

MARKER_SHAPES = ["o", "s", "^", "D", "v", "P", "X"]
LINE_STYLES = ["-", "--", "-.", ":"]


def _register_bundled_fonts() -> None:
    if BUNDLED_FONT_DIR.exists():
        for ttf in BUNDLED_FONT_DIR.glob("*.ttf"):
            try:
                font_manager.fontManager.addfont(str(ttf))
            except Exception:
                pass


_register_bundled_fonts()


def _configure_mpl_style(font_family: str, base_pt: float = 18.0) -> None:
    """Configure Matplotlib for crisp vector outlines and poster-scale legibility."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [font_family, "IBM Plex Sans", "Source Sans 3", "DejaVu Sans"],
        "font.size": base_pt,
        "axes.titlesize": base_pt * 1.18,
        "axes.titleweight": "bold",
        "axes.labelsize": base_pt * 1.04,
        "axes.labelweight": "bold",
        "xtick.labelsize": base_pt * 0.92,
        "ytick.labelsize": base_pt * 0.92,
        "legend.fontsize": base_pt * 0.90,
        "axes.edgecolor": "#475569",
        "axes.linewidth": 1.2,
        "xtick.major.width": 1.1,
        "ytick.major.width": 1.1,
        "xtick.color": "#334155",
        "ytick.color": "#334155",
        "text.color": "#16202A",
        "axes.labelcolor": "#16202A",
        "pdf.fonttype": 42,      # Embed TrueType fonts (never Type 3)
        "ps.fonttype": 42,
        "svg.fonttype": "path",  # Exact glyph paths for zero-drift vector PDF embedding
        "figure.facecolor": "#FFFFFF",
        "axes.facecolor": "#FFFFFF",
    })


def _despine(ax: plt.Axes, keep_bottom: bool = True, keep_left: bool = True) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(keep_bottom)
    ax.spines["left"].set_visible(keep_left)


def _save_outputs(
    fig: plt.Figure,
    out_stem: pathlib.Path,
    dpi: int = 300,
    formats: Tuple[str, ...] = ("svg", "pdf", "png"),
) -> Dict[str, str]:
    out_stem.parent.mkdir(parents=True, exist_ok=True)
    saved: Dict[str, str] = {}
    for fmt in formats:
        p = out_stem.with_suffix(f".{fmt}")
        if fmt == "png":
            fig.savefig(p, format="png", dpi=dpi, facecolor=fig.get_facecolor())
        else:
            fig.savefig(p, format=fmt, facecolor=fig.get_facecolor())
        saved[fmt] = str(p)
    plt.close(fig)
    return saved


# ---------------------------------------------------------------------------
# 1. Bar Chart (Mandatory Zero Baseline, CI Whiskers, Sample Sizes)
# ---------------------------------------------------------------------------

def render_bar_chart(
    spec: Dict[str, Any],
    width_in: float,
    height_in: float,
    palette: ColorPalette,
    base_pt: float,
) -> Tuple[plt.Figure, List[str]]:
    warnings: List[str] = []
    data = spec["data"]
    categories = [str(c) for c in data["categories"]]
    series_list = data.get("series")
    if not series_list:
        series_list = [{
            "name": data.get("series_name", "Outcome"),
            "values": data["values"],
            "ci_low": data.get("ci_low"),
            "ci_high": data.get("ci_high"),
            "se": data.get("se"),
        }]

    horizontal = bool(spec.get("horizontal", False))
    fig, ax = plt.subplots(figsize=(width_in, height_in))
    fig.subplots_adjust(
        left=0.22 if horizontal else 0.13,
        right=0.95,
        top=0.88 if spec.get("subtitle") or len(series_list) > 1 else 0.91,
        bottom=0.18 if not horizontal else 0.15,
    )

    n_cats = len(categories)
    n_ser = len(series_list)
    idx = np.arange(n_cats)
    bar_w = min(0.66 / max(1, n_ser), 0.52)
    colors = list(palette.chart_series)

    all_highs: List[float] = [0.0]
    all_lows: List[float] = [0.0]

    for s_i, ser in enumerate(series_list):
        vals = [float(v) for v in ser["values"]]
        offset = (s_i - (n_ser - 1) / 2.0) * (bar_w * 1.08)
        pos = idx + offset
        color = ser.get("color") or colors[s_i % len(colors)]

        err = None
        if ser.get("ci_low") is not None and ser.get("ci_high") is not None:
            lows = [ max(0.0, v - float(lo)) for v, lo in zip(vals, ser["ci_low"]) ]
            highs = [ max(0.0, float(hi) - v) for v, hi in zip(vals, ser["ci_high"]) ]
            err = np.array([lows, highs])
            all_highs.extend([float(hi) for hi in ser["ci_high"]])
            all_lows.extend([float(lo) for lo in ser["ci_low"]])
        elif ser.get("se") is not None:
            ses = [float(e) for e in ser["se"]]
            err = np.array(ses)
            all_highs.extend([v + e for v, e in zip(vals, ses)])
            all_lows.extend([v - e for v, e in zip(vals, ses)])
        else:
            all_highs.extend(vals)
            all_lows.extend(vals)

        err_kw = {"ecolor": "#1E293B", "elinewidth": 1.6, "capsize": 5, "capthick": 1.5}
        if horizontal:
            bars = ax.barh(
                pos, vals, height=bar_w, color=color, edgecolor="#FFFFFF",
                linewidth=1.0, xerr=err, error_kw=err_kw, label=ser.get("name", f"Series {s_i+1}"),
                zorder=3,
            )
        else:
            bars = ax.bar(
                pos, vals, width=bar_w, color=color, edgecolor="#FFFFFF",
                linewidth=1.0, yerr=err, error_kw=err_kw, label=ser.get("name", f"Series {s_i+1}"),
                zorder=3,
            )

        # Direct value annotations preserving precision
        val_fmt = spec.get("value_format", "{:.1f}")
        span = max(all_highs) - min(0.0, min(all_lows)) or 1.0
        if n_ser == 1 and n_cats >= 2 and not ser.get("color"):
            # Distinct high-contrast primary vs comparator coloring for 1-series group comparisons
            for b_i, b in enumerate(bars):
                b.set_facecolor(palette.accent if b_i == 0 else palette.dominant)
        for b_i, b in enumerate(bars):
            v = vals[b_i]
            top_v = (
                float(ser["ci_high"][b_i])
                if ser.get("ci_high") is not None
                else (v + float(ser["se"][b_i]) if ser.get("se") is not None else v)
            )
            txt = val_fmt.format(v)
            if horizontal:
                ax.text(
                    top_v + 0.02 * span, b.get_y() + b.get_height() / 2.0, txt,
                    va="center", ha="left", fontsize=base_pt * 0.84, fontweight="bold", color="#1E293B"
                )
            else:
                ax.text(
                    b.get_x() + b.get_width() / 2.0, top_v + 0.022 * span, txt,
                    va="bottom", ha="center", fontsize=base_pt * 0.84, fontweight="bold", color="#1E293B"
                )

    # Mandatory zero-baseline enforcement (never truncate bar axes!)
    max_bound = max(all_highs) * 1.18 if max(all_highs) > 0 else 1.0
    min_bound = min(0.0, min(all_lows) * 1.15)
    sample_ns = data.get("sample_sizes")
    cat_labels = [
        f"{c}\n(n={sample_ns[i]})" if sample_ns and i < len(sample_ns) else c
        for i, c in enumerate(categories)
    ]

    if horizontal:
        ax.set_yticks(idx)
        ax.set_yticklabels(cat_labels)
        ax.invert_yaxis()
        ax.set_xlim(min_bound, max_bound)
        ax.set_xlabel(spec.get("value_label", "Value"))
        ax.xaxis.grid(True, color="#E2E8F0", linewidth=0.9, zorder=0)
    else:
        ax.set_xticks(idx)
        ax.set_xticklabels(cat_labels)
        ax.set_ylim(min_bound, max_bound)
        ax.set_ylabel(spec.get("value_label", "Value"))
        ax.yaxis.grid(True, color="#E2E8F0", linewidth=0.9, zorder=0)

    _despine(ax)
    if spec.get("title"):
        ax.set_title(spec["title"], loc="left", pad=12, color=palette.dominant)
    if n_ser > 1:
        ax.legend(frameon=False, ncol=min(n_ser, 3), loc="upper right")
    if spec.get("annotation"):
        ax.text(
            0.99, 0.96, spec["annotation"], transform=ax.transAxes,
            ha="right", va="top", fontsize=base_pt * 0.84,
            bbox={"boxstyle": "round,pad=0.35", "facecolor": palette.surface_tint, "edgecolor": palette.rule_border},
        )
    return fig, warnings


# ---------------------------------------------------------------------------
# 2. Meta-Analysis Forest Plot (Individual Studies, Weights, Pooled Diamond, PI, I2)
# ---------------------------------------------------------------------------

def render_forest_plot(
    spec: Dict[str, Any],
    width_in: float,
    height_in: float,
    palette: ColorPalette,
    base_pt: float,
) -> Tuple[plt.Figure, List[str]]:
    warnings: List[str] = []
    data = spec["data"]
    studies = data["studies"]  # list of {study, effect, ci_low, ci_high, weight, subgroup?, events_tx?, events_ctrl?}
    pooled = data.get("pooled")  # {label, effect, ci_low, ci_high, pi_low?, pi_high?}
    measure = data.get("effect_measure", "OR")  # OR, RR, HR, MD, SMD
    is_ratio = measure.upper() in ("OR", "RR", "HR", "IRR")
    null_val = float(data.get("null_value", 1.0 if is_ratio else 0.0))
    use_log = bool(data.get("log_scale", is_ratio))

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.14)

    # Build row sequence (top to bottom)
    rows: List[Dict[str, Any]] = []
    current_sub = None
    for st in studies:
        if st.get("subgroup") and st["subgroup"] != current_sub:
            current_sub = st["subgroup"]
            rows.append({"type": "subgroup", "label": current_sub})
        rows.append({"type": "study", **st})
    if pooled:
        rows.append({"type": "spacer"})
        rows.append({"type": "pooled", **pooled})

    n_rows = len(rows)
    y_positions = list(range(n_rows, 0, -1))

    # Determine x transformation
    def tx(v: float) -> float:
        if use_log:
            return math.log(max(v, 1e-4))
        return float(v)

    raw_vals: List[float] = [null_val]
    for st in studies:
        raw_vals.extend([float(st["ci_low"]), float(st["ci_high"]), float(st["effect"])])
    if pooled:
        raw_vals.extend([float(pooled["ci_low"]), float(pooled["ci_high"]), float(pooled["effect"])])
        if pooled.get("pi_low") is not None and pooled.get("pi_high") is not None:
            raw_vals.extend([float(pooled["pi_low"]), float(pooled["pi_high"])])

    tx_vals = [tx(v) for v in raw_vals]
    plot_min = min(tx_vals)
    plot_max = max(tx_vals)
    span = max(plot_max - plot_min, 0.4)
    p_left = plot_min - 0.12 * span
    p_right = plot_max + 0.12 * span
    p_span = p_right - p_left

    # 3-zone coordinate mapping in unified x space:
    # Left study label zone: [p_left - 0.62*p_span, p_left - 0.04*p_span]
    # Center plot zone: [p_left, p_right]
    # Right numeric column zone: [p_right + 0.05*p_span, p_right + 0.72*p_span]
    x_full_min = p_left - 0.66 * p_span
    x_full_max = p_right + 0.76 * p_span
    ax.set_xlim(x_full_min, x_full_max)
    ax.set_ylim(0.1, n_rows + 1.65)

    # Header bar & rule
    header_y = n_rows + 1.05
    ax.plot([x_full_min, x_full_max], [n_rows + 0.65, n_rows + 0.65], color=palette.dominant, lw=1.6)
    ax.text(x_full_min + 0.01 * p_span, header_y, "Study / Subgroup", fontweight="bold", fontsize=base_pt * 0.90, va="center", color=palette.dominant)
    ax.text((p_left + p_right) / 2.0, header_y, f"{measure} (95% CI)", fontweight="bold", fontsize=base_pt * 0.90, va="center", ha="center", color=palette.dominant)
    ax.text(p_right + 0.36 * p_span, header_y, f"{measure} [95% CI]", fontweight="bold", fontsize=base_pt * 0.90, va="center", ha="right", color=palette.dominant)
    ax.text(x_full_max - 0.01 * p_span, header_y, "Weight", fontweight="bold", fontsize=base_pt * 0.90, va="center", ha="right", color=palette.dominant)

    # Null vertical reference line & pooled guide line
    ax.plot([tx(null_val), tx(null_val)], [0.4, n_rows + 0.62], color="#64748B", linestyle="--", lw=1.3, zorder=1)
    if pooled:
        ax.plot([tx(float(pooled["effect"])), tx(float(pooled["effect"]))], [0.85, n_rows + 0.62], color=palette.accent, linestyle=":", lw=1.1, alpha=0.8, zorder=1)

    weights = [float(st.get("weight", 10.0)) for st in studies]
    max_w = max(weights) if weights else 10.0

    for row, y in zip(rows, y_positions):
        rtype = row["type"]
        if rtype == "subgroup":
            ax.text(
                x_full_min + 0.01 * p_span, y, str(row["label"]),
                fontweight="bold", fontstyle="italic", fontsize=base_pt * 0.88,
                va="center", color=palette.supporting,
            )
        elif rtype == "study":
            # Subtle zebra tint on alternating rows
            if y % 2 == 0:
                rect = mpatches.Rectangle(
                    (x_full_min, y - 0.44), x_full_max - x_full_min, 0.88,
                    facecolor=palette.surface_tint, edgecolor="none", alpha=0.55, zorder=0,
                )
                ax.add_patch(rect)

            eff = float(row["effect"])
            lo = float(row["ci_low"])
            hi = float(row["ci_high"])
            w = float(row.get("weight", 100.0 / max(1, len(studies))))

            label = str(row["study"])
            if row.get("n") is not None:
                label = f"{label} (n={row['n']})"
            ax.text(x_full_min + 0.015 * p_span, y, label, va="center", fontsize=base_pt * 0.84, color=palette.body_ink)

            # CI Whisker
            ax.plot([tx(lo), tx(hi)], [y, y], color="#1E293B", lw=1.6, zorder=3)
            # Weight-scaled square marker
            msize = 7.0 + 9.0 * math.sqrt(max(w, 0.5) / max_w)
            ax.plot(tx(eff), y, marker="s", markersize=msize, color=palette.chart_series[1], markeredgecolor="#FFFFFF", markeredgewidth=0.7, zorder=4)

            ci_str = f"{eff:.2f} [{lo:.2f}, {hi:.2f}]"
            ax.text(p_right + 0.44 * p_span, y, ci_str, va="center", ha="right", fontsize=base_pt * 0.82, color=palette.body_ink)
            ax.text(x_full_max - 0.01 * p_span, y, f"{w:.1f}%", va="center", ha="right", fontsize=base_pt * 0.82, color=palette.muted_ink)

        elif rtype == "pooled":
            ax.plot([x_full_min, x_full_max], [y + 0.55, y + 0.55], color=palette.rule_border, lw=1.0)
            eff = float(row["effect"])
            lo = float(row["ci_low"])
            hi = float(row["ci_high"])
            plabel = row.get("label", "Pooled Random-Effects Estimate")
            ax.text(x_full_min + 0.01 * p_span, y, plabel, va="center", fontweight="bold", fontsize=base_pt * 0.88, color=palette.dominant)

            # Optional 95% Prediction Interval whiskers
            if row.get("pi_low") is not None and row.get("pi_high") is not None:
                ax.plot(
                    [tx(float(row["pi_low"])), tx(float(row["pi_high"]))],
                    [y, y], color=palette.dominant, linestyle="--", lw=1.5, zorder=2,
                )

            # Pooled Diamond
            diamond_x = [tx(lo), tx(eff), tx(hi), tx(eff)]
            diamond_y = [y, y + 0.32, y, y - 0.32]
            ax.fill(diamond_x, diamond_y, color=palette.accent, edgecolor=palette.dominant, linewidth=1.1, zorder=5)

            ci_str = f"{eff:.2f} [{lo:.2f}, {hi:.2f}]"
            ax.text(p_right + 0.44 * p_span, y, ci_str, va="center", ha="right", fontweight="bold", fontsize=base_pt * 0.86, color=palette.dominant)
            ax.text(x_full_max - 0.01 * p_span, y, "100.0%", va="center", ha="right", fontweight="bold", fontsize=base_pt * 0.84, color=palette.dominant)

    # Bottom axis strictly spanning [p_left, p_right]
    ax.plot([p_left, p_right], [0.35, 0.35], color="#334155", lw=1.2)
    if use_log:
        candidate_ticks = [0.1, 0.2, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 10.0]
        ticks = [t for t in candidate_ticks if p_left <= tx(t) <= p_right]
        if null_val not in ticks:
            ticks.append(null_val)
            ticks.sort()
        for t in ticks:
            xt = tx(t)
            ax.plot([xt, xt], [0.35, 0.20], color="#334155", lw=1.1)
            lbl = f"{t:g}"
            ax.text(xt, 0.02, lbl, ha="center", va="top", fontsize=base_pt * 0.80, color="#334155")
    else:
        ticks = np.linspace(p_left, p_right, 5)
        for t in ticks:
            ax.plot([t, t], [0.35, 0.20], color="#334155", lw=1.1)
            ax.text(t, 0.02, f"{t:.2f}", ha="center", va="top", fontsize=base_pt * 0.80, color="#334155")

    # Favors direction labels on dedicated line right beneath axis ticks
    favors_left = data.get("favors_left", "Favors Intervention")
    favors_right = data.get("favors_right", "Favors Control")
    ax.text(tx(null_val) - 0.04 * p_span, -0.42, f"← {favors_left}", ha="right", va="top", fontsize=base_pt * 0.80, fontweight="bold", color=palette.muted_ink)
    ax.text(tx(null_val) + 0.04 * p_span, -0.42, f"{favors_right} →", ha="left", va="top", fontsize=base_pt * 0.80, fontweight="bold", color=palette.muted_ink)

    # Heterogeneity summary strip on separate non-overlapping lower line
    het_parts: List[str] = []
    het = data.get("heterogeneity", {})
    if het.get("I2") is not None:
        het_parts.append(f"I² = {het['I2']}%")
    if het.get("tau2") is not None:
        het_parts.append(f"τ² = {het['tau2']}")
    if het.get("Q") is not None:
        het_parts.append(f"Q = {het['Q']}")
    if het.get("p_heterogeneity") is not None:
        het_parts.append(f"p_het = {het['p_heterogeneity']}")
    if het.get("p_overall") is not None:
        het_parts.append(f"Overall p = {het['p_overall']}")
    if pooled and pooled.get("pi_low") is not None:
        het_parts.append(f"95% PI [{pooled['pi_low']:.2f}, {pooled['pi_high']:.2f}] (dashed)")
    if het_parts:
        ax.text(
            x_full_min + 0.01 * p_span, -0.98,
            "Heterogeneity: " + "  |  ".join(het_parts),
            ha="left", va="top", fontsize=base_pt * 0.80, fontweight="bold", color=palette.body_ink,
        )

    ax.set_ylim(-1.42, n_rows + 1.50)
    ax.axis("off")
    if spec.get("title"):
        ax.set_title(spec["title"], loc="left", pad=10, color=palette.dominant)
    return fig, warnings


# ---------------------------------------------------------------------------
# 3. Funnel Plot (Publication Bias / Small-Study Effects)
# ---------------------------------------------------------------------------

def render_funnel_plot(
    spec: Dict[str, Any],
    width_in: float,
    height_in: float,
    palette: ColorPalette,
    base_pt: float,
) -> Tuple[plt.Figure, List[str]]:
    warnings: List[str] = []
    data = spec["data"]
    studies = data["studies"]  # {study, effect, se} (effect on log scale or linear, or raw ratio + log_scale)
    is_ratio = bool(data.get("log_scale", False))
    pooled_eff = float(data.get("pooled_effect", 1.0 if is_ratio else 0.0))
    theta_hat = math.log(pooled_eff) if is_ratio else pooled_eff

    xs = [math.log(float(s["effect"])) if is_ratio else float(s["effect"]) for s in studies]
    ses = [float(s["se"]) for s in studies]
    max_se = max(ses) * 1.15 if ses else 0.5

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    fig.subplots_adjust(left=0.20, right=0.96, top=0.92, bottom=0.16)

    se_grid = np.linspace(0.0, max_se, 100)
    low_cone = theta_hat - 1.96 * se_grid
    high_cone = theta_hat + 1.96 * se_grid

    ax.fill_betweenx(se_grid, low_cone, high_cone, color=palette.surface_tint, alpha=0.85, zorder=1)
    ax.plot(low_cone, se_grid, linestyle="--", color="#64748B", lw=1.3, zorder=2, label="Pseudo 95% CI")
    ax.plot(high_cone, se_grid, linestyle="--", color="#64748B", lw=1.3, zorder=2)
    ax.axvline(theta_hat, color=palette.accent, lw=1.6, zorder=2, label="Pooled Estimate")

    ax.scatter(
        xs, ses, s=95, color=palette.chart_series[1], edgecolor="#FFFFFF",
        linewidth=1.0, zorder=4, label=f"Studies (k={len(studies)})",
    )

    ax.set_ylim(max_se, 0.0)  # Inverted SE axis: highest precision at apex
    x_pad = max(abs(min(xs) - theta_hat), abs(max(xs) - theta_hat), 1.96 * max_se) * 1.15
    ax.set_xlim(theta_hat - x_pad, theta_hat + x_pad)

    if is_ratio:
        cand = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 4.0]
        valid = [c for c in cand if (theta_hat - x_pad) <= math.log(c) <= (theta_hat + x_pad)]
        if valid:
            ax.set_xticks([math.log(c) for c in valid])
            ax.set_xticklabels([f"{c:g}" for c in valid])

    ax.set_xlabel(spec.get("x_label", "Effect Estimate"), labelpad=8)
    ax.set_ylabel(spec.get("y_label", "Standard Error (SE)"), labelpad=10)
    ax.yaxis.grid(True, color="#E2E8F0", lw=0.8, zorder=0)
    _despine(ax)
    if spec.get("title"):
        ax.set_title(spec["title"], loc="left", pad=10, color=palette.dominant)
    ax.legend(frameon=False, loc="lower right")
    if data.get("egger_p") is not None:
        ax.text(
            0.03, 0.06, f"Egger's regression p = {data['egger_p']}",
            transform=ax.transAxes, fontsize=base_pt * 0.84,
            bbox={"boxstyle": "round,pad=0.3", "facecolor": "#FFFFFF", "edgecolor": palette.rule_border},
        )
    return fig, warnings


# ---------------------------------------------------------------------------
# 4. Kaplan-Meier Survival Curve + Aligned Number-at-Risk Table
# ---------------------------------------------------------------------------

def render_kaplan_meier(
    spec: Dict[str, Any],
    width_in: float,
    height_in: float,
    palette: ColorPalette,
    base_pt: float,
) -> Tuple[plt.Figure, List[str]]:
    warnings: List[str] = []
    data = spec["data"]
    groups = data["groups"]  # [{name, times, survival, ci_low?, ci_high?, censor_times?, censor_surv?, at_risk?}]
    has_risk_table = any(g.get("at_risk") for g in groups)

    if has_risk_table:
        fig, (ax, ax_tbl) = plt.subplots(
            2, 1, figsize=(width_in, height_in),
            gridspec_kw={"height_ratios": [3.6, 1.0], "hspace": 0.26},
        )
        fig.subplots_adjust(left=0.14, right=0.96, top=0.90, bottom=0.08)
    else:
        fig, ax = plt.subplots(figsize=(width_in, height_in))
        ax_tbl = None
        fig.subplots_adjust(left=0.13, right=0.96, top=0.90, bottom=0.15)

    colors = list(palette.chart_series)
    max_t = 0.0
    min_s = 1.0

    for i, grp in enumerate(groups):
        t = [float(x) for x in grp["times"]]
        s = [float(y) for y in grp["survival"]]
        max_t = max(max_t, max(t))
        min_s = min(min_s, min(s))
        c = grp.get("color") or colors[i % len(colors)]
        ls = LINE_STYLES[i % len(LINE_STYLES)]

        ax.step(t, s, where="post", color=c, linestyle=ls, lw=2.6, label=grp["name"], zorder=4)
        if grp.get("ci_low") and grp.get("ci_high"):
            lo = [float(v) for v in grp["ci_low"]]
            hi = [float(v) for v in grp["ci_high"]]
            min_s = min(min_s, min(lo))
            ax.fill_between(t, lo, hi, step="post", color=c, alpha=0.14, zorder=2)

        if grp.get("censor_times") and grp.get("censor_surv"):
            ax.scatter(
                grp["censor_times"], grp["censor_surv"],
                marker="+", s=70, color=c, linewidths=1.6, zorder=5,
            )

    y_floor = 0.0 if min_s < 0.45 or not spec.get("zoom_y") else max(0.0, math.floor(min_s * 10 - 1) / 10.0)
    ax.set_ylim(y_floor, 1.03)
    ax.set_xlim(0.0, max_t * 1.03)
    ax.set_ylabel(spec.get("y_label", "Event-Free Survival Probability"))
    ax.set_xlabel(spec.get("x_label", "Follow-up Time (Months)"))
    ax.yaxis.grid(True, color="#E2E8F0", lw=0.9, zorder=0)
    _despine(ax)
    ax.legend(frameon=False, loc="lower left")

    if spec.get("title"):
        ax.set_title(spec["title"], loc="left", pad=10, color=palette.dominant)

    if data.get("stat_summary"):
        ax.text(
            0.98, 0.95, data["stat_summary"], transform=ax.transAxes,
            ha="right", va="top", fontsize=base_pt * 0.88, fontweight="bold",
            bbox={"boxstyle": "round,pad=0.4", "facecolor": palette.surface_tint, "edgecolor": palette.dominant, "linewidth": 1.1},
        )

    if ax_tbl is not None:
        risk_times = [float(x) for x in data.get("risk_times", groups[0]["times"])]
        ax_tbl.set_xlim(ax.get_xlim())
        ax_tbl.set_ylim(-0.5, len(groups) + 0.4)
        ax_tbl.text(0.0, len(groups) - 0.05, "No. at Risk", fontweight="bold", fontsize=base_pt * 0.82, color=palette.dominant, va="bottom")
        for g_i, grp in enumerate(groups):
            y_row = len(groups) - 1 - g_i
            c = grp.get("color") or colors[g_i % len(colors)]
            short_name = grp.get("short_name", grp["name"].split("(")[0].strip())
            ax_tbl.text(-0.02 * max_t, y_row, short_name, ha="right", va="center", fontweight="bold", fontsize=base_pt * 0.80, color=c)
            at_risk = grp.get("at_risk", [])
            for r_t, count in zip(risk_times, at_risk):
                ax_tbl.text(r_t, y_row, str(count), ha="center", va="center", fontsize=base_pt * 0.80, color=palette.body_ink)
        ax_tbl.axis("off")

    return fig, warnings


# ---------------------------------------------------------------------------
# 5. ROC Curve
# ---------------------------------------------------------------------------

def render_roc_curve(
    spec: Dict[str, Any],
    width_in: float,
    height_in: float,
    palette: ColorPalette,
    base_pt: float,
) -> Tuple[plt.Figure, List[str]]:
    warnings: List[str] = []
    curves = spec["data"]["curves"]  # [{name, fpr, tpr, auc, ci_low?, ci_high?}]
    fig, ax = plt.subplots(figsize=(width_in, height_in))
    fig.subplots_adjust(left=0.14, right=0.95, top=0.89, bottom=0.16)

    ax.plot([0, 1], [0, 1], linestyle="--", color="#94A3B8", lw=1.4, label="Reference (AUC = 0.50)")
    colors = list(palette.chart_series)

    for i, c_spec in enumerate(curves):
        col = colors[i % len(colors)]
        ls = LINE_STYLES[i % len(LINE_STYLES)]
        auc_txt = f"AUC = {float(c_spec['auc']):.3f}"
        if c_spec.get("ci_low") is not None and c_spec.get("ci_high") is not None:
            auc_txt += f" (95% CI {float(c_spec['ci_low']):.3f}–{float(c_spec['ci_high']):.3f})"
        ax.plot(
            c_spec["fpr"], c_spec["tpr"], color=col, linestyle=ls, lw=2.6,
            label=f"{c_spec['name']}: {auc_txt}",
        )
        if c_spec.get("optimal_point"):
            op = c_spec["optimal_point"]
            ax.scatter([op["fpr"]], [op["tpr"]], s=95, color=col, edgecolor="#FFFFFF", linewidth=1.3, zorder=6)
            if op.get("label"):
                ax.annotate(
                    op["label"], xy=(op["fpr"], op["tpr"]),
                    xytext=(max(0.03, op["fpr"] + 0.09), min(0.95, op["tpr"] + 0.08)),
                    arrowprops={"arrowstyle": "->", "color": col, "lw": 1.3},
                    fontsize=base_pt * 0.80, fontweight="bold",
                    bbox={"boxstyle": "round,pad=0.28", "facecolor": "#FFFFFF", "edgecolor": palette.rule_border, "alpha": 0.94},
                    zorder=7,
                )

    ax.set_xlim(-0.01, 1.01)
    ax.set_ylim(-0.01, 1.02)
    ax.set_xlabel("1 − Specificity (False Positive Rate)")
    ax.set_ylabel("Sensitivity (True Positive Rate)")
    ax.grid(True, color="#E2E8F0", lw=0.8)
    _despine(ax)
    if spec.get("title"):
        ax.set_title(spec["title"], loc="left", pad=10, color=palette.dominant)
    ax.legend(frameon=True, facecolor="#FFFFFF", edgecolor=palette.rule_border, loc="lower right")
    return fig, warnings


# ---------------------------------------------------------------------------
# 6. Confusion Matrix (Perceptually Uniform, Count + Percentage)
# ---------------------------------------------------------------------------

def render_confusion_matrix(
    spec: Dict[str, Any],
    width_in: float,
    height_in: float,
    palette: ColorPalette,
    base_pt: float,
) -> Tuple[plt.Figure, List[str]]:
    warnings: List[str] = []
    data = spec["data"]
    mat = np.array(data["matrix"], dtype=float)
    labels = [str(l) for l in data["labels"]]
    row_sums = mat.sum(axis=1, keepdims=True)
    pct = np.divide(mat * 100.0, row_sums, out=np.zeros_like(mat), where=row_sums > 0)

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    fig.subplots_adjust(left=0.20, right=0.92, top=0.88, bottom=0.18)

    im = ax.imshow(pct, cmap="cividis", vmin=0, vmax=100, aspect="auto")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Row Percentage (%)", fontsize=base_pt * 0.88)

    for r in range(mat.shape[0]):
        for c in range(mat.shape[1]):
            val_pct = pct[r, c]
            txt_col = "#111827" if val_pct > 55 else "#FFFFFF"
            ax.text(
                c, r, f"n = {int(round(mat[r, c]))}\n({val_pct:.1f}%)",
                ha="center", va="center", color=txt_col,
                fontweight="bold", fontsize=base_pt * 0.88,
            )

    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    ax.set_xlabel(data.get("x_label", "Predicted Classification"))
    ax.set_ylabel(data.get("y_label", "Reference Standard"))
    if spec.get("title"):
        ax.set_title(spec["title"], loc="left", pad=10, color=palette.dominant)
    return fig, warnings


# ---------------------------------------------------------------------------
# 7. Scatter / Exposure-Response / Longitudinal Trend Plot
# ---------------------------------------------------------------------------

def render_scatter_plot(
    spec: Dict[str, Any],
    width_in: float,
    height_in: float,
    palette: ColorPalette,
    base_pt: float,
) -> Tuple[plt.Figure, List[str]]:
    warnings: List[str] = []
    data = spec["data"]
    groups = data.get("groups") or [{
        "name": data.get("series_name", "Observations"),
        "x": data["x"],
        "y": data["y"],
        "ci_low": data.get("ci_low"),
        "ci_high": data.get("ci_high"),
    }]
    connect = bool(spec.get("connect_lines", False))

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    fig.subplots_adjust(left=0.14, right=0.95, top=0.88, bottom=0.16)
    colors = list(palette.chart_series)

    for i, grp in enumerate(groups):
        xs = [float(v) for v in grp["x"]]
        ys = [float(v) for v in grp["y"]]
        col = grp.get("color") or colors[i % len(colors)]
        mk = MARKER_SHAPES[i % len(MARKER_SHAPES)]
        ls = LINE_STYLES[i % len(LINE_STYLES)]

        if connect:
            ax.plot(xs, ys, color=col, linestyle=ls, lw=2.4, marker=mk, markersize=8, label=grp["name"], zorder=4)
            if grp.get("ci_low") and grp.get("ci_high"):
                ax.fill_between(
                    xs, [float(v) for v in grp["ci_low"]], [float(v) for v in grp["ci_high"]],
                    color=col, alpha=0.14, zorder=2,
                )
        else:
            ax.scatter(
                xs, ys, s=75, color=col, marker=mk, alpha=0.85,
                edgecolor="#FFFFFF", linewidth=0.8, label=grp["name"], zorder=4,
            )

    if data.get("trend_line"):
        tl = data["trend_line"]
        ax.plot(tl["x"], tl["y"], color=palette.accent, linestyle="--", lw=2.0, label=tl.get("label", "Fitted Model"), zorder=3)
        if tl.get("ci_low") and tl.get("ci_high"):
            ax.fill_between(tl["x"], tl["ci_low"], tl["ci_high"], color=palette.accent, alpha=0.12, zorder=1)

    ax.set_xlabel(spec.get("x_label", "X"))
    ax.set_ylabel(spec.get("y_label", "Y"))
    ax.grid(True, color="#E2E8F0", lw=0.8, zorder=0)
    _despine(ax)
    if spec.get("title"):
        ax.set_title(spec["title"], loc="left", pad=10, color=palette.dominant)
    if len(groups) > 1 or data.get("trend_line"):
        ax.legend(frameon=False, loc=spec.get("legend_loc", "best"))
    if spec.get("annotation"):
        ax.text(
            0.98, 0.95, spec["annotation"], transform=ax.transAxes, ha="right", va="top",
            fontsize=base_pt * 0.84,
            bbox={"boxstyle": "round,pad=0.35", "facecolor": palette.surface_tint, "edgecolor": palette.rule_border},
        )
    return fig, warnings


# ---------------------------------------------------------------------------
# 8 & 9. Box Plot and Violin Plot
# ---------------------------------------------------------------------------

def render_distribution_plot(
    spec: Dict[str, Any],
    width_in: float,
    height_in: float,
    palette: ColorPalette,
    base_pt: float,
    kind: str = "box",
) -> Tuple[plt.Figure, List[str]]:
    warnings: List[str] = []
    groups = spec["data"]["groups"]  # [{name, values}]
    fig, ax = plt.subplots(figsize=(width_in, height_in))
    fig.subplots_adjust(left=0.14, right=0.95, top=0.89, bottom=0.17)

    arrays = [[float(v) for v in g["values"]] for g in groups]
    labels = [f"{g['name']}\n(n={len(g['values'])})" for g in groups]
    positions = np.arange(1, len(groups) + 1)
    colors = list(palette.chart_series)

    if kind == "violin":
        parts = ax.violinplot(arrays, positions=positions, showmeans=False, showmedians=False, showextrema=False, widths=0.68)
        for i, pc in enumerate(parts["bodies"]):
            pc.set_facecolor(colors[i % len(colors)])
            pc.set_edgecolor("#1E293B")
            pc.set_alpha(0.35)
            pc.set_linewidth(1.1)
        bp = ax.boxplot(arrays, positions=positions, widths=0.16, patch_artist=True, showfliers=False, zorder=4)
        for box in bp["boxes"]:
            box.set(facecolor="#FFFFFF", edgecolor="#1E293B", linewidth=1.3)
        for med in bp["medians"]:
            med.set(color=palette.accent, linewidth=2.2)
    else:
        bp = ax.boxplot(arrays, positions=positions, widths=0.46, patch_artist=True, showfliers=False, zorder=3)
        for i, box in enumerate(bp["boxes"]):
            box.set(facecolor=colors[i % len(colors)], alpha=0.32, edgecolor=colors[i % len(colors)], linewidth=1.6)
        for med in bp["medians"]:
            med.set(color="#111827", linewidth=2.2)
        rng = np.random.default_rng(42)
        for i, arr in enumerate(arrays):
            if len(arr) <= 150:
                jitter = rng.uniform(-0.11, 0.11, size=len(arr))
                ax.scatter(
                    np.full(len(arr), positions[i]) + jitter, arr,
                    s=32, color=colors[i % len(colors)], alpha=0.72, edgecolor="#FFFFFF", linewidth=0.5, zorder=4,
                )

    all_vals = [v for arr in arrays for v in arr]
    v_min, v_max = min(all_vals), max(all_vals)
    v_span = max(1e-6, v_max - v_min)
    ax.set_ylim(v_min - 0.08 * v_span, v_max + (0.18 if spec.get("annotation") else 0.08) * v_span)

    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    ax.set_ylabel(spec.get("y_label", "Measurement"))
    ax.yaxis.grid(True, color="#E2E8F0", lw=0.8, zorder=0)
    _despine(ax)
    if spec.get("title"):
        ax.set_title(spec["title"], loc="left", pad=10, color=palette.dominant)
    if spec.get("annotation"):
        ax.text(
            0.98, 0.95, spec["annotation"], transform=ax.transAxes, ha="right", va="top",
            fontsize=base_pt * 0.84,
            bbox={"boxstyle": "round,pad=0.35", "facecolor": palette.surface_tint, "edgecolor": palette.rule_border},
        )
    return fig, warnings


# ---------------------------------------------------------------------------
# 10. PRISMA 2020 Flow Diagram (with Count-Closure Verification)
# ---------------------------------------------------------------------------

def render_prisma_diagram(
    spec: Dict[str, Any],
    width_in: float,
    height_in: float,
    palette: ColorPalette,
    base_pt: float,
) -> Tuple[plt.Figure, List[str]]:
    warnings: List[str] = []
    d = spec["data"]
    identified = int(d["records_identified"])
    removed_pre = int(d.get("records_removed_before_screening", 0))
    screened = int(d["records_screened"])
    excluded_screen = int(d["records_excluded_screening"])
    sought = int(d.get("reports_sought", screened - excluded_screen))
    not_retrieved = int(d.get("reports_not_retrieved", 0))
    assessed = int(d["reports_assessed"])
    excluded_ft = int(d["reports_excluded_fulltext"])
    included_rev = int(d["studies_included_review"])
    included_ma = d.get("studies_included_meta_analysis")

    # Arithmetic count-closure verification
    if identified - removed_pre != screened:
        warnings.append(
            f"PRISMA count check: identified ({identified}) - removed ({removed_pre}) != screened ({screened})."
        )
    if screened - excluded_screen != sought:
        warnings.append(
            f"PRISMA count check: screened ({screened}) - excluded ({excluded_screen}) != sought ({sought})."
        )
    if sought - not_retrieved != assessed:
        warnings.append(
            f"PRISMA count check: sought ({sought}) - not_retrieved ({not_retrieved}) != assessed ({assessed})."
        )
    if assessed - excluded_ft != included_rev:
        warnings.append(
            f"PRISMA count check: assessed ({assessed}) - excluded_fulltext ({excluded_ft}) != included ({included_rev})."
        )

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.96, bottom=0.02)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    fs = base_pt * 0.96

    def draw_box(x: float, y: float, w: float, h: float, text: str, bg: str = "#FFFFFF", border: str = "#334155", bold_first: bool = True) -> None:
        box = mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.2",
            facecolor=bg, edgecolor=border, linewidth=1.4,
        )
        ax.add_patch(box)
        lines = text.split("\n")
        if bold_first and len(lines) > 1:
            ax.text(x + 2.2, y + h - 2.4, lines[0], fontsize=fs, fontweight="bold", va="top", ha="left", color=palette.dominant)
            ax.text(x + 2.2, y + h - 6.8, "\n".join(lines[1:]), fontsize=fs * 0.88, va="top", ha="left", color=palette.body_ink, linespacing=1.24)
        else:
            ax.text(x + w / 2, y + h / 2, text, fontsize=fs, fontweight="bold" if bold_first else "normal", va="center", ha="center", color=palette.body_ink)

    def draw_phase_rail(y_bottom: float, h: float, label: str) -> None:
        rail = mpatches.FancyBboxPatch(
            (1.0, y_bottom), 5.2, h, boxstyle="round,pad=0.3,rounding_size=0.8",
            facecolor=palette.dominant, edgecolor="none",
        )
        ax.add_patch(rail)
        ax.text(3.6, y_bottom + h / 2, label, rotation=90, va="center", ha="center", color="#FFFFFF", fontweight="bold", fontsize=fs * 0.92)

    def arrow(x1: float, y1: float, x2: float, y2: float) -> None:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops={"arrowstyle": "-|>", "color": "#334155", "lw": 1.4, "mutation_scale": 13})

    # Phase rails
    draw_phase_rail(75, 20, "Identification")
    draw_phase_rail(24, 48, "Screening")
    draw_phase_rail(3, 18, "Included")

    db_detail = d.get("identification_detail", f"Databases & registers\n(n = {identified:,})")
    rem_detail = d.get("removed_detail", f"Duplicates / ineligible\n(n = {removed_pre:,})")
    draw_box(9, 76, 40, 18, f"Records identified\n{db_detail}", bg="#FFFFFF", border=palette.dominant)
    draw_box(56, 76, 41, 18, f"Removed pre-screening\n{rem_detail}", bg=palette.surface_tint, border=palette.rule_border)
    arrow(49, 85, 55.6, 85)

    arrow(29, 75.5, 29, 70.5)
    draw_box(9, 55, 40, 15, f"Records screened\nTitle & abstract (n = {screened:,})")
    draw_box(56, 55, 41, 15, f"Records excluded\n(n = {excluded_screen:,})", bg=palette.surface_tint, border=palette.rule_border)
    arrow(49, 62.5, 55.6, 62.5)

    arrow(29, 54.5, 29, 49.5)
    reasons = d.get("exclusion_reasons", {})
    reason_lines = [f"• {k} (n = {v})" for k, v in list(reasons.items())[:4]]
    reason_txt = "\n".join(reason_lines) if reason_lines else f"(n = {excluded_ft:,})"
    elig_note = f"Assessed (n = {assessed:,})" + (f"\nNot retrieved (n = {not_retrieved})" if not_retrieved else "")
    draw_box(9, 25, 40, 24, f"Full-text eligibility\n{elig_note}")
    draw_box(56, 25, 41, 24, f"Reports excluded (n = {excluded_ft:,})\n{reason_txt}", bg=palette.surface_tint, border=palette.rule_border)
    arrow(49, 37, 55.6, 37)

    arrow(29, 24.5, 29, 19.5)
    inc_txt = f"Studies included\nSystematic review: n = {included_rev:,}"
    if included_ma is not None:
        inc_txt += f"\nMeta-analysis: n = {int(included_ma):,}"
    draw_box(9, 3.5, 88, 15.5, inc_txt, bg=palette.surface_tint, border=palette.dominant)

    if spec.get("title"):
        ax.set_title(spec["title"], loc="left", pad=4, color=palette.dominant, fontsize=base_pt * 1.05)
    return fig, warnings


# ---------------------------------------------------------------------------
# 11 & 12. CONSORT Participant Diagram & General Cohort Flow Diagram
# ---------------------------------------------------------------------------

def render_consort_or_flow_diagram(
    spec: Dict[str, Any],
    width_in: float,
    height_in: float,
    palette: ColorPalette,
    base_pt: float,
    is_consort: bool = True,
) -> Tuple[plt.Figure, List[str]]:
    warnings: List[str] = []
    d = spec["data"]
    fig, ax = plt.subplots(figsize=(width_in, height_in))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.03)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fs = base_pt * 0.96

    def box(x: float, y: float, w: float, h: float, title: str, body: str, tint: bool = False, accent_border: bool = False) -> None:
        p = mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.2",
            facecolor=palette.surface_tint if tint else "#FFFFFF",
            edgecolor=palette.dominant if accent_border else palette.rule_border,
            linewidth=1.5 if accent_border else 1.2,
        )
        ax.add_patch(p)
        ax.text(x + 2.2, y + h - 2.5, title, fontsize=fs, fontweight="bold", va="top", color=palette.dominant)
        ax.text(x + 2.2, y + h - 7.4, body, fontsize=fs * 0.88, va="top", color=palette.body_ink, linespacing=1.24)

    def arrow(x1: float, y1: float, x2: float, y2: float) -> None:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops={"arrowstyle": "-|>", "color": "#334155", "lw": 1.4, "mutation_scale": 13})

    if is_consort and d.get("arms"):
        assessed = int(d["assessed"])
        excluded = int(d["excluded"])
        randomized = int(d["randomized"])
        if assessed - excluded != randomized:
            warnings.append(f"CONSORT count check: assessed ({assessed}) - excluded ({excluded}) != randomized ({randomized}).")

        box(6, 78, 42, 18, "Enrollment", f"Assessed for eligibility (N = {assessed:,})", accent_border=True)
        excl_detail = d.get("excluded_detail", f"Not meeting criteria / declined")
        box(55, 78, 41, 18, f"Excluded (n = {excluded:,})", excl_detail, tint=True)
        arrow(48.5, 87, 54.5, 87)

        arrow(27, 77.5, 27, 71)
        box(22, 56, 56, 14.5, "Randomized", f"Total allocated (N = {randomized:,})", tint=True, accent_border=True)

        arms = d["arms"][:2]
        arm_sum = sum(int(a["allocated"]) for a in arms)
        if arm_sum != randomized and len(d["arms"]) == 2:
            warnings.append(f"CONSORT count check: sum of arms ({arm_sum}) != randomized ({randomized}).")

        xs = [4, 52]
        for idx_a, arm in enumerate(arms):
            ax_x = xs[idx_a]
            arrow(50, 55.5, ax_x + 22, 48.5)
            box(ax_x, 31, 44, 17, f"Allocation: {arm['name']}", f"Allocated (n = {int(arm['allocated']):,})\n{arm.get('followup_note', '')}")
            arrow(ax_x + 22, 30.5, ax_x + 22, 23.5)
            box(ax_x, 5, 44, 18, f"Primary Analysis", f"Analyzed (n = {int(arm['analyzed']):,})\n{arm.get('analysis_note', '')}", tint=True, accent_border=True)
    else:
        steps = d["steps"]  # [{title, detail, excluded_title?, excluded_detail?}]
        n_s = len(steps)
        step_h = min(19.0, 82.0 / max(1, n_s) - 4.0)
        gap = (88.0 - n_s * step_h) / max(1, n_s - 1) if n_s > 1 else 0.0
        for s_i, st in enumerate(steps):
            y_top = 92.0 - s_i * (step_h + gap)
            y_bot = y_top - step_h
            has_ex = bool(st.get("excluded_title"))
            main_w = 48.0 if has_ex else 88.0
            box(6, y_bot, main_w, step_h, st["title"], st["detail"], tint=(s_i == n_s - 1), accent_border=(s_i in (0, n_s - 1)))
            if has_ex:
                arrow(54.5, y_bot + step_h / 2, 60.5, y_bot + step_h / 2)
                box(61, y_bot, 35, step_h, st["excluded_title"], st.get("excluded_detail", ""), tint=True)
            if s_i < n_s - 1:
                arrow(30, y_bot - 0.5, 30, y_bot - gap + 0.5)

    if spec.get("title"):
        ax.set_title(spec["title"], loc="left", pad=4, color=palette.dominant)
    return fig, warnings


# ---------------------------------------------------------------------------
# 13. Research / Clinical Workflow or Timeline Diagram
# ---------------------------------------------------------------------------

def render_workflow_diagram(
    spec: Dict[str, Any],
    width_in: float,
    height_in: float,
    palette: ColorPalette,
    base_pt: float,
) -> Tuple[plt.Figure, List[str]]:
    warnings: List[str] = []
    stages = spec["data"]["stages"]  # [{step, title, detail, metric?}]
    horizontal = width_in >= height_in * 1.35

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.88 if spec.get("title") else 0.96, bottom=0.04)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    n = len(stages)
    fs = base_pt * 1.04

    if horizontal:
        gap = 2.6
        box_w = (96.0 - (n - 1) * gap) / max(1, n)
        for i, st in enumerate(stages):
            x = 2.0 + i * (box_w + gap)
            card = mpatches.FancyBboxPatch(
                (x, 6), box_w, 86, boxstyle="round,pad=0.5,rounding_size=1.2",
                facecolor=palette.surface_tint if i == n - 1 else "#FFFFFF",
                edgecolor=palette.dominant if i in (0, n - 1) else palette.rule_border,
                linewidth=1.5 if i in (0, n - 1) else 1.2,
            )
            ax.add_patch(card)
            # Top accent bar
            hdr = mpatches.Rectangle((x, 76), box_w, 16, facecolor=palette.dominant if i < n - 1 else palette.accent, edgecolor="none")
            ax.add_patch(hdr)
            step_lbl = st.get("step", f"0{i+1}")
            ax.text(x + 1.4, 84, f"{step_lbl}  ·  {st['title']}", color="#FFFFFF", fontweight="bold", fontsize=fs * 0.96, va="center")
            wrapped = "\n".join(textwrap.wrap(st["detail"], width=max(24, int(box_w * 1.55))))
            ax.text(x + 1.4, 69, wrapped, color=palette.body_ink, fontsize=fs * 0.92, va="top", linespacing=1.24)
            if st.get("metric"):
                ax.text(x + 1.4, 13, st["metric"], color=palette.dominant, fontweight="bold", fontsize=fs * 1.00, va="bottom")
            if i < n - 1:
                ax.annotate(
                    "", xy=(x + box_w + gap - 0.25, 49), xytext=(x + box_w + 0.25, 49),
                    arrowprops={"arrowstyle": "-|>", "color": palette.dominant, "lw": 2.0, "mutation_scale": 16},
                )
    else:
        gap = 3.5
        box_h = (92.0 - (n - 1) * gap) / max(1, n)
        for i, st in enumerate(stages):
            y = 96.0 - (i + 1) * box_h - i * gap
            card = mpatches.FancyBboxPatch(
                (4, y), 92, box_h, boxstyle="round,pad=0.5,rounding_size=1.2",
                facecolor=palette.surface_tint if i == n - 1 else "#FFFFFF",
                edgecolor=palette.dominant if i in (0, n - 1) else palette.rule_border,
                linewidth=1.4,
            )
            ax.add_patch(card)
            step_lbl = st.get("step", f"0{i+1}")
            ax.text(7, y + box_h - 3.2, f"{step_lbl} — {st['title']}", color=palette.dominant, fontweight="bold", fontsize=fs, va="top")
            ax.text(7, y + box_h - 8.5, st["detail"], color=palette.body_ink, fontsize=fs * 0.88, va="top")
            if i < n - 1:
                ax.annotate(
                    "", xy=(50, y - gap + 0.6), xytext=(50, y - 0.6),
                    arrowprops={"arrowstyle": "-|>", "color": palette.dominant, "lw": 1.6, "mutation_scale": 14},
                )

    if spec.get("title"):
        ax.set_title(spec["title"], loc="left", pad=4, color=palette.dominant)
    return fig, warnings


# ---------------------------------------------------------------------------
# 14 & 15. Booktabs Study Characteristics & Statistical Comparison Tables
# ---------------------------------------------------------------------------

def render_booktabs_table_figure(
    spec: Dict[str, Any],
    width_in: float,
    height_in: float,
    palette: ColorPalette,
    base_pt: float,
) -> Tuple[plt.Figure, List[str]]:
    warnings: List[str] = []
    headers = [str(h) for h in spec["data"]["headers"]]
    rows = [[str(c) for c in r] for r in spec["data"]["rows"]]

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.88 if spec.get("title") else 0.96, bottom=0.04)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    n_cols = len(headers)
    n_rows = len(rows)
    col_weights = spec["data"].get("col_weights") or ([2.0] + [1.0] * (n_cols - 1))
    w_sum = sum(col_weights)
    col_widths = [96.0 * (w / w_sum) for w in col_weights]
    col_xs = [2.0 + sum(col_widths[:i]) for i in range(n_cols)]

    top_y = 94.0
    row_h = min(13.0, 86.0 / (n_rows + 1.3))
    fs = base_pt * 0.78

    # Top heavy booktabs rule
    ax.plot([2.0, 98.0], [top_y, top_y], color=palette.dominant, lw=2.0)
    hdr_y = top_y - row_h * 0.62
    for c_i, h_txt in enumerate(headers):
        ha = "left" if c_i == 0 else "right"
        tx = col_xs[c_i] + 1.0 if c_i == 0 else col_xs[c_i] + col_widths[c_i] - 1.0
        ax.text(tx, hdr_y, h_txt, ha=ha, va="center", fontweight="bold", fontsize=fs, color=palette.dominant)

    # Mid rule under header
    mid_y = top_y - row_h * 1.15
    ax.plot([2.0, 98.0], [mid_y, mid_y], color=palette.dominant, lw=1.2)

    for r_i, row in enumerate(rows):
        ry_top = mid_y - r_i * row_h
        ry_mid = ry_top - row_h * 0.52
        if r_i % 2 == 1:
            tint = mpatches.Rectangle((2.0, ry_top - row_h), 96.0, row_h, facecolor=palette.surface_tint, edgecolor="none", alpha=0.65)
            ax.add_patch(tint)
        for c_i, cell in enumerate(row):
            ha = "left" if c_i == 0 else "right"
            tx = col_xs[c_i] + 1.0 if c_i == 0 else col_xs[c_i] + col_widths[c_i] - 1.0
            ax.text(tx, ry_mid, cell, ha=ha, va="center", fontsize=fs * 0.94, color=palette.body_ink)

    bot_y = mid_y - n_rows * row_h
    ax.plot([2.0, 98.0], [bot_y, bot_y], color=palette.dominant, lw=2.0)

    if spec.get("title"):
        ax.set_title(spec["title"], loc="left", pad=4, color=palette.dominant)
    return fig, warnings


# ---------------------------------------------------------------------------
# Public Dispatcher & CLI
# ---------------------------------------------------------------------------

SUPPORTED_CHART_TYPES = {
    "bar_chart",
    "forest_plot",
    "funnel_plot",
    "kaplan_meier",
    "roc_curve",
    "confusion_matrix",
    "scatter_plot",
    "box_plot",
    "violin_plot",
    "prisma_diagram",
    "consort_diagram",
    "flow_diagram",
    "workflow_diagram",
    "characteristics_table",
    "statistical_table",
}


def generate_scientific_chart(
    spec: Dict[str, Any],
    out_stem: pathlib.Path,
    width_in: float = 12.0,
    height_in: float = 7.5,
    palette_id: str = "academic_navy",
    palette_overrides: Optional[Dict[str, str]] = None,
    font_family: str = "IBM Plex Sans",
    base_pt: float = 18.0,
    dpi: int = 300,
    formats: Tuple[str, ...] = ("svg", "pdf", "png"),
) -> Dict[str, Any]:
    """Generate a single scientific chart at exact physical poster target dimensions."""
    ctype = spec.get("chart_type", "").strip().lower()
    if ctype not in SUPPORTED_CHART_TYPES:
        raise ValueError(f"Unsupported chart_type '{ctype}'. Must be one of {sorted(SUPPORTED_CHART_TYPES)}")

    palette = resolve_palette(palette_id, palette_overrides)
    _configure_mpl_style(font_family=font_family, base_pt=base_pt)

    if ctype == "bar_chart":
        fig, warnings = render_bar_chart(spec, width_in, height_in, palette, base_pt)
    elif ctype == "forest_plot":
        fig, warnings = render_forest_plot(spec, width_in, height_in, palette, base_pt)
    elif ctype == "funnel_plot":
        fig, warnings = render_funnel_plot(spec, width_in, height_in, palette, base_pt)
    elif ctype == "kaplan_meier":
        fig, warnings = render_kaplan_meier(spec, width_in, height_in, palette, base_pt)
    elif ctype == "roc_curve":
        fig, warnings = render_roc_curve(spec, width_in, height_in, palette, base_pt)
    elif ctype == "confusion_matrix":
        fig, warnings = render_confusion_matrix(spec, width_in, height_in, palette, base_pt)
    elif ctype == "scatter_plot":
        fig, warnings = render_scatter_plot(spec, width_in, height_in, palette, base_pt)
    elif ctype == "box_plot":
        fig, warnings = render_distribution_plot(spec, width_in, height_in, palette, base_pt, kind="box")
    elif ctype == "violin_plot":
        fig, warnings = render_distribution_plot(spec, width_in, height_in, palette, base_pt, kind="violin")
    elif ctype == "prisma_diagram":
        fig, warnings = render_prisma_diagram(spec, width_in, height_in, palette, base_pt)
    elif ctype == "consort_diagram":
        fig, warnings = render_consort_or_flow_diagram(spec, width_in, height_in, palette, base_pt, is_consort=True)
    elif ctype == "flow_diagram":
        fig, warnings = render_consort_or_flow_diagram(spec, width_in, height_in, palette, base_pt, is_consort=False)
    elif ctype == "workflow_diagram":
        fig, warnings = render_workflow_diagram(spec, width_in, height_in, palette, base_pt)
    elif ctype in ("characteristics_table", "statistical_table"):
        fig, warnings = render_booktabs_table_figure(spec, width_in, height_in, palette, base_pt)
    else:
        raise ValueError(f"Unhandled chart_type '{ctype}'")

    files = _save_outputs(fig, out_stem, dpi=dpi, formats=formats)
    return {
        "chart_id": spec.get("id", out_stem.name),
        "chart_type": ctype,
        "width_in": width_in,
        "height_in": height_in,
        "dpi": dpi,
        "files": files,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate vector & 300-DPI scientific charts for research posters.")
    parser.add_argument("--spec", required=True, help="Path to JSON file containing a chart spec or {'charts': [...]}")
    parser.add_argument("--output-dir", required=True, help="Output directory for generated SVG/PDF/PNG charts")
    parser.add_argument("--palette", default="academic_navy", help="Color palette ID")
    parser.add_argument("--font", default="IBM Plex Sans", help="Font family name")
    parser.add_argument("--dpi", type=int, default=300, help="Raster PNG export DPI (default: 300)")
    args = parser.parse_args()

    payload = json.loads(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    charts = payload["charts"] if isinstance(payload, dict) and "charts" in payload else ([payload] if isinstance(payload, dict) else payload)

    out_dir = pathlib.Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for idx, ch in enumerate(charts):
        cid = ch.get("id", f"figure_{idx+1}")
        res = generate_scientific_chart(
            spec=ch,
            out_stem=out_dir / cid,
            width_in=float(ch.get("width_in", 13.0)),
            height_in=float(ch.get("height_in", 8.0)),
            palette_id=args.palette,
            font_family=args.font,
            base_pt=float(ch.get("base_pt", 18.0)),
            dpi=args.dpi,
        )
        results.append(res)

    manifest_path = out_dir / "charts_manifest.json"
    manifest_path.write_text(json.dumps({"charts": results}, indent=2), encoding="utf-8")
    print(f"Generated {len(results)} chart(s) -> {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
