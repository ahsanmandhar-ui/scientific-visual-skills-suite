# Poster Design Specification & Production Report

## 1. Executive Specification Summary

```text
Poster Template : epidemiology
Orientation     : Landscape
Dimensions      : 46.811 × 33.1102 in (1189.0 × 841.0 mm) *(Explicitly configured)*
Layout Recipe   : timeline_flow
Masthead Style  : solid_banner
Typography      : Source Serif 4 + Source Sans 3
Color Palette   : Forest Pine & Warm Cream (#173B2D / #FAF9F4 / #C25E14)
Output Bundle   : PPTX + Print PDF (reportlab_vector) + PNG Preview + Markdown Reports
QA Verdict      : PASS (Iterations: 1)
```

## 2. Physical Print & Export Architecture

- **Physical Trim Size:** `46.811 × 33.1102 in` (`1189.0 × 841.0 mm`)
- **Bleed / Safe Margin:** Bleed `0.0 in` | Safe Margin `1.05 in`
- **PowerPoint Slide Scale:** 1:1 Full Physical Scale (100%)
- **Editable PPTX Objects:** `20` native shapes/tables/textframes (`0` native Office charts)
- **PDF Export Engine:** `reportlab_vector` — verified `46.811 × 33.11 in` with `6` embedded font resource(s)
- **Color Profile Note:** Authored in `sRGB` for wide-gamut conference inkjet plotters (HP DesignJet / Canon imagePROGRAF / Epson SureColor). If submitting to a commercial CMYK offset press requiring PDF/X-1a, perform an ICC prepress conversion first.

## 3. Typography & Viewing-Distance Scale

- **Heading Font:** Requested `Source Serif 4` → Resolved `Source Serif 4`
- **Body Font:** Requested `Source Sans 3` → Resolved `Source Sans 3`

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
| Body Copy on Canvas | `#18221D` | `#FAF9F4` | **15.5:1** | AAA |
| Callout Copy on Surface Tint | `#18221D` | `#EDF2EB` | **14.39:1** | AAA |
| Masthead Title | `#FFFFFF` | `#173B2D` | **12.35:1** | AAA |

## 5. Scientific Figures Inventory

- **`epi_timeline` (`workflow_diagram`):** `44.71 × 4.20 in` exported as vector `.svg`/`.pdf` + `300 DPI` `.png`.
- **`pm25_curve` (`scatter_plot`):** `15.60 × 8.40 in` exported as vector `.svg`/`.pdf` + `300 DPI` `.png`.

## 6. Production & Layout Solver Notes

- LibreOffice headless binary not detected; used native ReportLab + svglib vector scene renderer to produce true-scale PDF with embedded TrueType subsets and vector SVG charts.
