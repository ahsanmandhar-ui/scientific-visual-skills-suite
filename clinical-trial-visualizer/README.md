# `clinical-trial-visualizer`



Portable Agent Skill for **Claude Code** and **Cline** that produces EQUATOR/CONSORT-compliant clinical trial participant flow diagrams, SPIRIT protocol timelines, endpoint summary panels, and CTCAE adverse-event butterfly plots with strict arithmetic count-closure validation.

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
  A["clinical-trial-visualizer"] --> B[Capabilities]
  C0["CONSORT 4-phase flow"]
  B --> C0
  C1["SPIRIT timelines"]
  B --> C1
  C2["Efficacy cards"]
  B --> C2
  C3["CTCAE butterfly plots"]
  B --> C3
  B --> D["Generated Outputs"]
  D --> E["Preflight Validator"]
  E --> F["validation_report.json"]
```
