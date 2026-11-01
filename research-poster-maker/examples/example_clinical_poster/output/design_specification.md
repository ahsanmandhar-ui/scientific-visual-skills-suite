# Poster Design Specification & Production Report

## 1. Executive Specification Summary

```text
Poster Template : clinical-research
Orientation     : Landscape
Dimensions      : 48.0 × 36.0 in (1219.2 × 914.4 mm) *(Explicitly configured)*
Layout Recipe   : clinical_workflow
Masthead Style  : solid_banner
Typography      : IBM Plex Sans + IBM Plex Sans
Color Palette   : Oxford Navy & Crisp White (#0F2742 / #FFFFFF / #D55E00)
Output Bundle   : PPTX + Print PDF (reportlab_vector) + PNG Preview + Markdown Reports
QA Verdict      : PASS (Iterations: 1)
```

## 2. Physical Print & Export Architecture

- **Physical Trim Size:** `48.0 × 36.0 in` (`1219.2 × 914.4 mm`)
- **Bleed / Safe Margin:** Bleed `0.0 in` | Safe Margin `1.05 in`
- **PowerPoint Slide Scale:** 1:1 Full Physical Scale (100%)
- **Editable PPTX Objects:** `26` native shapes/tables/textframes (`0` native Office charts)
- **PDF Export Engine:** `reportlab_vector` — verified `48.0 × 36.0 in` with `5` embedded font resource(s)
- **Color Profile Note:** Authored in `sRGB` for wide-gamut conference inkjet plotters (HP DesignJet / Canon imagePROGRAF / Epson SureColor). If submitting to a commercial CMYK offset press requiring PDF/X-1a, perform an ICC prepress conversion first.

## 3. Typography & Viewing-Distance Scale

- **Heading Font:** Requested `IBM Plex Sans` → Resolved `IBM Plex Sans`
- **Body Font:** Requested `IBM Plex Sans` → Resolved `IBM Plex Sans`

| Element | Effective Printed Size | Minimum Floor |
|---|---|---|
| Main Title | `85.0 pt` | `72 pt` (full) / `54 pt` (compact) |
| Authors | `52.0 pt` | `40 pt` (full) / `30 pt` (compact) |
| Affiliations | `28.0 pt` | `24.0 pt` |
| Section Headings | `38.0 pt` | `36.0 pt` |
| Hero Quantitative Metric | `50.0 pt` | `36.0 pt` |
| Body Copy & Bullets | `25.0 pt` | `24.0 pt` |
| Table Cells | `21.0 pt` | `18.0 pt` |
| Captions & References | `19.0 / 18.0 pt` | `18.0 pt` |

## 4. Color System & WCAG 2.1 Accessibility Verification

| Surface Pair | Foreground | Background | Contrast Ratio | WCAG 2.1 Rating |
|---|---|---|---|---|
| Body Copy on Canvas | `#15202B` | `#FFFFFF` | **16.49:1** | AAA |
| Callout Copy on Surface Tint | `#15202B` | `#F2F6FA` | **15.19:1** | AAA |
| Masthead Title | `#FFFFFF` | `#0F2742` | **15.12:1** | AAA |

## 5. Scientific Figures Inventory

- **`cohort_flow` (`flow_diagram`):** `13.00 × 9.20 in` exported as vector `.svg`/`.pdf` + `300 DPI` `.png`.
- **`km_primary` (`kaplan_meier`):** `17.50 × 10.20 in` exported as vector `.svg`/`.pdf` + `300 DPI` `.png`.

## 6. Production & Layout Solver Notes

- LibreOffice headless binary not detected; used native ReportLab + svglib vector scene renderer to produce true-scale PDF with embedded TrueType subsets and vector SVG charts.
