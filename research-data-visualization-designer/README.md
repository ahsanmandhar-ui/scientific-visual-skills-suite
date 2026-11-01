# `research-data-visualization-designer`



Portable Agent Skill for **Claude Code** and **Cline** that profiles CSV/Excel datasets, integrates R/Python/SPSS multivariable model outputs, produces publication-quality multi-panel statistical visualizations (`SVG`, `PDF`, `PNG`), and emits standalone `reproduce_figure.py` + `SHA-256` data provenance manifests.

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
  A[research-data-visualization-designer] --> B[Capabilities]
  C0[CSV/Excel profiler]
  C1[Multivariable viz]
  C2[reproduce_figure.py]
  C3[SHA-256 manifest]
  B --> C0
  B --> C1
  B --> C2
  B --> C3
  B --> D[Generated Outputs]
  D --> E[Preflight Validator]
  E --> F[validation_report.json]
```
