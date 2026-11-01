#!/usr/bin/env python3
"""
Print-Ready Vector PDF Renderer for research-poster-maker.

Provides two verified export pathways:
  1. LibreOffice Impress headless conversion ('libreoffice') when installed.
  2. Native ReportLab + svglib Vector Scene Renderer ('reportlab_vector'),
     preserving exact physical MediaBox dimensions (even >56 in at 1:1 scale),
     embedded TrueType font subsets, and infinite-resolution SVG vector plots.
"""

from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image
Image.MAX_IMAGE_PIXELS = 250_000_000
from reportlab.graphics import renderPDF
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas

from .layout_solver import FontMetrics

PT_PER_INCH = 72.0


def _register_rl_fonts(typo: Dict[str, Any]) -> Dict[str, str]:
    """Register resolved TrueType fonts in ReportLab for true font embedding."""
    mapping = {
        "h_reg": typo["heading_font"]["regular_ttf"],
        "h_bold": typo["heading_font"]["bold_ttf"],
        "h_semi": typo["heading_font"]["semibold_ttf"],
        "b_reg": typo["body_font"]["regular_ttf"],
        "b_bold": typo["body_font"]["bold_ttf"],
        "b_ital": typo["body_font"]["italic_ttf"],
    }
    registered: Dict[str, str] = {}
    for key, ttf_path in mapping.items():
        rl_name = f"PosterFont_{key}_{pathlib.Path(ttf_path).stem}"
        if rl_name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(rl_name, ttf_path))
        registered[key] = rl_name
    return registered


def _draw_svg_or_png(
    c: rl_canvas.Canvas,
    svg_path: Optional[str],
    png_path: Optional[str],
    box_x_pt: float,
    box_y_bottom_pt: float,
    box_w_pt: float,
    box_h_pt: float,
) -> str:
    """Embed vector SVG via svglib if available; otherwise high-DPI PNG."""
    if svg_path and pathlib.Path(svg_path).exists():
        try:
            from svglib.svglib import svg2rlg

            drawing = svg2rlg(str(svg_path))
            if drawing and drawing.width > 0 and drawing.height > 0:
                sx = box_w_pt / float(drawing.width)
                sy = box_h_pt / float(drawing.height)
                scale = min(sx, sy)
                dw = float(drawing.width) * scale
                dh = float(drawing.height) * scale
                dx = box_x_pt + (box_w_pt - dw) / 2.0
                dy = box_y_bottom_pt + (box_h_pt - dh) / 2.0
                c.saveState()
                c.translate(dx, dy)
                c.scale(scale, scale)
                renderPDF.draw(drawing, c, 0, 0)
                c.restoreState()
                return "vector_svg"
        except Exception:
            pass

    if png_path and pathlib.Path(png_path).exists():
        with Image.open(png_path) as im:
            pw, ph = im.size
        scale = min(box_w_pt / max(1.0, float(pw)), box_h_pt / max(1.0, float(ph)))
        dw = pw * scale
        dh = ph * scale
        dx = box_x_pt + (box_w_pt - dw) / 2.0
        dy = box_y_bottom_pt + (box_h_pt - dh) / 2.0
        c.drawImage(ImageReader(str(png_path)), dx, dy, width=dw, height=dh, preserveAspectRatio=True, mask="auto")
        return "raster_png"

    return "missing"


