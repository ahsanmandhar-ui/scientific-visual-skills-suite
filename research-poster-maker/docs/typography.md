# Scientific Typography & Hierarchy System

## 1. Core Principles

1. **Maximum Two Font Families:** Pair at most one sans-serif family and one serif family (plus an optional monospace font strictly for genetic sequences, code, or registration IDs). Single-family sans-serif systems (e.g., `Source Sans 3` or `IBM Plex Sans` across weights) are equally authoritative and common in *Nature* and medical meetings.
2. **Physical Viewing Distance Governs Size:** Point sizes (`1 pt = 1/72 inch = 0.3528 mm`) only have meaning relative to final printed dimensions. Never treat a single point-size table as universally mandatory across A2, A1, A0, and 48 × 36 in boards.
3. **Never Shrink All Text to Cure Overcrowding:** If content exceeds column capacity at legible sizes, rewrite prose concisely, prune secondary background points, rebalance columns, or switch layouts.

---

## 2. Recommended Font Pairings & Cross-Platform Fallback Chains

Do not assume proprietary OS fonts (`Helvetica`, `Aptos`, `Georgia`, `Garamond`) are installed on Linux or headless build environments. Always resolve through an explicit fallback chain and log any substitution in the validation report.

| Pairing ID | Role | Primary Choice | Cross-Platform / Bundled OFL Fallbacks | Visual Character |
|---|---|---|---|---|
| `editorial_modern` | Headings & UI / Body | **Source Sans 3** + **Source Serif 4** | `Source Sans 3` -> `DejaVu Sans`; `Source Serif 4` -> `STIXGeneral` -> `DejaVu Serif` | High-impact academic journal feel (*BMJ* / *Lancet* editorial warmth) |
| `clinical_precision` | All-Sans Hierarchy | **IBM Plex Sans** (Bold / SemiBold / Regular) | `IBM Plex Sans` -> `Source Sans 3` -> `Arial` -> `DejaVu Sans` | Crisp clinical clarity, tabular numerals, unambiguous `I`/`l`/`1` |
| `swiss_scientific` | All-Sans Hierarchy | **Inter** or **Helvetica** | `Inter` -> `Helvetica` -> `Arial` -> `Source Sans 3` -> `DejaVu Sans` | Neutral Swiss modernist grid (*Nature* figure aesthetic) |
| `classic_symposium` | Serif Title + Sans Body | **Source Serif 4** / **Georgia** + **Source Sans 3** | `Georgia` -> `Libre Baskerville` -> `Source Serif 4`; `Source Sans 3` -> `Arial` | University symposium, epidemiology, health policy |
| `contemporary_clean` | Geometric Header + Humanist Body | **Montserrat** / **Aptos** + **Source Sans 3** | `Montserrat` -> `Aptos` -> `IBM Plex Sans` -> `Source Sans 3` | Clean contemporary biomedical presentation |

*Bundled OFL Fonts:* This skill bundles SIL Open Font License 1.1 TrueType files for `Source Sans 3`, `Source Serif 4`, and `IBM Plex Sans` in `assets/fonts/` so exact glyph metrics, PDF font embedding, and chart typography work identically on Windows, macOS, and bare Linux without network access.

---

## 3. Dimension-Aware Typographic Scale

Reference sizes below apply to **full-size conference boards** (e.g., `48 × 36 in`, `36 × 48 in`, `A0` `33.1 × 46.8 in`, `42 × 56 in`) printed at 100% scale:

| Element | Reference Target (Full Size) | Reference Floor (Full Size) | Medium Board (`A1` / `36×24 in`) Floor | Weight & Styling | Line Spacing |
|---|---|---|---|---|---|
| **Main Title** | `80 – 96 pt` | `72 pt` (85 pt nominal ref.) | `54 pt` | Bold, sentence case (avoid ALL CAPS titles!) | `1.08 – 1.14×` |
| **Author Names** | `48 – 58 pt` | `40 pt` (56 pt nominal ref.) | `30 pt` | SemiBold or Bold | `1.15×` |
| **Affiliations** | `28 – 36 pt` | `24 pt` | `18 pt` | Regular or Italic, muted ink | `1.15×` |
| **Section Headings** | `36 – 46 pt` | `34 pt` (36 pt nominal ref.) | `26 pt` | Bold, subtle tracking | `1.12×` |
| **Hero Takeaway / Metric** | `44 – 64 pt` | `36 pt` | `28 pt` | Bold tabular numerals | `1.10×` |
| **Subheadings** | `28 – 32 pt` | `26 pt` | `20 pt` | SemiBold | `1.18×` |
| **Body Copy & Bullets** | `24 – 30 pt` | `24 pt` | `18 pt` | Regular (bold lead-in phrases encouraged) | `1.22 – 1.30×` |
| **Table Cells & Figure Labels** | `20 – 26 pt` | `20 pt` | `16 pt` | Regular; Bold column headers | `1.15×` |
| **Captions** | `18 – 22 pt` | `18 pt` | `14 pt` | Regular with Bold `Figure N.` prefix | `1.18×` |
| **References & Disclosures** | `18 – 20 pt` | `18 pt` | `14 pt` | Regular compact | `1.12 – 1.16×` |

> **Half-Scale PowerPoint Note:** When a poster exceeds PowerPoint's `56 in` limit (e.g., `72 × 36 in`) and the `.pptx` is built at 50% physical scale (`36 × 18 in` for 200% print enlargement), point sizes inside the `.pptx` are halved (`42.5 pt` title prints at `85 pt`), and that 50% scale factor is explicitly recorded in metadata so QA validates effective printed size.

---

## 4. Micro-Typography & Scientific Notation Rules

1. **Line Length (Measure):** Target **45 to 75 characters per line** in body columns. On wide landscape layouts (`48 × 36 in` or `56 × 42 in`), use 3 or 4 columns—never span body paragraphs across half the poster width.
2. **Alignment:** Always **left-align (ragged right)** body text and bullet lists. Never full-justify narrow poster columns: full justification creates uneven word rivers that slow comprehension for dyslexic and standing readers.
3. **Sentence Case Titles:** Write poster titles in natural Sentence Case (preserving proper nouns, clinical trial acronyms, and gene/protein casing such as `EGFR`, `SARS-CoV-2`, `HbA1c`). Avoid setting multi-line titles in ALL CAPS.
4. **Statistical & Mathematical Typography:**
   - Use true en-dashes (`–`, U+2013) for numerical ranges and confidence intervals (`95% CI 0.56–0.82`), not hyphens (`-`).
   - Use true minus signs (`−`, U+2212) for negative values (`−3.4 mmHg`).
   - Use proper multiplication (`×`), plus-minus (`±`), inequality (`≤`, `≥`), and superscript (`I²`, `χ²`, `kg/m²`) glyphs verified against the active font's `cmap` table via `fontTools`.
   - Italicize statistical symbols (*p*, *n*, *r*, *t*, *I*²) where supported by rich-text runs; keep numerals and units upright (`p = 0.004`, not `p=.004`).
5. **Word Budget Discipline:**
   - Standard conference poster target: **350 to 650 words** of body prose (excluding tables, chart labels, title/affiliations, and references), never exceeding **800 words** even on dense systematic review boards.
