# `scientific-infographic-maker`

![scientific-infographic-maker](https://img.shields.io/badge/Agent%20Skill-scientific--infographic--maker-blue)


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
  A[scientific-infographic-maker] --> B[Capabilities]
  C0[Epidemiology KPIs]
  C1[Pathophysiology cascade]
  C2[Clinical pathway]
  C3[Outcome charts]
  C4[Clinical pearls]
  B --> C0
  B --> C1
  B --> C2
  B --> C3
  B --> C4
  B --> D[Generated Outputs]
  D --> E[Preflight Validator]
  E --> F[validation_report.json]
```
