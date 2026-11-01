---
name: journal-cover-art-designer
description: Designs scientific journal cover concepts and mathematical/vector editorial cover artwork formatted to exact publisher trim, bleed, and masthead safe-zone specifications (Nature, Cell Press, Science, ACS/Wiley). Emits both clean unlettered full-bleed production art and an editorial masthead mockup plus an 'On the Cover' submission statement.
license: MIT
metadata:
  version: "1.0.0"
  domain: "editorial-cover-art"
---

# Journal Cover Art Designer Skill

Create striking **algorithmic/vector scientific cover compositions** engineered around real publisher **trim, bleed, masthead occlusion, and barcode safe-zone geometry**.

All paths below are relative to `journal-cover-art-designer/`.

---

## Editorial Production Rules & Honest Scope

1. **Always Deliver Unlettered Art + Masthead Proof Separately:** Journals (*Nature*, *Science*, *Cell*, *JACS*) reject cover submissions that bake homemade journal logos into the final art file. This skill always emits:
   - `cover_artwork_unlettered.{pdf,svg,png}` — Clean, full-bleed (`trim + 2×bleed`), text-free production artwork.
   - `cover_editorial_mockup.{pdf,png}` — Proof overlay showing trim marks, top masthead reservation (`64–70 mm`), cover teaser line, and barcode safe zone so focal elements are guaranteed never to be occluded.
   - `cover_caption.md` — Concise `50–90` word *"On the Cover"* scientific metaphor statement.
2. **CPU-Only Vector & Parametric Artwork (Honest Scope):** Generates deterministic mathematical/geometric scientific metaphors (`helical_chromatin`, `molecular_lattice`, `neural_connectome`, `wave_topography`) in vector PDF/SVG and `300-DPI` sRGB PNG without GPUs or cloud image APIs. Exports are sRGB/RGB; if a commercial press requires ICC-profiled CMYK separation (`ISO Coated v2` / `SWOP`), convert during final prepress rather than claiming native CMYK separation.

---

## Workflow

1. Read `docs/journal-cover-specs.md` and select publisher preset (`nature-family`, `cell-press`, `science-aaas`, `acs-wiley`) and motif style in `<work_dir>/cover_spec.json`.
2. Generate and validate:
   ```bash
   python scripts/generate_cover_art.py \
     --spec <work_dir>/cover_spec.json \
     --output-dir <work_dir>/output

   python scripts/validate_cover_art.py \
     --output-dir <work_dir>/output \
     --spec <work_dir>/cover_spec.json
   ```
3. Visually inspect **both** `cover_artwork_unlettered.png` and `cover_editorial_mockup.png` to confirm focal balance and zero masthead/barcode encroachment.
