#!/usr/bin/env python3
"""
Editable PowerPoint (.pptx) Renderer for research-poster-maker.

Renders PosterSceneIR into native, human-editable OOXML shapes, rich multi-run
text frames, booktabs academic tables, native editable charts (where practical),
and high-DPI scientific figures—never flattening the poster into one image.
"""

from __future__ import annotations

import pathlib
import re
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image
Image.MAX_IMAGE_PIXELS = 250_000_000
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt

from .design_tokens import hex_to_rgb
from .layout_solver import PosterSceneIR, SceneElement


def _rgb(hex_color: str) -> RGBColor:
    r, g, b = hex_to_rgb(hex_color)
    return RGBColor(r, g, b)


def _add_rich_runs(
    paragraph,
    text: str,
    font_name: str,
    pt_size: float,
    color_hex: str,
    default_bold: bool = False,
) -> None:
    """
    Format scientific text runs natively in PowerPoint:
      - Bold lead-in labels before ':' on bullet lines (e.g., 'Primary Outcome: ...')
      - Italic statistical symbols (p =, p <, I²)
    """
    fg = _rgb(color_hex)

    # Bullet lead-in bolding (e.g. "•  Study Population: 4,820 adults...")
    lead_match = re.match(r"^([•–\-]\s+[^:]{2,42}:)(\s+.*)$", text)
    if lead_match and not default_bold:
        r1 = paragraph.add_run()
        r1.text = lead_match.group(1)
        r1.font.name = font_name
        r1.font.size = Pt(pt_size)
        r1.font.bold = True
        r1.font.color.rgb = fg
        remainder = lead_match.group(2)
    else:
        remainder = text

    # Split statistical tokens to italicize 'p' in 'p =' or 'p <'
    tokens = re.split(r"(\bp\s*[=<≤]\s*\d+(?:\.\d+)?)", remainder)
    for tok in tokens:
        if not tok:
            continue
        stat_m = re.match(r"^(p)(\s*[=<≤]\s*\d+(?:\.\d+)?)$", tok)
        if stat_m and not default_bold:
            rp = paragraph.add_run()
            rp.text = stat_m.group(1)
            rp.font.name = font_name
            rp.font.size = Pt(pt_size)
            rp.font.italic = True
            rp.font.color.rgb = fg

            rv = paragraph.add_run()
            rv.text = stat_m.group(2)
            rv.font.name = font_name
            rv.font.size = Pt(pt_size)
            rv.font.bold = default_bold
            rv.font.color.rgb = fg
        else:
            r = paragraph.add_run()
            r.text = tok
            r.font.name = font_name
            r.font.size = Pt(pt_size)
            r.font.bold = default_bold
            r.font.color.rgb = fg


def _set_cell_borders_booktabs(
    cell,
    top_hex: Optional[str] = None,
    top_pt: float = 0.0,
    bottom_hex: Optional[str] = None,
    bottom_pt: float = 0.0,
) -> None:
    """Apply clean journal booktabs horizontal rules and strip vertical borders."""
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("lnL", "lnR", "lnT", "lnB", "lnTlToBr", "lnBlToTr"):
        existing = tcPr.find(f"{{http://schemas.openxmlformats.org/drawingml/2006/main}}{tag}")
        if existing is not None:
            tcPr.remove(existing)

    def make_ln(tag: str, color_hex: Optional[str], width_pt: float):
        ln = OxmlElement(f"a:{tag}")
        if color_hex and width_pt > 0:
            ln.set("w", str(int(round(width_pt * 12700))))
            ln.set("cap", "flat")
            ln.set("cmpd", "sng")
            solid = OxmlElement("a:solidFill")
            srgb = OxmlElement("a:srgbClr")
            srgb.set("val", color_hex.lstrip("#").upper())
            solid.append(srgb)
            ln.append(solid)
        else:
            no_fill = OxmlElement("a:noFill")
            ln.append(no_fill)
        tcPr.append(ln)

    make_ln("lnL", None, 0)
    make_ln("lnR", None, 0)
    make_ln("lnT", top_hex, top_pt)
    make_ln("lnB", bottom_hex, bottom_pt)


