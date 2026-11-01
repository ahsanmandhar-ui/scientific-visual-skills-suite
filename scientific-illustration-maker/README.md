# `scientific-illustration-maker`



Portable Agent Skill for **Claude Code** and **Cline** that produces crisp 2D vector scientific illustrations and mechanism schematics (`cellular_signaling`, `molecular_pathway`, `organ_pathophysiology`, `medical_device`) in editable `SVG`, vector `PDF`, and high-DPI `PNG`.

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
  A["scientific-illustration-maker"] --> B[Capabilities]
  C0["Cellular signaling"]
  B --> C0
  C1["Molecular pathways"]
  B --> C1
  C2["Organ pathophysiology"]
  B --> C2
  C3["Device cross-sections"]
  B --> C3
  B --> D["Generated Outputs"]
  D --> E["Preflight Validator"]
  E --> F["validation_report.json"]
```
