# `academic-conference-design-maker`

![academic-conference-design-maker](https://img.shields.io/badge/Agent%20Skill-academic-conference-design-maker-blue)

Portable Agent Skill for **Claude Code** and **Cline** that builds a coordinated 6-asset academic conference visual identity kit (`banner`, `abstract_book_cover`, `event_poster`, `certificate`, `speaker_card`, `social_card`, and `kit_overview.png`).

## Workflow

```mermaid
flowchart LR
  A[Synthetic Input JSON] --> B[Python Generator]
  B --> C[Vector / Raster Outputs]
  C --> D[Preflight Validator]
  D --> E[validation_report.json]
```
