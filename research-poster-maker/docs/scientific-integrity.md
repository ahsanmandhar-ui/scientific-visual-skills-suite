# Scientific Integrity & Content Extraction Protocol

Scientific accuracy supersedes aesthetic convenience in every decision made by `research-poster-maker`.

---

## 1. The 18-Field Canonical Extraction Schema

Before any layout or visual design occurs, `scripts/analyze_research.py` (and the interactive agent workflow) extracts and structures source material into 18 canonical fields:

| # | Field Key | Poster Priority | Extraction & Distillation Rule |
|---|---|---|---|
| 1 | `title` | **Essential** | Exact study title (preserve study design descriptors, trial acronyms, and clinical accuracy). |
| 2 | `authors_affiliations` | **Essential** | Exact author list in source order mapped to institutional affiliations via superscript indices. |
| 3 | `background` | **Essential** | 2–3 concise sentences or bullets establishing clinical/scientific context. |
| 4 | `research_gap` | **High** | 1 crisp statement identifying what remained unknown or unresolved prior to this study. |
| 5 | `objectives` | **Essential** | Primary hypothesis or study aim(s), stated precisely. |
| 6 | `study_design` | **Essential** | Explicit design classification (e.g., *Prospective Multicenter Cohort*, *Double-Blind RCT*, *PRISMA 2020 Systematic Review & Meta-Analysis*). |
| 7 | `methods` | **Essential** | Concise summary of exposures/interventions, ascertainment, and protocol procedures. |
| 8 | `study_population` | **Essential** | Setting, eligibility criteria, dates, and demographic summary. |
| 9 | `sample_size` | **Essential** | Exact total `N` and group/arm `n` values; flag any discrepancy between abstract, text, and tables. |
| 10 | `statistical_methods` | **High** | Models used (e.g., Cox proportional hazards, DerSimonian–Laird / REML random-effects), covariates, significance threshold. |
| 11 | `primary_outcome` | **Essential** | Primary endpoint definition, exact effect size, 95% CI, and *p*-value. |
| 12 | `secondary_outcomes` | **Optional / Moderate** | Key secondary or subgroup endpoints; explicitly label exploratory/post-hoc analyses as exploratory. |
| 13 | `important_findings` | **Essential** | Quantitative synthesis of core empirical findings (never vague claims without numbers when numbers exist). |
| 14 | `tables_and_figures` | **Essential (if data exist)** | Source datasets, extracted tables, PRISMA/CONSORT counts, or supplied high-res figures. |
| 15 | `limitations` | **High** | Honest methodological caveats (e.g., residual confounding, heterogeneity, single-center scope, missingness). |
| 16 | `conclusion` | **Essential** | Strictly calibrated to findings—never extrapolate causal claims from observational associations. |
| 17 | `references` | **Moderate (3–6 key refs)** | Select the 3–6 most pertinent citations in compact numbered format; omit only on brief abstract-only posters if zero citations were supplied. |
| 18 | `funding_acknowledgements` | **High (when present)** | Grant numbers, funding agencies, trial/PROSPERO registration IDs, and conflict-of-interest disclosures. |

---

## 2. Hard Rules Against Hallucination & Distortion

1. **Never Invent Missing Data:**
   - If sample size, affiliations, funding, limitations, confidence intervals, or references are absent from the user's input (common when designing from a 250-word conference abstract), record them in `missing_fields` inside `research_extraction.json`.
   - Ask the user concisely for critical missing items (such as author affiliations or conference board dimensions) or omit optional absent sections cleanly—**never insert placeholder fake citations (`Smith et al., 2023`), invented grant numbers, or guessed confidence intervals.**
2. **Preserve Numerical & Statistical Fidelity:**
   - Never round `p = 0.054` to `p = 0.05` or claim statistical significance where the source reports a non-significant trend.
   - Preserve exact decimal precision and units (`mmol/L` vs `mg/dL`, `person-years`, `HR` vs `OR` vs `RR`).
   - Preserve directional framing (`non-inferiority`, `association` vs `causation`, `exploratory subgroup` vs `pre-specified primary endpoint`).
3. **Transform Prose Without Altering Meaning:**
   - Do not paste 300-word manuscript paragraphs verbatim onto the poster.
   - Distill dense paragraphs into crisp structured statements or parallel bullet points (`Lead-in concept: concise empirical detail with exact statistics`).
   - Every numerical token appearing on the generated poster is audited by `scripts/validate_poster.py` against the source corpus (`NUMERICAL_PROVENANCE_CHECK`).
