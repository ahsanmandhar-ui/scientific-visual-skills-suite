# Minimalist Editorial & Concise Abstract Poster (`minimalist-editorial`)

Restrained archival light-masthead editorial poster inspired by Swiss academic typography. Ideal for university symposia, methodological studies, and early-stage or abstract-only submissions where source data are concise.

## Default Design Tokens

- **Reporting Framework:** General Academic / Conference Abstract
- **Default Dimensions:** `36x48` (configurable to any preset or custom board size)
- **Landscape Layout Recipe:** `two_column_editorial`
- **Portrait Layout Recipe:** `two_column_editorial`
- **Default Color Palette:** `monochrome_editorial`
- **Default Font Pairing:** `editorial_modern`
- **Masthead Architecture:** `editorial_rule_light`
- **Target Body Word Budget:** ~360 words

## Recommended Scientific Visualizations

`bar_chart`, `scatter_plot`, `statistical_table`, `workflow_diagram`

## Section Blueprint

- **Context & Research Question** (`background`, style: `editorial_rule`, essential)
- **Study Design & Approach** (`methods`, style: `editorial_rule`, essential)
- **Principal Findings** (`primary_outcome`, style: `focal_callout`, essential)
- **Empirical Summary** (`primary_figure`, style: `figure_well`, optional)
- **Scope & Open Questions** (`limitations`, style: `editorial_rule`, optional)
- **Conclusions** (`conclusion`, style: `editorial_rule`, essential)
- **Notes & Correspondence** (`references_funding`, style: `colophon`, optional)

## Usage

```bash
python scripts/generate_poster.py \
  --spec poster_spec.json \
  --template minimalist-editorial \
  --output-dir output/
```
