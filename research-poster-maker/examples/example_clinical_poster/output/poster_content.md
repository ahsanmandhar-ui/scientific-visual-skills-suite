# Early SGLT2 Inhibitor Initiation Within 72 Hours of Acute Heart Failure Admission and 24-Month Cardiorenal Outcomes

**Study Classification:** MULTICENTER OBSERVATIONAL COHORT · STROBE · SYNTHETIC DEMO DATA  
**Authors:** Elena Rostova, MD, PhD¹; Marcus Vance, MD¹; Tariq Al-Mansoor, MPH²; Hannah Lindqvist, PhD²  
**Affiliations:** ¹Dept. of Cardiovascular Medicine, Synthetic Academic Health Network; ²Center for Clinical Biostatistics (Synthetic Demonstration Study)  

## Poster Sections

### 01  Clinical Background & Objective

Acute decompensated heart failure (ADHF) hospitalization marks high vulnerability for recurrent congestion and progressive kidney decline [1]. Whether initiating SGLT2 inhibitors within 72 hours of inpatient stabilization improves 24-month cardiorenal survival across ejection fraction strata remains uncertain.

- Primary Objective: Compare 24-month composite cardiovascular death, HF rehospitalization, or ≥40% sustained eGFR decline between early inpatient SGLT2i (≤72 h) vs. standard post-discharge care.

### 02  Cohort Derivation & Propensity Weighting

- **Rendered Figure Asset:** `methods_flow.png`
- **Caption:** Figure 1. STROBE cohort selection across 19 hospitals (N = 4,820; synthetic cohort).

### 03  Statistical Architecture

- Exposure: Empagliflozin or dapagliflozin started ≤72 h of IV loop diuretic stabilization.
- Models: Overlap propensity-weighted Cox models & Fine-Gray competing-risk regression adjusted for age, LVEF, NT-proBNP, baseline eGFR, and background GDMT [2].

### Primary 24-Month Cardiorenal Composite

**Key Quantitative Metric:** `aHR 0.68 (95% CI 0.56–0.82; p = 0.0001)`

Early SGLT2i initiation reduced cumulative 24-month event incidence from 29.8% (718/2,410) to 21.4% (516/2,410), corresponding to an absolute risk reduction of 8.4% (NNT = 12).

### 04  24-Month Event-Free Survival

- **Rendered Figure Asset:** `km_figure.png`
- **Caption:** Figure 2. Overlap-weighted Kaplan-Meier cardiorenal event-free survival with shaded 95% CIs and aligned number at risk (N = 4,820).

### 05  Component & Safety Endpoints

| Outcome (24 Months) | Early SGLT2i | Standard | aHR (95% CI) | p-value |
| --- | --- | --- | --- | --- |
| Primary composite | 21.4% | 29.8% | 0.68 (0.56–0.82) | 0.0001 |
| HF rehospitalization | 14.8% | 21.9% | 0.65 (0.53–0.80) | 0.0002 |
| CV mortality | 6.9% | 8.8% | 0.78 (0.61–0.99) | 0.041 |
| ≥40% eGFR decline | 5.2% | 7.3% | 0.71 (0.55–0.92) | 0.009 |
| HFrEF (<40%) stratum | 22.1% | 31.0% | 0.67 (0.54–0.83) | 0.0003 |
| HFpEF (≥50%) stratum | 20.3% | 28.1% | 0.70 (0.55–0.89) | 0.004 |
| Euglycemic DKA (safety) | 0.4% | 0.3% | 1.31 (0.52–3.30) | 0.56 |

*Subgroup p-interaction by LVEF phenotype = 0.64. Euglycemic DKA was exploratory safety outcome.*

### 06  Strengths & Limitations

- Strengths: Active-comparator new-user design across 19 centers with adjudicated renal laboratory trajectories.
- Limitations: Residual confounding by unmeasured inpatient diuretic responsiveness cannot be excluded; post-12-month adherence relied on dispensation claims.

### Clinical Conclusions

Initiating SGLT2 therapy within 72 hours of inpatient ADHF stabilization was associated with a 32% relative hazard reduction in 24-month cardiorenal events across HFrEF and HFpEF phenotypes, without excess ketoacidosis or acute renal injury.

## References

- [1] Voors AA et al. Nat Med 2022;28:568–574.
- [2] Li F, Morgan KL, Zaslavsky AM. JASA 2018;113:390–400.

## Funding, Disclosures & Correspondence

- Funding: Synthetic Translational Grant SYN-2026-014
- Correspondence: e.rostova@synthetic-ahn.org
- SYNTHETIC DATASET DISCLOSURE: Simulated cohort created strictly for poster skill testing.
