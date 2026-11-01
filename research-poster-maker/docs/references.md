# Authoritative References & Technical Standards

This document catalogs the primary university guidelines, scientific reporting frameworks, conference poster standards, accessibility specifications, open-source libraries, and Agent Skills documentation consulted in engineering `research-poster-maker`.

> **Note on Standards:** Conference poster dimensions, layout preferences, and font sizes vary by venue, discipline, and board size. None of the reference values cited in this skill are universally mandatory across all conferences; always check venue-specific author instructions first.

---

## 1. Academic & Medical Conference Poster Design Guidelines

1. **National Institutes of Health (NIH) Office of Intramural Training & Education (OITE)** — *Creating a Scientific Poster*
   - URL: https://www.training.nih.gov/creating-a-scientific-poster/
   - Key guidance: Landscape 48 × 36 in board allocation norms, light backgrounds with dark text, ~40% graphics / 20% text / 40% whitespace balance, structured visual hierarchy.
2. **Bodleian Libraries, University of Oxford** — *Designing a Conference Poster in Medicine: Getting Started*
   - URL: https://www.bodleian.ox.ac.uk/sites/default/files/bodreader/documents/media/iskills-designing-conference-poster.pdf
   - Key guidance: A0/A1/A2 ISO medical conference norms, high-contrast color schemes, >=24 pt body text guidance for full-size posters, concise key references (`[n]` citations), funding grant number acknowledgements.
3. **New York University (NYU) Libraries** — *How to Create a Research Poster: Poster Basics, Logos & Images*
   - URL: https://guides.nyu.edu/posters
   - Image resolution guidance: https://guides.nyu.edu/posters/logos-images
   - Key guidance: 300–500 word target for scannable posters, 120–300 PPI print resolution floor/target at final physical print dimensions, copyright compliance.
4. **Cornell University Library** — *Poster Making and Printing Guide*
   - URL: https://guides.library.cornell.edu/poster
   - Key guidance: 60-second poster evaluation criteria, visual hierarchy, Better Poster variants, institutional logo handling.
5. **University of Illinois Chicago (UIC) School of Public Health** — *Poster Guide for Students*
   - URL: https://publichealth.uic.edu/poster-guide-for-students/
   - Key guidance: Single-slide PowerPoint setup, 56-inch maximum PowerPoint slide size limit (designing >56 in posters at 50% scale for 200% print enlargement), >=1-inch outer margins, grid alignment.
6. **Southern Illinois University (SIU) School of Medicine** — *Posters and Presentations Guide*
   - URL: https://libguides.siumed.edu/presentations
   - Key guidance: Half-size PowerPoint setup for oversized boards (e.g., 18 × 30 in for 36 × 60 in at 200%), dark text on light paper to prevent ink saturation and eye fatigue.
7. **University of Toronto Libraries (Gerstein Science Information Centre & UTSC)** — *Poster Design & Student Poster Guide*
   - URL: https://guides.library.utoronto.ca/c.php?g=251602&p=1674771
   - PDF Guide: https://www.utsc.utoronto.ca/publications/coop-accreditation/wp-content/uploads/sites/3/2020/06/Co-op-WT-Poster-Guidelines.pdf
   - Key guidance: 45–65 character line widths, 2-meter readability for primary findings, acronym definition at first mention, 300 PPI ideal image resolution.
8. **University of New Mexico (UNM) University Libraries** — *Presentation Design: Posters*
   - URL: https://libguides.unm.edu/presentations/posters
   - Key guidance: Title legibility at 8+ feet (2.5–3 m), body legibility at 3–5 feet (1–1.5 m), interactive conversational focus, QR code integration.
9. **American Association of Colleges of Nursing (AACN)** — *Recommendations for Effective Abstract Poster Presentations*
   - URL: https://www.aacnnursing.org/Portals/0/PDFs/Conferences-Webinars/Recommendations-for-Poster-Presentations.pdf
   - Key guidance: 1–2 minute average viewer dwell time, left-to-right top-to-bottom column flow, graphical data presentation over dense raw text tables.
10. **University of Texas Medical Branch (UTMB)** — *Research & Poster Presentations Brand & File Setup*
    - URL: https://www.utmb.edu/brand/usage-guidelines/presentations
    - Key guidance: Custom page setup prior to placing elements, 56 × 56 in PowerPoint ceiling, proportional half-scale enlargement workflow.

---

## 2. Scientific Typography, Journal Figure Specs & Reporting Guidelines

11. **Nature Portfolio** — *Figure Preparation & Typography Specifications (Extended Data & Print Standards)*
    - URL: https://www.nature.com/nature-portfolio/for-authors/reporting-standards
    - Typography synthesis reference: https://figviz.com/blog/scientific-poster-figure-fonts-the-2026-typography-handbook-4ajjsveb
    - Key guidance: Clean sans-serif figure labels, consistent single font across figures, embedded fonts in vector PDF/EPS exports, explicit prohibition of red-green-only distinctions.
12. **EQUATOR Network — PRISMA 2020 Statement (Systematic Reviews & Meta-Analyses)**
    - Page MJ, McKenzie JE, Bossuyt PM, et al. *The PRISMA 2020 statement: an updated guideline for reporting systematic reviews.* BMJ 2021;372:n71.
    - URL: https://www.prisma-statement.org/
    - Preprint/Checklist PDF: https://hbg.cochrane.org/sites/hbg.cochrane.org/files/uploads/page-2020-the-prisma-statement-an-updated-gu.pdf
    - Key guidance: 27-item checklist, PRISMA for Abstracts (12 items), three-phase flow diagram (Identification → Screening → Included) with exact record/report count closure and explicit exclusion reasons.
