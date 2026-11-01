# Cross-Agent Compatibility

This suite targets four coding agents:

| Agent | Skill directory | Discovery |
|-------|-----------------|-----------|
| Claude Code | `.claude/skills/<skill-name>/` | Auto-discovers project or global |
| Cline | `.cline/skills/<skill-name>/` | Auto-discovers project or global |
| Codex | `.codex/skills/<skill-name>/` (or `AGENTS.md` references) | Project-scoped |
| OpenCode | `.opencode/skills/<skill-name>/` | Project-scoped |

## Installing

```bash
python install_skills.py --verify --install --agent both --scope project
```

The installer currently provisions Claude Code and Cline. Codex and OpenCode directories can be populated by copying the same skill folders (they follow the identical Agent Skills layout). A future revision will add `--agent codex|opencode|all`.

## AGENTS.md

For Codex/OpenCode, an `AGENTS.md` at the repository root summarizes available skills and how to invoke them. See repository root.
old_text">
null