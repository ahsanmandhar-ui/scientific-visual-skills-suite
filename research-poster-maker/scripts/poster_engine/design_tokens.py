#!/usr/bin/env python3
"""
Design tokens, physical dimension presets, WCAG 2.1 contrast verification,
curated academic color palettes, and cross-platform TrueType font resolution.
"""

from __future__ import annotations

import math
import pathlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

SKILL_ROOT = pathlib.Path(__file__).resolve().parents[2]
BUNDLED_FONT_DIR = SKILL_ROOT / "assets" / "fonts"
TEMPLATES_DIR = SKILL_ROOT / "templates"

PPTX_MAX_INCHES = 56.0  # Microsoft PowerPoint OOXML slide limit (142.24 cm)


# ---------------------------------------------------------------------------
# 1. Physical Poster Dimensions
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PosterDimensions:
    preset_id: str
    label: str
    width_in: float
    height_in: float
    bleed_in: float = 0.0
    safe_margin_in: float = 1.0
    target_dpi: int = 300
    is_default_assumption: bool = False

    @property
    def orientation(self) -> str:
        if abs(self.width_in - self.height_in) < 0.05:
            return "square"
        return "landscape" if self.width_in > self.height_in else "portrait"

    @property
    def width_mm(self) -> float:
        return round(self.width_in * 25.4, 2)

    @property
    def height_mm(self) -> float:
        return round(self.height_in * 25.4, 2)

    @property
    def pptx_scale_factor(self) -> float:
        """
        PowerPoint slides cannot exceed 56 x 56 inches.
        Posters exceeding 56 in on either axis use exact 1:2 half-scale (0.5)
        for 200% print enlargement, while vector PDFs retain 1:1 full scale.
        """
        if max(self.width_in, self.height_in) > PPTX_MAX_INCHES:
            return 0.5
        return 1.0

    @property
    def pptx_width_in(self) -> float:
        return round(self.width_in * self.pptx_scale_factor, 4)

    @property
    def pptx_height_in(self) -> float:
        return round(self.height_in * self.pptx_scale_factor, 4)

    @property
    def effective_pptx_raster_dpi(self) -> int:
        return int(round(self.target_dpi / self.pptx_scale_factor))

    @property
    def short_edge_in(self) -> float:
        return min(self.width_in, self.height_in)

    @property
    def area_sq_in(self) -> float:
        return self.width_in * self.height_in


DIMENSION_PRESETS: Dict[str, Tuple[str, float, float]] = {
    "a0_portrait": ("ISO A0 Portrait (841 × 1189 mm)", 841.0 / 25.4, 1189.0 / 25.4),
    "a0_landscape": ("ISO A0 Landscape (1189 × 841 mm)", 1189.0 / 25.4, 841.0 / 25.4),
    "a1_portrait": ("ISO A1 Portrait (594 × 841 mm)", 594.0 / 25.4, 841.0 / 25.4),
    "a1_landscape": ("ISO A1 Landscape (841 × 594 mm)", 841.0 / 25.4, 594.0 / 25.4),
    "48x36": ("US Standard Landscape (48 × 36 in)", 48.0, 36.0),
    "36x48": ("US Standard Portrait (36 × 48 in)", 36.0, 48.0),
    "42x56": ("Large Portrait (42 × 56 in)", 42.0, 56.0),
    "56x42": ("Large Landscape (56 × 42 in)", 56.0, 42.0),
    "36x24": ("Compact Landscape (36 × 24 in)", 36.0, 24.0),
    "24x36": ("Compact Portrait (24 × 36 in)", 24.0, 36.0),
}


