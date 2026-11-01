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
