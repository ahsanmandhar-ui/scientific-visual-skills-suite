# Poster Design Specification & Production Report

## 1. Executive Specification Summary

```text
Poster Template : meta-analysis
Orientation     : Landscape
Dimensions      : 56.0 × 42.0 in (1422.4 × 1066.8 mm) *(Explicitly configured)*
Layout Recipe   : systematic_review_prisma
Masthead Style  : solid_banner
Typography      : Source Sans 3 + Source Serif 4
Color Palette   : Academic Burgundy & Alabaster (#5B1627 / #FCFAF8 / #0072B2)
Output Bundle   : PPTX + Print PDF (reportlab_vector) + PNG Preview + Markdown Reports
QA Verdict      : PASS (Iterations: 1)
```

## 2. Physical Print & Export Architecture

- **Physical Trim Size:** `56.0 × 42.0 in` (`1422.4 × 1066.8 mm`)
- **Bleed / Safe Margin:** Bleed `0.0 in` | Safe Margin `1.05 in`
- **PowerPoint Slide Scale:** 1:1 Full Physical Scale (100%)
- **Editable PPTX Objects:** `25` native shapes/tables/textframes (`0` native Office charts)
- **PDF Export Engine:** `reportlab_vector` — verified `56.0 × 42.0 in` with `6` embedded font resource(s)
- **Color Profile Note:** Authored in `sRGB` for wide-gamut conference inkjet plotters (HP DesignJet / Canon imagePROGRAF / Epson SureColor). If submitting to a commercial CMYK offset press requiring PDF/X-1a, perform an ICC prepress conversion first.

## 3. Typography & Viewing-Distance Scale

- **Heading Font:** Requested `Source Sans 3` → Resolved `Source Sans 3`
- **Body Font:** Requested `Source Serif 4` → Resolved `Source Serif 4`

| Element | Effective Printed Size | Minimum Floor |
|---|---|---|
| Main Title | `85.8 pt` | `72 pt` (full) / `54 pt` (compact) |
| Authors | `60.3 pt` | `40 pt` (full) / `30 pt` (compact) |
| Affiliations | `32.5 pt` | `24.0 pt` |
| Section Headings | `44.1 pt` | `36.0 pt` |
| Hero Quantitative Metric | `58.0 pt` | `36.0 pt` |
| Body Copy & Bullets | `29.0 pt` | `24.0 pt` |
| Table Cells | `24.4 pt` | `18.0 pt` |
| Captions & References | `22.0 / 20.9 pt` | `18.0 pt` |

## 4. Color System & WCAG 2.1 Accessibility Verification

| Surface Pair | Foreground | Background | Contrast Ratio | WCAG 2.1 Rating |
|---|---|---|---|---|
| Body Copy on Canvas | `#201619` | `#FCFAF8` | **16.95:1** | AAA |
| Callout Copy on Surface Tint | `#201619` | `#F4ECEE` | **15.19:1** | AAA |
| Masthead Title | `#FFFFFF` | `#5B1627` | **13.22:1** | AAA |

## 5. Scientific Figures Inventory

- **`glp1_forest` (`forest_plot`):** `21.50 × 13.80 in` exported as vector `.svg`/`.pdf` + `300 DPI` `.png`.
- **`glp1_funnel` (`funnel_plot`):** `13.50 × 9.50 in` exported as vector `.svg`/`.pdf` + `300 DPI` `.png`.

## 6. Production & Layout Solver Notes

- LibreOffice headless binary not detected; used native ReportLab + svglib vector scene renderer to produce true-scale PDF with embedded TrueType subsets and vector SVG charts.
