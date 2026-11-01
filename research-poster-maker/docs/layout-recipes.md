# Poster Layout Recipes & Composition Strategies

`research-poster-maker` implements **eight distinct architectural layout recipes**, avoiding generic cookie-cutter card grids. Each recipe defines exact column proportions, reading trajectory, focal anchor location, and compatible study types.

---

## Overview of the 8 Composition Strategies

| Recipe ID | Name | Preferred Orientation | Column Proportions | Primary Focal Point | Ideal Study Designs |
|---|---|---|---|---|---|
| `three_column_classic` | Traditional Three-Column | Landscape (`48×36`, `A0-L`, `56×42`) | `31% : 38% : 31%` | Top of Column 2 (Primary Outcome + Hero Figure) | Experimental studies, RCTs, observational cohorts |
| `two_column_editorial` | Two-Column Editorial | Portrait (`A0-P`, `36×48`, `A1-P`) or Compact | `42% : 58%` | Upper-Right Showcase Zone (Column 2) | Portrait posters, concise research abstracts, humanities/policy |
| `asymmetric_grid` | Asymmetric Scientific Grid | Landscape (`48×36`, `56×42`) | `26% : 48% : 26%` | Wide Double-Weight Center Showcase (`48%`) | Multi-panel results, biomarker studies, clinical imaging/omics |
| `results_focused` | Results-Focused Scientific | Landscape or Portrait | Full-width Headline Findings Band + `27% : 46% : 27%` | Headline empirical takeaway bar + central chart stack | High-impact conference sessions where rapid 3m comprehension is paramount |
| `timeline_flow` | Timeline-Based Longitudinal | Landscape (`48×36`, `56×42`, `36×24`) | Full-width Upper Study Timeline Band + `33% : 34% : 33%` | Longitudinal milestone/exposure ribbon across upper body | Prospective cohorts, longitudinal epidemiology, multi-stage interventions |
| `central_visual` | Central Visual Anchor | Landscape or Portrait | `28% : 44% : 28%` (Portrait: Top Context + Central Hero + Bottom 2-Col) | Oversized singular centerpiece visual in center frame | Mechanistic pathways, large survival analyses, network meta-analysis |
| `clinical_workflow` | Clinical Translational Workflow | Landscape (`48×36`, `A0-L`) | `30% : 40% : 30%` | Patient Selection (CONSORT/STROBE) → Endpoint Plot → Clinical Takeaway Box | Clinical trials, diagnostic accuracy (STARD), hospital quality cohorts |
| `systematic_review_prisma` | Systematic Review & Meta-Analysis | Landscape or Portrait (`A0-P`, `48×36`) | `29% : 43% : 28%` (Portrait: `44% : 56%` + Full-Width Forest Zone) | PRISMA 2020 Flow Diagram paired with Forest Plot & Pooled Effect Diamond | PRISMA systematic reviews, pairwise & subgroup meta-analyses |

---

## Detailed Recipe Blueprints

### 1. `three_column_classic` (Traditional Academic Three-Column)
```text
+-----------------------------------------------------------------------+
| MASTHEAD: Study Badge | Title | Authors & Affiliations   [Logo] [QR]  |
+----------------------+-------------------------+----------------------+
| 01 BACKGROUND        | PRIMARY FINDING CALLOUT | 04 SECONDARY &       |
|                      |                         |    SUBGROUP ANALYSES |
| 02 OBJECTIVES        | [ FIGURE 1: PRIMARY     | [ TABLE 1 / FIG 2 ]  |
|                      |   EMPIRICAL EVIDENCE ]  |                      |
| 03 METHODS &         |                         | 05 LIMITATIONS       |
|    POPULATION        |                         | 06 CONCLUSIONS       |
|                      |                         | REFERENCES & FUNDING |
+----------------------+-------------------------+----------------------+
```
- **Reading order:** Top-to-bottom within Column 1 → Column 2 → Column 3.
- **Why it works:** The slightly wider center column (`38%`) prevents figure cramping while preserving classic conference navigation familiarity.

