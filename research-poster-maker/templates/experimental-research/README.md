# Experimental, Translational & Basic Science Poster (`experimental-research`)

Engineered for laboratory, preclinical, omics, and engineering research (Nature Conferences / Cell Symposia aesthetic). Emphasizes experimental workflow, multi-panel quantitative distributions (box/violin/scatter/ROC), and mechanistic conclusions.

## Default Design Tokens

- **Reporting Framework:** ARRIVE / Nature Reporting Summary
- **Default Dimensions:** `a0_landscape` (configurable to any preset or custom board size)
- **Landscape Layout Recipe:** `asymmetric_grid`
- **Portrait Layout Recipe:** `two_column_editorial`
- **Default Color Palette:** `charcoal_ivory`
- **Default Font Pairing:** `swiss_scientific`
- **Masthead Architecture:** `split_accent_header`
- **Target Body Word Budget:** ~480 words

## Recommended Scientific Visualizations

`workflow_diagram`, `violin_plot`, `box_plot`, `scatter_plot`, `roc_curve`, `confusion_matrix`, `bar_chart`

## Section Blueprint

- **Biological Rationale & Hypothesis** (`background`, style: `editorial_rule`, essential)
- **Experimental Architecture & Assays** (`methods`, style: `editorial_rule`, essential)
- **Experimental Pipeline** (`workflow`, style: `figure_well`, optional)
- **Key Experimental Finding** (`primary_outcome`, style: `focal_callout`, essential)
- **Quantitative Assay Results** (`primary_figure`, style: `figure_well`, essential)
- **Validation & Dose/Model Performance** (`secondary_figure`, style: `figure_well`, optional)
- **Reproducibility Controls & Limitations** (`limitations`, style: `editorial_rule`, essential)
- **Mechanistic & Translational Conclusions** (`conclusion`, style: `focal_callout_subtle`, essential)
- **Data Availability, Grants & References** (`references_funding`, style: `colophon`, optional)

## Usage

```bash
python scripts/generate_poster.py \
  --spec poster_spec.json \
  --template experimental-research \
  --output-dir output/
```