13. **EQUATOR Network — CONSORT Statement (Randomized Controlled Trials) & STROBE Statement (Observational Studies)**
    - CONSORT URL: https://www.equator-network.org/reporting-guidelines/consort/
    - STROBE URL: https://www.equator-network.org/reporting-guidelines/strobe/
    - Flow diagram validation examples: https://github.com/cooldk/prisma-consort-flow-diagram-examples
    - Key guidance: Participant flow tracking (Enrollment → Allocation → Follow-up → Analysis), baseline demographics reporting, effect estimates with precision (95% confidence intervals) alongside exact *p*-values.

---

## 3. Accessibility, Color Contrast & Scientific Color Palettes

14. **W3C Web Content Accessibility Guidelines (WCAG) 2.1 — Contrast (Minimum & Enhanced)**
    - URL: https://www.w3.org/TR/WCAG21/#contrast-minimum
    - Key guidance: Relative luminance contrast ratio >= 4.5:1 (AA) and >= 7.0:1 (AAA) for normal text; >= 3.0:1 for large text and graphical data marks.
15. **Okabe & Ito — Color Universal Design (CUD) / Wong *Nature Methods* Palette**
    - Okabe M, Ito K. *Color Universal Design (CUD): How to make figures and presentations that are friendly to Colorblind people.* (2008).
    - Wong B. *Points of view: Color blindness.* Nature Methods 8, 441 (2011). https://doi.org/10.1038/nmeth.1618
    - Reference HEX table (`#0072B2`, `#E69F00`, `#009E73`, `#D55E00`, `#56B4E9`, `#CC79A7`, `#F0E442`, `#000000`): https://sci-draw.com/blog/scientific-color-palettes-for-research-papers
16. **Cornell University Info 3312 — Implementing Accessibility in Data Visualization**
    - URL: https://info3312.infosci.cornell.edu/notes/implementing-accessibility.html
    - Key guidance: Redundant encoding (color + marker shape/line style + direct labels), whitespace separation between bars/segments, perceptual uniformity (`Viridis`, `Cividis`).

---

## 4. Agent Skills Specification, Claude Code & Cline Documentation

17. **Agent Skills Open Specification (`agentskills.io`)**
    - Core format specification: https://agentskills.io/specification
    - Progressive disclosure & client implementation: https://agentskills.io/client-implementation/adding-skills-support
    - Using scripts in skills: https://agentskills.io/skill-creation/using-scripts
    - Optimizing skill descriptions: https://agentskills.io/skill-creation/optimizing-descriptions
    - Key guidance: `SKILL.md` with YAML frontmatter (`name` lowercase alphanumeric + single hyphens matching parent directory, max 64 chars; `description` max 1024 chars), 3-tier progressive disclosure (Metadata ~100 tokens -> `SKILL.md` <5,000 tokens -> `docs/` & `scripts/` loaded/executed on demand).
18. **Anthropic Claude Code & Platform Documentation — Agent Skills**
    - Claude Code Skills documentation: https://code.claude.com/docs/en/skills
    - Claude Agent SDK Skills: https://code.claude.com/docs/en/agent-sdk/skills
    - Claude Platform Agent Skills Overview: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
    - Key guidance: Project installation at `.claude/skills/<skill-name>/SKILL.md`, personal/global installation at `~/.claude/skills/<skill-name>/SKILL.md`, automatic semantic triggering + `/research-poster-maker` slash command invocation.
19. **Cline Official Documentation — Skills**
    - Cline Skills documentation: https://docs.cline.bot/customization/skills
    - Cline 3.48+ Skills release notes: https://cline.bot/blog/cline-3-48-0-skills-and-websearch-make-cline-smarter
    - Key guidance: Project installation at `.cline/skills/<skill-name>/SKILL.md` (also supports `.claude/skills/`), global installation at `~/.cline/skills/<skill-name>/SKILL.md`, progressive loading of `SKILL.md` and on-demand reading/execution of `docs/` and `scripts/`.

---

## 5. Python Libraries & Open-Source Scientific Poster Projects

20. **`python-pptx` Official Documentation**
    - URL: https://python-pptx.readthedocs.io/en/latest/
    - Presentation slide dimensions & EMU reference: https://python-pptx.readthedocs.io/en/latest/api/presentation.html
21. **`Matplotlib` Official Documentation — Fonts, Vector Backends & `rcParams`**
    - Fonts in PDF/PS/SVG (`pdf.fonttype = 42` TrueType subsetting, `svg.fonttype = 'path'`/`'none'`): https://matplotlib.org/stable/users/explain/text/fonts.html
    - Configuration `rcParams`: https://matplotlib.org/stable/users/explain/configuration.html
22. **ReportLab, `svglib`, `pypdf`, `fontTools`, & PyMuPDF**
    - ReportLab PDF Library: https://docs.reportlab.com/
    - `pypdf` PDF inspection & page box verification: https://pypdf.readthedocs.io/
    - `svglib` vector SVG-to-ReportLab conversion: https://github.com/deeplook/svglib
    - `fontTools` OpenType/TrueType font inspection: https://fonttools.readthedocs.io/
23. **Open-Source Scientific Poster Frameworks Studied for Design Patterns**
    - `posterdown` (W. Brent Thorne — reproducible academic & BetterPoster templates): https://github.com/brentthorne/posterdown
    - `peace-of-posters` (Jonas Pleyer — modular scientific poster layout system): https://github.com/jonaspleyer/peace-of-posters
    - `typst-poster` (academic horizontal/vertical grid poster system): https://github.com/pncnmnp/typst-poster
    - `Paper2Poster` (scientific manuscript-to-editable-PPTX evaluation insights on visual hierarchy & text density): https://github.com/Paper2Poster/Paper2Poster
