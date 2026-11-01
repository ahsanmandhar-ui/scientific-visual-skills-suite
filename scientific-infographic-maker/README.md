# `scientific-infographic-maker`



Portable Agent Skill for **Claude Code** and **Cline** that converts complex medical, public-health, and translational evidence into structured 4-band editorial infographics (`SVG`, vector `PDF`, `300-DPI PNG`, and editable `PPTX`).

## Capabilities
- Epidemiology & Disease Burden KPI strips
- Mechanism of Disease / Pathophysiology causal cascades
- Stepwise Clinical Pathways & Triage Protocols
- Zero-baseline quantitative outcome charts & medical education pearls

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
  A["scientific-infographic-maker"] --> B[Capabilities]
  C0["Epidemiology KPIs"]
  B --> C0
  C1["Pathophysiology cascade"]
  B --> C1
  C2["Clinical pathway"]
  B --> C2
  C3["Outcome charts"]
  B --> C3
  C4["Clinical pearls"]
  B --> C4
  B --> D["Generated Outputs"]
  D --> E["Preflight Validator"]
  E --> F["validation_report.json"]
```
