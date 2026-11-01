# Epidemiology, Surveillance & Public Health Cohort Poster (`epidemiology`)

Tailored for population-scale cohorts, infectious/chronic disease surveillance, and environmental epidemiology. Highlights person-years follow-up, standardized incidence trends, multivariable adjusted rate/hazard ratios, and policy implications.

## Default Design Tokens

- **Reporting Framework:** STROBE / RECORD
- **Default Dimensions:** `48x36` (configurable to any preset or custom board size)
- **Landscape Layout Recipe:** `timeline_flow`
- **Portrait Layout Recipe:** `three_column_classic`
- **Default Color Palette:** `forest_cream`
- **Default Font Pairing:** `classic_symposium`
- **Masthead Architecture:** `solid_banner`
- **Target Body Word Budget:** ~520 words

## Recommended Scientific Visualizations

`workflow_diagram`, `scatter_plot`, `bar_chart`, `forest_plot`, `flow_diagram`, `statistical_table`

## Section Blueprint

- **Public Health Burden & Objective** (`background`, style: `editorial_rule`, essential)
- **Cohort Ascertainment & Statistical Modeling** (`methods`, style: `editorial_rule`, essential)
- **Population-Level Risk Findings** (`primary_outcome`, style: `focal_callout`, essential)
- **Incidence & Adjusted Risk Estimates** (`primary_figure`, style: `figure_well`, essential)
- **Multivariable Stratified Models** (`statistical_table`, style: `booktabs_table`, optional)
- **Bias Mitigation & Study Limitations** (`limitations`, style: `editorial_rule`, essential)
- **Public Health & Policy Implications** (`conclusion`, style: `focal_callout_subtle`, essential)
- **Surveillance Sources, Funding & References** (`references_funding`, style: `colophon`, optional)

## Usage

```bash
python scripts/generate_poster.py \
  --spec poster_spec.json \
  --template epidemiology \
  --output-dir output/
```
