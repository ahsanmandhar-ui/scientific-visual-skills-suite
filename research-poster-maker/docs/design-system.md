# Scientific Poster Design System

## 1. Editorial Philosophy: Human Art-Direction vs. Generic AI Infographics

A conference research poster is a **large-format work of scientific editorial design**, not a slide deck crammed onto one page and not a SaaS marketing infographic. Viewers navigate a busy poster hall at three distinct distances:

- **3 meters (10 ft) — Discovery:** The title, primary visual focal point (central figure or headline statistical finding), and institutional provenance must register effortlessly.
- **1.5 meters (5 ft) — Orientation:** Section headers, study flow, primary outcomes, and chart axes/annotations must read cleanly without squinting.
- **1 meter (3 ft) — Conversation:** Methods details, statistical tables, confidence intervals, limitations, and key references support deeper dialogue with the presenter.

### Anti-Patterns Strictly Prohibited

| Anti-Pattern | Why It Fails | Editorial Replacement |
|---|---|---|
| Identical rounded pastel boxes around every section | Creates monotonous "dashboard card" fatigue and wastes 15–20% of layout width on redundant borders | Open typographic columns separated by generous gutters (`0.65–0.90 in`) and crisp top hairline/accent rules (`1.5–2.5 pt`); reserve tinted panels strictly for 1–2 focal callouts (e.g., Primary Finding or Clinical Takeaway) |
| Emoji or generic clip-art icons in section headers | Undermines academic credibility at medical/scientific venues | Clean typographic section numerals (`01`, `02` or unadorned bold uppercase/title-case headers) with disciplined letterspacing |
| Rainbow gradients, drop shadows, and 3D charts | Distorts perceptual data reading and prints muddy on large-format plotters | Flat archival surfaces, crisp `0.5–1.0 pt` vector rules, and perceptually accurate 2D scientific plots |
| Default blue for every medical poster | Cliché and ignores institutional identity or research domain | Context-selected palettes (Oxford Navy, Charcoal & Ivory, Deep Teal, Academic Burgundy, Forest & Cream, Editorial Monochrome) |
| Shrinking all fonts to 12–14 pt to fit pasted manuscript text | Renders poster unreadable beyond 0.5 m | Distill prose into concise analytical statements and structured bullets; offload secondary tables to QR supplement if needed |

---

## 2. Curated Academic Color Palettes

Every palette follows a **60–30–10 editorial hierarchy**:
- **Canvas & Surface (60–75%):** Pure archival white (`#FFFFFF`) or warm paper ivory (`#FAF9F5`) to maximize print legibility and prevent ink cockling.
- **Dominant Structural Color (15–25%):** Masthead banner or masthead rule, section rules, primary headings, table header rules.
- **Supporting Neutral / Tinted Well (5–10%):** Subtle surface tint (`4–7%` luminance shift) for focal takeaway panels or alternating table rows.
- **Semantic Accent (<= 5%):** Reserved strictly for primary intervention series, statistically significant pooled diamonds, or key callout numerals.

### Built-In Palette Specifications

| Palette ID | Name | Canvas | Surface Tint | Dominant | Supporting | Accent | Body Ink | Body Contrast on Canvas | Recommended Contexts |
|---|---|---|---|---|---|---|---|---|---|
| `academic_navy` | Oxford Navy & Crisp White | `#FFFFFF` | `#F3F6FA` | `#0F2742` | `#334E68` | `#0072B2` / `#D55E00` | `#16202A` | **16.4 : 1** (AAA) | Clinical trials, cardiology, multi-center hospital research |
| `charcoal_ivory` | Charcoal & Warm Ivory | `#FAF9F5` | `#F0EEE6` | `#1F2421` | `#4A524D` | `#B84A27` | `#1B1E1C` | **15.8 : 1** (AAA) | Nature/BMJ-style editorial, experimental biology, humanities/policy |
| `deep_teal` | Deep Teal & Cool Slate | `#FFFFFF` | `#F1F7F7` | `#0D4A52` | `#2C6E76` | `#D96B27` | `#182426` | **15.6 : 1** (AAA) | Epidemiology, public health, systematic reviews, nephrology |
| `burgundy_offwhite` | Academic Burgundy & Alabaster | `#FCFAF8` | `#F5EEF0` | `#5C1628` | `#7D2E42` | `#1F6E8C` | `#22181B` | **16.1 : 1** (AAA) | Oncology, hematology, university symposia, translational medicine |
| `forest_cream` | Forest Pine & Warm Cream | `#FAF9F4` | `#EEF2EC` | `#183A2C` | `#2F5D48` | `#C86D1F` | `#1A241F` | **15.5 : 1** (AAA) | Environmental health, ecology, infectious disease, cohort studies |
| `monochrome_editorial` | Monochromatic Scientific | `#FFFFFF` | `#F4F5F7` | `#111827` | `#374151` | `#0072B2` | `#111827` | **17.7 : 1** (AAA) | Minimalist editorial, physics, biostatistics, methodology |

