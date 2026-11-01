# `journal-cover-art-designer`



Portable Agent Skill for **Claude Code** and **Cline** that designs mathematical/vector scientific journal cover art formatted to exact publisher trim, bleed, and masthead safe-zone specifications (`Nature`, `Cell Press`, `Science`, `ACS/Wiley`), emitting both clean **unlettered full-bleed production art** and an **editorial masthead safe-zone mockup**.

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
  A["journal-cover-art-designer"] --> B[Capabilities]
  C0["Trim + bleed art"]
  B --> C0
  C1["Nature/Cell/Science/ACS/Wiley"]
  B --> C1
  C2["Clean full-bleed"]
  B --> C2
  C3["Masthead mockup"]
  B --> C3
  B --> D["Generated Outputs"]
  D --> E["Preflight Validator"]
  E --> F["validation_report.json"]
```
