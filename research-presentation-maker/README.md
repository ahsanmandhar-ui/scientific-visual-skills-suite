# `research-presentation-maker`

![research-presentation-maker](https://img.shields.io/badge/Agent%20Skill-research-presentation-maker-blue)

Portable Agent Skill for **Claude Code** and **Cline** that converts manuscripts and thesis chapters into **Assertion-Evidence** scientific presentations (`deck.pptx` with native speaker notes, vector `deck_handout.pdf`, `deck_overview.png`, and timed `speaker_notes.md`).

## Workflow

```mermaid
flowchart LR
  A[Synthetic Input JSON] --> B[Python Generator]
  B --> C[Vector / Raster Outputs]
  C --> D[Preflight Validator]
  D --> E[validation_report.json]
```
