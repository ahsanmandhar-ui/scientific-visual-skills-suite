# `research-poster-maker` — Scientific Research Poster Maker Skill

A portable, production-grade **Agent Skill** (compatible with **Claude Code**, **Cline**, and any client implementing the [Agent Skills Open Specification](https://agentskills.io/specification)) that transforms scientific research manuscripts, conference abstracts, tabular datasets, statistical outputs, and figures into **art-directed, scientifically accurate, conference-ready research posters**.

Designed to produce posters with the restrained editorial craft of *Nature* conferences, *BMJ* meetings, ACC, ASN, European medical congresses, and university research symposia—never generic AI infographics.

---

## Key Capabilities

- **18-Field Scientific Input Extraction (`scripts/analyze_research.py`):** Parses `.docx`, `.pdf`, `.md`, `.txt`, `.json`, `.csv`, `.xlsx`, and image assets into a structured 18-field schema, auditing missing fields explicitly without fabricating numbers, citations, or affiliations.
- **Exact-Metrics Design & Layout Engine (`scripts/generate_poster.py`):** Measures real TrueType glyph outlines (`Source Sans 3`, `Source Serif 4`, `IBM Plex Sans`, or installed system fonts) to solve physical coordinates in inches across **10+ board presets and custom conference dimensions** without text clipping, object collisions, or illegibly shrunk fonts.
- **8 Architectural Layout Strategies:**
  1. `three_column_classic` — Traditional academic three-column (`31% : 38% : 31%`)
  2. `two_column_editorial` — Journal-inspired portrait/concise two-column (`42% : 58%`)
  3. `asymmetric_grid` — Wide central evidence stage (`26% : 48% : 26%`)
  4. `results_focused` — Headline empirical takeaway band + 3-column evidence grid
  5. `timeline_flow` — Full-width upper longitudinal protocol/surveillance ribbon + 3 columns
  6. `central_visual` — Commanding central visual anchor with flanking sections
  7. `clinical_workflow` — Clinical translational flow (Cohort/CONSORT → Endpoint → Practice)
  8. `systematic_review_prisma` — PRISMA 2020 flow + quantitative Forest/Funnel synthesis
- **15 Genuine Scientific Visualization Types (`scripts/generate_charts.py`):**
  - Quantitative plots: `bar_chart` (mandatory zero baseline), `forest_plot` (weights, pooled diamond, 95% prediction interval, $I^2$, $\tau^2$, $Q$), `funnel_plot`, `kaplan_meier` (with aligned Number-at-Risk table), `roc_curve`, `confusion_matrix`, `scatter_plot` (and longitudinal incidence curves), `box_plot`, `violin_plot`.
  - Methodological diagrams: `prisma_diagram` (PRISMA 2020 with arithmetic count-closure check), `consort_diagram` (CONSORT with count-closure check), `flow_diagram`, `workflow_diagram`.
  - Evidence tables: `characteristics_table`, `statistical_table` (plus native editable PowerPoint booktabs tables).
- **Multi-Layer Quality Assurance (`scripts/validate_poster.py`):** Audits physical dimensions, slide bounds, shape overlaps, minimum font floors, image print PPI, PDF `MediaBox` & embedded fonts, numerical provenance against source files, citation consistency, WCAG 2.1 contrast ratios, and rendered PNG visual density/balance.

---

## Directory Structure

```text
research-poster-maker/
├── SKILL.md                        # Concise Agent Skills entry point & workflow
├── requirements.txt                # Lightweight CPU-only Python dependencies
├── assets/
│   └── fonts/                      # Bundled SIL OFL TrueType families + licenses
├── docs/
│   ├── design-system.md            # Color palettes, 60-30-10 rules & anti-patterns
│   ├── typography.md               # Font pairings, viewing-distance scales & floors
│   ├── scientific-integrity.md     # 18-field schema & zero-fabrication rules
│   ├── print-specifications.md     # ISO/US board sizes, 56-in PPTX limit, DPI & bleed
│   ├── layout-recipes.md           # Blueprints for all 8 layout strategies
│   ├── visualization-guide.md      # Rules for all 15 chart & diagram types
│   ├── accessibility.md            # WCAG 2.1 contrast & Okabe-Ito colorblind safety
│   └── references.md               # University, EQUATOR, conference & tool citations
├── templates/
│   ├── clinical-research/          # Clinical trials & observational cohorts
│   ├── systematic-review/          # PRISMA 2020 systematic reviews
│   ├── meta-analysis/              # Quantitative pooled syntheses & forest plots
│   ├── experimental-research/      # Basic/translational science & biomarker validation
│   ├── epidemiology/               # Population surveillance & cohort incidence
│   └── minimalist-editorial/       # Swiss editorial & concise abstract posters
├── scripts/
│   ├── analyze_research.py         # Phase 3: Manuscript/dataset/image analyzer
│   ├── generate_charts.py          # Phase 5: Vector SVG/PDF + 300/600-DPI chart engine
│   ├── generate_poster.py          # Master orchestrator + iterative QA loop
│   ├── export_poster.py            # Phase 7: LibreOffice / ReportLab vector PDF + TIFF
│   ├── generate_preview.py         # Phase 7/8: PyMuPDF / pdftoppm PNG preview renderer
│   ├── validate_poster.py          # Phase 8: Technical, scientific & visual QA validator
│   ├── verify_skill_compat.py      # Claude Code & Cline portability verifier
│   └── poster_engine/              # Modular internal layout, token, PPTX & PDF engine
├── examples/
│   ├── example_clinical_poster/    # Complete clinical cohort poster bundle (synthetic)
│   └── example_meta_analysis_poster/ # Complete meta-analysis forest poster (synthetic)
└── tests/
    ├── run_all_tests.py            # Reproducible 6-scenario end-to-end test suite
    └── TEST_REPORT.md              # Verified QA & portability audit report
```

---

## Supported Inputs & Output Deliverables

### Supported Research Inputs
- **Manuscripts & Proposals:** `.docx`, `.pdf`, `.md`, `.txt`, `.json`
- **Tabular Data & Statistical Output:** `.csv`, `.xlsx`
- **Figures & Institutional Branding:** `.svg`, `.png`, `.jpg`, `.tiff`

### Output Formats
- **Mandatory Deliverables (generated in `<output_dir>`):**
  1. `poster.pptx` — Editable native PowerPoint poster (shapes, text runs, booktabs tables, charts/figures).
  2. `poster.pdf` — Print-ready PDF verified at exact physical board dimensions with embedded TrueType font subsets and vector figures.
  3. `poster_preview.png` — Full-poster rasterized preview image for visual QA and sharing.
  4. `poster_content.md` — Structured poster prose, tables, captions, and explicit missing-data disclosures.
  5. `design_specification.md` — Physical print specs, scale factors, font audit, WCAG contrast table, and QA summary (paired with `validation_report.md`).
- **Optional Deliverables:**
  - Individual vector `.svg` and `.pdf` scientific figures (`<output_dir>/figures/`).
  - High-resolution LZW-compressed `.tiff` (`--tiff`).
  - Vector/high-DPI study QR code (`study_url` in spec).
  - Safe-margin QA overlay (`generate_preview.py --qa-grid`).

---

## Dependencies & Hardware Requirements

Runs on ordinary **Windows, macOS, and Linux** laptops/workstations (CPU-only; no GPU, local LLM, or cloud API required).

```bash
pip install -r requirements.txt
```

- **Core packages:** `python-pptx`, `matplotlib`, `numpy`, `Pillow`, `reportlab`, `svglib`, `pypdf`, `fonttools`, `pymupdf`.
- **Optional packages:** `python-docx` (for `.docx` input), `openpyxl` (for `.xlsx` input), `pdfplumber` (enhanced PDF table extraction), `qrcode` (for QR code generation), `pandas`.
- **Optional system binary:** `libreoffice` (`soffice`) if direct Impress PPTX-to-PDF conversion is desired; when absent, `export_poster.py` uses its built-in `reportlab_vector` + `svglib` vector PDF engine transparently.

---

## Installation for Claude Code & Cline

Keep one canonical copy of `research-poster-maker` and copy or symlink it into your agent's skill directory—**no code changes or duplication required**.

### Claude Code Installation

- **Project-scoped (shared with repository collaborators):**
  ```text
  .claude/skills/research-poster-maker/
  ```
  ```bash
  mkdir -p .claude/skills
  cp -R /path/to/research-poster-maker .claude/skills/research-poster-maker
  # Or symlink without duplicating files:
  ln -s /path/to/research-poster-maker .claude/skills/research-poster-maker
  ```
- **Personal / Global (available across all projects on your machine):**
  - macOS / Linux: `~/.claude/skills/research-poster-maker/`
  - Windows: `C:\Users\<username>\.claude\skills\research-poster-maker\`

Invoke automatically by asking Claude Code to create a scientific poster, or invoke explicitly via `/research-poster-maker`.

### Cline Installation

- **Project-scoped (workspace skill):**
  ```text
  .cline/skills/research-poster-maker/
  ```
  ```bash
  mkdir -p .cline/skills
  cp -R /path/to/research-poster-maker .cline/skills/research-poster-maker
  # Or symlink:
  ln -s /path/to/research-poster-maker .cline/skills/research-poster-maker
  ```
- **Global (available across all VS Code workspaces):**
  - macOS / Linux: `~/.cline/skills/research-poster-maker/`
  - Windows: `%USERPROFILE%\.cline\skills\research-poster-maker\`

Ensure Skills are enabled in Cline Settings → Features → Enable Skills, then trigger naturally in chat or via `/research-poster-maker`.

---

## Usage Examples

### 1. Interactive Agent Prompts (Claude Code / Cline)

- *"Create an A0 portrait PRISMA 2020 systematic review and meta-analysis poster from `manuscript.pdf` and `trial_effects.csv` for the European Renal Association congress."*
- *"Turn `adhf_cohort.docx`, `survival_counts.csv`, and `hospital_logo.png` into a 48 × 36 inch clinical research poster with a Kaplan-Meier curve and QR link to `https://doi.org/...`."*
- *"Design a minimalist 36 × 48 inch symposium poster strictly from `abstract.txt`—do not invent any missing numbers or citations."*

### 2. Direct CLI Execution

```bash
# Step 1: Analyze source manuscript & datasets
python scripts/analyze_research.py \
  examples/example_clinical_poster/inputs/ \
  --output-dir build_clinical/analysis

# Step 2: Generate full poster bundle (PPTX + Vector PDF + PNG + Reports + QA)
python scripts/generate_poster.py \
  --spec examples/example_clinical_poster/poster_spec.json \
  --extraction build_clinical/analysis/research_extraction.json \
  --output-dir build_clinical/output

# Step 3: Re-validate or export custom TIFF independently if needed
python scripts/validate_poster.py \
  --output-dir build_clinical/output \
  --spec examples/example_clinical_poster/poster_spec.json

# Step 4: Run full 6-scenario QA & agent compatibility suite
python tests/run_all_tests.py
```

---

## Validation Procedures

Every generated poster runs through four automated validation layers in `scripts/validate_poster.py`:

1. **Technical Validation:** Verifies all 5 mandatory files exist, single-slide PPTX dimensions & orientation match target (accounting for `0.5×` scale when `>56 in`), zero out-of-bounds shapes, zero unintended object overlaps, minimum effective font sizes respected, raster PPI audited honestly (`>=150 PPI` warning floor, `300 PPI` target), chart references intact, and PDF `MediaBox` + embedded `/Font` resources verified via `pypdf`.
2. **Scientific Integrity Validation:** Audits title/author consistency, bracketed citation matching (`[1]`, `[2]`), analytical figure captions, significance-language calibration, and **decimal numerical provenance** against the supplied source files.
3. **Accessibility Validation:** Verifies WCAG 2.1 luminance contrast ratios (`>=4.5:1` AA hard minimum; all built-in palettes exceed `15:1` AAA on body copy) and Okabe-Ito colorblind-safe chart series.
4. **Visual Composition QA:** Inspects `poster_preview.png` pixel luminance arrays to verify clean outer safe margins, balanced body ink density (`~8%–38%`), and lateral column visual weight, paired with multimodal agent image inspection.

---

## Honest Technical Limitations & Troubleshooting

1. **PowerPoint's 56-Inch Slide Limit (`142.24 cm`):**
   - Microsoft PowerPoint cannot save a slide wider or taller than `56.0 in`. When you request a custom board exceeding `56 in` (e.g., `64 × 36 in` or `72 × 36 in`), `generate_poster.py` builds `poster.pptx` at **exact 50% proportional scale** (`32 × 18 in` with `600 DPI` chart PNGs) for **200% print enlargement**, while `poster.pdf` (via `reportlab_vector`) is exported at **100% full physical dimensions** (`64 × 36 in`). Always inform the print shop when printing from a half-scale `.pptx`.
2. **PDF Export Engines (`libreoffice` vs. `reportlab_vector`):**
   - When LibreOffice is absent, `export_poster.py` renders `poster.pdf` directly from the poster's unified scene-graph IR using `reportlab` + `svglib`. This guarantees exact physical PDF dimensions, embedded TrueType subsets, and infinite-resolution vector charts, though subtle line-wrap differences can occur if you subsequently edit `poster.pptx` manually in desktop PowerPoint without re-exporting from PowerPoint.
3. **Color Space (`sRGB` vs. Offset `CMYK`):**
   - Outputs use `sRGB`, which university and conference wide-gamut aqueous plotters (HP DesignJet, Canon imagePROGRAF, Epson SureColor) print natively via onboard ICC profiles. If a commercial lithographic press mandates `CMYK PDF/X-1a`, convert the PDF in Adobe Acrobat Pro or Ghostscript with the press's ICC profile prior to submission.
4. **Low-Resolution Source Photographs:**
   - The skill never upscales a low-resolution user image to fake 300 DPI. If `validate_poster.py` emits an `IMAGE_RESOLUTION_PPI` warning (`<150 PPI`), replace the source figure with a vector export or higher-resolution original, or reduce its physical display width on the poster.
5. **Font Availability Across Machines:**
   - Bundled SIL OFL fonts (`Source Sans 3`, `Source Serif 4`, `IBM Plex Sans`) render identically everywhere for PDFs, charts, and previews. When opening `poster.pptx` in desktop PowerPoint on a machine lacking those fonts, install the `.ttf` files from `assets/fonts/` or select system-universal fonts (`Arial` / `Georgia`).
