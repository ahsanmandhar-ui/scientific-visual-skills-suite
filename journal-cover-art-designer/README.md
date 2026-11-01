# `journal-cover-art-designer`

![journal-cover-art-designer](https://img.shields.io/badge/Agent%20Skill-journal-cover-art-designer-blue)

Portable Agent Skill for **Claude Code** and **Cline** that designs mathematical/vector scientific journal cover art formatted to exact publisher trim, bleed, and masthead safe-zone specifications (`Nature`, `Cell Press`, `Science`, `ACS/Wiley`), emitting both clean **unlettered full-bleed production art** and an **editorial masthead safe-zone mockup**.

## Workflow

```mermaid
flowchart LR
  A[Synthetic Input JSON] --> B[Python Generator]
  B --> C[Vector / Raster Outputs]
  C --> D[Preflight Validator]
  D --> E[validation_report.json]
```
