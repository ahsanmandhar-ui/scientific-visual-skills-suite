# Quantitative Meta-Analysis & Evidence Synthesis Poster (`meta-analysis`)

Designed around quantitative pooled effect estimation. Features a wide central stage for multi-study forest plots with inverse-variance weights, pooled diamonds, prediction intervals, I-squared/tau-squared heterogeneity metrics, and publication-bias funnel plots.

## Default Design Tokens

- **Reporting Framework:** PRISMA 2020 / MOOSE
- **Default Dimensions:** `48x36` (configurable to any preset or custom board size)
- **Landscape Layout Recipe:** `systematic_review_prisma`
- **Portrait Layout Recipe:** `central_visual`
- **Default Color Palette:** `burgundy_offwhite`
- **Default Font Pairing:** `editorial_modern`
- **Masthead Architecture:** `solid_banner`
- **Target Body Word Budget:** ~500 words

## Recommended Scientific Visualizations

`forest_plot`, `funnel_plot`, `prisma_diagram`, `statistical_table`

## Section Blueprint

- **Clinical Context & Evidence Gap** (`background`, style: `editorial_rule`, essential)
- **Data Sources & Quantitative Synthesis** (`methods`, style: `editorial_rule`, essential)
- **Study Identification & Selection** (`prisma_or_summary`, style: `figure_well`, optional)
- **Pooled Effect Estimate & Heterogeneity** (`primary_outcome`, style: `focal_callout`, essential)
- **Random-Effects Forest Plot** (`forest_plot`, style: `figure_well`, essential)
- **Small-Study Effects & Subgroup Sensitivity** (`funnel_or_subgroup`, style: `figure_well`, optional)
- **Heterogeneity & Methodological Limitations** (`limitations`, style: `editorial_rule`, essential)
- **Summary of Quantitative Evidence** (`conclusion`, style: `focal_callout_subtle`, essential)
- **Protocol Registration, Funding & Key Citations** (`references_funding`, style: `colophon`, optional)

## Usage

```bash
python scripts/generate_poster.py \
  --spec poster_spec.json \
  --template meta-analysis \
  --output-dir output/
```