### 2. `two_column_editorial` (Journal-Inspired Two-Column)
```text
+---------------------------------------------------+
| EDITORIAL MASTHEAD (Crisp Light or Deep Banner)   |
| Title, Authors, Affiliations              [Logo]  |
+---------------------+-----------------------------+
| 01 BACKGROUND       | PRIMARY FINDING CALLOUT     |
|                     |                             |
| 02 OBJECTIVES       | [ FIGURE 1: MAIN CHART ]    |
|                     |                             |
| 03 METHODS          | [ TABLE 1 / FIGURE 2 ]      |
|                     |                             |
| 04 LIMITATIONS      | 05 CONCLUSIONS              |
| REFERENCES / FUND.  |                             |
+---------------------+-----------------------------+
```
- **Reading order:** Left narrative/methodology rail (`42%`) → Right empirical evidence & synthesis rail (`58%`).
- **Why it works:** Eliminates narrow 9-inch columns on `A0 Portrait` (`33.1 in` wide) where 3 columns force awkward word hyphenation; keeps line lengths right in the `50–68` character sweet spot.

### 3. `asymmetric_grid` (Asymmetric Showcase Grid)
- **Structure:** `26%` compact context rail | `48%` wide data visualization stage | `26%` interpretation & clinical translation rail.
- **Best for:** Posters with complex wide figures (e.g., multi-subgroup forest plots, wide Kaplan-Meier survival curves with at-risk tables, or side-by-side ROC + calibration curves).

### 4. `results_focused` (Empirical Takeaway-First Layout)
- **Structure:** Immediately beneath the masthead sits a restrained **Empirical Headline Strip** stating the primary quantitative finding in plain scientific language (backed by exact effect estimate, 95% CI, and *p*-value), followed by a 3-column evidence grid (`27% : 46% : 27%`).
- **Design guardrail:** Unlike gimmicky giant-billboard posters that leave 60% of the board blank with one sentence, this academic adaptation retains full methodological rigor, real data visualizations, limitations, and references while giving 3-meter passersby immediate clarity.

### 5. `timeline_flow` (Longitudinal / Protocol Timeline Layout)
- **Structure:** Upper horizontal **Study Architecture & Follow-Up Ribbon** (`workflow_diagram` spanning full content width) illustrating baseline enrollment, exposure/intervention windows, follow-up person-years, and outcome ascertainment, above a balanced 3-column grid for Cohort Characteristics, Incidence/Hazard Curves, and Public Health Conclusions.

### 6. `central_visual` (Central Visual Anchor)
- **Structure:** Centers a commanding visual artifact (`44%` width in landscape; full-width middle band in portrait) framed by generous whitespace, surrounded by concise supporting sections.

### 7. `clinical_workflow` (Clinical Translational Layout)
- **Structure:** Column 1 houses *Clinical Rationale*, *Eligibility*, and *CONSORT / Cohort Selection Flow*; Column 2 showcases *Primary Endpoint Callout*, *Primary Survival / Outcome Plot*, and *Baseline/Outcome Table*; Column 3 presents *Safety / Secondary Outcomes*, *Study Limitations*, *Clinical Implications*, and *References*.

### 8. `systematic_review_prisma` (Systematic Review & Meta-Analysis Layout)
- **Structure:**
  - **Column 1 (`29%`):** Clinical Question (PICOS), Search Databases & Dates, Risk-of-Bias / Quality Assessment method, and **PRISMA 2020 Flow Diagram** with verified record counts.
  - **Column 2 (`43%`):** **Pooled Effect Synthesis Callout** (Pooled OR/RR/HR/SMD, 95% CI, $I^2$, $\tau^2$, prediction interval if available) + **Forest Plot** of individual studies and pooled diamond.
  - **Column 3 (`28%`):** Study Characteristics / Subgroup Summary Table, **Funnel Plot** or Heterogeneity / Sensitivity Analysis, Limitations (GRADE certainty if reported), Conclusions, Registration (e.g., PROSPERO ID if supplied), and References.

---

## Overflow & Density Resolution Protocol

When measured section heights exceed column vertical capacity:
1. **Never shrink global font sizes below reference floors.**
2. **Re-partition flexible middle sections** across adjacent columns while strictly maintaining topological order (`Background < Objectives < Methods < Results < Limitations < Conclusion < References`).
3. **Adjust non-essential vertical whitespace** within safe typographic minimums (`section_gap >= 0.35 in`).
4. **Apply deterministic prose condensation** (trimming redundant introductory clauses while locking every numeric token, CI, sample size, and *p*-value).
5. **Recommend layout upgrade** (e.g., switching `three_column_classic` → `asymmetric_grid`, or switching `A1` → `A0`) if user-supplied tables/figures physically exceed board area.
