---
name: research-poster-maker
description: Transforms scientific research manuscripts (DOCX, PDF, Markdown), conference abstracts, CSV/XLSX datasets, tables, and clinical/epidemiological/meta-analysis results into professionally art-directed, scientifically accurate, conference-ready research posters (.pptx, print-ready .pdf, .png preview, and QA reports). Use whenever the user asks to create, design, format, or validate an academic, medical, clinical, systematic review, meta-analysis, or scientific conference poster.
license: MIT
metadata:
  version: "1.0.0"
  domain: "scientific-communication"
---

# Research Poster Maker Skill

Produce conference-ready scientific research posters that read as if art-directed by an experienced academic graphic designer (suitable for *Nature* conferences, *BMJ* meetings, ACC, ASN, European congresses, and university symposia)—never generic AI infographics.

All file paths below are relative to this skill's root directory (`research-poster-maker/`).

---

## Core Non-Negotiable Rules

1. **Zero Scientific Fabrication:** Never invent sample sizes, effect estimates, confidence intervals, *p*-values, exclusion counts, citations, grant numbers, or affiliations. Preserve exact decimal precision, units, and statistical significance framing.
2. **Distill Prose—Do Not Paste Walls of Text:** Transform manuscript paragraphs into concise, high-clarity analytical statements and parallel bullets (~350–600 body words total) while preserving exact meaning.
3. **Never Shrink All Fonts to Cure Overcrowding:** If content overflows a layout at legible viewing-distance sizes, rewrite verbose prose, prune secondary background points, rebalance columns, or switch layouts.
4. **Restrained Editorial Design:** Avoid identical rounded cards around every section, decorative clip-art/emojis, drop shadows, rainbow gradients, and knee-jerk medical blue. Use clean typographic rules, intentional whitespace, high WCAG contrast, and real data visualizations.
5. **Honest Print & Technical Reporting:** Never upscale a low-resolution raster image and claim it is 300 DPI. Never claim CMYK offset-press PDF/X compliance on sRGB outputs. Report exact dimensions, `.pptx` scale factor (if >56 in), and PDF export backend transparently.

---

## Step-by-Step Workflow

### Step 1 — Inspect Available Research Material First

Before asking the user questions, locate and inspect all supplied manuscripts (`.docx`, `.pdf`, `.md`, `.txt`), datasets (`.csv`, `.xlsx`), and existing figures/logos:

```bash
python scripts/analyze_research.py <input_files_or_folder> --output-dir <work_dir>
```

Review `<work_dir>/research_extraction.json` and `<work_dir>/extraction_summary.md` to check the **18 canonical fields** (Title, Authors/Affiliations, Background, Research Gap, Objectives, Study Design, Methods, Population, Sample Size, Statistical Methods, Primary Outcome, Secondary Outcomes, Important Findings, Tables/Figures, Limitations, Conclusion, References, Funding/Acknowledgements).

### Step 2 — Request Only Essential Missing Information

Do **not** present a long questionnaire when the manuscript already supplies the study details. Ask concisely **only** when:
- Critical scientific facts are missing from the source (e.g., missing authors/affiliations or missing primary outcome numbers) and cannot be inferred.
- Conference board dimensions/orientation were not specified (offer a sensible regional default—e.g., `48 × 36 in` landscape or `ISO A0` portrait—clearly labeled as an assumption).
- Institutional branding/logo or study QR URL is desired.

### Step 3 — Select Architecture & Consult Reference Docs as Needed

Load detailed reference guides from `docs/` on demand:
- **Dimensions, 56-in PowerPoint ceiling & print specs:** `docs/print-specifications.md`
- **Color palettes & editorial anti-patterns:** `docs/design-system.md`
- **Typography pairings & viewing-distance point scales:** `docs/typography.md`
- **8 Layout composition strategies:** `docs/layout-recipes.md`
- **15 Scientific chart/diagram types:** `docs/visualization-guide.md`
- **Scientific integrity & extraction rules:** `docs/scientific-integrity.md`
- **WCAG 2.1 contrast & Okabe-Ito colorblind safety:** `docs/accessibility.md`

Available templates in `templates/<id>/template.json`:
- `clinical-research` | `systematic-review` | `meta-analysis` | `experimental-research` | `epidemiology` | `minimalist-editorial`

Available layout recipes:
- `three_column_classic` | `two_column_editorial` | `asymmetric_grid` | `results_focused` | `timeline_flow` | `central_visual` | `clinical_workflow` | `systematic_review_prisma`

Available palettes:
- `academic_navy` | `charcoal_ivory` | `deep_teal` | `burgundy_offwhite` | `forest_cream` | `monochrome_editorial` (plus custom hex overrides)

### Step 4 — Present Brief Pre-Generation Design Specification

Before final rendering, present a concise specification block:

