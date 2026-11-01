---
name: research-data-visualization-designer
description: Converts CSV/Excel datasets and R, Python, or SPSS statistical outputs into publication-quality statistical visualizations and multi-panel analytical dashboards, emitting standalone reproducible Python figure scripts and SHA-256 data provenance manifests.
license: MIT
metadata:
  version: "1.0.0"
  domain: "statistical-visualization"
---

# Research Data Visualization Designer Skill

Transform raw tabular research datasets (`.csv`, `.xlsx`) and statistical model outputs (`R broom/tidy`, `Python statsmodels/scipy`, `SPSS ANOVA/regression exports`) into **reproducible, publication-grade statistical figures and analytical dashboards**.

All paths below are relative to `research-data-visualization-designer/`.

---

## Core Statistical & Reproducibility Rules

1. **Deterministic Computation, Zero Hallucinated Numbers:** Compute sample sizes, missingness, group summaries, regressions, and correlation matrices directly from the input `.csv` / `.xlsx` or supplied model table. Never invent p-values or drop outliers silently.
2. **Mandatory Code Reproducibility:** Every run emits a standalone, dependency-minimal `reproduce_figure.py` script plus `reproducibility_manifest.json` recording the input dataset's `SHA-256` digest and exact software versions.
3. **Perceptually Uniform & Colorblind-Safe Encodings:** Use Okabe-Ito categorical palettes and `cividis` / diverging blue-vermilion colormaps (never `jet` or rainbow).

---

## Workflow

1. **Profile Dataset:** Inspect columns, types, missingness, and summary distributions:
   ```bash
   python scripts/profile_dataset.py --data <path/to/dataset.csv_or_xlsx> --out <work_dir>/dataset_profile.json
   ```
2. **Generate Statistical Figure / Dashboard + Reproduction Script:**
   ```bash
   python scripts/generate_dataviz.py \
     --spec <work_dir>/dataviz_spec.json \
     --output-dir <work_dir>/output
   ```
3. **Validate & Verify Standalone Script Execution:**
   ```bash
   python scripts/validate_dataviz.py \
     --output-dir <work_dir>/output \
     --spec <work_dir>/dataviz_spec.json
   ```
4. Visually inspect `<work_dir>/output/dataviz_figure.png` to confirm distribution clarity, axis labels, and correlation matrix legibility.