def resolve_dimensions(
    preset: Optional[str] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    units: str = "in",
    bleed_in: float = 0.0,
    safe_margin_in: Optional[float] = None,
    target_dpi: int = 300,
) -> PosterDimensions:
    """Resolve preset or custom conference dimensions into exact physical inches."""
    is_assumed = False
    if width is not None and height is not None:
        u = units.lower().strip()
        if u in ("mm", "millimeter", "millimeters"):
            w_in, h_in = width / 25.4, height / 25.4
        elif u in ("cm", "centimeter", "centimeters"):
            w_in, h_in = width / 2.54, height / 2.54
        elif u in ("in", "inch", "inches"):
            w_in, h_in = float(width), float(height)
        else:
            raise ValueError(f"Unsupported dimension unit '{units}'. Use 'in', 'mm', or 'cm'.")
        label = f"Custom ({w_in:.2f} × {h_in:.2f} in / {w_in*25.4:.0f} × {h_in*25.4:.0f} mm)"
        preset_id = "custom"
    else:
        if not preset:
            preset = "48x36"
            is_assumed = True
        key = preset.lower().strip().replace(" ", "_").replace("×", "x")
        if key not in DIMENSION_PRESETS:
            raise ValueError(
                f"Unknown dimension preset '{preset}'. Supported presets: {sorted(DIMENSION_PRESETS.keys())}"
            )
        label, w_in, h_in = DIMENSION_PRESETS[key]
        preset_id = key

    short_edge = min(w_in, h_in)
    if safe_margin_in is None:
        safe_margin_in = 1.05 if short_edge >= 32.0 else 0.75

    return PosterDimensions(
        preset_id=preset_id,
        label=label,
        width_in=round(w_in, 4),
        height_in=round(h_in, 4),
        bleed_in=max(0.0, float(bleed_in)),
        safe_margin_in=round(float(safe_margin_in), 4),
        target_dpi=int(target_dpi),
        is_default_assumption=is_assumed,
    )


# ---------------------------------------------------------------------------
# 2. WCAG 2.1 Contrast & Curated Color Palettes
# ---------------------------------------------------------------------------

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    h = hex_color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    if len(h) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def hex_to_rgb_norm(hex_color: str) -> Tuple[float, float, float]:
    r, g, b = hex_to_rgb(hex_color)
    return r / 255.0, g / 255.0, b / 255.0


def relative_luminance(hex_color: str) -> float:
    """Compute WCAG 2.1 relative luminance for an sRGB hex color."""
    def channel(c: int) -> float:
        v = c / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = hex_to_rgb(hex_color)
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def wcag_contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    l1 = relative_luminance(fg_hex)
    l2 = relative_luminance(bg_hex)
    lighter, darker = max(l1, l2), min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


# Okabe-Ito Color Universal Design series ordered for white-background legibility
OKABE_ITO_SERIES: List[str] = [
    "#0072B2",  # Blue
    "#D55E00",  # Vermilion
    "#009E73",  # Bluish green
    "#334155",  # Deep neutral slate (high-contrast control reference)
    "#CC79A7",  # Reddish purple
    "#E69F00",  # Orange (pair with dark stroke on light bg)
    "#56B4E9",  # Sky blue
]


@dataclass(frozen=True)
class ColorPalette:
    palette_id: str
    name: str
    canvas_bg: str
    surface_tint: str
    figure_bg: str
    dominant: str
    supporting: str
    accent: str
    masthead_fg: str
    masthead_sub_fg: str
    body_ink: str
    muted_ink: str
    rule_border: str
    chart_series: Tuple[str, ...] = field(default_factory=lambda: tuple(OKABE_ITO_SERIES))


