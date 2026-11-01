# `publication-figure-designer`



Portable Agent Skill for **Claude Code** and **Cline** that generates single-panel and multi-panel composite research figures (`a, b, c, d` or `A, B, C, D`) formatted to exact physical journal column widths (`Nature`, `Cell`, `Science`, `NEJM`, `Lancet`, `JAMA`, `BMJ`) in vector `SVG`/`PDF` and `600-DPI PNG`.

## Supported Panel Types
- `forest` (Subgroup/study inverse-variance forest plots with pooled diamond)
- `funnel` (Inverted-SE publication bias funnel plots)
- `kaplan_meier` (Survival step curves with 95% CI shading)
- `roc` (Multi-model Receiver Operating Characteristic curves)
- `box_strip` (Boxplot + individual replicate jitter points for small-`n` transparency)
- `bar_ci` (Zero-baseline categorical CI bars)
- `scatter_fit` (Bivariate observations + fitted regression curve)

## Installation
- **Claude Code:** `.claude/skills/publication-figure-designer/`
- **Cline:** `.cline/skills/publication-figure-designer/`

## Workflow

```mermaid
flowchart LR
  A[Synthetic Input JSON] --> B[Python Generator]
  B --> C[Vector / Raster Outputs]
  C --> D[Preflight Validator]
  D --> E[validation_report.json]
```

## Skill Aspects

```mermaid
flowchart TD
  A[publication-figure-designer] --> B[Capabilities]
  C0[Single-panel figures]
  C1[Multi-panel (a,b,c,d)]
  C2[Journal widths 84-183mm]
  C3[Nature/Cell/Science/NEJM/Lancet/JAMA/BMJ]
  B --> C0
  B --> C1
  B --> C2
  B --> C3
  B --> D[Generated Outputs]
  D --> E[Preflight Validator]
  E --> F[validation_report.json]
```
