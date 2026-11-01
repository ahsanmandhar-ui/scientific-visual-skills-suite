# Scientific Illustration & Pathway Conventions

## 1. Standard Biological Arrow Semantics (SBGN-Aligned)
- **Solid Pointed Arrow (`→`):** Direct activation, catalytic conversion, or directional translocation.
- **Solid Flat T-Bar (`⊣`):** Direct competitive/allosteric inhibition or receptor blockade.
- **Dashed Arrow (`⇢`):** Indirect downstream effect or nuclear transcriptional upregulation.
- **Phosphorylation Badge (`P`):** Covalent post-translational modification state.

## 2. Four Built-In Schematic Modes
1. `cellular_signaling`: Renders extracellular space, double-leaflet phospholipid membrane, transmembrane receptors, cytosolic signaling nodes, nuclear pore envelope, and target gene locus.
2. `molecular_pathway`: Multi-tier biochemical network with custom coordinates, shapes (`receptor`, `kinase`, `transcription_factor`, `drug`), and interaction edges.
3. `organ_pathophysiology`: Side-by-side `Homeostatic Physiology` vs. `Pathophysiological Remodeling` compartmental comparison.
4. `medical_device`: Multi-layer biosensor/catheter/implant cross-section with leader-line callout pins (`1..N`) and component specification table.
