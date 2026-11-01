# `scientific-infographic-maker`

![scientific-infographic-maker](https://img.shields.io/badge/Agent%20Skill-scientific-infographic-maker-blue)

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