def render_scene_to_vector_pdf(scene_dict: Dict[str, Any], out_pdf: pathlib.Path) -> Dict[str, Any]:
    """Render poster scene IR directly to an exact-dimension vector PDF."""
    dims = scene_dict["dimensions"]
    pal = scene_dict["palette"]
    typo = scene_dict["typography"]

    W_in = float(dims["width_in"])
    H_in = float(dims["height_in"])
    W_pt = W_in * PT_PER_INCH
    H_pt = H_in * PT_PER_INCH

    fonts = _register_rl_fonts(typo)
    fm = FontMetrics()

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    c = rl_canvas.Canvas(str(out_pdf), pagesize=(W_pt, H_pt))
    c.setTitle(scene_dict.get("poster_title", "Scientific Research Poster"))
    c.setAuthor("research-poster-maker")

    def y_top_to_rl(y_in: float, h_in: float = 0.0) -> float:
        """Convert top-down inches to ReportLab bottom-up points."""
        return (H_in - y_in - h_in) * PT_PER_INCH

    def draw_wrapped_lines(
        lines: List[str],
        x_in: float,
        cursor_top_in: float,
        font_key: str,
        pt: float,
        color_hex: str,
        line_spacing: float = 1.22,
        bold_bullet_prefix: bool = False,
    ) -> float:
        c.setFillColor(HexColor(color_hex))
        step_in = (pt / PT_PER_INCH) * line_spacing
        for idx_l, line in enumerate(lines):
            baseline_y_pt = (H_in - (cursor_top_in + (idx_l + 0.84) * step_in)) * PT_PER_INCH
            x_pt = x_in * PT_PER_INCH
            if bold_bullet_prefix and idx_l == 0:
                m_lead = re.match(r"^([•–\-]\s+[^:]{2,42}:)(\s+.*)$", line)
                if m_lead:
                    pre, rest = m_lead.group(1), m_lead.group(2)
                    c.setFont(fonts["b_bold"], pt)
                    c.drawString(x_pt, baseline_y_pt, pre)
                    pre_w = pdfmetrics.stringWidth(pre, fonts["b_bold"], pt)
                    c.setFont(fonts[font_key], pt)
                    c.drawString(x_pt + pre_w, baseline_y_pt, rest)
                    continue
            c.setFont(fonts[font_key], pt)
            c.drawString(x_pt, baseline_y_pt, line)
        return cursor_top_in + len(lines) * step_in

    vector_fig_count = 0
    raster_fig_count = 0

    # Background canvas
    c.setFillColor(HexColor(pal["canvas_bg"]))
    c.rect(0, 0, W_pt, H_pt, stroke=0, fill=1)

    for el in scene_dict["elements"]:
        kind = el["kind"]
        if kind == "background":
            continue

        x = float(el["x_in"])
        y = float(el["y_in"])
        w = float(el["w_in"])
        h = float(el["h_in"])
        p = el["payload"]

        if kind == "masthead":
            style = p.get("style", "solid_banner")
            mx = float(p.get("margin_x_in", 0.0))
            pad_top = float(p.get("pad_top_in", 0.45))

            if style == "solid_banner":
                c.setFillColor(HexColor(p["bg_color"]))
                c.rect(x * PT_PER_INCH, y_top_to_rl(y, h - 0.06), w * PT_PER_INCH, (h - 0.06) * PT_PER_INCH, stroke=0, fill=1)
                c.setFillColor(HexColor(p["accent_color"]))
                c.rect(x * PT_PER_INCH, y_top_to_rl(y + h - 0.06, 0.06), w * PT_PER_INCH, 0.06 * PT_PER_INCH, stroke=0, fill=1)
            else:
                c.setFillColor(HexColor(pal["dominant"]))
                c.rect(x * PT_PER_INCH, y_top_to_rl(y + h - 0.05, 0.04), w * PT_PER_INCH, 0.04 * PT_PER_INCH, stroke=0, fill=1)

            cur = y + pad_top
            tx = x + mx
            if p.get("badge"):
                cur = draw_wrapped_lines(
                    [p["badge"].upper()], tx, cur, "h_bold", float(typo["badge_pt"]),
                    p["accent_color"] if style != "solid_banner" else p["sub_fg_color"], line_spacing=1.35,
                ) + 0.06
            cur = draw_wrapped_lines(
                p.get("title_lines") or [p["title"]], tx, cur, "h_bold", float(typo["title_pt"]),
                p["fg_color"], line_spacing=1.10,
            ) + 0.12
            if p.get("author_lines"):
                cur = draw_wrapped_lines(
                    p["author_lines"], tx, cur, "h_semi", float(typo["authors_pt"]),
                    p["fg_color"], line_spacing=1.14,
                ) + 0.07
            if p.get("affil_lines"):
                draw_wrapped_lines(
                    p["affil_lines"], tx, cur, "b_reg", float(typo["affiliations_pt"]),
                    p["sub_fg_color"], line_spacing=1.16,
                )

            right_cursor = x + w - mx
            if p.get("qr_path") and pathlib.Path(p["qr_path"]).exists():
                qr_sz = min(2.25, h - 0.85)
                qx = right_cursor - qr_sz
                qy = y + (h - qr_sz) / 2.0 - 0.08
                _draw_svg_or_png(c, None, p["qr_path"], qx * PT_PER_INCH, y_top_to_rl(qy, qr_sz), qr_sz * PT_PER_INCH, qr_sz * PT_PER_INCH)
                right_cursor = qx - 0.35
            if p.get("logo_path") and pathlib.Path(p["logo_path"]).exists():
                lw, lh = 2.8, min(2.1, h - 0.9)
                lx = right_cursor - lw
                ly = y + (h - lh) / 2.0
                _draw_svg_or_png(c, None, p["logo_path"], lx * PT_PER_INCH, y_top_to_rl(ly, lh), lw * PT_PER_INCH, lh * PT_PER_INCH)

        elif kind == "banner_band":
            c.setFillColor(HexColor(p["bg_color"]))
            c.setStrokeColor(HexColor(pal["rule_border"]))
            c.setLineWidth(0.75)
            c.rect(x * PT_PER_INCH, y_top_to_rl(y, h), w * PT_PER_INCH, h * PT_PER_INCH, stroke=1, fill=1)
            c.setFillColor(HexColor(p["accent_color"]))
            c.rect(x * PT_PER_INCH, y_top_to_rl(y, h), 0.09 * PT_PER_INCH, h * PT_PER_INCH, stroke=0, fill=1)

            cur = y + 0.20
            cur = draw_wrapped_lines([p.get("label", "KEY FINDING")], x + 0.42, cur, "h_bold", float(typo["badge_pt"]), p["accent_color"], 1.25) + 0.04
            draw_wrapped_lines(p.get("lines") or [p["text"]], x + 0.42, cur, "h_bold", float(p["pt"]), p["fg_color"], 1.15)

        elif kind in ("section_text", "callout"):
            m = p.get("metrics", {})
            style = p.get("style", "editorial_rule")
            if kind == "callout":
                c.setFillColor(HexColor(pal["surface_tint"]))
                c.setStrokeColor(HexColor(pal["rule_border"]))
                c.setLineWidth(0.75)
                c.rect(x * PT_PER_INCH, y_top_to_rl(y, h), w * PT_PER_INCH, h * PT_PER_INCH, stroke=1, fill=1)
                bar_col = pal["accent"] if style == "focal_callout" else pal["dominant"]
                c.setFillColor(HexColor(bar_col))
                c.rect(x * PT_PER_INCH, y_top_to_rl(y, h), 0.08 * PT_PER_INCH, h * PT_PER_INCH, stroke=0, fill=1)
                tx = x + float(m.get("pad_x", 0.38))
                cur = y + float(m.get("pad_y", 0.28))
            else:
                c.setFillColor(HexColor(pal["dominant"]))
                c.rect(x * PT_PER_INCH, y_top_to_rl(y, 0.032), w * PT_PER_INCH, 0.032 * PT_PER_INCH, stroke=0, fill=1)
                tx = x + 0.04
                cur = y + 0.14

            if m.get("title_lines"):
                cur = draw_wrapped_lines(m["title_lines"], tx, cur, "h_bold", float(typo["section_heading_pt"]), pal["dominant"], 1.14) + 0.12
            if m.get("hero_lines"):
                cur = draw_wrapped_lines(m["hero_lines"], tx, cur, "h_bold", float(typo["hero_metric_pt"]), pal["accent"], 1.10) + 0.12
            for plines in m.get("para_wrapped", []):
                cur = draw_wrapped_lines(plines, tx, cur, "b_reg", float(typo["body_pt"]), pal["body_ink"], 1.24) + 0.10
            for blines in m.get("bullet_wrapped", []):
                cur = draw_wrapped_lines(blines, tx, cur, "b_reg", float(typo["body_pt"]), pal["body_ink"], 1.22, bold_bullet_prefix=True) + 0.09

        elif kind == "figure":
            m = p.get("metrics", {})
            cur = y
            t_lines = m.get("title_lines") or ([p["title"]] if p.get("title") else [])
            if t_lines:
                cur = draw_wrapped_lines(t_lines, x, cur, "h_bold", float(typo["section_heading_pt"]), pal["dominant"], 1.14) + 0.10

            c_lines = m.get("caption_lines") or (
                fm.wrap_lines(p["caption"], typo["body_font"]["regular_ttf"], float(typo["caption_pt"]), w - 0.2)
                if p.get("caption") else []
            )
            cap_h = (len(c_lines) * (float(typo["caption_pt"]) / PT_PER_INCH) * 1.18 + 0.10) if c_lines else 0.0
            img_h = max(1.2, (y + h) - cur - cap_h - (0.08 if c_lines else 0.0))

            # Clean white figure well with hairline border
            c.setFillColor(HexColor(pal["figure_bg"]))
            c.setStrokeColor(HexColor(pal["rule_border"]))
            c.setLineWidth(0.65)
            c.rect(x * PT_PER_INCH, y_top_to_rl(cur, img_h), w * PT_PER_INCH, img_h * PT_PER_INCH, stroke=1, fill=1)

            mode = _draw_svg_or_png(
                c, p.get("svg_path"), p.get("png_path"),
                (x + 0.08) * PT_PER_INCH,
                y_top_to_rl(cur + 0.06, img_h - 0.12),
                (w - 0.16) * PT_PER_INCH,
                (img_h - 0.12) * PT_PER_INCH,
            )
            if mode == "vector_svg":
                vector_fig_count += 1
            elif mode == "raster_png":
                raster_fig_count += 1

            if c_lines:
                draw_wrapped_lines(c_lines, x + 0.04, cur + img_h + 0.08, "b_reg", float(typo["caption_pt"]), pal["muted_ink"], 1.18)

        elif kind == "table":
            m = p.get("metrics", {})
            cur = y
            if m.get("title_lines"):
                cur = draw_wrapped_lines(m["title_lines"], x, cur, "h_bold", float(typo["section_heading_pt"]), pal["dominant"], 1.14) + 0.10

            tdata = p["table_data"]
            headers = [str(v) for v in tdata["headers"]]
            rows = [[str(v) for v in r] for r in tdata["rows"]]
            col_ws = m.get("col_widths_in") or ([w / len(headers)] * len(headers))
            scale_w = w / max(0.1, sum(col_ws))
            col_ws = [cw * scale_w for cw in col_ws]
            col_xs = [x + sum(col_ws[:i]) for i in range(len(headers))]

            hdr_h = float(m.get("header_h_in", 0.50))
            row_hs = [float(rh) for rh in m.get("row_heights_in", [0.44] * len(rows))]
            tpt = float(typo["table_pt"])

            # Header background + booktabs rules
            c.setFillColor(HexColor(pal["surface_tint"]))
            c.rect(x * PT_PER_INCH, y_top_to_rl(cur, hdr_h), w * PT_PER_INCH, hdr_h * PT_PER_INCH, stroke=0, fill=1)
            c.setStrokeColor(HexColor(pal["dominant"]))
            c.setLineWidth(1.8)
            c.line(x * PT_PER_INCH, y_top_to_rl(cur, 0), (x + w) * PT_PER_INCH, y_top_to_rl(cur, 0))
            c.setLineWidth(1.1)
            c.line(x * PT_PER_INCH, y_top_to_rl(cur + hdr_h, 0), (x + w) * PT_PER_INCH, y_top_to_rl(cur + hdr_h, 0))

            c.setFillColor(HexColor(pal["dominant"]))
            c.setFont(fonts["b_bold"], tpt)
            for c_i, h_txt in enumerate(headers):
                ls = fm.wrap_lines(h_txt, typo["body_font"]["bold_ttf"], tpt, col_ws[c_i] - 0.16, 0.90)
                for li, line in enumerate(ls):
                    by = (H_in - (cur + 0.10 + (li + 0.82) * (tpt / PT_PER_INCH) * 1.15)) * PT_PER_INCH
                    if c_i == 0:
                        c.drawString((col_xs[c_i] + 0.08) * PT_PER_INCH, by, line)
                    else:
                        c.drawRightString((col_xs[c_i] + col_ws[c_i] - 0.08) * PT_PER_INCH, by, line)

            cur += hdr_h
            for r_i, (r_vals, rh) in enumerate(zip(rows, row_hs)):
                if r_i % 2 == 1:
                    c.setFillColor(HexColor(pal["surface_tint"]))
                    c.rect(x * PT_PER_INCH, y_top_to_rl(cur, rh), w * PT_PER_INCH, rh * PT_PER_INCH, stroke=0, fill=1)
                c.setFillColor(HexColor(pal["body_ink"]))
                for c_i, cell_txt in enumerate(r_vals[: len(headers)]):
                    is_bold = c_i == 0 and cell_txt.lower().startswith(("pooled", "overall", "primary"))
                    f_key = "b_bold" if is_bold else "b_reg"
                    c.setFont(fonts[f_key], tpt)
                    ls = fm.wrap_lines(cell_txt, typo["body_font"]["regular_ttf"], tpt, col_ws[c_i] - 0.16, 0.90)
                    for li, line in enumerate(ls):
                        by = (H_in - (cur + 0.08 + (li + 0.82) * (tpt / PT_PER_INCH) * 1.15)) * PT_PER_INCH
                        if c_i == 0:
                            c.drawString((col_xs[c_i] + 0.08) * PT_PER_INCH, by, line)
                        else:
                            c.drawRightString((col_xs[c_i] + col_ws[c_i] - 0.08) * PT_PER_INCH, by, line)
                cur += rh
                c.setStrokeColor(HexColor(pal["dominant"] if r_i == len(rows) - 1 else pal["rule_border"]))
                c.setLineWidth(1.8 if r_i == len(rows) - 1 else 0.45)
                c.line(x * PT_PER_INCH, y_top_to_rl(cur, 0), (x + w) * PT_PER_INCH, y_top_to_rl(cur, 0))

            if m.get("footnote_lines"):
                draw_wrapped_lines(m["footnote_lines"], x + 0.04, cur + 0.07, "b_ital", float(typo["caption_pt"]), pal["muted_ink"], 1.16)

        elif kind == "colophon":
            c.setStrokeColor(HexColor(p["rule_color"]))
            c.setLineWidth(0.8)
            c.line(x * PT_PER_INCH, y_top_to_rl(y, 0), (x + w) * PT_PER_INCH, y_top_to_rl(y, 0))
            draw_wrapped_lines(p["lines"], x, y + 0.10, "b_reg", float(typo["reference_pt"]), p["fg_color"], 1.18)

    c.showPage()
    c.save()

    return {
        "pdf_path": str(out_pdf),
        "backend": "reportlab_vector",
        "width_in": W_in,
        "height_in": H_in,
        "vector_svg_figures_embedded": vector_fig_count,
        "raster_figures_embedded": raster_fig_count,
    }


def export_pptx_with_libreoffice(pptx_path: pathlib.Path, out_pdf: pathlib.Path, timeout_sec: int = 120) -> Optional[Dict[str, Any]]:
    """Convert PPTX to PDF using LibreOffice headless if installed."""
    soffice = shutil.which("libreoffice") or shutil.which("soffice")
    if not soffice:
        return None
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    cmd = [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(out_pdf.parent), str(pptx_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
    expected = out_pdf.parent / f"{pptx_path.stem}.pdf"
    if proc.returncode != 0 or not expected.exists():
        return None
    if expected.resolve() != out_pdf.resolve():
        shutil.move(str(expected), str(out_pdf))
    return {
        "pdf_path": str(out_pdf),
        "backend": "libreoffice",
        "binary": soffice,
    }
