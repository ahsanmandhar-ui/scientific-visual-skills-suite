---
name: scientific-infographic-maker
description: Converts complex medical, epidemiological, and scientific evidence into structured editorial infographics covering disease burden, mechanisms of disease, clinical pathways, and medical education summaries. Exports print-ready SVG, vector PDF, 300-DPI PNG, and editable PPTX.
license: MIT
metadata:
  version: "1.0.0"
  domain: "medical-communication"
---

# Scientific Infographic Maker Skill

Transform dense clinical guidelines, epidemiological reports, or translational papers into clean, authoritative **editorial scientific infographics** (`NEJM Catalyst` / `The Lancet` Infographics / `WHO` Technical Brief aesthetic — never noisy AI-style clip-art posters).

All paths below are relative to `scientific-infographic-maker/`.

---

## Non-Negotiable Editorial Standards

1. **Zero Fabricated Burden Metrics:** Every incidence, prevalence, relative risk, NNT, or diagnostic cutoff must trace directly to user-supplied inputs or cited sources.
2. **Avoid Generic AI Infographic Clichés:** Never use random emojis, neon gradients, radial gauges that distort proportions, or automatic "medical blue" defaults. Choose deliberate editorial palettes (`terracotta_epidemiology`, `emerald_public_health`, `burgundy_pathology`, `slate_clinical`).
3. **Structured 4-Band Editorial Hierarchy:**
   - **Band 1 — Epidemiology & Disease Burden:** 3–4 quantitative KPI callouts with exact denominators/timeframes.
   - **Band 2 — Mechanism of Disease / Pathophysiology:** Sequential causal chain (`Trigger → Mediator → Organ Target`).
   - **Band 3 — Clinical Pathway & Quantitative Evidence:** Actionable diagnostic/treatment steps paired with a zero-baseline comparative chart.
   - **Band 4 — Clinical Pearls, Red Flags & References:** Concise clinician/educator takeaways and source attribution.

---

## Workflow

1. Read `docs/infographic-design-guide.md` and select canvas preset (`editorial-legal` `8.5×14 in`, `a3-clinical-sheet` `11.69×16.54 in`, or `digital-vertical` `9×16 in`) plus palette from `templates/infographic_presets.json`.
2. Author `<work_dir>/infographic_spec.json` concisely (target `<= 220` words across all bands).
3. Generate and validate:
   ```bash
   python scripts/generate_infographic.py \
     --spec <work_dir>/infographic_spec.json \
     --output-dir <work_dir>/output

   python scripts/validate_infographic.py \
     --output-dir <work_dir>/output \
     --spec <work_dir>/infographic_spec.json
   ```
4. Visually inspect `<work_dir>/output/infographic.png` for text clipping, hierarchy, contrast, and chart alignment.
