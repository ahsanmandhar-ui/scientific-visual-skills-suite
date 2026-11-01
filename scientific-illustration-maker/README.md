# `scientific-illustration-maker`

![scientific-illustration-maker](https://img.shields.io/badge/Agent%20Skill-scientific--illustration--maker-blue)


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
  A[scientific-illustration-maker] --> B[Capabilities]
  C0[Cellular signaling]
  C1[Molecular pathways]
  C2[Organ pathophysiology]
  C3[Device cross-sections]
  B --> C0
  B --> C1
  B --> C2
  B --> C3
  B --> D[Generated Outputs]
  D --> E[Preflight Validator]
  E --> F[validation_report.json]
```