PALETTES: Dict[str, ColorPalette] = {
    "academic_navy": ColorPalette(
        palette_id="academic_navy",
        name="Oxford Navy & Crisp White",
        canvas_bg="#FFFFFF",
        surface_tint="#F2F6FA",
        figure_bg="#FFFFFF",
        dominant="#0F2742",
        supporting="#2B4C7E",
        accent="#D55E00",
        masthead_fg="#FFFFFF",
        masthead_sub_fg="#DCE6F2",
        body_ink="#15202B",
        muted_ink="#475569",
        rule_border="#CBD5E1",
        chart_series=("#0F2742", "#0072B2", "#D55E00", "#009E73", "#64748B", "#CC79A7"),
    ),
    "charcoal_ivory": ColorPalette(
        palette_id="charcoal_ivory",
        name="Charcoal & Warm Ivory",
        canvas_bg="#FAF9F5",
        surface_tint="#F0EEE6",
        figure_bg="#FFFFFF",
        dominant="#1E2421",
        supporting="#46514B",
        accent="#B84A27",
        masthead_fg="#FAF9F5",
        masthead_sub_fg="#E2E0D8",
        body_ink="#1A1E1C",
        muted_ink="#4B5550",
        rule_border="#D4D1C7",
        chart_series=("#1E2421", "#B84A27", "#0072B2", "#009E73", "#6B7280", "#CC79A7"),
    ),
    "deep_teal": ColorPalette(
        palette_id="deep_teal",
        name="Deep Teal & Neutral Slate",
        canvas_bg="#FFFFFF",
        surface_tint="#EFF6F6",
        figure_bg="#FFFFFF",
        dominant="#0D4A52",
        supporting="#236B73",
        accent="#C85A17",
        masthead_fg="#FFFFFF",
        masthead_sub_fg="#D9ECEE",
        body_ink="#162325",
        muted_ink="#465A5E",
        rule_border="#CBD8DA",
        chart_series=("#0D4A52", "#C85A17", "#0072B2", "#009E73", "#52666A", "#CC79A7"),
    ),
    "burgundy_offwhite": ColorPalette(
        palette_id="burgundy_offwhite",
        name="Academic Burgundy & Alabaster",
        canvas_bg="#FCFAF8",
        surface_tint="#F4ECEE",
        figure_bg="#FFFFFF",
        dominant="#5B1627",
        supporting="#7F2B40",
        accent="#0072B2",
        masthead_fg="#FFFFFF",
        masthead_sub_fg="#F2DCE1",
        body_ink="#201619",
        muted_ink="#57464B",
        rule_border="#DCCFD2",
        chart_series=("#5B1627", "#0072B2", "#009E73", "#D55E00", "#57534E", "#CC79A7"),
    ),
    "forest_cream": ColorPalette(
        palette_id="forest_cream",
        name="Forest Pine & Warm Cream",
        canvas_bg="#FAF9F4",
        surface_tint="#EDF2EB",
        figure_bg="#FFFFFF",
        dominant="#173B2D",
        supporting="#2D5E4A",
        accent="#C25E14",
        masthead_fg="#FFFFFF",
        masthead_sub_fg="#DCE8E2",
        body_ink="#18221D",
        muted_ink="#475950",
        rule_border="#CCD7D0",
        chart_series=("#173B2D", "#C25E14", "#0072B2", "#009E73", "#57685F", "#CC79A7"),
    ),
    "monochrome_editorial": ColorPalette(
        palette_id="monochrome_editorial",
        name="Monochromatic Scientific Editorial",
        canvas_bg="#FFFFFF",
        surface_tint="#F3F4F6",
        figure_bg="#FFFFFF",
        dominant="#111827",
        supporting="#374151",
        accent="#0072B2",
        masthead_fg="#FFFFFF",
        masthead_sub_fg="#E5E7EB",
        body_ink="#111827",
        muted_ink="#4B5563",
        rule_border="#D1D5DB",
        chart_series=("#111827", "#0072B2", "#D55E00", "#009E73", "#6B7280", "#CC79A7"),
    ),
}


def resolve_palette(
    palette_id: str = "academic_navy",
    custom_overrides: Optional[Dict[str, str]] = None,
) -> ColorPalette:
    base = PALETTES.get(palette_id, PALETTES["academic_navy"])
    if not custom_overrides:
        return base
    merged = {
        "palette_id": custom_overrides.get("palette_id", f"{base.palette_id}_custom"),
        "name": custom_overrides.get("name", f"{base.name} (Institutional Override)"),
        "canvas_bg": custom_overrides.get("canvas_bg", base.canvas_bg),
        "surface_tint": custom_overrides.get("surface_tint", base.surface_tint),
        "figure_bg": custom_overrides.get("figure_bg", base.figure_bg),
        "dominant": custom_overrides.get("dominant", base.dominant),
        "supporting": custom_overrides.get("supporting", base.supporting),
        "accent": custom_overrides.get("accent", base.accent),
        "masthead_fg": custom_overrides.get("masthead_fg", base.masthead_fg),
        "masthead_sub_fg": custom_overrides.get("masthead_sub_fg", base.masthead_sub_fg),
        "body_ink": custom_overrides.get("body_ink", base.body_ink),
        "muted_ink": custom_overrides.get("muted_ink", base.muted_ink),
        "rule_border": custom_overrides.get("rule_border", base.rule_border),
        "chart_series": tuple(custom_overrides.get("chart_series", base.chart_series)),
    }
    # Auto-guard masthead foreground contrast if user supplied a custom dominant color
    if "dominant" in custom_overrides and "masthead_fg" not in custom_overrides:
        if wcag_contrast_ratio("#FFFFFF", merged["dominant"]) >= 4.5:
            merged["masthead_fg"] = "#FFFFFF"
            merged["masthead_sub_fg"] = "#E2E8F0"
        else:
            merged["masthead_fg"] = "#111827"
            merged["masthead_sub_fg"] = "#374151"
    return ColorPalette(**merged)


# ---------------------------------------------------------------------------
# 3. Font Discovery, Fallback Resolution & Dimension-Scaled Typography
# ---------------------------------------------------------------------------

