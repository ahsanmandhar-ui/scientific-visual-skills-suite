# End-to-End Test & Quality Assurance Report

> **Synthetic Data Disclosure:** Every manuscript, dataset, trial table, and abstract in `tests/` and `examples/` uses **explicitly labeled synthetic demonstration data** generated solely to validate layout geometry, chart rendering, missing-data detection, and scientific provenance checks.

## 1. Agent Skills, Claude Code & Cline Compatibility Matrix

**Overall Portability Verdict:** **PASS**

| Check | Status | Details |
|---|---|---|
| `SKILL_MD_EXISTS` | **PASS** | /home/user/research-poster-maker/SKILL.md |
| `AGENTSKILLS_NAME_SPEC` | **PASS** | name='research-poster-maker' (len=21, matches_dir=True) |
| `AGENTSKILLS_DESCRIPTION_SPEC` | **PASS** | description length=480 chars (limit 1024) |
| `PROGRESSIVE_DISCLOSURE_TOKEN_BUDGET` | **PASS** | Level-1 metadata ~125 tokens; Level-2 SKILL.md body ~2255 tokens (<5,000 limit). |
| `REFERENCED_FILES_EXIST` | **PASS** | Verified 13 referenced doc/script path(s). |
| `CLAUDE_CODE_PORTABILITY_TEST` | **PASS** | Installed via symlink at .claude/skills/research-poster-maker/SKILL.md; dir_match=True; script CLI exit=0. |
| `CLINE_PORTABILITY_TEST` | **PASS** | Installed via symlink at .cline/skills/research-poster-maker/SKILL.md; dir_match=True; script CLI exit=0. |

## 2. Poster Generation & Multi-Layer QA Matrix (6 Scenarios)

| Case | Scenario | Physical Dimensions | PPTX Scale | Layout Recipe | Palette | Extracted | QA Verdict | Pass / Warn / Fail |
|---|---|---|---|---|---|---|---|---|
| `case_01_clinical_observational` | Clinical Observational Cohort (48×36 in Landscape) | `48.0 × 36.0 in (landscape)` | `1.0x` | `clinical_workflow` | `academic_navy` | `14/18` | **PASS** | 15 / 0 / 0 |
| `case_02_systematic_review` | PRISMA 2020 Systematic Review (ISO A0 Portrait) | `33.1102 × 46.811 in (portrait)` | `1.0x` | `systematic_review_prisma` | `deep_teal` | `10/18` | **PASS** | 15 / 0 / 0 |
| `case_03_meta_analysis` | Quantitative Meta-Analysis + Forest & Funnel (56×42 in) | `56.0 × 42.0 in (landscape)` | `1.0x` | `systematic_review_prisma` | `burgundy_offwhite` | `11/18` | **PASS** | 15 / 0 / 0 |
| `case_04_epidemiology` | Epidemiological Surveillance + Timeline Band (ISO A0 Landscape) | `46.811 × 33.1102 in (landscape)` | `1.0x` | `timeline_flow` | `forest_cream` | `8/18` | **PASS** | 15 / 0 / 0 |
| `case_05_limited_abstract` | Concise Abstract With Missing Info Audit (36×48 in Portrait) | `36.0 × 48.0 in (portrait)` | `1.0x` | `two_column_editorial` | `monochrome_editorial` | `8/18` | **PASS** | 15 / 0 / 0 |
| `case_06_oversized_experimental` | Oversized 64×36 in (>56 in PPTX Half-Scale) + Experimental | `64.0 × 36.0 in (landscape)` | `0.5x` | `results_focused` | `charcoal_ivory` | `4/18` | **WARN** | 14 / 1 / 0 |

## 3. Per-Scenario Observations & Documented Limitations

### `case_01_clinical_observational` — Clinical Observational Cohort (48×36 in Landscape)
- **Missing Essential Fields Flagged by `analyze_research.py`:** 8. Study population
- All 12 Technical, Scientific Integrity, WCAG 2.1 Contrast, and Image-Based Visual QA checks passed without warnings.

### `case_02_systematic_review` — PRISMA 2020 Systematic Review (ISO A0 Portrait)
- **Missing Essential Fields Flagged by `analyze_research.py`:** 6. Study design, 8. Study population, 11. Primary outcome
- All 12 Technical, Scientific Integrity, WCAG 2.1 Contrast, and Image-Based Visual QA checks passed without warnings.

### `case_03_meta_analysis` — Quantitative Meta-Analysis + Forest & Funnel (56×42 in)
- **Missing Essential Fields Flagged by `analyze_research.py`:** 8. Study population, 11. Primary outcome
- All 12 Technical, Scientific Integrity, WCAG 2.1 Contrast, and Image-Based Visual QA checks passed without warnings.

### `case_04_epidemiology` — Epidemiological Surveillance + Timeline Band (ISO A0 Landscape)
- **Missing Essential Fields Flagged by `analyze_research.py`:** 5. Objectives, 6. Study design, 8. Study population, 9. Sample size, 11. Primary outcome
- All 12 Technical, Scientific Integrity, WCAG 2.1 Contrast, and Image-Based Visual QA checks passed without warnings.

### `case_05_limited_abstract` — Concise Abstract With Missing Info Audit (36×48 in Portrait)
- **Missing Essential Fields Flagged by `analyze_research.py`:** 6. Study design, 8. Study population, 11. Primary outcome
- All 12 Technical, Scientific Integrity, WCAG 2.1 Contrast, and Image-Based Visual QA checks passed without warnings.

### `case_06_oversized_experimental` — Oversized 64×36 in (>56 in PPTX Half-Scale) + Experimental
- **Missing Essential Fields Flagged by `analyze_research.py`:** 3. Background, 5. Objectives, 6. Study design, 7. Methods, 8. Study population, 11. Primary outcome, 16. Conclusion
- **WARN (`TYPOGRAPHY_FLOOR_AND_FONTS`):** Minimum effective text size is 20.9 pt (floor 18.0 pt). Font fallback logged: Requested font 'Helvetica' is not installed locally; resolved to metrically verified 'IBM Plex Sans' for layout, charts, and PDF embedding.; Requested font 'Georgia' is not installed locally; resolved to metrically verified 'Source Serif 4' for layout, charts, and PDF embedding.

## 4. Honest Technical Environment Notes

- **PDF Export Backend:** Where LibreOffice (`soffice`) is not installed, `export_poster.py` uses the native `reportlab_vector` + `svglib` scene renderer. Physical PDF `MediaBox` dimensions match target board sizes within `<0.01 in`, TrueType subsets are embedded directly, and Matplotlib `.svg` plots remain crisp vector paths inside the PDF.
- **Oversized Boards (`>56 in`):** Verified in `case_06_oversized_experimental` (`64 × 36 in`): `.pptx` is generated at `32.0 × 18.0 in` (`0.5×` proportional scale with `600 DPI` chart PNGs for `200%` print enlargement), while `poster.pdf` is generated at true `1:1` (`64.0 × 36.0 in` / `1625.6 × 914.4 mm`).
- **Color Management:** Outputs are authored in `sRGB` suitable for university and conference wide-gamut inkjet plotters; offset CMYK PDF/X conversion is not claimed.
