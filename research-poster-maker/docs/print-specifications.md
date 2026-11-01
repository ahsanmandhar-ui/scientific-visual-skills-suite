# Poster Dimensions, PowerPoint Production & Print Specifications

## 1. Standard Conference Dimensions

Never assume all conferences share one size. European and international societies predominantly specify ISO A-series **portrait** boards (`A0`), whereas North American societies predominantly specify imperial **landscape** boards (`48 × 36 in` or `56 × 42 in`).

| Preset Key | Format Name | Orientation | Inches (`W × H`) | Millimeters (`W × H`) | Centimeters (`W × H`) | Typical Venue Norm |
|---|---|---|---|---|---|---|
| `a0_portrait` | ISO A0 Portrait | Portrait | `33.11 × 46.81 in` | `841 × 1189 mm` | `84.1 × 118.9 cm` | European & international medical/science congresses |
| `a0_landscape` | ISO A0 Landscape | Landscape | `46.81 × 33.11 in` | `1189 × 841 mm` | `118.9 × 84.1 cm` | Selected international engineering & biomedical venues |
| `a1_portrait` | ISO A1 Portrait | Portrait | `23.39 × 33.11 in` | `594 × 841 mm` | `59.4 × 84.1 cm` | Departmental symposia, compact boards, student sessions |
| `a1_landscape` | ISO A1 Landscape | Landscape | `33.11 × 23.39 in` | `841 × 594 mm` | `84.1 × 59.4 cm` | Compact landscape sessions |
| `48x36` | US Standard Landscape | Landscape | `48.00 × 36.00 in` | `1219.2 × 914.4 mm` | `121.9 × 91.4 cm` | North American conferences (NIH, AACN, major US meetings) |
| `36x48` | US Standard Portrait | Portrait | `36.00 × 48.00 in` | `914.4 × 1219.2 mm` | `91.4 × 121.9 cm` | US vertical poster boards |
| `42x56` | Large Portrait | Portrait | `42.00 × 56.00 in` | `1066.8 × 1422.4 mm` | `106.7 × 142.2 cm` | High-capacity vertical boards |
| `56x42` | Large Landscape | Landscape | `56.00 × 42.00 in` | `1422.4 × 1066.8 mm` | `142.2 × 106.7 cm` | Large medical societies (e.g., ACC / ASN / AHA generous boards) |
| `36x24` | Compact Landscape | Landscape | `36.00 × 24.00 in` | `914.4 × 609.6 mm` | `91.4 × 61.0 cm` | Institutional research days & tabletop easels |
| `custom` | Custom Dimensions | Auto (`W>=H` vs `H>W`) | User-supplied (`in`, `mm`, `cm`) | Exact conversion (`1 in = 25.4 mm`) | Exact conversion | Conference-specific board call |

> **Board Size vs. Poster Size Warning:** Conferences often state *board dimensions* (e.g., "4 ft × 8 ft board") alongside *maximum poster dimensions* (e.g., "44 × 44 in" or "48 × 36 in"). Leaving 1–2 inches inside the physical board frame accommodates push-pins, Velcro strips, and aluminum trim.

---

## 2. PowerPoint's 56-Inch Slide Limit & Proportional Scaling

Microsoft PowerPoint's OOXML canvas enforces a maximum slide width and height of **56.0 inches (`142.24 cm` / `51,206,400 EMU`)**.

- **Posters `<= 56.0 in` on both axes** (`A0`, `A1`, `48×36`, `36×48`, `42×56`, `56×42`, `36×24`):
  - Built at **1:1 (100%) exact physical dimensions** in `.pptx` and `.pdf`.
- **Posters `> 56.0 in` on either axis** (e.g., custom `72 × 36 in` or `60 × 42 in`):
  - `.pptx` is automatically authored at **1:2 (50%) exact proportional scale** (`36.0 × 18.0 in`) with embedded raster charts rendered at **600 DPI** so that **200% print enlargement** yields **300 DPI** at final print size.
  - Vector `.pdf` generated via ReportLab preserves **1:1 (100%) full physical dimensions** natively (PDF 1.4+ supports up to `200 × 200 in` directly in `MediaBox` at `72 pt/in`).
  - Both the Design Specification Report and Validation Report prominently document the `.pptx` scale factor (`0.5×`, print at `200%`) so print-shop operators never misprint at half size.

---

## 3. Bleed, Trim & Safe Margins

1. **Standard Conference Plotter Printing (Default):** Most university and conference roll-fed inkjet plotters (`36 in` or `42 in` wide paper/fabric rolls) print on white media without full-bleed trimming, or trim flush. Keep all text, logos, rules, and figures strictly inside a **`1.0 in` (`25.4 mm`) safe margin** (`0.75 in` on `A1` / `36×24 in`).
2. **Commercial Full-Bleed Printing (`--bleed-in 0.125` or `0.25`):** When full-bleed edge-to-edge header banners are sent to a commercial trim shop, extend background/header fills to the bleed boundary (`+0.125 in` / `3.175 mm` per side) while keeping all text and logos inside the safe margin (`>= 1.0 in` from trim edge).

---

## 4. Resolution, Vector Graphics & Font Embedding

1. **Vector Priority:** Charts, forest plots, survival curves, PRISMA/CONSORT diagrams, QR codes, and geometric shapes should be authored in vector formats (`SVG` / `PDF`) wherever supported.
   - In Matplotlib: set `rcParams['pdf.fonttype'] = 42` and `rcParams['ps.fonttype'] = 42` (TrueType outline embedding, avoiding legacy Type 3 bitmap/unhinted fonts) and `rcParams['svg.fonttype'] = 'path'` when passing through `svglib` so glyphs never shift across machines.
2. **Raster Resolution Standards:**
   - **Target:** `300 PPI` (pixels per inch) at final printed physical size on the poster (`600 PPI` inside a 50%-scale `.pptx`).
   - **Acceptable photographic floor:** `150–200 PPI` for large microscopy, radiology, or clinical photographs.
   - **Hard warning threshold:** `< 150 PPI` at printed dimensions triggers an explicit `LOW_RESOLUTION_IMAGE` warning in `validate_poster.py`.
   - **Strict Anti-Upscaling Rule:** Never bicubic-upsample a low-resolution user image (e.g., `400 × 300 px` screenshot) and claim it is "300 DPI print-ready." Preserve original pixel integrity and report its true effective print PPI honestly.
3. **Color Space Honesty:**
   - `python-pptx` and standard Matplotlib PNG/SVG pipelines operate in **sRGB**. Modern wide-gamut aqueous pigment plotters (HP DesignJet, Canon imagePROGRAF, Epson SureColor) used by university and conference print centers accept sRGB PDFs natively via onboard ICC RIP conversion.
   - Do **not** claim offset-press CMYK PDF/X-1a compliance unless the output has actually been ICC-profile converted and verified in a CMYK prepress workflow. State `sRGB (wide-gamut inkjet plotter ready)` accurately in the Design Specification Report.
