---
name: publication-figure-designer
description: Creates publication-quality single-panel and multi-panel scientific research figures formatted to exact journal column specifications (Nature, Science, Cell, NEJM, Lancet, JAMA, BMJ). Supports forest plots, funnel plots, Kaplan-Meier survival curves, ROC curves, replicate-overlaid distributions, and multi-panel GridSpec composites in vector SVG/PDF and 600-DPI PNG/TIFF.
license: MIT
metadata:
  version: "1.0.0"
  domain: "scientific-visualization"
  priority: "high"
---

# Publication Figure Designer Skill

Produce camera-ready manuscript figures formatted at **exact physical journal column widths** (`85–89 mm` single column, `120–136 mm` 1.5-column, `174–183 mm` double column) with embedded TrueType vector typography, colorblind-safe Okabe-Ito palettes, and zero chartjunk.

All paths below are relative to `publication-figure-designer/`.

---

## Non-Negotiable Scientific Figure Rules

1. **Exact Journal Physical Widths:** Author figures at the exact millimeter column width of the target journal (`templates/journal_figure_specs.json`) so fonts (`6–8 pt` at print size) are never scaled arbitrarily during typesetting.
2. **Zero Data Fabrication:** Plot supplied datasets and statistics verbatim. Never smooth survival steps, invent error bars, or truncate bar-chart zero baselines.
3. **Small-Sample Data Transparency:** When plotting continuous group comparisons with `n < 30` per group, overlay individual replicate points (`box_strip`) rather than hiding distributions behind bare bars (*Nature* / *Cell* / *PLOS Biology* reporting standard).
4. **Vector Outlines & Colorblind Safety:** Export vector `.pdf` (`pdf.fonttype = 42`, zero Type 3 fonts) and `.svg` alongside `600 DPI` `.png` (and optional `.tiff`), using Okabe-Ito colorblind-safe series + distinct line/marker encodings.

---

## Workflow

1. **Consult Journal Specs:** Read `docs/journal-figure-standards.md` and select a journal profile (`nature-portfolio`, `nejm-lancet`, `cell-science`, `jama-bmj`) and column span (`single`, `one_half`, `double`).
2. **Author Multi-Panel or Single-Panel Spec:** Define `<work_dir>/figure_spec.json` specifying `grid` (`rows`, `cols`) and `panels` (`forest`, `funnel`, `kaplan_meier`, `roc`, `bar_ci`, `box_strip`, `scatter_fit`).
3. **Generate & Validate:**
   ```bash
   python scripts/generate_publication_figure.py \
     --spec <work_dir>/figure_spec.json \
     --output-dir <work_dir>/output

   python scripts/validate_publication_figure.py \
     --output-dir <work_dir>/output \
     --spec <work_dir>/figure_spec.json
   ```
4. **Visual Inspection:** Inspect `<work_dir>/output/figure.png` to verify panel labels (`a, b, c` or `A, B, C`), tick legibility, legend placement, and axis alignment. Revise spacing (`wspace`, `hspace`) if any label approaches an adjacent panel.
