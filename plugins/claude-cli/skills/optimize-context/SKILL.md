---
name: optimize-context
description: >-
  Reduces Claude Code context bloat by running two complementary passes: (1)
  duplicate skill deduplication — detects skills loaded from both .agents/skills/
  and .claude/skills/ and clears the .claude/ copies since Claude Code already
  reads from .agents/ directly; (2) CLAUDE.md optimization — audits the project
  CLAUDE.md for token bloat and rewrites it to under ~80 lines, keeping only rules
  that directly change Claude behaviour. Trigger with "optimize claude context",
  "reduce context bloat", "deduplicate skills", "trim CLAUDE.md", "fix my context
  usage", "why are my skills loading twice", or "clean up .claude directory".
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

**Root cause**: Claude Code loads skills from both `.agents/skills/` (Project)
and `.claude/skills/` (Plugin). These are the same content — `.claude/skills/`
is just symlinks created by the bridge installer. Claude Code already reads
`.agents/skills/` natively, so the `.claude/skills/` copies are redundant.

**Fix — clear `.claude/` skill copies** (Claude Code-specific, safe for all other IDEs):

```bash
# Report what's there
ls .claude/skills 2>/dev/null | wc -l
ls .claude/agents 2>/dev/null | wc -l
ls .claude/commands 2>/dev/null | wc -l
ls .claude/hooks 2>/dev/null | wc -l

# Remove the duplicates (Claude Code reads these from .agents/ directly)
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

> **Future installs**: `bridge_installer.py` has been updated to set
> `"skills": None` for `.claude` — new installations will not recreate the
> duplicate copies.

---

## Phase 3: CLAUDE.md Optimization

Read the project `CLAUDE.md` (check both `./CLAUDE.md` and `./.claude/CLAUDE.md`).

**Token target**: ≤ 80 lines / ≤ ~800 tokens.

**Keep** (changes Claude's behaviour on every request):
- Project purpose — 2-3 sentences max
- Key dev commands (build, test, install) — one-liners only
- Universal coding rules / ADRs — keep as bullet list
- Skill/agent standards — if they gate mistakes
- Scratch/temp directory rules

**Remove** (descriptive, aspirational, or reference-only):
- Stats that go stale (counts of skills/plugins)
- Duplicate install command variants — keep the canonical one only
- Architecture diagrams with more detail than needed
- Descriptions of how subsystems work internally
- Script tables — reference the directory instead
- Any content where "removing it would not cause a mistake"

**Rewrite approach**:
1. Summarize the current CLAUDE.md in one sentence per section
2. Present the proposed lean rewrite to the user before applying
3. Wait for explicit confirmation, then write

---

## Phase 4: Post-Fix Validation

```bash
wc -l CLAUDE.md   # confirm ≤ 80 lines
python3 plugins/claude-cli/scripts/optimize_context.py --dry-run  # confirm 0 skill duplicates
```

---

## Phase 5: Report

```
✅ optimize-context complete

Pass 1 — Skill deduplication:
  .claude/skills cleared : [N] entries removed
  .claude/agents cleared : [N] entries removed
  .claude/commands cleared: [N] entries removed
  Scanner result         : ✅ No filesystem duplicates

Pass 2 — CLAUDE.md:
  Before : [N] lines / ~[N]k tokens
  After  : [N] lines / ~[N]k tokens (-[N]%)

Next: reload Claude Code and run /context to measure token delta
```

---

## Fallback Rules

- **`.claude/` empty already**: Skip Pass 1, report clean.
- **`plugins/` not found**: Skip scanner, report warning.
- **CLAUDE.md already lean (≤ 80 lines)**: Report it as-is, suggest no changes.
- **User declines CLAUDE.md rewrite**: Skip Phase 3, complete Pass 1 only.

---

## References

- [`scripts/optimize_context.py`](../../scripts/optimize_context.py) — filesystem duplicate scanner
- [`references/acceptance-criteria.md`](references/acceptance-criteria.md) — structural pass/fail criteria
- **`claude-project-setup`** *(same plugin)*: full `.claude/` scaffold including CLAUDE.md
