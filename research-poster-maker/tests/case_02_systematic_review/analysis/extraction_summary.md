# Research Input Analysis Report

- **Source Files Analyzed:** 2
- **Source Word Count:** 192 words
- **Canonical Fields Extracted:** 10 / 18

## Recommended Poster Direction

- **Template:** `systematic-review`
- **Layout Recipe:** `systematic_review_prisma`
- **Color Palette:** `deep_teal`
- **Typography Pairing:** `editorial_modern`
- **Rationale:** Detected systematic review / PRISMA screening methodology.

## Missing Information Audit (Zero-Fabrication Check)

### Essential Fields Not Found in Source (Clarification Recommended)
- [ ] 6. Study design
- [ ] 8. Study population
- [ ] 11. Primary outcome

### Optional / Secondary Fields Not Present (Omit Cleanly Unless Supplied)
- 4. Research gap
- 10. Statistical methods
- 12. Secondary outcomes
- 17. References
- 18. Funding and acknowledgements

## Extracted 18-Field Summary

### 1. Research title
Machine-Learning Sepsis Early Warning Systems in Adult ICUs: A Synthetic PRISMA 2020 Systematic Re

### 2. Authors and affiliations
Priya Nair, MD; Lukas Meyer, PhD; Mei-Ling Zhou, MSc | Affiliations: Institute of Critical Care Informatics, Synthetic University Hospital (SYNTHETIC DATA)

### 3. Background
Automated sepsis alerts aim to shorten time-to-antibiotics in adult intensive care units, yet
prospective clinical impact remains heterogeneous.

### 4. Research gap
_Not present in supplied source material._

### 5. Objectives
Synthesize prospective ICU implementations evaluating mortality, antibiotic timing, and false
-alarm burden under PRISMA 2020 guidelines.

### 6. Study design
_Not present in supplied source material._

### 7. Methods
MEDLINE, Embase, Cochrane CENTRAL, and IEEE Xplore were searched through June 2026 (PROSPERO CRD
42026000999-SYN). Risk of bias was assessed via ROBINS-I and RoB 2.

### 8. Study population
_Not present in supplied source material._

### 9. Sample size
3,420 records; N = 94,300

### 10. Statistical methods
_Not present in supplied source material._

### 11. Primary outcome
_Not present in supplied source material._

### 12. Secondary outcomes
_Not present in supplied source material._

### 13. Important findings
Of 3,420 records identified (610 duplicates removed), 2,810 titles/abstracts were screened, 2,66
4 excluded, 146 full texts assessed, 128 excluded, and 18 prospective studies (N = 94,300 ICU admissions; 6 RCTs, 12 interventional cohorts) were included.
Waveform+EHR multimodal models achieved median AUROC 0.87 (IQR 0.84-0.90) vs 0.78 (0.74-0.81) for vitals-
only alerts, reducing median time-to-antimicrobials by 1.8 hours.

### 14. Tables and figures
```json
{
  "manuscript_tables": [],
  "datasets": [
    {
      "file": "/home/user/research-poster-maker/tests/case_02_systematic_review/inputs/study_characteristics.xlsx",
      "format": "xlsx",
      "sheets": [
        {
          "sheet": "Included_Studies",
          "row_count": 3,
          "columns": [
            "Tier",
            "Studies (k)",
            "Admissions (N)",
            "Median AUROC",
            "Antibiotic Delta (h)",
            "RoB Low/Mod"
          ],
          "preview_rows": [
            [
              "Multimodal EHR + Waveform",
              "7",
              "41,200",
              "0.87",
              "-2.1 h",
              "6 / 7"
            ],
            [
              "Gradient-Boosted EHR Lab/Vitals",
              "6",
              "34,600",
              "0.83",
              "-1.7 h",
              "4 / 6"
            ],
            [
              "Rule/Logistic Vitals-Only",
              "5",
              "18,500",
              "0.78",
              "-0.9 h",
              "2 / 5"
            ]
          ]
        }
      ]
    }
  ],
  "images": []
}
```

### 15. Limitations
High alert fatigue in uncalibrated thresholds; heterogeneous Sepsis-3 adjudication across si
tes.

### 16. Conclusion
Prospective ICU sepsis warning systems consistently accelerate antimicrobial delivery, while
mortality benefit clusters in studies pairing human nurse-physician workflow integration.

### 17. References
_Not present in supplied source material._

### 18. Funding and acknowledgements
_Not present in supplied source material._
