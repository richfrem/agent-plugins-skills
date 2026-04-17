---
concept: optimize-context-claude-context-hygiene
source: plugin-code
source_file: claude-cli/skills/optimize-context/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.538395+00:00
cluster: plugin-code
content_hash: 5e94e7d62156780f
---

# optimize-context: Claude Context Hygiene

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: optimize-context
description: >-
  Reduces Claude Code context bloat across three dimensions: (1) duplicate skill
  deduplication — clears .claude/ copies since Claude Code already reads from
  plugins/ directly; (2) CLAUDE.md optimization — rewrites to under ~80 lines,
  keeping only rules that directly change Claude behaviour; (3) session token
  efficiency — guidance on cheap subagent delegation, context compounding across
  turns, and session hygiene. Trigger with "optimize claude context", "reduce
  context bloat", "deduplicate skills", "trim CLAUDE.md", "fix my context usage",
  "why are my skills loading twice", "how do I reduce token usage", or "clean up
  .claude directory".
argument-hint: "[--dry-run] [--verbose] [--project-root PATH]"
allowed-tools: Bash, Read, Write
---

<example>
<commentary>User sees skills duplicated in /context and high token usage.</commentary>
user: "optimize claude context"
assistant: [triggers optimize-context, runs duplicate scan then audits CLAUDE.md, reports all changes]
</example>

<example>
<commentary>User wants to preview changes only.</commentary>
user: "optimize claude context --dry-run"
assistant: [triggers optimize-context, runs both passes in dry-run mode, reports what would change without modifying anything]
</example>

<example>
<commentary>User specifically wants CLAUDE.md trimmed.</commentary>
user: "trim my CLAUDE.md, it's too big"
assistant: [triggers optimize-context, skips to Phase 3 CLAUDE.md audit]
</example>

<example>
<commentary>Negative — user wants to create a new skill from scratch, not optimize context.</commentary>
user: "Create a new skill called link-validator"
assistant: [triggers create-skill, not optimize-context]
</example>

# optimize-context: Claude Context Hygiene

Two-pass context optimization. Run both passes each time unless the user
specifies otherwise.

---

## Prerequisites

- `plugins/` directory present (plugin-canonical skills source)
- `scripts/optimize_context.py` available in this plugin
- `CLAUDE.md` or `.claude/CLAUDE.md` readable at project root

---

## Phase 1: Intent Capture

Parse `$ARGUMENTS`:
- `--dry-run` → report only, no writes
- `--verbose` → print every skill found
- `--project-root PATH` → override project root (default: CWD)
- `--skills-only` → skip CLAUDE.md audit
- `--claude-md-only` → skip skill deduplication

Confirm with the user before writing in live mode.

---

## Phase 2: Skill Deduplication

**Root cause**: Through experiment, we confirmed Claude Code auto-scans the entire 
repository for `SKILL.md` files (identifying them as **"Plugin"** skills). It 
**also** scans `.claude/skills/` (identifying them as **"Project"** skills). 
Because the installer used to symlink everything into `.claude/`, Claude Code 
was loading every skill twice.

**The Fix**: Clear the `.claude/` symlink folders. This forces Claude Code to 
rely on its auto-scan of the canonical source (`plugins/`), which fixes the 
double-loading without breaking Antigravity (which relies on `.agents/`).

**Fix — clear `.claude/` skill copies**:

```bash
# Report what's there
ls .claude/skills 2>/dev/null | wc -l
ls .claude/agents 2>/dev/null | wc -l
ls .claude/commands 2>/dev/null | wc -l
ls .claude/hooks 2>/dev/null | wc -l

# Remove the duplicates (Claude Code picks these up via repository scan)
rm -rf .claude/skills/* .claude/agents/* .claude/commands/* .claude/hooks/*
```

Run the scanner to confirm no remaining filesystem duplicates:

```bash
python3 plugins/claude-cli/scripts/optimize_context.py [--dry-run if requested]
```

**Exit 0**: Clean — report counts cleared and confirm scanner is satisfied.
**Exit 2**: Dry-run with remaining duplicates — show list and ask to apply.
**Non-zero/error**: Surface traceback verbatim.

> **Multi-IDE note**: Only `.claude/` copies are removed. `.agents/skills/` is
> the shared multi-IDE store and is **never touched**. Gemini CLI, Copilot, and
> Antigravity continue to work unchanged.

> **Future installs*

*(content truncated)*

## See Also

- [[acceptance-criteria-optimize-context]]
- [[context-folder-patterns]]
- [[memory-hygiene-when-to-write-promote-and-archive]]
- [[context-status-specification-contextstatusmd]]
- [[quick-start-zero-context-guide]]
- [[claude-md-hierarchy]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `claude-cli/skills/optimize-context/SKILL.md`
- **Indexed:** 2026-04-17T06:42:09.538395+00:00
