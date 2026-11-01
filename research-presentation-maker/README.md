# `research-presentation-maker`



Portable Agent Skill for **Claude Code** and **Cline** that converts manuscripts and thesis chapters into **Assertion-Evidence** scientific presentations (`deck.pptx` with native speaker notes, vector `deck_handout.pdf`, `deck_overview.png`, and timed `speaker_notes.md`).

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
  A["research-presentation-maker"] --> B[Capabilities]
  C0["Assertion-Evidence slides"]
  B --> C0
  C1["Speaker notes"]
  B --> C1
  C2["Handout PDF"]
  B --> C2
  C3["Overview PNG"]
  B --> C3
  B --> D["Generated Outputs"]
  D --> E["Preflight Validator"]
  E --> F["validation_report.json"]
```
