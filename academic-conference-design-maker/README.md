# `academic-conference-design-maker`



Portable Agent Skill for **Claude Code** and **Cline** that builds a coordinated 6-asset academic conference visual identity kit (`banner`, `abstract_book_cover`, `event_poster`, `certificate`, `speaker_card`, `social_card`, and `kit_overview.png`).

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
  A[academic-conference-design-maker] --> B[Capabilities]
  C0[Stage banner]
  C1[Abstract-book cover]
  C2[CFP poster + QR]
  C3[Certificate]
  C4[Speaker card]
  C5[Social card]
  B --> C0
  B --> C1
  B --> C2
  B --> C3
  B --> C4
  B --> C5
  B --> D[Generated Outputs]
  D --> E[Preflight Validator]
  E --> F[validation_report.json]
```
