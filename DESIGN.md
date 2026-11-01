# Design System & Architecture

## Overview

This suite follows a consistent visual design system across all 11 skills. Every generated artifact (posters, figures, infographics, covers) derives from shared JSON presets and a common typographic palette.

## Typography

- **Sans**: Source Sans 3 (SIL OFL)
- **Serif**: Source Serif 4 (SIL OFL)
- **Mono/Technical**: IBM Plex Sans (SIL OFL)

Fonts are bundled once in `research-poster-maker/assets/fonts/` and referenced by relative path from other skills.

## Color

- Colorblind-safe palettes defined per skill in `templates/*_presets.json`.
- Editorial palettes calibrated for print (CMYK-safe) and screen (sRGB).
- All charts use redundant encoding (color + pattern/shape) for accessibility.

## Architecture

Each skill is a self-contained package:

```
<skill-name>/
├── SKILL.md               # Progressive-disclosure entry point (< 120 lines)
├── README.md              # Skill-specific documentation
├── docs/                  # Detailed reference specifications
├── scripts/               # Executable Python generation & validation
├── templates/             # JSON design presets & palettes
└── examples/
    ├── synthetic_*.json   # Synthetic input data
    └── output/            # Generated artifacts + validation_report.json
```

## Cross-agent compatibility

See `docs/CROSS_AGENT.md`. Skills conform to the Agent Skills Open Standard and are installable into Claude Code, Cline, Codex, and OpenCode skill directories.

## Validation

Every skill's `examples/output/validation_report.json` records the result of its preflight QA pipeline. The suite-level audit is produced by `install_skills.py --verify`.
old_text">
null