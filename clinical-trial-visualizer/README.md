# `clinical-trial-visualizer`

![clinical-trial-visualizer](https://img.shields.io/badge/Agent%20Skill-clinical-trial-visualizer-blue)

Portable Agent Skill for **Claude Code** and **Cline** that produces EQUATOR/CONSORT-compliant clinical trial participant flow diagrams, SPIRIT protocol timelines, endpoint summary panels, and CTCAE adverse-event butterfly plots with strict arithmetic count-closure validation.

## Workflow

```mermaid
flowchart LR
  A[Synthetic Input JSON] --> B[Python Generator]
  B --> C[Vector / Raster Outputs]
  C --> D[Preflight Validator]
  D --> E[validation_report.json]
```
