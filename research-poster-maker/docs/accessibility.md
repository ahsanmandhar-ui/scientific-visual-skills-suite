# Accessibility, Color Contrast & Color Universal Design

Conference poster halls often feature uneven overhead fluorescent or warm spotlighting, glare on satin paper, crowds blocking close viewing, and readers (~8% of XY males and ~0.5% of XX females) with congenital color vision deficiency (protanopia, deuteranopia, tritanopia).

---

## 1. WCAG 2.1 Luminance Contrast Standards

`scripts/validate_poster.py` computes exact W3C relative luminance contrast ratios for every foreground/background pair:

$$L = 0.2126 R_{\text{lin}} + 0.7152 G_{\text{lin}} + 0.0722 B_{\text{lin}}, \qquad \text{Contrast Ratio} = \frac{L_{\max} + 0.05}{L_{\min} + 0.05}$$

| Poster Element | Minimum Permitted Ratio | Design System Target | Validation Check |
|---|---|---|---|
| Body copy, bullets, table cells, captions, references | **4.5 : 1** (WCAG AA) | **>= 12.0 : 1** (exceeds AAA `7:1`) | `HARD FAIL` if `< 4.5:1` |
| Masthead title, author names, large section headings (`>= 24 pt`) | **3.0 : 1** (WCAG AA Large) | **>= 7.0 : 1** (WCAG AAA) | `HARD FAIL` if `< 3.0:1`; `WARN` if `< 4.5:1` |
| Graphical data marks, error bars, flow-box borders | **3.0 : 1** against chart background | **>= 4.5 : 1** (or dark outline stroke) | `WARN` if `< 3.0:1` |

### Practical Contrast Rules
- **Never place colored text on colored backgrounds** unless contrast is verified `>= 7.0:1`.
- **Avoid light yellow (`#F0E442`) or pale cyan text/lines on white backgrounds.** When using Okabe-Ito yellow in a bar or area fill, outline the bar with a dark neutral stroke (`#1F2937`, `0.8 pt`) and use black text labels.
- **Prefer light backgrounds with dark ink** over edge-to-edge black/navy backgrounds: full-bleed dark posters suffer severe specular glare under conference hall lights and heavy ink banding on aqueous plotters.

---

## 2. Colorblind-Safe Scientific Visualization Palettes

### Categorical Data: Okabe-Ito (Color Universal Design)
Default categorical series order in `scripts/generate_charts.py` (selected for high white-background contrast first):

1. **Blue:** `#0072B2` (Primary intervention / Group A)
2. **Vermilion:** `#D55E00` (Comparator / High-risk highlight)
3. **Bluish Green:** `#009E73` (Secondary group / Favorable outcome)
4. **Orange:** `#E69F00` (Group D — always paired with thin dark stroke on white)
5. **Reddish Purple:** `#CC79A7` (Group E)
6. **Sky Blue:** `#56B4E9` (Group F)
7. **Charcoal Slate:** `#334155` (Control / Reference group)

*Prohibited Pairings:* Pure red (`#FF0000`) + pure green (`#00FF00` / `#008000`) without redundant shape/label encoding; `jet` / rainbow colormaps.

### Sequential & Diverging Data
- **Sequential continuous (heatmaps, confusion matrices, incidence gradients):** `Cividis` (optimal across deuteranopia, protanopia, and grayscale) or `Viridis`.
- **Diverging continuous (log fold-change, centered risk differences):** `RdBu` or `PRGn` with a crisp white/neutral midpoint at zero/null.

---

## 3. Redundant Encoding & Cognitive Accessibility

1. **Never Rely on Color Alone:**
   - Line & Kaplan-Meier plots combine **distinct color + distinct line style** (`solid`, `dashed`, `dash-dot`, `dotted`) + direct endpoint/legend labels.
   - Scatter plots combine **distinct color + distinct marker shape** (`circle`, `square`, `triangle`, `diamond`).
   - Bars and stacked segments include `1.0 pt` white separator strokes and direct numerical value labels.
2. **Predictable Reading Trajectory:**
   - Top-to-bottom within columns, left-to-right across columns.
   - Optional subtle section index numerals (`01`, `02`, `03`...) guide navigation when asymmetric or multi-span layouts are used.
3. **Dyslexia- and Vision-Friendly Typography:**
   - Left-aligned ragged-right body paragraphs (`45–75` chars/line), open humanist apertures (`Source Sans 3`, `IBM Plex Sans`), `1.22–1.30×` line height, and explicit acronym expansion on first mention.
