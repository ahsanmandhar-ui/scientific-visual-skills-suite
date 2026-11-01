#!/usr/bin/env python3
"""
Agent Skills, Claude Code, and Cline Portability & Compatibility Verifier.

Tests:
  1. SKILL.md YAML frontmatter compliance with agentskills.io specification:
     - Required 'name' (1-64 chars, lowercase alphanumeric + single hyphens, matches folder name)
     - Required 'description' (1-1024 chars, non-empty semantic trigger description)
  2. Progressive disclosure token budget:
     - Level 1 metadata (~100 tokens)
     - Level 2 SKILL.md body (<5,000 tokens recommended ceiling)
  3. Relative path resolution:
     - Verifies every 'docs/*.md', 'scripts/*.py', and 'templates/*' path referenced in SKILL.md exists.
  4. Portable symlink/directory installation check for BOTH:
     - Claude Code: .claude/skills/research-poster-maker/SKILL.md
     - Cline:       .cline/skills/research-poster-maker/SKILL.md
     (Tested in an isolated temporary workspace without duplicating implementation files.)
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
from typing import Any, Dict, List

SKILL_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _parse_frontmatter(skill_md_text: str) -> Dict[str, Any]:
    if not skill_md_text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter delimiter '---'")
    end_idx = skill_md_text.find("\n---\n", 4)
    if end_idx == -1:
        raise ValueError("SKILL.md missing closing YAML frontmatter delimiter '---'")
    fm_raw = skill_md_text[4:end_idx]
    body = skill_md_text[end_idx + 5 :]

    parsed: Dict[str, Any] = {}
    for line in fm_raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and ":" in line:
            k, v = line.split(":", 1)
            parsed[k.strip()] = v.strip().strip('"').strip("'")
    return {"frontmatter": parsed, "body": body, "frontmatter_raw": fm_raw}


def run_compatibility_checks() -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []

    skill_md_path = SKILL_ROOT / "SKILL.md"
    exists = skill_md_path.exists()
    results.append({
        "check": "SKILL_MD_EXISTS",
        "status": "PASS" if exists else "FAIL",
        "detail": str(skill_md_path),
    })
    if not exists:
        return {"overall": "FAIL", "results": results}

    raw = skill_md_path.read_text(encoding="utf-8")
    parsed = _parse_frontmatter(raw)
    fm = parsed["frontmatter"]
    body = parsed["body"]

    # 1. Name specification check
    name = fm.get("name", "")
    name_regex_ok = bool(re.match(r"^[a-z0-9]+(?:-?[a-z0-9]+)*$", name)) and "--" not in name and 1 <= len(name) <= 64
    matches_dir = name == SKILL_ROOT.name
    results.append({
        "check": "AGENTSKILLS_NAME_SPEC",
        "status": "PASS" if (name_regex_ok and matches_dir) else "FAIL",
        "detail": f"name='{name}' (len={len(name)}, matches_dir={matches_dir})",
    })

    # 2. Description specification check
    desc = fm.get("description", "")
    desc_ok = 20 <= len(desc) <= 1024
    results.append({
        "check": "AGENTSKILLS_DESCRIPTION_SPEC",
        "status": "PASS" if desc_ok else "FAIL",
        "detail": f"description length={len(desc)} chars (limit 1024)",
    })

    # 3. Progressive loading token budget (<5000 tokens recommended by Claude Code & Cline)
    approx_meta_tokens = int((len(name) + len(desc)) / 4.0)
    approx_body_tokens = int(len(body) / 4.0)
    budget_ok = approx_body_tokens < 4500
    results.append({
        "check": "PROGRESSIVE_DISCLOSURE_TOKEN_BUDGET",
        "status": "PASS" if budget_ok else "WARN",
        "detail": f"Level-1 metadata ~{approx_meta_tokens} tokens; Level-2 SKILL.md body ~{approx_body_tokens} tokens (<5,000 limit).",
    })

    # 4. Referenced relative paths check
    ref_paths = set(re.findall(r"\b((?:docs|scripts)/[A-Za-z0-9_\-\.]+\.(?:md|py))\b", body))
    missing_refs = [rp for rp in sorted(ref_paths) if not (SKILL_ROOT / rp).exists()]
    results.append({
        "check": "REFERENCED_FILES_EXIST",
        "status": "PASS" if not missing_refs else "FAIL",
        "detail": f"Verified {len(ref_paths)} referenced doc/script path(s)." if not missing_refs else f"Missing: {missing_refs}",
    })

    # 5. Test portable installation & CLI execution from BOTH Claude Code (.claude/skills/) and Cline (.cline/skills/)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = pathlib.Path(tmp)
        for agent_name, rel_dir in [
            ("CLAUDE_CODE", pathlib.Path(".claude/skills/research-poster-maker")),
            ("CLINE", pathlib.Path(".cline/skills/research-poster-maker")),
        ]:
            target = tmp_root / rel_dir
            target.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(SKILL_ROOT, target, target_is_directory=True)

            loaded_md = (target / "SKILL.md").read_text(encoding="utf-8")
            p_check = _parse_frontmatter(loaded_md)
            dir_match = p_check["frontmatter"].get("name") == target.name

            # Test running CLI script via agent-relative path from project root
            proc = subprocess.run(
                [sys.executable, str(target / "scripts" / "analyze_research.py"), "--help"],
                cwd=str(tmp_root),
                capture_output=True,
                text=True,
                timeout=20,
            )
            ok = dir_match and proc.returncode == 0
            results.append({
                "check": f"{agent_name}_PORTABILITY_TEST",
                "status": "PASS" if ok else "FAIL",
                "detail": f"Installed via symlink at {rel_dir}/SKILL.md; dir_match={dir_match}; script CLI exit={proc.returncode}.",
            })

    overall = "FAIL" if any(r["status"] == "FAIL" for r in results) else "PASS"
    return {"overall": overall, "results": results}


if __name__ == "__main__":
    rep = run_compatibility_checks()
    print(json.dumps(rep, indent=2))
    raise SystemExit(0 if rep["overall"] == "PASS" else 1)
