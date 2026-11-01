#!/usr/bin/env python3
"""
Academic Conference Visual Identity Kit Generator.
Generates all 6 coordinated assets + kit_overview.png contact sheet.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import textwrap
from typing import Any, Dict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
import numpy as np
from PIL import Image
import qrcode
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


def _draw_geometric_motif(ax: plt.Axes, x0: float, y0: float, w: float, h: float, col1: str, col2: str) -> None:
    """Subtle parametric wave/lattice academic identity motif."""
    t = np.linspace(0, 1, 90)
    for k in range(6):
        ph = k * 0.42
        xs = x0 + t * w
        ys = y0 + h * (0.25 + 0.50 * (k / 5.0) + 0.14 * np.sin(2 * np.pi * t + ph))
        ax.plot(xs, ys, color=col1 if k % 2 == 0 else col2, alpha=0.26, lw=1.3)


def generate_kit(spec: Dict[str, Any], out_dir: pathlib.Path) -> Dict[str, Any]:
    pal = json.loads((SKILL_ROOT / "templates" / "conference_themes.json").read_text(encoding="utf-8"))["palettes"].get(spec.get("theme", "geneva_symposium"))
    out_dir.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["IBM Plex Sans", "Source Sans 3", "DejaVu Sans"],
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "path",
    })

    # QR code for registration URL
    qr_img = qrcode.make(spec.get("registration_url", "https://example.org/conference")).convert("RGB")
    qr_path = out_dir / "_reg_qr.png"
    qr_img.save(qr_path)

    # 1. Stage / Web Banner (24 x 8 in @ 150 DPI -> 3600 x 1200 px)
    fig = plt.figure(figsize=(12.0, 4.0), facecolor=pal["primary"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    ax.add_patch(mpatches.Rectangle((0, 0), 100, 100, facecolor=pal["primary"]))
    _draw_geometric_motif(ax, 58, 8, 40, 84, pal["secondary"], pal["accent"])
    ax.add_patch(mpatches.Rectangle((4.0, 78.0), 16.0, 1.8, facecolor=pal["accent"]))
    ax.text(4.0, 84.0, spec["acronym"].upper() + " · " + spec["host_society"].upper(), color="#CBD5E1", fontsize=10.5, fontweight="bold")
    ax.text(4.0, 56.0, "\n".join(textwrap.wrap(spec["conference_title"], width=44)), color="#FFFFFF", fontsize=20.0, fontweight="bold", va="center", linespacing=1.16)
    ax.text(4.0, 20.0, f"{spec['dates']}   |   {spec['location']}", color="#F8FAFC", fontsize=12.5, fontweight="bold")
    fig.savefig(out_dir / "banner.pdf", format="pdf", facecolor=pal["primary"])
    fig.savefig(out_dir / "banner.png", format="png", dpi=300, facecolor=pal["primary"])
    plt.close(fig)

    # 2. Abstract-Book Cover (A4: 8.27 x 11.69 in @ 300 DPI)
    fig = plt.figure(figsize=(8.27, 11.69), facecolor=pal["canvas"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    ax.add_patch(mpatches.Rectangle((0, 42), 100, 58, facecolor=pal["primary"]))
    ax.add_patch(mpatches.Rectangle((0, 40.8), 100, 1.2, facecolor=pal["accent"]))
    _draw_geometric_motif(ax, 8, 44, 84, 22, "#56B4E9", pal["accent"])
    ax.text(8.0, 92.0, spec["host_society"].upper(), color="#CBD5E1", fontsize=10.0, fontweight="bold")
    ax.text(8.0, 77.0, "\n".join(textwrap.wrap(spec["conference_title"], width=28)), color="#FFFFFF", fontsize=21.5, fontweight="bold", va="center", linespacing=1.18)
    ax.add_patch(mpatches.FancyBboxPatch((8.0, 26.0), 84.0, 10.0, boxstyle="round,pad=0.2,rounding_size=0.8", facecolor="#FFFFFF", edgecolor=pal["secondary"], lw=1.4))
    ax.text(50.0, 31.0, "BOOK OF ABSTRACTS & SCIENTIFIC PROCEEDINGS", color=pal["primary"], fontsize=12.5, fontweight="bold", ha="center", va="center")
    ax.text(8.0, 18.0, f"Dates: {spec['dates']}\nVenue: {spec['location']}\nProceedings ID: {spec.get('proceedings_id', 'ISSN 0000-000X (Synthetic)')}", color=pal["ink"], fontsize=10.5, linespacing=1.45, va="top")
    ax.text(8.0, 4.5, spec.get("disclaimer", "SYNTHETIC CONFERENCE KIT FOR SKILL VALIDATION"), color=pal["muted"], fontsize=8.0)
    fig.savefig(out_dir / "abstract_book_cover.pdf", format="pdf", facecolor=pal["canvas"])
    fig.savefig(out_dir / "abstract_book_cover.png", format="png", dpi=300, facecolor=pal["canvas"])
    plt.close(fig)

    # 3. Event / Call-for-Abstracts Poster (18 x 24 in @ 180 DPI)
    fig = plt.figure(figsize=(9.0, 12.0), facecolor=pal["canvas"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    ax.add_patch(mpatches.Rectangle((0, 72), 100, 28, facecolor=pal["primary"]))
    ax.add_patch(mpatches.Rectangle((0, 71), 100, 1.0, facecolor=pal["accent"]))
    ax.text(6.0, 94.0, f"CALL FOR ABSTRACTS & REGISTRATION · {spec['acronym']}", color="#FCD34D", fontsize=10.0, fontweight="bold")
    ax.text(6.0, 84.0, "\n".join(textwrap.wrap(spec["conference_title"], width=32)), color="#FFFFFF", fontsize=19.5, fontweight="bold", va="center")
    ax.text(6.0, 74.5, f"{spec['dates']}  ·  {spec['location']}", color="#E2E8F0", fontsize=11.0, fontweight="bold")

    ax.text(6.0, 66.5, "SCIENTIFIC TRACKS", color=pal["primary"], fontsize=11.5, fontweight="bold")
    for ti, trk in enumerate(spec.get("tracks", [])[:4]):
        ty = 61.5 - ti * 6.2
        ax.add_patch(mpatches.FancyBboxPatch((6.0, ty - 2.2), 42.0, 4.8, boxstyle="round,pad=0.1,rounding_size=0.6", facecolor="#FFFFFF", edgecolor="#CBD5E1", lw=1.0))
        ax.text(8.0, ty + 0.2, f"• {trk}", color=pal["ink"], fontsize=9.2, fontweight="bold", va="center")

    ax.text(54.0, 66.5, "KEY DEADLINES", color=pal["primary"], fontsize=11.5, fontweight="bold")
    for di, dl in enumerate(spec.get("deadlines", [])[:3]):
        dy = 61.0 - di * 8.0
        ax.add_patch(mpatches.FancyBboxPatch((54.0, dy - 3.2), 40.0, 6.4, boxstyle="round,pad=0.1,rounding_size=0.6", facecolor="#FFFBEB" if di == 0 else "#FFFFFF", edgecolor=pal["accent"] if di == 0 else "#CBD5E1", lw=1.1))
        ax.text(56.0, dy + 1.2, dl["milestone"], color=pal["primary"], fontsize=9.0, fontweight="bold", va="center")
        ax.text(56.0, dy - 1.4, dl["date"], color=pal["accent"], fontsize=9.2, fontweight="bold", va="center")

    ax.text(6.0, 34.0, "PLENARY KEYNOTE SPEAKERS", color=pal["primary"], fontsize=11.5, fontweight="bold")
    for ki, spk in enumerate(spec.get("keynotes", [])[:2]):
        ky = 25.0 - ki * 9.5
        ax.add_patch(mpatches.FancyBboxPatch((6.0, ky - 3.5), 62.0, 7.6, boxstyle="round,pad=0.1,rounding_size=0.6", facecolor="#FFFFFF", edgecolor=pal["secondary"], lw=1.1))
        ax.text(8.0, ky + 1.6, f"{spk['name']} ({spk['affiliation']})", color=pal["primary"], fontsize=9.5, fontweight="bold", va="center")
        ax.text(8.0, ky - 1.4, f"Keynote: {spk['talk']}", color=pal["muted"], fontsize=8.4, va="center")

    q_ax = fig.add_axes([0.73, 0.11, 0.20, 0.16])
    q_ax.imshow(qr_img); q_ax.axis("off")
    ax.text(83.0, 9.5, "Scan to Submit", color=pal["primary"], fontsize=8.8, fontweight="bold", ha="center")
    ax.text(6.0, 3.5, spec.get("disclaimer", "SYNTHETIC CONFERENCE POSTER"), color=pal["muted"], fontsize=7.6)
    fig.savefig(out_dir / "event_poster.pdf", format="pdf", facecolor=pal["canvas"])
    fig.savefig(out_dir / "event_poster.png", format="png", dpi=260, facecolor=pal["canvas"])
    plt.close(fig)

    # 4. Certificate of Presentation (11 x 8.5 in Landscape + Editable PPTX)
    cert = spec["certificate"]
    fig = plt.figure(figsize=(11.0, 8.5), facecolor="#FFFEFA")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    ax.add_patch(mpatches.Rectangle((3.0, 3.5), 94.0, 93.0, facecolor="none", edgecolor=pal["primary"], lw=2.6))
    ax.add_patch(mpatches.Rectangle((4.4, 5.0), 91.2, 90.0, facecolor="none", edgecolor=pal["gold"], lw=1.1))
    ax.text(50.0, 86.5, spec["host_society"].upper(), color=pal["secondary"], fontsize=10.5, fontweight="bold", ha="center")
    ax.text(50.0, 78.0, "CERTIFICATE OF SCIENTIFIC PRESENTATION", color=pal["primary"], fontsize=21.0, fontweight="bold", ha="center")
    ax.text(50.0, 68.5, "This certifies that", color=pal["muted"], fontsize=11.5, ha="center")
    ax.text(50.0, 60.5, cert["recipient"], color=pal["primary"], fontsize=23.0, fontweight="bold", ha="center")
    ax.plot([26.0, 74.0], [56.8, 56.8], color=pal["gold"], lw=1.2)
    ax.text(50.0, 48.0, "\n".join(textwrap.wrap(f"delivered the {cert['role']} entitled \"{cert['presentation_title']}\" at {spec['conference_title']} ({spec['dates']}, {spec['location']}).", width=68)), color=pal["ink"], fontsize=11.5, ha="center", va="center", linespacing=1.35)
    for sx, sig in [(26.0, cert["signatory_1"]), (74.0, cert["signatory_2"])]:
        ax.plot([sx - 14.0, sx + 14.0], [22.0, 22.0], color=pal["ink"], lw=1.0)
        ax.text(sx, 18.2, sig["name"], color=pal["primary"], fontsize=10.2, fontweight="bold", ha="center")
        ax.text(sx, 14.8, sig["title"], color=pal["muted"], fontsize=8.8, ha="center")
    ax.text(50.0, 8.2, f"Verification ID: {cert['serial_id']}", color=pal["muted"], fontsize=8.2, ha="center")
    fig.savefig(out_dir / "certificate.pdf", format="pdf", facecolor="#FFFEFA")
    fig.savefig(out_dir / "certificate.png", format="png", dpi=260, facecolor="#FFFEFA")
    plt.close(fig)

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(11.0), Inches(8.5)
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    sl.shapes.add_picture(str(out_dir / "certificate.png"), Inches(0), Inches(0), width=Inches(11.0))
    prs.save(str(out_dir / "certificate.pptx"))

    # 5. Speaker Spotlight Graphic (1:1, 1200 x 1200 px)
    spk0 = spec["keynotes"][0]
    fig = plt.figure(figsize=(4.0, 4.0), facecolor=pal["primary"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    ax.add_patch(mpatches.Rectangle((0, 0), 100, 100, facecolor=pal["primary"]))
    ax.add_patch(mpatches.Rectangle((0, 0), 100, 3.0, facecolor=pal["accent"]))
    ax.text(7.0, 90.0, f"KEYNOTE SPEAKER · {spec['acronym']}", color="#FCD34D", fontsize=8.8, fontweight="bold")
    # Monogram avatar emblem
    initials = "".join(w[0] for w in spk0["name"].replace("Prof.", "").replace("Dr.", "").split()[:2]).upper()
    ax.add_patch(mpatches.Circle((20.0, 68.0), 11.5, facecolor=pal["secondary"], edgecolor=pal["gold"], lw=2.0))
    ax.text(20.0, 68.0, initials, color="#FFFFFF", fontsize=16.0, fontweight="bold", ha="center", va="center")
    ax.text(36.0, 71.5, spk0["name"], color="#FFFFFF", fontsize=12.5, fontweight="bold", va="center")
    ax.text(36.0, 63.5, spk0["affiliation"], color="#CBD5E1", fontsize=8.8, va="center")
    ax.text(7.0, 40.0, "\n".join(textwrap.wrap(f"\"{spk0['talk']}\"", width=34)), color="#F8FAFC", fontsize=10.8, fontweight="bold", va="center", linespacing=1.25)
    ax.text(7.0, 14.5, "\n".join(textwrap.wrap(f"{spec['dates']} · {spec['location']}", width=42)), color="#CBD5E1", fontsize=8.0, va="top", linespacing=1.2)
    fig.savefig(out_dir / "speaker_card.svg", format="svg", facecolor=pal["primary"])
    fig.savefig(out_dir / "speaker_card.png", format="png", dpi=300, facecolor=pal["primary"])
    plt.close(fig)

    # 6. Social Announcement Graphic (16:9, exact 1600 x 900 px)
    fig = plt.figure(figsize=(8.0, 4.5), facecolor=pal["primary"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    ax.add_patch(mpatches.Rectangle((0, 0), 100, 100, facecolor=pal["primary"]))
    _draw_geometric_motif(ax, 62, 10, 35, 80, pal["secondary"], pal["accent"])
    ax.text(6.0, 86.0, f"ABSTRACT SUBMISSION OPEN · {spec['acronym']}", color="#FCD34D", fontsize=12.0, fontweight="bold")
    ax.text(6.0, 58.0, "\n".join(textwrap.wrap(spec["conference_title"], width=36)), color="#FFFFFF", fontsize=19.5, fontweight="bold", va="center", linespacing=1.18)
    ax.add_patch(mpatches.FancyBboxPatch((6.0, 14.0), 48.0, 16.0, boxstyle="round,pad=0.2,rounding_size=1.2", facecolor=pal["accent"], edgecolor="none"))
    ax.text(30.0, 22.0, f"Deadline: {spec['deadlines'][0]['date']}", color="#FFFFFF", fontsize=13.5, fontweight="bold", ha="center", va="center")
    fig.savefig(out_dir / "social_card.svg", format="svg", facecolor=pal["primary"])
    fig.savefig(out_dir / "social_card.png", format="png", dpi=200, facecolor=pal["primary"])
    plt.close(fig)

    # Composite kit_overview.png contact sheet
    asset_pngs = ["banner.png", "abstract_book_cover.png", "event_poster.png", "certificate.png", "speaker_card.png", "social_card.png"]
    fig, axes = plt.subplots(2, 3, figsize=(14.0, 9.0), dpi=180, facecolor="#EEF2F6")
    fig.suptitle(f"Conference Visual Identity System — {spec['acronym']} (6 Coordinated Deliverables)", fontsize=14, fontweight="bold", color="#0F172A", y=0.97)
    for ax_i, fname in zip(axes.flat, asset_pngs):
        with Image.open(out_dir / fname) as im:
            ax_i.imshow(im)
        ax_i.set_title(fname, fontsize=9.5, fontweight="bold", color="#1E293B")
        ax_i.axis("off")
    fig.tight_layout(rect=[0.01, 0.01, 0.99, 0.94])
    fig.savefig(out_dir / "kit_overview.png", dpi=180, facecolor="#EEF2F6")
    plt.close(fig)

    return {"deliverables": asset_pngs, "overview": str(out_dir / "kit_overview.png")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    spec = json.loads(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    print(json.dumps(generate_kit(spec, pathlib.Path(args.output_dir)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
