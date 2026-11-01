# `medical-education-poster-maker`

![medical-education-poster-maker](https://img.shields.io/badge/Agent%20Skill-medical--education--poster--maker-blue)


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
  A[medical-education-poster-maker] --> B[Capabilities]
  C0[Teaching posters A1/A2/24x36]
  C1[Diagnostic algorithms]
  C2[Pharmacology matrices]
  C3[OSCE/OSPE checklists]
  B --> C0
  B --> C1
  B --> C2
  B --> C3
  B --> D[Generated Outputs]
  D --> E[Preflight Validator]
  E --> F[validation_report.json]
```
