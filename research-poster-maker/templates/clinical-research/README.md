# Clinical Trial & Observational Cohort Poster (`clinical-research`)

High-clarity clinical research template engineered for ACC, ASN, AHA, BMJ, and hospital clinical congresses. Integrates patient flow, primary clinical endpoint callout, survival/outcome visualization, baseline/subgroup tables, and bedside implications.

## Default Design Tokens

- **Reporting Framework:** CONSORT / STROBE / STARD
- **Default Dimensions:** `48x36` (configurable to any preset or custom board size)
- **Landscape Layout Recipe:** `clinical_workflow`
- **Portrait Layout Recipe:** `two_column_editorial`
- **Default Color Palette:** `academic_navy`
- **Default Font Pairing:** `clinical_precision`
- **Masthead Architecture:** `solid_banner`
- **Target Body Word Budget:** ~520 words

## Recommended Scientific Visualizations

`kaplan_meier`, `consort_diagram`, `flow_diagram`, `bar_chart`, `roc_curve`, `characteristics_table`, `statistical_table`

## Section Blueprint

- **Clinical Background & Rationale** (`background`, style: `editorial_rule`, essential)
- **Study Objectives** (`objectives`, style: `editorial_rule`, essential)
- **Study Design, Population & Methods** (`methods`, style: `editorial_rule`, essential)
- **Primary Clinical Endpoint** (`primary_outcome`, style: `focal_callout`, essential)
- **Primary Outcome Visualization** (`primary_figure`, style: `figure_well`, essential)
- **Baseline Characteristics & Subgroup Outcomes** (`secondary_table_or_figure`, style: `booktabs_table`, optional)
- **Secondary & Safety Outcomes** (`secondary_outcomes`, style: `editorial_rule`, optional)
- **Strengths & Limitations** (`limitations`, style: `editorial_rule`, essential)
- **Clinical Conclusions & Practice Implications** (`conclusion`, style: `focal_callout_subtle`, essential)
- **References, Registration & Disclosures** (`references_funding`, style: `colophon`, optional)

## Usage

```bash
python scripts/generate_poster.py \
  --spec poster_spec.json \
  --template clinical-research \
  --output-dir output/
```
