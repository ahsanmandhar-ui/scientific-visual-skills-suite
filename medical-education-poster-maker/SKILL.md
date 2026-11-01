---
name: medical-education-poster-maker
description: Creates pedagogical medical education teaching posters for medical students, residents, and clinical skills laboratories covering anatomy/physiology integration, pharmacology summary matrices, pathology classifications, branching diagnostic algorithms, and OSCE/OSPE clinical examination guides.
license: MIT
metadata:
  version: "1.0.0"
  domain: "medical-education"
---

# Medical Education Poster Maker Skill

Design structured, high-retention **clinical teaching posters** (`24 × 36 in`, `A1` `23.39 × 33.11 in`, or `A2` `16.54 × 23.39 in`) tailored for medical school teaching wards, pharmacology/pathology review walls, and **OSCE / OSPE clinical skills stations**.

All paths below are relative to `medical-education-poster-maker/`.

---

## Pedagogical Design Rules

1. **Cognitive Chunking Over Textbook Dumping:** Organize content into 4 distinct visual learning modules: (A) Physiological/Pathological Foundation, (B) Branching Diagnostic Algorithm, (C) Structured Pharmacology or Pathology Comparison Matrix, and (D) OSCE/OSPE Practical Checklist & Red Flags.
2. **Accurate Clinical Terminology:** Never invent drug dosages, diagnostic cutoffs, or grading criteria; mark any synthetic teaching cases explicitly.
3. **Deliberate Non-Cliché Palettes:** Use high-contrast academic palettes (`warm_anatomical`, `sage_pharmacology`, `plum_pathology`, `navy_osce`) with `>= 4.5:1` text contrast.

---

## Workflow

1. Read `docs/medical-pedagogy-guide.md` and prepare `<work_dir>/meded_poster_spec.json`.
2. Generate and validate:
   ```bash
   python scripts/generate_meded_poster.py \
     --spec <work_dir>/meded_poster_spec.json \
     --output-dir <work_dir>/output

   python scripts/validate_meded_poster.py \
     --output-dir <work_dir>/output \
     --spec <work_dir>/meded_poster_spec.json
   ```
3. Inspect `<work_dir>/output/meded_poster.png` to verify algorithm arrows, matrix column alignment, and OSCE checklist legibility.
