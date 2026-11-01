---
name: scientific-illustration-maker
description: Produces clean vector scientific illustrations and mechanism schematics including cellular phospholipid-bilayer signaling, molecular activation/inhibition pathways, compartmental pathophysiology diagrams, and medical device cross-sections in editable SVG, vector PDF, and high-DPI PNG.
license: MIT
metadata:
  version: "1.0.0"
  domain: "scientific-illustration"
---

# Scientific Illustration Maker Skill

Generate crisp, textbook- and journal-style **2D vector scientific schematics** covering cellular mechanisms, molecular pathways, compartmental physiology/pathophysiology, and medical device architectures.

All paths below are relative to `scientific-illustration-maker/`.

---

## Scope & Honest Technical Boundaries

- **What this skill excels at (CPU-only, offline, deterministic):** Clean geometric 2D vector schematics — phospholipid bilayers, transmembrane receptors, intracellular signaling cascades (`→` activation, `⊣` flat-bar inhibition, `P` phosphorylation), nuclear transcription compartments, physiological barrier/flux diagrams, and layered medical-device cross-sections with numbered callout leaders.
- **Honest limitation:** Pure-Python vector geometry does not produce painterly 3D gross-anatomy paintings or cryo-EM surface meshes; when 2D schematic abstraction is used to represent organs or devices, label it clearly as a **schematic cross-section / mechanism diagram**.

---

## Workflow

1. Read `docs/illustration-conventions.md` (SBGN-inspired arrow semantics: pointed arrow = activation/transport; flat T-bar = inhibition; dashed arrow = transcriptional/indirect regulation).
2. Select a mode in `<work_dir>/illustration_spec.json`:
   - `cellular_signaling` (extracellular → phospholipid bilayer + receptors → cytoplasm → nucleus/DNA)
   - `molecular_pathway` (node-and-edge signaling or metabolic network)
   - `organ_pathophysiology` (healthy vs. pathological tissue/vascular interface)
   - `medical_device` (layered cross-section with numbered callouts + engineering legend)
3. Generate and validate:
   ```bash
   python scripts/generate_illustration.py \
     --spec <work_dir>/illustration_spec.json \
     --output-dir <work_dir>/output

   python scripts/validate_illustration.py \
     --output-dir <work_dir>/output \
     --spec <work_dir>/illustration_spec.json
   ```
4. Inspect `<work_dir>/output/illustration.png` to verify zero node/arrow/label collisions and clear compartmental hierarchy.
