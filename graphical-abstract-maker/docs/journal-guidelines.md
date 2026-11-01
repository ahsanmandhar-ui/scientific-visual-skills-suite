# Journal Graphical & Visual Abstract Specifications

## 1. Official Journal Dimension & Typography Norms

Always verify the specific target journal's Instructions for Authors before submission; the presets below reflect standard publisher specifications:

| Preset ID | Publisher / Style | Aspect Ratio | Physical Canvas | Raster @ 300 DPI | Panel Topology | Recommended Font Range |
|---|---|---|---|---|---|---|
| `elsevier-landscape` | Elsevier Journals | `2.5 : 1` (min `1328×531 px`) | `12.50 × 5.00 in` (`317.5 × 127.0 mm`) | `3750 × 1500 px` | Left-to-Right 3-Stage Flow (`Cohort/Context → Method/Mechanism → Finding`) | `11–20 pt` |
| `cell-press-square` | Cell Press | `1 : 1` Square (`1200×1200 px` @ 120–300 DPI) | `10.00 × 10.00 in` (`254.0 × 254.0 mm`) | `3000 × 3000 px` | Top-to-Bottom 3-Tier (`Context → Mechanism/Assay → Quantitative Outcome`) | `12–22 pt` |
| `bmj-visual-abstract` | *BMJ* / *JAMA* / *NEJM* Clinical Visual Abstract | `16 : 9` Widescreen | `16.00 × 9.00 in` (`406.4 × 228.6 mm`) | `4800 × 2700 px` | Study Banner + 3 Columns (`Population | Intervention | Primary & Secondary Endpoints`) + DOI Footer | `14–28 pt` |
| `springer-nature-compact` | Springer Nature | `2 : 1` Double-Column (`180 × 90 mm`) | `7.09 × 3.54 in` (`180.0 × 90.0 mm`) | `2126 × 1063 px` | Minimalist 3-Panel Editorial (`Design → Process → Result`) | `7–12 pt` (at `180 mm` print width) |

---

## 2. Editorial Anti-Clutter Rules

1. **No Redundant "Graphical Abstract" Title:** Cell Press and Elsevier explicitly instruct authors *not* to write the literal words "Graphical Abstract" as a header inside the artwork; use the concise scientific takeaway headline or omit the header when journal rules require headerless art (`show_header: false`).
2. **Word Budget Ceiling:** Aim for **40–75 words total** (hard warning above **95 words**). Replace full sentences with crisp noun phrases and exact statistics (`aHR 0.68 [95% CI 0.56–0.82], p < 0.001`).
3. **Directional Clarity:** Every multi-panel graphical abstract must read unmistakably **Left → Right** or **Top → Bottom**, reinforced by subtle vector chevron/arrow connectors—never cyclical spaghetti arrows unless illustrating a true biological feedback cycle.
4. **Color Universal Design:** Use Okabe-Ito colorblind-safe accents (`#0072B2` blue, `#D55E00` vermilion, `#009E73` bluish green) on crisp white (`#FFFFFF`) or subtle warm ivory (`#FAF9F6`) panels with WCAG 2.1 contrast `>= 4.5:1`.
