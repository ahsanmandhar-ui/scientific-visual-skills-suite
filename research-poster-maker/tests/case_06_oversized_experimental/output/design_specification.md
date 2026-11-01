# Poster Design Specification & Production Report

## 1. Executive Specification Summary

```text
Poster Template : experimental-research
Orientation     : Landscape
Dimensions      : 64.0 × 36.0 in (1625.6 × 914.4 mm) *(Explicitly configured)*
Layout Recipe   : results_focused
Masthead Style  : split_accent_header
Typography      : IBM Plex Sans + Source Serif 4
Color Palette   : Charcoal & Warm Ivory (#1E2421 / #FAF9F5 / #B84A27)
Output Bundle   : PPTX + Print PDF (reportlab_vector) + PNG Preview + Markdown Reports
QA Verdict      : WARN (Iterations: 1)
```

## 2. Physical Print & Export Architecture

- **Physical Trim Size:** `64.0 × 36.0 in` (`1625.6 × 914.4 mm`)
- **Bleed / Safe Margin:** Bleed `0.0 in` | Safe Margin `1.05 in`
- **PowerPoint Slide Scale:** 1:2 Proportional Half-Scale (50% in PPTX due to PowerPoint 56-in ceiling — enlarge 200% when printing from PPTX; PDF is 1:1 full size)
- **Editable PPTX Objects:** `18` native shapes/tables/textframes (`0` native Office charts)
- **PDF Export Engine:** `reportlab_vector` — verified `64.0 × 36.0 in` with `5` embedded font resource(s)
- **Color Profile Note:** Authored in `sRGB` for wide-gamut conference inkjet plotters (HP DesignJet / Canon imagePROGRAF / Epson SureColor). If submitting to a commercial CMYK offset press requiring PDF/X-1a, perform an ICC prepress conversion first.

## 3. Typography & Viewing-Distance Scale

- **Heading Font:** Requested `Helvetica` → Resolved `IBM Plex Sans`
- **Body Font:** Requested `Georgia` → Resolved `Source Serif 4`

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
| Body Copy on Canvas | `#1A1E1C` | `#FAF9F5` | **15.99:1** | AAA |
| Callout Copy on Surface Tint | `#1A1E1C` | `#F0EEE6` | **14.5:1** | AAA |
| Masthead Title | `#1E2421` | `#FAF9F5` | **14.99:1** | AAA |

## 5. Scientific Figures Inventory

- **`cfdna_violin` (`violin_plot`):** `24.00 × 11.20 in` exported as vector `.svg`/`.pdf` + `600 DPI` `.png`.
- **`cfdna_cm` (`confusion_matrix`):** `14.00 × 9.80 in` exported as vector `.svg`/`.pdf` + `600 DPI` `.png`.

## 6. Production & Layout Solver Notes

- Poster exceeds PowerPoint's 56-inch canvas limit; used ReportLab vector renderer to emit 1:1 full-size PDF (while .pptx is saved at exact 50% scale for 200% print enlargement).
