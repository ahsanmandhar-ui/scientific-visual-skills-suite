# Machine-Learning Sepsis Early Warning Systems in Adult Intensive Care Units: A PRISMA 2020 Systematic Review

**Study Classification:** PRISMA 2020 SYSTEMATIC REVIEW · SYNTHETIC DEMONSTRATION DATA  
**Authors:** Priya Nair, MD¹; Lukas Meyer, PhD²; Mei-Ling Zhou, MSc¹  
**Affiliations:** ¹Institute of Critical Care Informatics; ²Dept. of Health Data Science, Synthetic University Hospital  

## Poster Sections

### 01  Clinical Question & PICOS

- Population: Adult medical/surgical ICU admissions (Sepsis-3 criteria).
- Intervention: Real-time prospective ML sepsis early warning systems.
- Comparator: Standard clinical surveillance or MEWS/SOFA rules.
- Outcomes: Diagnostic discrimination (AUROC), time-to-antimicrobials, and 28-day ICU mortality.

### 02  Search & Appraisal Methods

- Databases: MEDLINE, Embase, CENTRAL, IEEE Xplore (Jan 2018 – Jun 2026).
- Dual independent screening (κ = 0.86); bias appraised via RoB 2 (RCTs) and ROBINS-I (non-randomized studies); certainty graded with GRADE [1].

### 03  PRISMA 2020 Study Selection

- **Rendered Figure Asset:** `prisma_fig.png`
- **Caption:** Figure 1. PRISMA 2020 flow diagram verifying arithmetic count closure across 3,420 records to 18 prospective ICU studies.

### 06  GRADE Certainty & Limitations

- Moderate GRADE certainty for faster antibiotic administration; low-to-moderate certainty for mortality due to workflow co-interventions.
- Unstandardized positive-predictive-value reporting limited quantitative pooling across alert thresholds.

### Synthesis Across 18 Prospective Studies (N = 94,300)

**Key Quantitative Metric:** `−1.8 h Time-to-Antibiotics  |  AUROC 0.87`

Across 6 RCTs and 12 prospective interventional cohorts, multimodal EHR + waveform models achieved median AUROC 0.87 (IQR 0.84–0.90) and shortened antimicrobial initiation by 1.8 hours overall (−2.1 h in huddles-integrated ICUs).

### 04  Prospective Model Discrimination by Architecture

- **Rendered Figure Asset:** `roc_fig.png`
- **Caption:** Figure 2. Summary prospective ROC profiles across model architecture tiers (18 ICU studies, N = 94,300).

### 05  Evidence Summary by Implementation Tier

| Architecture Tier | Studies | Admissions | Median AUROC | Abx Δ (h) | Low/Mod RoB |
| --- | --- | --- | --- | --- | --- |
| Multimodal EHR + Waveform | 7 (3 RCT) | 41,200 | 0.87 (0.84–0.90) | −2.1 h | 6 / 7 (86%) |
| Boosted EHR Labs + Vitals | 6 (2 RCT) | 34,600 | 0.83 (0.80–0.86) | −1.7 h | 4 / 6 (67%) |
| Vitals-Only Rule / Logistic | 5 (1 RCT) | 18,500 | 0.78 (0.74–0.81) | −0.9 h | 2 / 5 (40%) |
| Overall Synthesis | 18 (6 RCT) | 94,300 | 0.84 (0.78–0.89) | −1.8 h | 12 / 18 (67%) |

*RoB 2 applied to randomized trials; ROBINS-I applied to prospective interventional cohorts.*

### 07  Conclusions & Implementation Guidance

Prospective ML sepsis alerts reliably accelerate antibiotic administration only when paired with structured nurse-physician escalation workflows and precision-calibrated alert thresholds (PPV ≥0.30) to prevent alarm fatigue [2].

## References

- [1] Page MJ et al. PRISMA 2020 statement. BMJ 2021;372:n71.
- [2] Adams R et al. Nat Med 2022;28:1455–1460.

## Funding, Disclosures & Correspondence

- Protocol: PROSPERO CRD42026000999-SYN (Synthetic)
- Correspondence: p.nair@synthetic-icu.org
- SYNTHETIC DATASET DISCLOSURE: Simulated review data for skill validation.
