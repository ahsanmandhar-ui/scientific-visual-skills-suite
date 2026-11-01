---
name: graphical-abstract-maker
description: Converts scientific research papers, clinical trials, and manuscripts into journal-quality graphical abstracts and visual abstracts (Elsevier, Cell Press, BMJ/JAMA, Springer Nature, ACS, and custom formats). Generates study design summaries, scientific flow diagrams, and embedded outcome mini-charts in publication-ready vector SVG, print PDF, 300-DPI PNG, and editable PPTX.
license: MIT
metadata:
  version: "1.0.0"
  domain: "scientific-communication"
  priority: "high"
---

# Graphical Abstract Maker Skill

Transform research manuscripts and clinical trial reports into crisp, scannable, journal-compliant **Graphical Abstracts** and **Visual Abstracts**—without cartoonish AI clip-art or walls of pasted text.

All paths below are relative to this skill's root (`graphical-abstract-maker/`).

---

## Core Design & Scientific Rules

1. **Not a Mini-Poster:** Keep total body word count strictly concise (**35–85 words** across panels). Viewers must grasp the *Question/Cohort → Intervention/Mechanism → Quantitative Finding* in **10–15 seconds**.
2. **Zero Data Fabrication:** Every sample size (`N`), effect size (`HR`, `OR`, `RR`, `Δ`), 95% CI, and *p*-value must originate verbatim from the source manuscript.
3. **Journal-Exact Dimensions & Vector Export:** Match target journal specifications (`templates/journal_presets.json`) and always output vector `.svg` and `.pdf` (`pdf.fonttype = 42` TrueType outlines) alongside `300+ DPI` `.png` and editable `.pptx`.
4. **Restrained Scientific Visuals:** Use clean vector process flows, subtle typographic hierarchy, Okabe-Ito colorblind-safe accents, and real embedded mini-plots (bars, forest intervals, survival deltas)—never emoji icons or stock illustrations.

---

## Workflow

### Step 1 — Extract Study Brief & Check Completeness

```bash
python scripts/extract_ga_brief.py <manuscript_file> --output <work_dir>/ga_brief.json
```

Inspect `<work_dir>/ga_brief.json`. Ask the user **only** if target journal format or essential primary outcome data are missing.

### Step 2 — Choose Journal Preset & Layout Topology

Consult `docs/journal-guidelines.md` and `templates/journal_presets.json`:
- `elsevier-landscape` (`12.5 × 5.0 in`, 2.5:1 horizontal 3-stage ribbon; matches `1328 × 531 px` minimum)
- `cell-press-square` (`10.0 × 10.0 in`, 1:1 square 3-tier top-to-bottom architecture; `1200 × 1200 px` @ 300 DPI = `3000 × 3000 px`)
- `bmj-visual-abstract` (`16.0 × 9.0 in`, 16:9 clinical visual abstract with header banner, 3 PICO/Outcome columns, mini-chart, and citation footer)
- `springer-nature-compact` (`7.09 × 3.54 in` / `180 × 90 mm`, clean minimalist 2:1 summary)

### Step 3 — Generate & Validate Graphical Abstract

Create `<work_dir>/ga_spec.json` and run:

```bash
python scripts/generate_graphical_abstract.py \
  --spec <work_dir>/ga_spec.json \
  --output-dir <work_dir>/output

python scripts/validate_graphical_abstract.py \
  --output-dir <work_dir>/output \
  --spec <work_dir>/ga_spec.json
```

Visually inspect `<work_dir>/output/graphical_abstract.png` to confirm zero overlapping labels, clear directional reading flow, high contrast, and crisp mini-chart legibility. Revise and re-render if needed.

---

## Mandatory Outputs

- `graphical_abstract.svg` — Publication-ready scalable vector graphic
- `graphical_abstract.pdf` — Vector PDF with embedded TrueType outlines
- `graphical_abstract.png` — High-resolution 300-DPI raster export
- `graphical_abstract.pptx` — Editable native PowerPoint slide
- `validation_report.json` / `validation_report.md` — Dimension, word-budget, contrast & numerical audit
