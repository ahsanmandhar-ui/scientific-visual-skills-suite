# `medical-education-poster-maker`



Portable Agent Skill for **Claude Code** and **Cline** that generates medical student and residency teaching posters (`A1`, `A2`, `24×36 in`) integrating physiology, branching diagnostic algorithms, pharmacology/pathology matrices, and OSCE/OSPE clinical examination guides.

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
  A["medical-education-poster-maker"] --> B[Capabilities]
  C0["Teaching posters A1/A2/24x36"]
  B --> C0
  C1["Diagnostic algorithms"]
  B --> C1
  C2["Pharmacology matrices"]
  B --> C2
  C3["OSCE/OSPE checklists"]
  B --> C3
  B --> D["Generated Outputs"]
  D --> E["Preflight Validator"]
  E --> F["validation_report.json"]
```
