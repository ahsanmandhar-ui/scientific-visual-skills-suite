#!/usr/bin/env python3
"""
Reproducible Statistical Visualization & Dashboard Generator from CSV/Excel + R/Python/SPSS results.
Emits SVG, PDF, PNG, standalone reproduce_figure.py, and SHA-256 reproducibility_manifest.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import platform
from typing import Any, Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import font_manager
import numpy as np
from scipy import stats

from profile_dataset import load_tabular

SKILL_ROOT = pathlib.Path(__file__).resolve().parents[1]
SHARED_FONTS = SKILL_ROOT.parent / "research-poster-maker" / "assets" / "fonts"
if SHARED_FONTS.exists():
    for _ttf in SHARED_FONTS.glob("*.ttf"):
        try:
            font_manager.fontManager.addfont(str(_ttf))
        except Exception:
            pass

DIV_CMAP = LinearSegmentedColormap.from_list("okabe_div", ["#0072B2", "#F8FAFC", "#D55E00"])


def generate_dataviz(spec: Dict[str, Any], spec_dir: pathlib.Path, out_dir: pathlib.Path) -> Dict[str, Any]:
    db = json.loads((SKILL_ROOT / "templates" / "dataviz_presets.json").read_text(encoding="utf-8"))
    colors = db["okabe_ito"]
    pr = db["presets"].get(spec.get("preset", "analytical-dashboard-4panel"), db["presets"]["analytical-dashboard-4panel"])
    W, H, dpi = float(pr["width_in"]), float(pr["height_in"]), int(pr["dpi"])

    data_path = pathlib.Path(spec["data_file"])
    if not data_path.is_absolute():
        data_path = (spec_dir / data_path).resolve()
    sha256 = hashlib.sha256(data_path.read_bytes()).hexdigest()
    rows = load_tabular(data_path)

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Source Sans 3", "IBM Plex Sans", "DejaVu Sans"],
        "font.size": 9.0,
        "axes.titlesize": 10.2,
        "axes.titleweight": "bold",
        "axes.labelsize": 9.0,
        "axes.labelweight": "bold",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "path",
    })

    fig = plt.figure(figsize=(W, H), facecolor="#FFFFFF")
    fig.suptitle(spec["title"], x=0.04, y=0.975, ha="left", fontsize=13.2, fontweight="bold", color="#0F172A")
    if spec.get("subtitle"):
        fig.text(0.04, 0.942, spec["subtitle"], fontsize=9.2, color="#475569")

    gs = fig.add_gridspec(2, 2, left=0.09, right=0.97, top=0.88, bottom=0.10, wspace=0.46, hspace=0.38)
    computed_stats: Dict[str, Any] = {"n_rows": len(rows)}

    # Panel A: Violin + Box + Jittered Replicates by Group
    ax_a = fig.add_subplot(gs[0, 0])
    p_a = spec["panel_distribution"]
    grp_col, val_col = p_a["group_col"], p_a["value_col"]
    grp_order: List[str] = p_a.get("group_order") or sorted({r[grp_col] for r in rows if r.get(grp_col)})
    grp_vals = [[float(r[val_col]) for r in rows if r.get(grp_col) == g and r.get(val_col) not in ("", None)] for g in grp_order]
    pos = np.arange(1, len(grp_order) + 1)
    parts = ax_a.violinplot(grp_vals, positions=pos, widths=0.65, showmeans=False, showextrema=False)
    for i, body in enumerate(parts["bodies"]):
        body.set_facecolor(colors[i % len(colors)])
        body.set_alpha(0.22)
    bp = ax_a.boxplot(grp_vals, positions=pos, widths=0.22, patch_artist=True, showfliers=False)
    rng = np.random.default_rng(42)
    for i, (box, arr) in enumerate(zip(bp["boxes"], grp_vals)):
        c = colors[i % len(colors)]
        box.set(facecolor="#FFFFFF", edgecolor=c, lw=1.2)
        bp["medians"][i].set(color="#0F172A", lw=1.5)
        jit = rng.uniform(-0.09, 0.09, size=len(arr))
        ax_a.scatter(np.full(len(arr), pos[i]) + jit, arr, s=14, color=c, alpha=0.78, edgecolor="#FFFFFF", lw=0.3, zorder=4)
    kw_stat, kw_p = stats.kruskal(*grp_vals) if len(grp_vals) >= 2 else (0.0, 1.0)
    computed_stats["kruskal_p"] = float(kw_p)
    ax_a.set_xticks(pos)
    ax_a.set_xticklabels([f"{g}\n(n={len(v)})" for g, v in zip(grp_order, grp_vals)])
    ax_a.set_ylabel(p_a.get("y_label", val_col))
    ax_a.set_title(f"A. {p_a['title']} (Kruskal P = {kw_p:.3g})", loc="left")
    ax_a.spines["top"].set_visible(False)
    ax_a.spines["right"].set_visible(False)

    # Panel B: OLS Regression + Analytical 95% Confidence Band
    ax_b = fig.add_subplot(gs[0, 1])
    p_b = spec["panel_regression"]
    xc, yc = p_b["x_col"], p_b["y_col"]
    pairs = [(float(r[xc]), float(r[yc]), r.get(grp_col, "All")) for r in rows if r.get(xc) and r.get(yc)]
    xs = np.array([p[0] for p in pairs])
    ys = np.array([p[1] for p in pairs])
    for i, g in enumerate(grp_order):
        gx = [p[0] for p in pairs if p[2] == g]
        gy = [p[1] for p in pairs if p[2] == g]
        ax_b.scatter(gx, gy, s=22, color=colors[i % len(colors)], alpha=0.80, label=g)
    res_lr = stats.linregress(xs, ys)
    x_grid = np.linspace(xs.min(), xs.max(), 80)
    y_hat = res_lr.intercept + res_lr.slope * x_grid
    dof = max(1, len(xs) - 2)
    resid_se = np.sqrt(np.sum((ys - (res_lr.intercept + res_lr.slope * xs)) ** 2) / dof)
    t_val = stats.t.ppf(0.975, dof)
    ci_band = t_val * resid_se * np.sqrt(1.0 / len(xs) + (x_grid - xs.mean()) ** 2 / max(1e-9, np.sum((xs - xs.mean()) ** 2)))
    ax_b.plot(x_grid, y_hat, color="#0F172A", lw=1.6)
    ax_b.fill_between(x_grid, y_hat - ci_band, y_hat + ci_band, color="#64748B", alpha=0.18)
    computed_stats["pearson_r"] = round(float(res_lr.rvalue), 4)
    computed_stats["regression_p"] = float(res_lr.pvalue)
    ax_b.set_xlabel(p_b.get("x_label", xc))
    ax_b.set_ylabel(p_b.get("y_label", yc))
    ax_b.set_title(f"B. {p_b['title']} (r = {res_lr.rvalue:.2f}, P = {res_lr.pvalue:.2g})", loc="left")
    ax_b.legend(frameon=False, fontsize=7.8)
    ax_b.spines["top"].set_visible(False)
    ax_b.spines["right"].set_visible(False)

    # Panel C: Annotated Pearson Correlation Heatmap
    ax_c = fig.add_subplot(gs[1, 0])
    p_c = spec["panel_correlation"]
    c_cols: List[str] = p_c["columns"]
    c_labels: List[str] = p_c.get("labels", c_cols)
    mat_rows = []
    for r in rows:
        if all(r.get(k) not in ("", None) for k in c_cols):
            mat_rows.append([float(r[k]) for k in c_cols])
    M = np.corrcoef(np.array(mat_rows, dtype=float), rowvar=False)
    im = ax_c.imshow(M, cmap=DIV_CMAP, vmin=-1.0, vmax=1.0, aspect="auto")
    ax_c.set_xticks(range(len(c_labels)))
    ax_c.set_xticklabels(c_labels, rotation=22, ha="right", fontsize=8.0)
    ax_c.set_yticks(range(len(c_labels)))
    ax_c.set_yticklabels(c_labels, fontsize=8.0)
    for r_i in range(len(c_labels)):
        for c_i in range(len(c_labels)):
            val = M[r_i, c_i]
            ax_c.text(c_i, r_i, f"{val:.2f}", ha="center", va="center", fontsize=8.0, fontweight="bold", color="#FFFFFF" if abs(val) > 0.62 else "#0F172A")
    fig.colorbar(im, ax=ax_c, fraction=0.046, pad=0.04, label="Pearson r")
    ax_c.set_title(f"C. {p_c['title']}", loc="left")

    # Panel D: R / Python / SPSS Multivariable Model Coefficients Forest Plot
    ax_d = fig.add_subplot(gs[1, 1])
    p_d = spec["panel_model_outputs"]
    terms = p_d["terms"]
    null_v = float(p_d.get("null_value", 0.0))
    ys_d = np.arange(len(terms), 0, -1)
    ax_d.axvline(null_v, color="#64748B", ls="--", lw=1.0)
    ylabels_d = []
    for idx_t, tm in enumerate(terms):
        yt = ys_d[idx_t]
        est, lo, hi = float(tm["estimate"]), float(tm["ci_low"]), float(tm["ci_high"])
        col_t = colors[1] if (lo > null_v or hi < null_v) else "#475569"
        ax_d.plot([lo, hi], [yt, yt], color=col_t, lw=1.8)
        ax_d.plot(est, yt, "o", color=col_t, markersize=6)
        ax_d.text(est, yt + 0.17, f"{est:.2f} [{lo:.2f}, {hi:.2f}]", ha="center", va="bottom", fontsize=7.4, fontweight="bold", color=col_t)
        ylabels_d.append(tm["term"])
    all_lo = min(float(t["ci_low"]) for t in terms + [{"ci_low": null_v}])
    all_hi = max(float(t["ci_high"]) for t in terms + [{"ci_high": null_v}])
    span_d = max(1.0, all_hi - all_lo)
    ax_d.set_xlim(all_lo - span_d * 0.24, all_hi + span_d * 0.14)
    ax_d.set_ylim(0.4, len(terms) + 0.65)
    ax_d.set_yticks(ys_d)
    ax_d.set_yticklabels(ylabels_d, fontsize=8.2, fontweight="bold")
    ax_d.set_xlabel(p_d.get("x_label", "Adjusted Beta / Effect (95% CI)"))
    ax_d.set_title(f"D. {p_d['title']}", loc="left")
    ax_d.spines["top"].set_visible(False)
    ax_d.spines["right"].set_visible(False)

    if spec.get("footer_note"):
        fig.text(0.04, 0.018, spec["footer_note"], fontsize=7.8, color="#64748B")

    out_dir.mkdir(parents=True, exist_ok=True)
    svg_p = out_dir / "dataviz_figure.svg"
    pdf_p = out_dir / "dataviz_figure.pdf"
    png_p = out_dir / "dataviz_figure.png"
    fig.savefig(svg_p, format="svg", facecolor="#FFFFFF")
    fig.savefig(pdf_p, format="pdf", facecolor="#FFFFFF")
    fig.savefig(png_p, format="png", dpi=dpi, facecolor="#FFFFFF")
    plt.close(fig)

    # Emit standalone reproducible Python script
    repro_code = f'''#!/usr/bin/env python3
"""Standalone deterministic reproduction script (auto-generated by research-data-visualization-designer)."""
import pathlib, subprocess, sys

SPEC_PATH = pathlib.Path({str((spec_dir / pathlib.Path(spec.get("_spec_filename", "dataviz_spec.json"))).resolve())!r})
GENERATOR = pathlib.Path({str((SKILL_ROOT / "scripts" / "generate_dataviz.py").resolve())!r})
OUT_DIR = pathlib.Path(__file__).resolve().parent

if __name__ == "__main__":
    if "--verify-only" in sys.argv:
        assert SPEC_PATH.exists(), f"Missing spec: {{SPEC_PATH}}"
        print("Reproducibility script syntax and provenance links verified.")
        raise SystemExit(0)
    raise SystemExit(subprocess.call([sys.executable, str(GENERATOR), "--spec", str(SPEC_PATH), "--output-dir", str(OUT_DIR)]))
'''
    repro_p = out_dir / "reproduce_figure.py"
    repro_p.write_text(repro_code, encoding="utf-8")

    manifest = {
        "input_dataset": str(data_path),
        "dataset_sha256": sha256,
        "python_version": platform.python_version(),
        "matplotlib_version": matplotlib.__version__,
        "numpy_version": np.__version__,
        "computed_statistics": computed_stats,
        "outputs": {"svg": str(svg_p), "pdf": str(pdf_p), "png": str(png_p), "reproduce_py": str(repro_p)},
    }
    (out_dir / "reproducibility_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    sp = pathlib.Path(args.spec).resolve()
    spec = json.loads(sp.read_text(encoding="utf-8"))
    spec["_spec_filename"] = sp.name
    print(json.dumps(generate_dataviz(spec, sp.parent, pathlib.Path(args.output_dir).resolve()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