```text
Poster: Clinical Research
Orientation: Landscape
Dimensions: 48 × 36 inches (explicit / assumed default)
Layout: clinical_workflow (30% : 41% : 29%)
Typography: IBM Plex Sans
Palette: Oxford Navy & Crisp White (#0F2742 / #FFFFFF / #D55E00)
Visual focus: Kaplan-Meier primary endpoint curve + subgroup outcomes table
Output: PPTX + PDF + PNG + Content & Design Reports
```

### Step 5 — Author `poster_spec.json` & Execute Production Pipeline

Construct `<work_dir>/poster_spec.json` strictly from verified source data:

```json
{
  "template_id": "clinical-research",
  "dimensions_preset": "48x36",
  "layout_recipe": "clinical_workflow",
  "palette": "academic_navy",
  "font_pairing": "clinical_precision",
  "study_badge": "PROSPECTIVE MULTICENTER COHORT · STROBE",
  "title": "Exact Verified Study Title in Sentence Case",
  "authors_line": "First Author, MD¹; Second Author, PhD²",
  "affiliations_line": "¹Dept. of Medicine, Institution A; ²Dept. of Biostatistics, Institution B",
  "study_url": "https://doi.org/...",
  "logo_path": null,
  "items": [
    {
      "id": "background",
      "column": 0,
      "item_type": "text",
      "style": "editorial_rule",
      "title": "01  Clinical Background & Objective",
      "paragraphs": ["Concise context distilled from source."],
      "bullets": ["Objective: Precise primary hypothesis."]
    },
    {
      "id": "primary_outcome",
      "column": 1,
      "item_type": "callout",
      "style": "focal_callout",
      "title": "Primary Clinical Endpoint",
      "hero_metric": "aHR 0.68 (95% CI 0.56–0.82; p < 0.001)",
      "paragraphs": ["Exact analytical summary of primary finding."]
    },
    {
      "id": "fig1",
      "column": 1,
      "item_type": "figure",
      "title": "03  Cumulative Event-Free Survival",
      "chart_spec": {
        "id": "fig1_km",
        "chart_type": "kaplan_meier",
        "width_in": 16.5,
        "height_in": 9.2,
        "x_label": "Follow-up (Months)",
        "y_label": "Event-Free Survival",
        "data": { "groups": [], "risk_times": [], "stat_summary": "..." }
      },
      "caption": "Figure 1. Kaplan-Meier survival curves with number at risk (N = ...)."
    },
    {
      "id": "tbl1",
      "column": 2,
      "item_type": "table",
      "title": "04  Multivariable Outcomes",
      "table_data": {
        "headers": ["Endpoint", "Adjusted HR (95% CI)", "p-value"],
        "rows": [["Primary composite", "0.68 (0.56–0.82)", "<0.001"]],
        "col_weights": [1.9, 1.3, 0.7]
      },
      "footnote": "Adjusted for pre-specified baseline covariates."
    }
  ],
  "colophon": {
    "references": ["[1] Author et al. Journal Year;Vol:Pages."],
    "funding": "Funding: Grant ID.",
    "correspondence": "Correspondence: author@institution.edu"
  },
  "missing_information_notes": []
}
```

Run the unified generator (which runs chart generation, layout solving, PPTX build, PDF export, PNG preview rendering, and multi-layer QA validation):

```bash
python scripts/generate_poster.py \
  --spec <work_dir>/poster_spec.json \
  --extraction <work_dir>/research_extraction.json \
  --output-dir <work_dir>/output
```

Individual pipeline stages can also be invoked independently via `scripts/generate_charts.py`, `scripts/export_poster.py`, `scripts/generate_preview.py`, and `scripts/validate_poster.py`.

### Step 6 — Visual Inspection & Bounded Iterative Refinement

1. Read `<work_dir>/output/validation_report.md` to confirm Technical, Scientific, Accessibility, and Visual checks passed.
2. **Visually inspect `<work_dir>/output/poster_preview.png`** using image-viewing tools whenever available. Check overall visual hierarchy, column balance, chart legibility, alignment, and whitespace.
3. If any issue is found (`Generate → Export → Render → Inspect → Validate → Revise → Finalize`), adjust `poster_spec.json` (condense verbose bullets, adjust `column` assignments or `aspect_ratio`, or switch `layout_recipe`) and re-run. Stop once objective checks pass or honestly report any unresolved constraint (such as low-resolution user-supplied photography).

---

## Mandatory Deliverables Checklist

Verify all five files exist in `<output_dir>` before concluding:
1. `poster.pptx` — Editable native PowerPoint poster (shapes, text runs, booktabs tables, high-DPI/native charts).
2. `poster.pdf` — Print-ready PDF preserving exact physical dimensions and embedded fonts.
3. `poster_preview.png` — Full-poster rendered preview image.
4. `poster_content.md` — Extracted and distilled poster content with completeness notes.
5. `design_specification.md` — Complete physical, typographic, color-contrast, and QA audit report (accompanied by `validation_report.md`).
