#!/usr/bin/env python3
"""
Scientific Presentation Deck Generator (.pptx with speaker notes + vector .pdf + overview .png + speaker_notes.md).
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import textwrap
from typing import Any, Dict, List

import fitz
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import font_manager
import numpy as np
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

SKILL_ROOT = pathlib.Path(__file__).resolve().parents[1]
SHARED_FONTS = SKILL_ROOT.parent / "research-poster-maker" / "assets" / "fonts"
if SHARED_FONTS.exists():
    for _ttf in SHARED_FONTS.glob("*.ttf"):
        try:
            font_manager.fontManager.addfont(str(_ttf))
        except Exception:
            pass


def _rgb(h: str) -> RGBColor:
    s = h.lstrip("#")
    return RGBColor(int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def _render_slide_chart(chart_spec: Dict[str, Any], pal: Dict[str, str], out_png: pathlib.Path) -> None:
    fig, ax = plt.subplots(figsize=(5.6, 3.8), dpi=260, facecolor="#FFFFFF")
    ctype = chart_spec.get("type", "bar_ci")
    cols = [pal["dominant"], pal["accent"], pal["secondary"], "#64748B"]
    if ctype == "line_series":
        for i, s in enumerate(chart_spec["series"]):
            ax.plot(s["x"], s["y"], marker="o", lw=2.0, color=cols[i % 4], label=s["name"])
        ax.set_xlabel(chart_spec.get("x_label", "Time"), fontweight="bold", fontsize=9.5)
        ax.set_ylabel(chart_spec.get("y_label", "Outcome"), fontweight="bold", fontsize=9.5)
        ax.legend(frameon=False, fontsize=8.5)
    else:
        labels = chart_spec["labels"]
        vals = [float(v) for v in chart_spec["values"]]
        idx = np.arange(len(labels))
        err = None
        if chart_spec.get("ci_low") and chart_spec.get("ci_high"):
            err = np.array([[v - float(lo) for v, lo in zip(vals, chart_spec["ci_low"])], [float(hi) - v for v, hi in zip(vals, chart_spec["ci_high"])]])
        bars = ax.bar(idx, vals, width=0.52, color=[cols[i % 4] for i in range(len(labels))], yerr=err, capsize=4)
        ax.set_ylim(0, max(chart_spec.get("ci_high", vals)) * 1.22)
        ax.set_xticks(idx)
        ax.set_xticklabels(labels, fontweight="bold", fontsize=8.8)
        ax.set_ylabel(chart_spec.get("y_label", "Value"), fontweight="bold", fontsize=9.5)
        unit = chart_spec.get("unit", "")
        tops = [float(h) for h in chart_spec["ci_high"]] if chart_spec.get("ci_high") else vals
        for b, v, top_v in zip(bars, vals, tops):
            ax.text(b.get_x() + b.get_width() / 2, top_v + max(tops) * 0.03, f"{v:g}{unit}", ha="center", fontsize=8.6, fontweight="bold")
    if chart_spec.get("title"):
        ax.set_title(chart_spec["title"], loc="left", fontweight="bold", fontsize=10.2, pad=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_png, dpi=260, facecolor="#FFFFFF")
    plt.close(fig)


def generate_deck(spec: Dict[str, Any], out_dir: pathlib.Path) -> Dict[str, Any]:
    db = json.loads((SKILL_ROOT / "templates" / "deck_archetypes.json").read_text(encoding="utf-8"))
    pal = db["palettes"].get(spec.get("palette", "oxford_academic"), db["palettes"]["oxford_academic"])
    aspect = spec.get("aspect", "16:9")
    W, H = (13.333, 7.5) if aspect == "16:9" else (10.0, 7.5)

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["IBM Plex Sans", "Source Sans 3", "DejaVu Sans"],
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    out_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = out_dir / "_slide_assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    pdf_path = out_dir / "deck_handout.pdf"
    notes_lines = [f"# Speaker Notes & Timing Script — {spec['deck_title']}", ""]
    elapsed_sec = 0

    slides: List[Dict[str, Any]] = spec["slides"]
    with PdfPages(pdf_path) as pdf:
        for idx, s in enumerate(slides, start=1):
            sl = prs.slides.add_slide(prs.slide_layouts[6])
            sl.background.fill.solid()
            sl.background.fill.fore_color.rgb = _rgb(pal["canvas"])
            stype = s.get("layout", "split_evidence")

            fig = plt.figure(figsize=(W, H), facecolor=pal["canvas"])
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)
            ax.axis("off")

            if stype == "title":
                # PPTX Title Slide
                bg = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(W), Inches(H))
                bg.fill.solid()
                bg.fill.fore_color.rgb = _rgb(pal["dominant"])
                bg.line.fill.background()
                bar = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(H * 0.62), Inches(2.6), Inches(0.08))
                bar.fill.solid()
                bar.fill.fore_color.rgb = _rgb(pal["accent"])
                bar.line.fill.background()

                tb = sl.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(W - 1.6), Inches(3.2))
                tf = tb.text_frame
                tf.word_wrap = True
                r0 = tf.paragraphs[0].add_run()
                r0.text = s["headline"]
                r0.font.size = Pt(32)
                r0.font.bold = True
                r0.font.color.rgb = _rgb("#FFFFFF")
                if s.get("subtitle"):
                    p1 = tf.add_paragraph()
                    r1 = p1.add_run()
                    r1.text = s["subtitle"]
                    r1.font.size = Pt(18)
                    r1.font.color.rgb = _rgb("#DCE6F2")

                # PDF Title Page
                ax.add_patch(mpatches.Rectangle((0, 0), 100, 100, facecolor=pal["dominant"], edgecolor="none"))
                ax.add_patch(mpatches.Rectangle((6.5, 38.0), 22.0, 1.1, facecolor=pal["accent"], edgecolor="none"))
                ax.text(6.5, 84.0, spec.get("venue_tag", "SCIENTIFIC RESEARCH PRESENTATION").upper(), color="#CBD5E1", fontsize=11, fontweight="bold")
                ax.text(6.5, 62.0, "\n".join(textwrap.wrap(s["headline"], width=46)), color="#FFFFFF", fontsize=24, fontweight="bold", va="center", linespacing=1.2)
                if s.get("subtitle"):
                    ax.text(6.5, 29.0, s["subtitle"], color="#E2E8F0", fontsize=13.5, va="top")
                if spec.get("authors"):
                    ax.text(6.5, 17.0, spec["authors"], color="#FFFFFF", fontsize=12.5, fontweight="bold")
            else:
                # Header Assertion Banner (PPTX + PDF)
                hb = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(W), Inches(1.15))
                hb.fill.solid()
                hb.fill.fore_color.rgb = _rgb(pal["dominant"])
                hb.line.fill.background()
                htf = hb.text_frame
                htf.word_wrap = True
                hr = htf.paragraphs[0].add_run()
                hr.text = s["headline"]
                hr.font.size = Pt(21)
                hr.font.bold = True
                hr.font.color.rgb = _rgb("#FFFFFF")

                ax.add_patch(mpatches.Rectangle((0, 84.5), 100, 15.5, facecolor=pal["dominant"], edgecolor="none"))
                ax.add_patch(mpatches.Rectangle((0, 83.7), 100, 0.8, facecolor=pal["accent"], edgecolor="none"))
                ax.text(4.2, 92.2, "\n".join(textwrap.wrap(s["headline"], width=68)), color="#FFFFFF", fontsize=16.5, fontweight="bold", va="center", linespacing=1.16)
                ax.text(96.0, 4.0, f"{idx} / {len(slides)}", color=pal["muted"], fontsize=9.5, ha="right")
                if s.get("footnote"):
                    ax.text(4.2, 4.0, s["footnote"], color=pal["muted"], fontsize=8.8)

                if stype == "methodology_flow":
                    stages = s.get("stages", [])[:4]
                    sw = (91.0 - 2.6 * (len(stages) - 1)) / max(1, len(stages))
                    for si, stg in enumerate(stages):
                        sx = 4.5 + si * (sw + 2.6)
                        ax.add_patch(mpatches.FancyBboxPatch((sx, 22.0), sw, 52.0, boxstyle="round,pad=0.2,rounding_size=1.2", facecolor=pal["tint"], edgecolor=pal["secondary"], lw=1.3))
                        ax.add_patch(mpatches.Rectangle((sx, 66.0), sw, 8.0, facecolor=pal["secondary"] if si < len(stages) - 1 else pal["accent"], edgecolor="none"))
                        ax.text(sx + sw / 2, 70.0, stg["step"], color="#FFFFFF", fontsize=11.0, fontweight="bold", ha="center", va="center")
                        ax.text(sx + 1.8, 60.5, "\n".join(textwrap.wrap(stg["detail"], width=23)), color=pal["ink"], fontsize=10.5, va="top", linespacing=1.28)
                        if si < len(stages) - 1:
                            ax.annotate("", xy=(sx + sw + 2.2, 48.0), xytext=(sx + sw + 0.4, 48.0), arrowprops={"arrowstyle": "-|>", "color": pal["dominant"], "lw": 2.0, "mutation_scale": 14})
                        # PPTX card
                        bx = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(W * sx / 100.0), Inches(1.8), Inches(W * sw / 100.0), Inches(4.6))
                        bx.fill.solid()
                        bx.fill.fore_color.rgb = _rgb(pal["tint"])
                        bx.line.color.rgb = _rgb(pal["secondary"])
                        btf = bx.text_frame
                        btf.word_wrap = True
                        r_s = btf.paragraphs[0].add_run()
                        r_s.text = f"{stg['step']}\n{stg['detail']}"
                        r_s.font.size = Pt(14)

                elif stype == "table_summary":
                    headers = s["table"]["headers"]
                    rows = s["table"]["rows"]
                    # PPTX native table
                    t_shape = sl.shapes.add_table(len(rows) + 1, len(headers), Inches(0.6), Inches(1.55), Inches(W - 1.2), Inches(4.5))
                    tbl = t_shape.table
                    for ci, h_txt in enumerate(headers):
                        cell = tbl.cell(0, ci)
                        cell.text = h_txt
                    for ri, row in enumerate(rows, start=1):
                        for ci, val in enumerate(row):
                            tbl.cell(ri, ci).text = str(val)

                    # PDF clean booktabs table
                    ty_top = 74.0
                    rh = min(9.5, 52.0 / (len(rows) + 1))
                    cw = 91.0 / len(headers)
                    ax.add_patch(mpatches.Rectangle((4.5, ty_top - rh), 91.0, rh, facecolor=pal["dominant"], edgecolor="none"))
                    for ci, h_txt in enumerate(headers):
                        ax.text(4.5 + ci * cw + 1.5, ty_top - rh / 2, h_txt, color="#FFFFFF", fontsize=10.5, fontweight="bold", va="center")
                    for ri, row in enumerate(rows):
                        ry = ty_top - (ri + 2) * rh
                        ax.add_patch(mpatches.Rectangle((4.5, ry), 91.0, rh, facecolor=pal["tint"] if ri % 2 == 1 else "#FFFFFF", edgecolor="none"))
                        ax.plot([4.5, 95.5], [ry, ry], color=pal["border"], lw=0.7)
                        for ci, val in enumerate(row):
                            ax.text(4.5 + ci * cw + 1.5, ry + rh / 2, str(val), color=pal["ink"], fontsize=10.2, fontweight="bold" if ci == 0 else "normal", va="center")

                else:  # split_evidence or conclusion_takeaways
                    bullets = s.get("bullets", [])
                    has_chart = bool(s.get("chart"))
                    left_w = 44.0 if has_chart else 88.0
                    tb = sl.shapes.add_textbox(Inches(0.6), Inches(1.55), Inches(W * (0.44 if has_chart else 0.88)), Inches(5.1))
                    tf = tb.text_frame
                    tf.word_wrap = True
                    cy = 74.0
                    for bi, btxt in enumerate(bullets):
                        p = tf.paragraphs[0] if bi == 0 else tf.add_paragraph()
                        run = p.add_run()
                        run.text = f"• {btxt}"
                        run.font.size = Pt(17)
                        run.font.color.rgb = _rgb(pal["ink"])
                        wrapped = "\n".join(textwrap.wrap(f"• {btxt}", width=44 if has_chart else 86))
                        ax.text(4.5, cy, wrapped, color=pal["ink"], fontsize=12.2, va="top", linespacing=1.28)
                        cy -= (wrapped.count("\n") + 1) * 5.6 + 4.2

                    if has_chart:
                        c_png = assets_dir / f"slide_{idx:02d}_chart.png"
                        _render_slide_chart(s["chart"], pal, c_png)
                        sl.shapes.add_picture(str(c_png), Inches(W * 0.50), Inches(1.50), width=Inches(W * 0.45))
                        with Image.open(c_png) as cim:
                            cax = fig.add_axes([0.50, 0.14, 0.46, 0.64])
                            cax.imshow(cim)
                            cax.axis("off")

            # Native PPTX Speaker Notes
            sec_dur = int(s.get("seconds_budget", 60))
            note_body = s.get("speaker_notes", "Present assertion headline, walk through visual evidence, and transition to next slide.")
            notes_tf = sl.notes_slide.notes_text_frame
            notes_tf.text = f"[Target: {sec_dur}s] {note_body}"

            mm_s, ss_s = divmod(elapsed_sec, 60)
            elapsed_sec += sec_dur
            mm_e, ss_e = divmod(elapsed_sec, 60)
            notes_lines.extend([
                f"## Slide {idx}: {s['headline']} (`{mm_s:02d}:{ss_s:02d} – {mm_e:02d}:{ss_e:02d}`)",
                "",
                note_body,
                "",
            ])

            pdf.savefig(fig, facecolor=fig.get_facecolor())
            plt.close(fig)

    pptx_path = out_dir / "deck.pptx"
    prs.save(str(pptx_path))
    notes_md_path = out_dir / "speaker_notes.md"
    notes_md_path.write_text("\n".join(notes_lines), encoding="utf-8")

    # Render contact-sheet overview PNG of all slides via PyMuPDF for instant visual QA
    doc = fitz.open(str(pdf_path))
    n_p = len(doc)
    cols_g = min(3, n_p)
    rows_g = math.ceil(n_p / cols_g)
    thumbs = []
    for p in doc:
        pix = p.get_pixmap(dpi=110)
        thumbs.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
    tw, th = thumbs[0].size
    pad = 24
    sheet = Image.new("RGB", (cols_g * tw + (cols_g + 1) * pad, rows_g * th + (rows_g + 1) * pad), (236, 240, 245))
    for i, im in enumerate(thumbs):
        r, c = divmod(i, cols_g)
        sheet.paste(im, (pad + c * (tw + pad), pad + r * (th + pad)))
    overview_png = out_dir / "deck_overview.png"
    sheet.save(overview_png)
    doc.close()

    return {
        "slide_count": len(slides),
        "total_duration_sec": elapsed_sec,
        "files": {"pptx": str(pptx_path), "pdf": str(pdf_path), "overview_png": str(overview_png), "speaker_notes_md": str(notes_md_path)},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    spec = json.loads(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    print(json.dumps(generate_deck(spec, pathlib.Path(args.output_dir)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