@dataclass
class ResolvedFontFamily:
    requested_name: str
    resolved_name: str
    regular_ttf: str
    bold_ttf: str
    italic_ttf: str
    semibold_ttf: str
    was_substituted: bool = False
    substitution_note: str = ""


@dataclass
class TypographySpec:
    pairing_id: str
    heading_font: ResolvedFontFamily
    body_font: ResolvedFontFamily
    scale_multiplier: float
    # Effective printed point sizes (1:1 poster scale)
    badge_pt: float
    title_pt: float
    authors_pt: float
    affiliations_pt: float
    section_heading_pt: float
    subheading_pt: float
    hero_metric_pt: float
    body_pt: float
    table_pt: float
    figure_label_pt: float
    caption_pt: float
    reference_pt: float
    # Reference floors at this physical size
    min_body_pt: float
    min_heading_pt: float
    min_caption_pt: float


BUNDLED_FAMILIES: Dict[str, Dict[str, str]] = {
    "Source Sans 3": {
        "regular": str(BUNDLED_FONT_DIR / "SourceSans3-Regular.ttf"),
        "bold": str(BUNDLED_FONT_DIR / "SourceSans3-Bold.ttf"),
        "italic": str(BUNDLED_FONT_DIR / "SourceSans3-It.ttf"),
        "semibold": str(BUNDLED_FONT_DIR / "SourceSans3-Semibold.ttf"),
    },
    "Source Serif 4": {
        "regular": str(BUNDLED_FONT_DIR / "SourceSerif4-Regular.ttf"),
        "bold": str(BUNDLED_FONT_DIR / "SourceSerif4-Bold.ttf"),
        "italic": str(BUNDLED_FONT_DIR / "SourceSerif4-It.ttf"),
        "semibold": str(BUNDLED_FONT_DIR / "SourceSerif4-Semibold.ttf"),
    },
    "IBM Plex Sans": {
        "regular": str(BUNDLED_FONT_DIR / "IBMPlexSans-Regular.ttf"),
        "bold": str(BUNDLED_FONT_DIR / "IBMPlexSans-Bold.ttf"),
        "italic": str(BUNDLED_FONT_DIR / "IBMPlexSans-Italic.ttf"),
        "semibold": str(BUNDLED_FONT_DIR / "IBMPlexSans-SemiBold.ttf"),
    },
}

FONT_PAIRING_PRESETS: Dict[str, Tuple[str, str]] = {
    "editorial_modern": ("Source Sans 3", "Source Serif 4"),
    "clinical_precision": ("IBM Plex Sans", "IBM Plex Sans"),
    "swiss_scientific": ("Source Sans 3", "Source Sans 3"),
    "classic_symposium": ("Source Serif 4", "Source Sans 3"),
    "contemporary_clean": ("IBM Plex Sans", "Source Sans 3"),
}

SERIF_HINTS = {"serif", "georgia", "garamond", "baskerville", "times", "palatino", "cambria", "stix"}


def _discover_system_font_files(family_name: str) -> Optional[Dict[str, str]]:
    """Inspect bundled OFL fonts first, then system font manager."""
    # Check exact or case-insensitive bundled fonts
    for b_name, paths in BUNDLED_FAMILIES.items():
        if b_name.lower() == family_name.strip().lower():
            if all(pathlib.Path(p).exists() for p in paths.values()):
                return {"resolved_name": b_name, **paths}

    # Check Matplotlib's font_manager for system-installed TrueType fonts
    try:
        from matplotlib import font_manager

        matches = [
            f for f in font_manager.fontManager.ttflist
            if f.name.lower() == family_name.strip().lower() and f.fname.lower().endswith((".ttf", ".otf"))
        ]
        if matches:
            reg = next((f.fname for f in matches if f.style == "normal" and int(f.weight) in (400, 500)), matches[0].fname)
            bold = next((f.fname for f in matches if int(f.weight) >= 650 and f.style == "normal"), reg)
            semi = next((f.fname for f in matches if 550 <= int(f.weight) < 650 and f.style == "normal"), bold)
            ital = next((f.fname for f in matches if f.style in ("italic", "oblique")), reg)
            return {
                "resolved_name": matches[0].name,
                "regular": reg,
                "bold": bold,
                "italic": ital,
                "semibold": semi,
            }
    except Exception:
        pass
    return None


