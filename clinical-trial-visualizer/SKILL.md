---
name: clinical-trial-visualizer
description: Generates EQUATOR/CONSORT-compliant clinical trial flow diagrams, randomization and allocation schemas, SPIRIT-style treatment timelines, primary/secondary endpoint summaries, and CTCAE adverse-event butterfly plots with strict participant count-closure validation.
license: MIT
metadata:
  version: "1.0.0"
  domain: "clinical-trials"
---

# Clinical Trial Visualizer Skill

Create rigorous, audit-verified visual summaries and diagrams for randomized and non-randomized interventional clinical trials (`CONSORT 2010/2025` participant flow, `SPIRIT` protocol timelines, efficacy endpoints, and `CTCAE` safety profiles).

All paths below are relative to `clinical-trial-visualizer/`.

---

## Non-Negotiable Trial Reporting Rules

1. **CONSORT Arithmetic Count Closure:** Every participant must be accounted for across all 4 phases (`Enrollment`, `Allocation`, `Follow-Up`, `Analysis`):
   - `assessed - sum(excluded_reasons) == randomized`
   - `sum(arm.allocated) == randomized`
   - If `analysis_population == "ITT"`, `analyzed == allocated` with explicit exclusion-from-analysis notes; otherwise `allocated - lost_to_followup == analyzed`.
   - `scripts/validate_clinical_trial.py` **FAILs** any diagram with unclosed participant arithmetic.
2. **Complete Safety & Efficacy Attribution:** Report exact denominators (`n / N (%)`), effect estimates with `95% CI`, and distinguish all-grade adverse events from Grade `>= 3` serious/severe events.

---

## Workflow

1. Read `docs/consort-and-spirit-guide.md` and structure `<work_dir>/trial_spec.json` (`mode`: `"composite_summary"` or `"consort_only"`).
2. Generate and validate:
   ```bash
   python scripts/generate_clinical_trial.py \
     --spec <work_dir>/trial_spec.json \
     --output-dir <work_dir>/output

   python scripts/validate_clinical_trial.py \
     --output-dir <work_dir>/output \
     --spec <work_dir>/trial_spec.json
   ```
3. Visually inspect `<work_dir>/output/clinical_trial_visual.png` to confirm box legibility, arrow alignment, timeline clarity, and safety chart spacing.
