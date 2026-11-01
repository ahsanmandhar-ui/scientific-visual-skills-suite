# Poster Design Specification & Production Report

## 1. Executive Specification Summary

```text
Poster Template : minimalist-editorial
Orientation     : Portrait
Dimensions      : 36.0 × 48.0 in (914.4 × 1219.2 mm) *(Explicitly configured)*
Layout Recipe   : two_column_editorial
Masthead Style  : editorial_rule_light
Typography      : Source Sans 3 + Source Serif 4
Color Palette   : Monochromatic Scientific Editorial (#111827 / #FFFFFF / #0072B2)
Output Bundle   : PPTX + Print PDF (reportlab_vector) + PNG Preview + Markdown Reports
QA Verdict      : PASS (Iterations: 1)
```

## 2. Physical Print & Export Architecture

- **Physical Trim Size:** `36.0 × 48.0 in` (`914.4 × 1219.2 mm`)
- **Bleed / Safe Margin:** Bleed `0.0 in` | Safe Margin `1.05 in`
- **PowerPoint Slide Scale:** 1:1 Full Physical Scale (100%)
- **Editable PPTX Objects:** `17` native shapes/tables/textframes (`0` native Office charts)
- **PDF Export Engine:** `reportlab_vector` — verified `36.0 × 48.0 in` with `5` embedded font resource(s)
- **Color Profile Note:** Authored in `sRGB` for wide-gamut conference inkjet plotters (HP DesignJet / Canon imagePROGRAF / Epson SureColor). If submitting to a commercial CMYK offset press requiring PDF/X-1a, perform an ICC prepress conversion first.

## 3. Typography & Viewing-Distance Scale

- **Heading Font:** Requested `Source Sans 3` → Resolved `Source Sans 3`
- **Body Font:** Requested `Source Serif 4` → Resolved `Source Serif 4`

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
| Body Copy on Canvas | `#111827` | `#FFFFFF` | **17.74:1** | AAA |
| Callout Copy on Surface Tint | `#111827` | `#F3F4F6` | **16.12:1** | AAA |
| Masthead Title | `#111827` | `#FFFFFF` | **17.74:1** | AAA |

## 5. Scientific Figures Inventory

- **`lactate_bar` (`bar_chart`):** `16.50 × 11.20 in` exported as vector `.svg`/`.pdf` + `300 DPI` `.png`.

## 6. Production & Layout Solver Notes

- LibreOffice headless binary not detected; used native ReportLab + svglib vector scene renderer to produce true-scale PDF with embedded TrueType subsets and vector SVG charts.