def resolve_font_family(requested_name: str) -> ResolvedFontFamily:
    """Resolve requested font family to concrete TrueType files, logging any fallback."""
    found = _discover_system_font_files(requested_name)
    if found:
        return ResolvedFontFamily(
            requested_name=requested_name,
            resolved_name=found["resolved_name"],
            regular_ttf=found["regular"],
            bold_ttf=found["bold"],
            italic_ttf=found["italic"],
            semibold_ttf=found["semibold"],
            was_substituted=False,
        )

    is_serif = any(tok in requested_name.lower() for tok in SERIF_HINTS)
    fallback_candidates = (
        ["Source Serif 4", "DejaVu Serif"]
        if is_serif
        else ["IBM Plex Sans", "Source Sans 3", "DejaVu Sans"]
    )
    for cand in fallback_candidates:
        fb = _discover_system_font_files(cand)
        if fb:
            note = (
                f"Requested font '{requested_name}' is not installed locally; "
                f"resolved to metrically verified '{fb['resolved_name']}' for layout, charts, and PDF embedding."
            )
            return ResolvedFontFamily(
                requested_name=requested_name,
                resolved_name=fb["resolved_name"],
                regular_ttf=fb["regular"],
                bold_ttf=fb["bold"],
                italic_ttf=fb["italic"],
                semibold_ttf=fb["semibold"],
                was_substituted=True,
                substitution_note=note,
            )

    raise RuntimeError(
        f"Could not locate requested font '{requested_name}' or any fallback TrueType font."
    )


def resolve_typography(
    dimensions: PosterDimensions,
    pairing_id: str = "clinical_precision",
    heading_font_override: Optional[str] = None,
    body_font_override: Optional[str] = None,
) -> TypographySpec:
    """
    Calculate physical poster-scale typography anchored to viewing distance
    and poster board dimensions.
    Reference baseline (1.0x): 48 x 36 in / ISO A0 (short edge ~33-36 in):
      - Title ~84-88 pt (ref 85 pt)
      - Authors ~48-56 pt (ref 56 pt)
      - Headings ~36-40 pt (ref 36 pt)
      - Body ~24-26 pt (ref 24 pt)
      - Captions/Refs ~18-20 pt (ref 18 pt)
    """
    default_h, default_b = FONT_PAIRING_PRESETS.get(
        pairing_id, FONT_PAIRING_PRESETS["clinical_precision"]
    )
    h_family = resolve_font_family(heading_font_override or default_h)
    b_family = resolve_font_family(body_font_override or default_b)

    # Proportional physical scaling for compact vs oversized boards
    # Reference area: 48 * 36 = 1728 sq in (A0 = 1550 sq in)
    diag = math.hypot(dimensions.width_in, dimensions.height_in)
    ref_diag = math.hypot(48.0, 36.0)  # 60.0 in
    raw_ratio = diag / ref_diag

    if dimensions.short_edge_in >= 32.0:
        # Full-size conference poster (A0, 48x36, 36x48, 42x56, 56x42)
        scale = max(1.0, min(1.16, raw_ratio))
        min_body, min_heading, min_caption = 24.0, 36.0, 18.0
    else:
        # Medium/compact symposium poster (A1, 36x24)
        scale = max(0.75, min(0.95, raw_ratio))
        min_body = round(max(18.0, 24.0 * scale), 1)
        min_heading = round(max(26.0, 36.0 * scale), 1)
        min_caption = round(max(14.0, 18.0 * scale), 1)

    return TypographySpec(
        pairing_id=pairing_id,
        heading_font=h_family,
        body_font=b_family,
        scale_multiplier=round(scale, 3),
        badge_pt=round(20.0 * scale, 1),
        title_pt=round(max(74.0 * scale, 85.0 * (scale if scale < 1.0 else 1.0)), 1),
        authors_pt=round(52.0 * scale, 1),
        affiliations_pt=round(28.0 * scale, 1),
        section_heading_pt=round(max(min_heading, 38.0 * scale), 1),
        subheading_pt=round(28.0 * scale, 1),
        hero_metric_pt=round(50.0 * scale, 1),
        body_pt=round(max(min_body, 25.0 * scale), 1),
        table_pt=round(max(min_caption + 2.0, 21.0 * scale), 1),
        figure_label_pt=round(max(min_caption + 3.0, 22.0 * scale), 1),
        caption_pt=round(max(min_caption, 19.0 * scale), 1),
        reference_pt=round(max(min_caption, 18.0 * scale), 1),
        min_body_pt=min_body,
        min_heading_pt=min_heading,
        min_caption_pt=min_caption,
    )
