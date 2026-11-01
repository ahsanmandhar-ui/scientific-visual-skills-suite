# PRISMA 2020 Systematic Review Poster (`systematic-review`)

Structured evidence-synthesis poster adhering to PRISMA 2020 reporting items. Pairs PICOS eligibility and verified PRISMA 2020 study selection flow with structured study characteristics, Risk of Bias synthesis, and GRADE-calibrated conclusions.

## Default Design Tokens

- **Reporting Framework:** PRISMA 2020
- **Default Dimensions:** `a0_portrait` (configurable to any preset or custom board size)
- **Landscape Layout Recipe:** `systematic_review_prisma`
- **Portrait Layout Recipe:** `systematic_review_prisma`
- **Default Color Palette:** `deep_teal`
- **Default Font Pairing:** `editorial_modern`
- **Masthead Architecture:** `solid_banner`
- **Target Body Word Budget:** ~550 words

## Recommended Scientific Visualizations

`prisma_diagram`, `characteristics_table`, `bar_chart`, `statistical_table`

## Section Blueprint

- **Rationale & Review Question (PICOS)** (`background`, style: `editorial_rule`, essential)
- **Search Strategy, Eligibility & Quality Appraisal** (`methods`, style: `editorial_rule`, essential)
- **PRISMA 2020 Study Selection** (`prisma_flow`, style: `figure_well`, essential)
- **Evidence Synthesis Highlights** (`primary_outcome`, style: `focal_callout`, essential)
- **Characteristics of Included Studies** (`characteristics_table`, style: `booktabs_table`, essential)
- **Risk of Bias & Outcome Directionality** (`secondary_figure`, style: `figure_well`, optional)
- **Certainty of Evidence & Review Limitations** (`limitations`, style: `editorial_rule`, essential)
- **Conclusions & Research Priorities** (`conclusion`, style: `focal_callout_subtle`, essential)
- **Registration (PROSPERO), Funding & References** (`references_funding`, style: `colophon`, optional)

## Usage

```bash
python scripts/generate_poster.py \
  --spec poster_spec.json \
  --template systematic-review \
  --output-dir output/
```
