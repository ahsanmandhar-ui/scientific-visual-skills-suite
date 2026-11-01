# Poster Quality Assurance & Scientific Validation Report

- **Overall QA Verdict:** **WARN**
- **Checks Passed:** 14  |  **Warnings:** 1  |  **Failures:** 0

## Detailed Check Results

| Category | Check ID | Status | Summary |
|---|---|---|---|
| `technical` | `MANDATORY_OUTPUT_FILES` | **PASS** | All 5 mandatory deliverables exist and are non-empty. |
| `technical` | `PPTX_DIMENSIONS_AND_ORIENTATION` | **PASS** | PPTX single slide verified at effective 64.0 × 36.0 in (scale=0.5x, landscape). |
| `technical` | `BOUNDARY_CONTAINMENT` | **PASS** | Zero shapes extend outside poster boundaries. |
| `technical` | `OBJECT_OVERLAP_CHECK` | **PASS** | Zero unintended shape overlaps detected. |
| `technical` | `TYPOGRAPHY_FLOOR_AND_FONTS` | **WARN** | Minimum effective text size is 20.9 pt (floor 18.0 pt). Font fallback logged: Requested font 'Helvetica' is not installed locally; resolved to metrically verified 'IBM Plex Sans' for layout, charts, and PDF embedding.; Requested font 'Georgia' is not installed locally; resolved to metrically verified 'Source Serif 4' for layout, charts, and PDF embedding. |
| `technical` | `IMAGE_RESOLUTION_PPI` | **PASS** | Inspected 2 embedded image(s); all meet >=250–300 PPI print target. |
| `technical` | `CHART_INTEGRITY` | **PASS** | All embedded chart references intact. |
| `technical` | `PDF_DIMENSIONS_AND_EMBEDDED_FONTS` | **PASS** | PDF verified: 1 page, 64.0 × 36.0 in (1625.6 × 914.4 mm), 5 embedded font resource(s). |
| `scientific` | `TITLE_AND_AUTHOR_CONSISTENCY` | **PASS** | Poster title and author block match source specification. |
| `scientific` | `REFERENCE_CONSISTENCY` | **PASS** | Verified 0 reference entry/entries. |
| `scientific` | `NUMERICAL_PROVENANCE_CHECK` | **PASS** | All 2 decimal statistical value(s) on poster trace directly to supplied source data. |
| `scientific` | `FIGURE_CAPTION_CONSISTENCY` | **PASS** | All 2 primary/secondary figure(s) carry analytical captions. |
| `scientific` | `CONCLUSION_STATISTICAL_CALIBRATION` | **PASS** | Conclusions and statistical significance language are appropriately calibrated. |
| `accessibility` | `WCAG_COLOR_CONTRAST` | **PASS** | WCAG 2.1 contrast verified — Body/Canvas: 15.99:1, Callout: 14.5:1, Masthead: 14.99:1 (minimum 4.5:1 AA; 7.0:1 AAA). |
| `visual` | `RENDERED_VISUAL_COMPOSITION` | **PASS** | Rendered preview (3456×1944 px): body ink density=10.3%, whitespace=89.7%, lateral balance Δ=10.1%, safe-margin perimeter clean=True. |