def _fit_image_box(
    img_path: str,
    box_x: float,
    box_y: float,
    box_w: float,
    box_h: float,
) -> Tuple[float, float, float, float]:
    """Fit an image inside (box_x, box_y, box_w, box_h) preserving exact aspect ratio."""
    with Image.open(img_path) as im:
        px_w, px_h = im.size
    aspect = px_w / max(1.0, float(px_h))
    box_aspect = box_w / max(0.1, box_h)
    if aspect >= box_aspect:
        w = box_w
        h = box_w / aspect
        x = box_x
        y = box_y + (box_h - h) / 2.0
    else:
        h = box_h
        w = box_h * aspect
        x = box_x + (box_w - w) / 2.0
        y = box_y
    return x, y, w, h


def render_scene_to_pptx(scene: PosterSceneIR, out_pptx: pathlib.Path) -> Dict[str, Any]:
    """Render PosterSceneIR into a native, single-slide editable PowerPoint file."""
    dims = scene.dimensions
    pal = scene.palette
    typo = scene.typography
    s = float(dims["pptx_scale_factor"])  # 1.0 for <=56 in; 0.5 for >56 in

    h_font = typo["heading_font"]["resolved_name"]
    b_font = typo["body_font"]["resolved_name"]

    prs = Presentation()
    prs.slide_width = Inches(dims["pptx_width_in"])
    prs.slide_height = Inches(dims["pptx_height_in"])
    prs.core_properties.title = scene.poster_title
    prs.core_properties.subject = f"Scientific Research Poster ({dims['label']})"

    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)

    # Set native slide background color cleanly (avoids giant background shape collisions)
    bg_fill = slide.background.fill
    bg_fill.solid()
    bg_fill.fore_color.rgb = _rgb(pal["canvas_bg"])

    shape_count = 0
    native_chart_count = 0

    for el in scene.elements:
        if el.kind == "background":
            continue

        x = el.x_in * s
        y = el.y_in * s
        w = el.w_in * s
        h = el.h_in * s
        p = el.payload

        if el.kind == "masthead":
            style = p.get("style", "solid_banner")
            mx = float(p.get("margin_x_in", 0.0)) * s
            pad_top = float(p.get("pad_top_in", 0.4)) * s
            tmax_w = float(p.get("title_max_w_in", el.w_in)) * s

            if style == "solid_banner":
                banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h - 0.06 * s))
                banner.name = "container:masthead_banner"
                banner.fill.solid()
                banner.fill.fore_color.rgb = _rgb(p["bg_color"])
                banner.line.fill.background()

                accent_rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y + h - 0.06 * s), Inches(w), Inches(0.06 * s))
                accent_rule.name = "rule:masthead_accent"
                accent_rule.fill.solid()
                accent_rule.fill.fore_color.rgb = _rgb(p["accent_color"])
                accent_rule.line.fill.background()
                shape_count += 2
            else:
                # Editorial light masthead with bottom architectural rule
                rule_y = y + h - 0.05 * s
                top_rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(rule_y), Inches(w), Inches(0.04 * s))
                top_rule.name = "rule:masthead_editorial"
                top_rule.fill.solid()
                top_rule.fill.fore_color.rgb = _rgb(pal["dominant"])
                top_rule.line.fill.background()
                shape_count += 1

            # Masthead text frame (Badge + Title + Authors + Affiliations)
            tb_x = x + mx
            tb_y = y + pad_top
            tb_h = max(0.5, h - pad_top - 0.14 * s)
            tb = slide.shapes.add_textbox(Inches(tb_x), Inches(tb_y), Inches(tmax_w), Inches(tb_h))
            tb.name = "text:masthead_header"
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0)
            tf.margin_right = Inches(0)
            tf.margin_top = Inches(0)
            tf.margin_bottom = Inches(0)

            first_para = True

            def next_para():
                nonlocal first_para
                if first_para:
                    first_para = False
                    return tf.paragraphs[0]
                return tf.add_paragraph()

            if p.get("badge"):
                bp = next_para()
                bp.alignment = PP_ALIGN.LEFT
                bp.space_after = Pt(6 * s)
                run = bp.add_run()
                run.text = p["badge"].upper()
                run.font.name = h_font
                run.font.size = Pt(typo["badge_pt"] * s)
                run.font.bold = True
                run.font.color.rgb = _rgb(p["accent_color"] if style != "solid_banner" else p["sub_fg_color"])

            tp = next_para()
            tp.alignment = PP_ALIGN.LEFT
            tp.line_spacing = 1.08
            tp.space_after = Pt(10 * s)
            tr = tp.add_run()
            tr.text = p["title"]
            tr.font.name = h_font
            tr.font.size = Pt(typo["title_pt"] * s)
            tr.font.bold = True
            tr.font.color.rgb = _rgb(p["fg_color"])

            if p.get("authors"):
                ap = next_para()
                ap.alignment = PP_ALIGN.LEFT
                ap.line_spacing = 1.12
                ap.space_after = Pt(5 * s)
                ar = ap.add_run()
                ar.text = p["authors"]
                ar.font.name = h_font
                ar.font.size = Pt(typo["authors_pt"] * s)
                ar.font.bold = True
                ar.font.color.rgb = _rgb(p["fg_color"])

            if p.get("affiliations"):
                fp = next_para()
                fp.alignment = PP_ALIGN.LEFT
                fp.line_spacing = 1.14
                fr = fp.add_run()
                fr.text = p["affiliations"]
                fr.font.name = b_font
                fr.font.size = Pt(typo["affiliations_pt"] * s)
                fr.font.color.rgb = _rgb(p["sub_fg_color"])
            shape_count += 1

            # Right-side Logo & QR Code (strictly disjoint coordinates inside safe margin)
            right_cursor = x + w - mx
            if p.get("qr_path") and pathlib.Path(p["qr_path"]).exists():
                qr_size = min(2.25 * s, h - 0.85 * s)
                qr_x = right_cursor - qr_size
                qr_y = y + (h - qr_size) / 2.0 - 0.08 * s
                pic = slide.shapes.add_picture(str(p["qr_path"]), Inches(qr_x), Inches(qr_y), Inches(qr_size), Inches(qr_size))
                pic.name = "image:qr_code"
                right_cursor = qr_x - 0.35 * s
                shape_count += 1

            if p.get("logo_path") and pathlib.Path(p["logo_path"]).exists():
                lw_box = 2.8 * s
                lh_box = min(2.1 * s, h - 0.9 * s)
                lx_box = right_cursor - lw_box
                ly_box = y + (h - lh_box) / 2.0
                fx, fy, fw, fh = _fit_image_box(str(p["logo_path"]), lx_box, ly_box, lw_box, lh_box)
                lpic = slide.shapes.add_picture(str(p["logo_path"]), Inches(fx), Inches(fy), Inches(fw), Inches(fh))
                lpic.name = "image:institution_logo"
                shape_count += 1

        elif el.kind == "banner_band":
            accent_w = 0.09 * s
            bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(accent_w), Inches(h))
            bar.name = f"rule:{el.id}_accent"
            bar.fill.solid()
            bar.fill.fore_color.rgb = _rgb(p["accent_color"])
            bar.line.fill.background()

            box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x + accent_w), Inches(y), Inches(w - accent_w), Inches(h))
            box.name = f"callout:{el.id}"
            box.fill.solid()
            box.fill.fore_color.rgb = _rgb(p["bg_color"])
            box.line.color.rgb = _rgb(pal["rule_border"])
            box.line.width = Pt(0.75)

            tf = box.text_frame
            tf.word_wrap = True
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf.margin_left = Inches(0.35 * s)
            tf.margin_right = Inches(0.35 * s)
            tf.margin_top = Inches(0.18 * s)
            tf.margin_bottom = Inches(0.18 * s)

            p0 = tf.paragraphs[0]
            p0.space_after = Pt(4 * s)
            r0 = p0.add_run()
            r0.text = p.get("label", "KEY FINDING")
            r0.font.name = h_font
            r0.font.size = Pt(typo["badge_pt"] * s)
            r0.font.bold = True
            r0.font.color.rgb = _rgb(p["accent_color"])

            p1 = tf.add_paragraph()
            p1.line_spacing = 1.14
            r1 = p1.add_run()
            r1.text = p["text"]
            r1.font.name = h_font
            r1.font.size = Pt(float(p["pt"]) * s)
            r1.font.bold = True
            r1.font.color.rgb = _rgb(p["fg_color"])
            shape_count += 2

        elif el.kind in ("section_text", "callout"):
            is_callout = el.kind == "callout"
            style = p.get("style", "editorial_rule")

            if is_callout:
                accent_w = 0.08 * s
                accent_col = pal["accent"] if style == "focal_callout" else pal["dominant"]
                bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(accent_w), Inches(h))
                bar.name = f"rule:{el.id}_bar"
                bar.fill.solid()
                bar.fill.fore_color.rgb = _rgb(accent_col)
                bar.line.fill.background()

                panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x + accent_w), Inches(y), Inches(w - accent_w), Inches(h))
                panel.name = f"callout:{el.id}"
                panel.fill.solid()
                panel.fill.fore_color.rgb = _rgb(pal["surface_tint"])
                panel.line.color.rgb = _rgb(pal["rule_border"])
                panel.line.width = Pt(0.75)
                tf = panel.text_frame
                tf.margin_left = Inches(0.32 * s)
                tf.margin_right = Inches(0.30 * s)
                tf.margin_top = Inches(0.26 * s)
                tf.margin_bottom = Inches(0.22 * s)
                shape_count += 2
            else:
                rule_h = 0.032 * s
                rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(rule_h))
                rule.name = f"rule:{el.id}_top"
                rule.fill.solid()
                rule.fill.fore_color.rgb = _rgb(pal["dominant"])
                rule.line.fill.background()

                tb = slide.shapes.add_textbox(Inches(x), Inches(y + rule_h + 0.06 * s), Inches(w), Inches(max(0.4, h - rule_h - 0.06 * s)))
                tb.name = f"section:{el.id}"
                tf = tb.text_frame
                tf.margin_left = Inches(0.04 * s)
                tf.margin_right = Inches(0.04 * s)
                tf.margin_top = Inches(0.04 * s)
                tf.margin_bottom = Inches(0.04 * s)
                shape_count += 2

            tf.word_wrap = True
            tf.vertical_anchor = MSO_ANCHOR.TOP

            first = True

            def add_p():
                nonlocal first
                if first:
                    first = False
                    return tf.paragraphs[0]
                return tf.add_paragraph()

            if p.get("title"):
                hp = add_p()
                hp.alignment = PP_ALIGN.LEFT
                hp.line_spacing = 1.12
                hp.space_after = Pt(8 * s)
                hr = hp.add_run()
                hr.text = p["title"]
                hr.font.name = h_font
                hr.font.size = Pt(typo["section_heading_pt"] * s)
                hr.font.bold = True
                hr.font.color.rgb = _rgb(pal["dominant"])

            if p.get("hero_metric"):
                mp = add_p()
                mp.alignment = PP_ALIGN.LEFT
                mp.line_spacing = 1.08
                mp.space_after = Pt(8 * s)
                mr = mp.add_run()
                mr.text = p["hero_metric"]
                mr.font.name = h_font
                mr.font.size = Pt(typo["hero_metric_pt"] * s)
                mr.font.bold = True
                mr.font.color.rgb = _rgb(pal["accent"])

            for para_txt in p.get("paragraphs", []):
                bp = add_p()
                bp.alignment = PP_ALIGN.LEFT
                bp.line_spacing = 1.22
                bp.space_after = Pt(7 * s)
                _add_rich_runs(bp, para_txt, b_font, typo["body_pt"] * s, pal["body_ink"])

            for bul_txt in p.get("bullets", []):
                b_clean = bul_txt if bul_txt.startswith(("•", "–", "-")) else f"•  {bul_txt}"
                bp = add_p()
                bp.alignment = PP_ALIGN.LEFT
                bp.line_spacing = 1.20
                bp.space_after = Pt(6 * s)
                _add_rich_runs(bp, b_clean, b_font, typo["body_pt"] * s, pal["body_ink"])

        elif el.kind == "figure":
            m = p.get("metrics", {})
            cur_y = y
            if p.get("title"):
                th = max(0.45, float(m.get("title_h_in", 0.62))) * s
                htb = slide.shapes.add_textbox(Inches(x), Inches(cur_y), Inches(w), Inches(th))
                htb.name = f"heading:{el.id}"
                htf = htb.text_frame
                htf.word_wrap = True
                htf.margin_left = Inches(0)
                htf.margin_top = Inches(0)
                hp = htf.paragraphs[0]
                hr = hp.add_run()
                hr.text = p["title"]
                hr.font.name = h_font
                hr.font.size = Pt(typo["section_heading_pt"] * s)
                hr.font.bold = True
                hr.font.color.rgb = _rgb(pal["dominant"])
                cur_y += th + 0.04 * s
                shape_count += 1

            cap_txt = p.get("caption", "")
            cap_h = (max(0.42, float(m.get("caption_h_in", 0.55))) * s) if cap_txt else 0.0
            img_avail_h = max(1.2 * s, (y + h) - cur_y - cap_h - (0.08 * s if cap_txt else 0.0))

            # Option A: Native editable PowerPoint chart if requested for simple bar/column data
            chart_spec = p.get("chart_spec")
            if p.get("native_pptx_chart") and chart_spec and chart_spec.get("chart_type") == "bar_chart":
                cdata = CategoryChartData()
                raw_d = chart_spec["data"]
                cdata.categories = [str(c) for c in raw_d["categories"]]
                s_list = raw_d.get("series") or [{"name": raw_d.get("series_name", "Outcome"), "values": raw_d["values"]}]
                for ser in s_list:
                    cdata.add_series(ser.get("name", "Series"), [float(v) for v in ser["values"]])
                c_type = XL_CHART_TYPE.BAR_CLUSTERED if chart_spec.get("horizontal") else XL_CHART_TYPE.COLUMN_CLUSTERED
                c_frame = slide.shapes.add_chart(c_type, Inches(x), Inches(cur_y), Inches(w), Inches(img_avail_h), cdata)
                c_frame.name = f"chart:{el.id}"
                chart = c_frame.chart
                chart.has_legend = len(s_list) > 1
                if chart.has_legend:
                    chart.legend.position = XL_LEGEND_POSITION.TOP
                    chart.legend.include_in_layout = False
                native_chart_count += 1
                shape_count += 1
            elif p.get("png_path") and pathlib.Path(p["png_path"]).exists():
                fx, fy, fw, fh = _fit_image_box(str(p["png_path"]), x + 0.04 * s, cur_y, w - 0.08 * s, img_avail_h)
                pic = slide.shapes.add_picture(str(p["png_path"]), Inches(fx), Inches(fy), Inches(fw), Inches(fh))
                pic.name = f"figure:{el.id}"
                shape_count += 1

            if cap_txt:
                ctb = slide.shapes.add_textbox(Inches(x), Inches(cur_y + img_avail_h + 0.06 * s), Inches(w), Inches(cap_h))
                ctb.name = f"caption:{el.id}"
                ctf = ctb.text_frame
                ctf.word_wrap = True
                ctf.margin_left = Inches(0.04 * s)
                ctf.margin_right = Inches(0.04 * s)
                ctf.margin_top = Inches(0)
                ctf.margin_bottom = Inches(0)
                cp = ctf.paragraphs[0]
                cp.line_spacing = 1.15
                # Bold 'Figure N.' prefix if present
                fm_cap = re.match(r"^((?:Figure|Fig\.|Table)\s*\d+[\.:])\s*(.*)$", cap_txt)
                if fm_cap:
                    r_pre = cp.add_run()
                    r_pre.text = fm_cap.group(1) + " "
                    r_pre.font.name = b_font
                    r_pre.font.size = Pt(typo["caption_pt"] * s)
                    r_pre.font.bold = True
                    r_pre.font.color.rgb = _rgb(pal["dominant"])
                    r_rest = cp.add_run()
                    r_rest.text = fm_cap.group(2)
                    r_rest.font.name = b_font
                    r_rest.font.size = Pt(typo["caption_pt"] * s)
                    r_rest.font.color.rgb = _rgb(pal["muted_ink"])
                else:
                    r_all = cp.add_run()
                    r_all.text = cap_txt
                    r_all.font.name = b_font
                    r_all.font.size = Pt(typo["caption_pt"] * s)
                    r_all.font.color.rgb = _rgb(pal["muted_ink"])
                shape_count += 1

        elif el.kind == "table":
            m = p.get("metrics", {})
            cur_y = y
            if p.get("title"):
                th = max(0.45, float(m.get("title_h_in", 0.62))) * s
                htb = slide.shapes.add_textbox(Inches(x), Inches(cur_y), Inches(w), Inches(th))
                htb.name = f"heading:{el.id}"
                htf = htb.text_frame
                htf.word_wrap = True
                htf.margin_left = Inches(0)
                htf.margin_top = Inches(0)
                hp = htf.paragraphs[0]
                hr = hp.add_run()
                hr.text = p["title"]
                hr.font.name = h_font
                hr.font.size = Pt(typo["section_heading_pt"] * s)
                hr.font.bold = True
                hr.font.color.rgb = _rgb(pal["dominant"])
                cur_y += th + 0.04 * s
                shape_count += 1

            tdata = p["table_data"]
            headers = [str(h_txt) for h_txt in tdata["headers"]]
            rows = [[str(c) for c in r] for r in tdata["rows"]]
            n_rows_total = 1 + len(rows)
            n_cols_total = len(headers)

            fn_txt = p.get("footnote", "")
            fn_h = (max(0.35, float(m.get("footnote_h_in", 0.42))) * s) if fn_txt else 0.0
            tbl_h = max(1.0 * s, (y + h) - cur_y - fn_h - (0.06 * s if fn_txt else 0.0))

            t_shape = slide.shapes.add_table(n_rows_total, n_cols_total, Inches(x), Inches(cur_y), Inches(w), Inches(tbl_h))
            t_shape.name = f"table:{el.id}"
            table = t_shape.table

            col_ws = m.get("col_widths_in") or ([el.w_in / n_cols_total] * n_cols_total)
            w_scale = w / max(0.1, sum(cw * s for cw in col_ws))
            for c_i, cw in enumerate(col_ws):
                table.columns[c_i].width = Inches(cw * s * w_scale)

            # Style header row (booktabs top heavy rule + mid rule)
            for c_i, h_txt in enumerate(headers):
                cell = table.cell(0, c_i)
                cell.fill.solid()
                cell.fill.fore_color.rgb = _rgb(pal["surface_tint"])
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                cell.margin_left = Inches(0.08 * s)
                cell.margin_right = Inches(0.08 * s)
                cell.margin_top = Inches(0.06 * s)
                cell.margin_bottom = Inches(0.06 * s)
                _set_cell_borders_booktabs(cell, top_hex=pal["dominant"], top_pt=2.0 * s, bottom_hex=pal["dominant"], bottom_pt=1.2 * s)
                cp = cell.text_frame.paragraphs[0]
                cp.alignment = PP_ALIGN.LEFT if c_i == 0 else PP_ALIGN.RIGHT
                cr = cp.add_run()
                cr.text = h_txt
                cr.font.name = b_font
                cr.font.size = Pt(typo["table_pt"] * s)
                cr.font.bold = True
                cr.font.color.rgb = _rgb(pal["dominant"])

            # Style data rows
            for r_i, row_vals in enumerate(rows):
                is_last = r_i == len(rows) - 1
                for c_i in range(n_cols_total):
                    val = row_vals[c_i] if c_i < len(row_vals) else ""
                    cell = table.cell(r_i + 1, c_i)
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = _rgb(pal["surface_tint"] if r_i % 2 == 1 else "#FFFFFF")
                    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                    cell.margin_left = Inches(0.08 * s)
                    cell.margin_right = Inches(0.08 * s)
                    cell.margin_top = Inches(0.05 * s)
                    cell.margin_bottom = Inches(0.05 * s)
                    _set_cell_borders_booktabs(
                        cell,
                        top_hex=None,
                        top_pt=0.0,
                        bottom_hex=pal["dominant"] if is_last else pal["rule_border"],
                        bottom_pt=(2.0 if is_last else 0.5) * s,
                    )
                    cp = cell.text_frame.paragraphs[0]
                    cp.alignment = PP_ALIGN.LEFT if c_i == 0 else PP_ALIGN.RIGHT
                    cr = cp.add_run()
                    cr.text = val
                    cr.font.name = b_font
                    cr.font.size = Pt(typo["table_pt"] * s)
                    cr.font.bold = (c_i == 0 and val.lower().startswith(("pooled", "overall", "primary")))
                    cr.font.color.rgb = _rgb(pal["body_ink"])
            shape_count += 1

            if fn_txt:
                ftb = slide.shapes.add_textbox(Inches(x), Inches(cur_y + tbl_h + 0.05 * s), Inches(w), Inches(fn_h))
                ftb.name = f"footnote:{el.id}"
                ftf = ftb.text_frame
                ftf.word_wrap = True
                ftf.margin_left = Inches(0.04 * s)
                ftf.margin_top = Inches(0)
                fp = ftf.paragraphs[0]
                fr = fp.add_run()
                fr.text = fn_txt
                fr.font.name = b_font
                fr.font.size = Pt(typo["caption_pt"] * s)
                fr.font.italic = True
                fr.font.color.rgb = _rgb(pal["muted_ink"])
                shape_count += 1

        elif el.kind == "colophon":
            rule_h = 0.022 * s
            rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(rule_h))
            rule.name = "rule:colophon_top"
            rule.fill.solid()
            rule.fill.fore_color.rgb = _rgb(p["rule_color"])
            rule.line.fill.background()

            ctb = slide.shapes.add_textbox(Inches(x), Inches(y + rule_h + 0.06 * s), Inches(w), Inches(max(0.25, h - rule_h - 0.06 * s)))
            ctb.name = "text:colophon"
            ctf = ctb.text_frame
            ctf.word_wrap = True
            ctf.margin_left = Inches(0)
            ctf.margin_right = Inches(0)
            ctf.margin_top = Inches(0)
            ctf.margin_bottom = Inches(0)
            for idx_p, part in enumerate(p.get("raw_parts", [])):
                cp = ctf.paragraphs[0] if idx_p == 0 else ctf.add_paragraph()
                cp.line_spacing = 1.14
                cp.space_after = Pt(3 * s)
                cr = cp.add_run()
                cr.text = part
                cr.font.name = b_font
                cr.font.size = Pt(typo["reference_pt"] * s)
                cr.font.color.rgb = _rgb(p["fg_color"])
            shape_count += 2

    out_pptx.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out_pptx))
    return {
        "pptx_path": str(out_pptx),
        "slide_width_in": dims["pptx_width_in"],
        "slide_height_in": dims["pptx_height_in"],
        "scale_factor": s,
        "editable_shape_count": shape_count,
        "native_chart_count": native_chart_count,
    }