*Institutional Branding Override:* When the user supplies institutional hex codes or a university/hospital logo, validate contrast ratios (`>= 4.5:1` minimum, `>= 7.0:1` preferred for body copy) before applying them to text or masthead backgrounds.

---

## 3. Spatial Proportions & Whitespace Budget

Target area allocation across the poster canvas:
- **Masthead (Title, Authors, Affiliations, Logos/QR):** `11% – 15%` of poster height.
- **Visual Evidence (Charts, Forest Plots, Flow Diagrams, Tables):** `35% – 48%` of body area.
- **Structured Text (Background, Methods, Findings, Limitations, Conclusions):** `25% – 35%` of body area.
- **Open Whitespace (Margins, Column Gutters, Section Breathing Room):** `25% – 35%` of total canvas area.

### Margin & Gutter Scaling Rules

| Poster Class | Short Edge | Outer Margin | Column Gutter | Vertical Section Gap | Internal Callout Padding |
|---|---|---|---|---|---|
| Large Format (`48×36 in`, `A0`, `42×56 in`) | `33–42 in` | `1.00 – 1.25 in` | `0.70 – 0.85 in` | `0.55 – 0.70 in` | `0.38 – 0.48 in` |
| Medium Format (`A1`, `36×24 in`) | `23–24 in` | `0.75 – 0.90 in` | `0.50 – 0.65 in` | `0.40 – 0.50 in` | `0.28 – 0.35 in` |

---

## 4. Section Visual Treatments

To prevent repetitive visual monotony, assign distinct structural roles to sections:

1. **Editorial Rule Section (`style: "editorial_rule"`):** Default for *Background*, *Objectives*, *Methods*, *Limitations*. Uses a crisp `2.0 pt` top horizontal rule in the dominant color, bold section title, and clean unboxed prose/bullets directly on the archival canvas.
2. **Hero Metric / Primary Takeaway Panel (`style: "focal_callout"`):** Used **once** per poster for *Primary Outcome* or *Headline Finding*. Uses the subtle surface tint fill (`Surface Tint`), a `4.0 pt` left accent bar in the dominant/accent color, and prominent statistical callouts.
3. **Evidence Frame (`style: "figure_well"`):** Used for *Figures* and *Diagrams*. Pure white background (`#FFFFFF`) with a hairline `0.75 pt` neutral border (`#D5DCE4`), vector/300-DPI artwork centered with breathing room, and a structured journal caption underneath (`Figure N. Bold title.` Analytical summary + sample size/test note).
4. **Booktabs Academic Table (`style: "booktabs_table"`):** Used for *Baseline Characteristics* or *Subgroup Outcomes*. Clean horizontal rules only (`1.75 pt` top rule, `1.0 pt` header separator, `1.75 pt` bottom rule, optional `0.4 pt` light row rules), zero vertical borders, left-aligned text labels, right-aligned tabular numbers.
5. **Colophon Footer (`style: "colophon"`):** Used for *References*, *Funding*, *Disclosures*, and *Correspondence*. Separated at the bottom of the poster or bottom of the final column by a `0.75 pt` hairline rule in compact legible type.
