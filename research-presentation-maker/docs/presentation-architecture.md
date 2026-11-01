# Assertion-Evidence Scientific Presentation Architecture

## 1. Slide Layout Types Supported
- `title`: Full-bleed academic title slide with authors, affiliations, conference/venue badge, and disclosure note.
- `split_evidence`: Left column concise evidence bullets (`<= 4`) + Right column native high-DPI chart (`bar_ci`, `line_series`, `forest`) or process cards.
- `table_summary`: Structured academic booktabs-style comparison or baseline/outcomes table + key callout banner.
- `methodology_flow`: Horizontal 3–5 stage experimental or clinical study workflow with directional connectors.
- `conclusion_takeaways`: Numbered key conclusions + honest study limitations box + QR/DOI reference.

## 2. Speaker Notes & Pacing Standard
- Speaking pace benchmark: `~130 words/minute` (`~60–75 seconds` per slide for a 10-minute conference talk).
- Every slide in `deck.pptx` stores speaker notes in `slide.notes_slide.notes_text_frame` AND exports `speaker_notes.md` with cumulative timestamps (`00:00 -> 10:00`).
