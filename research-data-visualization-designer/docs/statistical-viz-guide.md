# Statistical Data Visualization & Reproducibility Guide

## 1. Choosing the Right Statistical Encoding
| Data Structure | Recommended Panel | Anti-Pattern Avoided |
|---|---|---|
| Continuous outcome across 2–5 groups | `violin_box_jitter` (Violin density + IQR box + raw observations) | Bare bar chart ("dynamite plunger") hiding bimodality/skew |
| Continuous predictor vs continuous outcome | `regression_ci` (Scatter + OLS line + analytical 95% CI band + $r, P$) | Unannotated trendline without uncertainty |
| Multivariate continuous panel (`3–8` variables) | `corr_heatmap` (Diverging blue-orange `[-1, +1]` with cell $r$ values) | Rainbow/jet heatmap with unlabelled scale |
| R / Python / SPSS multivariable regression table | `coef_forest` (Adjusted $\beta$ / OR / HR with 95% CIs & null line) | Dense raw SPSS text printout screenshot |

## 2. Reproducibility Artifact Standard
Every output directory includes:
- `dataviz_figure.svg`, `dataviz_figure.pdf` (Type 42 TrueType), `dataviz_figure.png` (`350 DPI`)
- `reproduce_figure.py` (standalone runnable Python script regenerating the figure from the CSV/XLSX)
- `reproducibility_manifest.json` (`SHA-256` dataset checksum + exact computed statistics)
