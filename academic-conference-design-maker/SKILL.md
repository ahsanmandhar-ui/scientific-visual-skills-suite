---
name: academic-conference-design-maker
description: Creates a unified visual identity and complete communication kit for academic conferences, symposia, and workshops—generating stage/web banners, A4 abstract-book covers, event call-for-papers posters, presenter certificates, keynote speaker spotlight cards, and social media announcements.
license: MIT
metadata:
  version: "1.0.0"
  domain: "academic-events"
---

# Academic Conference Design Maker Skill

Build a cohesive, institution-grade **visual identity system** across all 6 core academic conference deliverables from a single structured specification (`conference_spec.json`), guaranteeing unified typography, shared geometric scientific motif, and consistent color tokens across print and digital assets.

All paths below are relative to `academic-conference-design-maker/`.

---

## Complete 6-Asset Conference Suite

1. **Conference Banner (`banner.pdf`, `banner.png`):** `24 × 8 in` (`3:1`) stage backdrop / website header banner.
2. **Abstract-Book Cover (`abstract_book_cover.pdf`, `abstract_book_cover.png`):** ISO `A4` (`8.27 × 11.69 in`) proceedings cover with volume/ISSN metadata, dates, venue, and host society.
3. **Event / Call-for-Abstracts Poster (`event_poster.pdf`, `event_poster.png`):** `18 × 24 in` wall/digital poster with submission deadlines, symposium tracks, keynote speakers, and scannable registration QR code.
4. **Certificate of Participation / Presentation (`certificate.pdf`, `certificate.png`, `certificate.pptx`):** `11 × 8.5 in` landscape formal academic certificate with recipient/presentation title, dual signatory blocks, and verification serial ID.
5. **Keynote Speaker Announcement (`speaker_card.png`, `speaker_card.svg`):** `1200 × 1200 px` (`1:1`) speaker spotlight graphic.
6. **Social Media Announcement (`social_card.png`, `social_card.svg`):** `1600 × 900 px` (`16:9`) registration / abstract-deadline announcement graphic.
7. **Suite Contact Sheet (`kit_overview.png`):** Visual proof displaying all 6 coordinated assets side-by-side.

---

## Workflow

1. Read `docs/conference-identity-guide.md` and prepare `<work_dir>/conference_spec.json` (never invent dates, fees, accreditation credits, or speaker affiliations).
2. Generate and validate the complete kit:
   ```bash
   python scripts/generate_conference_kit.py \
     --spec <work_dir>/conference_spec.json \
     --output-dir <work_dir>/output

   python scripts/validate_conference_kit.py \
     --output-dir <work_dir>/output \
     --spec <work_dir>/conference_spec.json
   ```
3. Visually inspect `<work_dir>/output/kit_overview.png` to verify unified branding, legibility, and zero text overlap across all 6 assets.
