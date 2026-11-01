# Scientific & Medical Visual Communication Agent Skills Suite (11 Skills)

A complete, CPU-only, cross-platform (`Windows`, `Linux`, `macOS`) suite of **11 portable Agent Skills** compatible with **Claude Code** (`.claude/skills/<skill-name>/`) and **Cline** (`.cline/skills/<skill-name>/`) following the [Agent Skills Open Standard](https://agentskills.io/specification).

Every skill includes:
- Concise progressive-disclosure `SKILL.md` (`< 120` lines) + detailed `docs/` reference specifications
- Domain-calibrated JSON design presets & colorblind-safe editorial palettes (`templates/`)
- Real executable Python generation & preflight QA validation pipelines (`scripts/`)
- Explicitly labeled **synthetic** end-to-end examples & verified vector/high-DPI outputs (`examples/`)

---

## Complete Skill Catalog (11 Skills)

| # | Skill Name | Priority / Role | Key Capabilities & Outputs |
|---|---|---|---|
| **0** | [`research-poster-maker`](./research-poster-maker/README.md) | **Foundation** | Conference posters (`A0`, `A1`, `48×36`, `>56-in` auto `0.5x` OOXML scaling), native editable `.pptx`, print vector `.pdf`, `PRISMA`/`CONSORT`/`STROBE`, KM/Forest/ROC charts, 15-check validator |
| **1** | [`graphical-abstract-maker`](./graphical-abstract-maker/README.md) | **High Priority** | Journal graphical & visual abstracts (`Elsevier`, `Cell Press`, `BMJ`, `Springer Nature`) in vector `SVG`, `PDF`, `300-DPI PNG`, and editable `PPTX` |
| **2** | [`scientific-infographic-maker`](./scientific-infographic-maker/README.md) | Core Suite | 4-band medical & public-health infographics (epidemiology KPIs, pathophysiology cascade, clinical pathway, outcome chart & clinical pearls) |
| **3** | [`publication-figure-designer`](./publication-figure-designer/README.md) | **High Priority** | Camera-ready single & multi-panel (`a, b, c, d` / `A, B, C, D`) manuscript figures at exact journal widths (`84–183 mm`) for *Nature*, *Cell*, *Science*, *NEJM*, *Lancet*, *JAMA*, *BMJ* |
| **4** | [`scientific-illustration-maker`](./scientific-illustration-maker/README.md) | Core Suite | 2D vector mechanism schematics: phospholipid-bilayer cellular signaling (`→` activation, `[-|]` flat T-bar inhibition, `(P)` phosphorylation), molecular pathways, organ pathophysiology, medical device cross-sections |
| **5** | [`research-presentation-maker`](./research-presentation-maker/README.md) | Core Suite | Assertion-Evidence scientific slide decks (`deck.pptx` with native embedded speaker notes, `deck_handout.pdf`, `deck_overview.png`, timed `speaker_notes.md`) |
| **6** | [`clinical-trial-visualizer`](./clinical-trial-visualizer/README.md) | Core Suite | `CONSORT` 4-phase flow diagrams (with strict participant arithmetic conservation checks), `SPIRIT` timelines, efficacy cards, and `CTCAE` adverse-event butterfly plots |
| **7** | [`medical-education-poster-maker`](./medical-education-poster-maker/README.md) | Core Suite | Teaching posters (`A1`, `A2`, `24×36 in`) integrating physiology, branching diagnostic algorithms, pharmacology/pathology matrices, and `OSCE`/`OSPE` station checklists |
| **8** | [`research-data-visualization-designer`](./research-data-visualization-designer/README.md) | Core Suite | CSV/Excel dataset profiler + R/Python/SPSS multivariable visualization + standalone `reproduce_figure.py` + `SHA-256` `reproducibility_manifest.json` |
| **9** | [`academic-conference-design-maker`](./academic-conference-design-maker/README.md) | Core Suite | Coordinated 6-asset conference identity kit: stage banner, `A4` abstract-book cover, CFP poster + QR, certificate (`.pdf`/`.pptx`), `1:1` speaker card, `16:9` social card |
| **10** | [`journal-cover-art-designer`](./journal-cover-art-designer/README.md) | Core Suite | Publisher trim + bleed scientific cover art (`Nature`, `Cell`, `Science`, `ACS/Wiley`), emitting both **clean unlettered full-bleed production art** and an **editorial masthead safe-zone mockup** |

---

## Quick Installation (Claude Code & Cline)

### 1. Install Lightweight CPU-Only Python Dependencies
```bash
pip install -r requirements.txt
```
*(No GPU, local LLM, paid API, or commercial software required. SIL Open Font License `.ttf` families `Source Sans 3`, `Source Serif 4`, and `IBM Plex Sans` are bundled in `research-poster-maker/assets/fonts/` and automatically shared across all 11 skills.)*

### 2. Verify & Install All 11 Skills into Claude Code and Cline
```bash
# Audit all 11 skills and install into project .claude/skills/ and .cline/skills/
python install_skills.py --verify --install --agent both --scope project

# Or install globally into ~/.claude/skills/ and ~/.cline/skills/ (Windows/macOS/Linux)
python install_skills.py --verify --install --agent both --scope global --mode copy
```

See [`SUITE_VALIDATION_REPORT.md`](./SUITE_VALIDATION_REPORT.md) for the automated portability and preflight QA results across all 11 skills.
