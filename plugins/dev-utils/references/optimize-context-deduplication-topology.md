# Discovery Topology & Skill Deduplication

## Discovery Hierarchy in Claude Code vs Multi-IDE

1. **Plugin Source (Canonical)**: Claude Code auto-scans the repository for any `SKILL.md` files, labeling matches found in `plugins/` as **"Plugin"** skills in `/context`.
2. **Project Source (Redundant)**: Claude Code also scans `.claude/skills/` and labels these as **"Project"** skills.
3. **Multi-IDE Fallback**: Antigravity, Gemini CLI, and Copilot require skills to be physically present in `.agents/skills/`.

## The Root Cause of Bloat
The legacy installer symlinked `.agents/skills/` → `.claude/skills/`. This caused Claude Code to load the same definition twice (once as "Plugin" and once as "Project").

## Remediation Commands
```bash
# Clear .claude/ duplicate symlinks
rm -rf .claude/skills/* .claude/agents/* .claude/commands/* .claude/hooks/*

# Verify with scanner
python3 plugins/dev-utils/scripts/optimize_context.py
```
> **Multi-IDE Guarantee:** `.agents/skills/` is never touched, ensuring Antigravity, Gemini CLI, and Copilot retain their working runtime.
