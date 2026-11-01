---
name: research-presentation-maker
description: Converts scientific manuscripts, clinical studies, and thesis chapters into assertion-evidence academic slide decks (.pptx with native speaker notes, multi-page vector PDF, contact-sheet PNG preview, and timed speaker_notes.md) for conference talks, journal clubs, thesis defenses, and methodology seminars.
license: MIT
metadata:
  version: "1.0.0"
  domain: "scientific-presentations"
---

# Research Presentation Maker Skill

Build structured, **Assertion-Evidence** scientific presentations (`16:9` widescreen `13.333 × 7.5 in` or `4:3` `10 × 7.5 in`) with native editable PowerPoint shapes, tables, data charts, and **embedded per-slide speaker notes**.

All paths below are relative to `research-presentation-maker/`.

---

## Core Scientific Slide Principles

1. **Assertion-Evidence Titles:** Every content slide headline states a concise scientific finding or methodological claim (`<= 14` words), not a vague topic noun like `"Results II"`.
2. **Anti-Wall-of-Text Discipline:** Keep slide body text `<= 50` words per slide (`<= 4` concise bullets); move detailed narration, statistical caveats, and Q&A defense prep into `speaker_notes`.
3. **Zero Fabricated Study Data:** Never invent sample sizes, p-values, limitations, or literature citations.
4. **Four Deck Archetypes (`templates/deck_archetypes.json`):**
   - `conference-oral-10min` (8–10 slides: Title → Clinical Gap → Study Design → Primary Result → Secondary/Subgroup → Limitations & Conclusion)
   - `journal-club-appraisal` (PICO → Internal Validity/Bias Audit → Endpoints → Clinical Practice Impact)
   - `thesis-defense` (Specific Aims → Methodology → Aim 1–3 Findings → Synthesis & Future Directions)
   - `methodology-seminar` (Problem Formulation → Pipeline Architecture → Benchmarks → Failure Modes)

---

## Workflow

1. Read `docs/presentation-architecture.md` and author `<work_dir>/deck_spec.json`.
2. Generate deck, PDF handout, speaker script, and visual contact sheet:
   ```bash
   python scripts/generate_presentation.py \
     --spec <work_dir>/deck_spec.json \
     --output-dir <work_dir>/output

   python scripts/validate_presentation.py \
     --output-dir <work_dir>/output \
     --spec <work_dir>/deck_spec.json
   ```
3. Inspect `<work_dir>/output/deck_overview.png` to verify every slide's layout, chart legibility, table alignment, and whitespace.
