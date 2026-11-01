# `research-data-visualization-designer`

![research-data-visualization-designer](https://img.shields.io/badge/Agent%20Skill-research-data-visualization-designer-blue)

Portable Agent Skill for **Claude Code** and **Cline** that profiles CSV/Excel datasets, integrates R/Python/SPSS multivariable model outputs, produces publication-quality multi-panel statistical visualizations (`SVG`, `PDF`, `PNG`), and emits standalone `reproduce_figure.py` + `SHA-256` data provenance manifests.

## Workflow

```mermaid
flowchart LR
  A[Synthetic Input JSON] --> B[Python Generator]
  B --> C[Vector / Raster Outputs]
  C --> D[Preflight Validator]
  D --> E[validation_report.json]
```
