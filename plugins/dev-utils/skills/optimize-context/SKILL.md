---
name: optimize-context
plugin: dev-utils
description: >-
  Reduces AI agent context bloat across three dimensions: (1) duplicate skill
  deduplication — clears stale agent directory copies since the IDE already reads
  from plugins/ directly; (2) instruction file optimization — rewrites CLAUDE.md,
  GEMINI.md, or .github/copilot-instructions.md to under ~80 lines, keeping only
  rules that directly change agent behaviour; (3) session token efficiency —
  guidance on cheap subagent delegation, context compounding across turns, and
  session hygiene. Trigger with "optimize context", "reduce context bloat",
  "deduplicate skills", "trim CLAUDE.md", "trim GEMINI.md", "fix my context usage",
  "why are my skills loading twice", "how do I reduce token usage", or "clean up
  agent directories".
argument-hint: "[--dry-run] [--verbose] [--project-root PATH]"
allowed-tools: Bash, Read, Write
---

<example>
<commentary>User sees skills duplicated in /context and high token usage.</commentary>
user: "optimize context"
assistant: [triggers optimize-context, runs duplicate scan then audits instruction files, reports all changes]
</example>

<example>
<commentary>User wants to preview changes only.</commentary>
user: "optimize context --dry-run"
assistant: [triggers optimize-context, runs both passes in dry-run mode, reports what would change without modifying anything]
</example>

<example>
<commentary>User specifically wants their instruction file trimmed.</commentary>
user: "trim my GEMINI.md, it's too big"
assistant: [triggers optimize-context, skips to Phase 3 instruction file audit]
</example>

<example>
<commentary>Negative — user wants to create a new skill from scratch, not optimize context.</commentary>
user: "Create a new skill called link-validator"
assistant: [triggers create-skill, not optimize-context]
</example>

# optimize-context: Agent Context Hygiene

Two-pass context optimization. Run both passes each time unless the user
specifies otherwise.

---

## Prerequisites

- `plugins/` directory present (plugin-canonical skills source)
- `scripts/optimize_context.py` available in this plugin
- At least one instruction file readable at project root: `CLAUDE.md`, `GEMINI.md`, or `.github/copilot-instructions.md`

---

## Phase 1: Intent Capture

Parse `$ARGUMENTS`:
- `--dry-run` → report only, no writes
- `--verbose` → print every skill found
- `--project-root PATH` → override project root (default: CWD)
- `--skills-only` → skip instruction file audit
- `--instructions-only` → skip skill deduplication

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
python plugins/dev-utils/scripts/optimize_context.py [--dry-run if requested]
```

**Exit 0**: Clean — report counts cleared and confirm scanner is satisfied.
**Exit 2**: Dry-run with remaining duplicates — show list and ask to apply.
**Non-zero/error**: Surface traceback verbatim.

> **Multi-IDE note**: Only `.claude/` copies are removed. `.agents/skills/` is
> the shared multi-IDE store and is **never touched**. Gemini CLI, Copilot, and
> Antigravity continue to work unchanged.

> **Future installs**: `plugin_installer.py` has been updated to set
> `"skills": None` for `.claude` — new installations will not recreate the
> duplicate copies.

---

## Phase 3: Instruction File Optimization

Detect which instruction files are present and apply to each:
- `CLAUDE.md` / `.claude/CLAUDE.md` (Claude Code)
- `GEMINI.md` / `.gemini/GEMINI.md` (Gemini CLI / Antigravity)
- `.github/copilot-instructions.md` (GitHub Copilot)

**Token target per file**: ≤ 80 lines / ≤ ~800 tokens.

**Keep** (changes agent behaviour on every request):
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

## Phase 3.5: Session Token Efficiency

> Skip this phase if the user only asked about file-level deduplication or CLAUDE.md trimming.
> Surface it when the user asks about token usage, conversation cost, or why sessions feel slow.

Token costs are **cumulative across turns** — every message in a multi-turn session re-pays the
full context window cost including all prior messages, all loaded skills, and all CLAUDE.md content.
A 200-line CLAUDE.md isn't 1× the cost of an 80-line one — it's that cost multiplied by every
turn in every session.

### 3.5.1 — Identify delegation candidates

Present this as a quick diagnostic. Ask the user:

> "Are there any tasks in this session where you're asking me to produce a structured output from
> well-defined inputs? (e.g., filling templates, extracting information, converting formats,
> writing first-draft documentation) — those can be delegated to a cheap sub-agent so your
> main session context stays light."

**Delegation rule of thumb:**

| Task type | Use cheap subagent? | Why |
|---|---|---|
| Template filling from provided input | Yes | No dialogue needed |
| Single-pass document generation | Yes | One-shot, no iteration |
| Data extraction / format conversion | Yes | Deterministic, bounded |
| Clarifying questions → structured answers | Yes | Cheap model handles Q&A; write answers to a file |
| Multi-turn refinement with feedback loops | No | Needs full model for judgment |
| Coordination, synthesis, orchestration | No | Outer-loop reasoning, full context required |
| Discovery sessions with SMEs | No | Interactive, nuanced |

### 3.5.2 — Context compounding advice

If the session is getting long or the user reports high token costs, surface these practices:

1. **Delegate Q&A to cheap subagents** — instead of asking questions interactively in the main
   session, batch 3–5 clarifying questions, dispatch a cheap model to collect answers from the
   user or from files, write results to `temp/clarifications.md`, and read that back. This converts
   expensive main-context Q&A into a cheap dispatch + one read.

2. **Use `/compact` between major topic switches** — if you've finished one task and are starting
   an unrelated one in the same session, run `/compact` first to compress prior context.

3. **Start fresh sessions for unrelated work** — context from a debugging session does not help
   a documentation session. Fresh session = zero context debt.

4. **Pipe artifacts, not transcripts** — when chaining agent tasks, pass structured files
   (e.g., `brd-draft.md`) as context rather than pasting conversation history. Structured files
   are token-dense and re-readable; pasted transcripts are token-bloated and partially redundant.

5. **Keep orchestrator turns light** — if you are coordinating multiple sub-agents, the main
   session should only hold the coordination decisions and the summary artifacts. Sub-agents
   run in isolated context and their outputs land in files; only the summaries come back to you.

### 3.5.3 — Cheap dispatch model selection

| You have | Simple tasks | Complex tasks |
|---|---|---|
| GitHub Copilot Pro | `gpt-5-mini` (free, via Copilot CLI) | `claude-sonnet` (1 premium req) |
| Claude only | `claude-haiku-4-5` (cheapest) | `claude-sonnet-4-6` (standard) |
| No sub-agent tooling | Main session (direct mode) | Main session (direct mode) |

For Claude Code specifically: use the `Agent` tool with `model: "haiku"` for cheap sub-agent
dispatches. For Copilot CLI: use `copilot gpt-5-mini` for free-tier passes.

---

## Phase 4: Post-Fix Validation

```bash
wc -l CLAUDE.md   # confirm ≤ 80 lines
python plugins/dev-utils/scripts/optimize_context.py --dry-run  # confirm 0 skill duplicates
```

---

## Key Learning: Discovery Topology

Through iterative testing (RED-GREEN-REFACTOR), we confirmed the discovery 
hierarchy for Claude Code:

1.  **Plugin Source (Canonical)**: Claude auto-scans the repository for any 
    `SKILL.md` files. It labels matches found in `plugins/` as **"Plugin"** in 
    the `/context` report.
2.  **Project Source (Redundant)**: Claude also scans `.claude/skills/` and 
    labels these as **"Project"** skills.
3.  **Multi-IDE fallback**: Antigravity, Gemini CLI, and Copilot **do not** 
    auto-scan; they require skills to be physically present in `.agents/skills/`.

**The Root Cause of Bloat**: The legacy installer was symlinking 
`.agents/skills/` → `.claude/skills/`. This caused Claude Code to load the same 
definition twice (once as "Plugin" from its scan of `plugins/`, and once as 
"Project" from its scan of the `.claude/` symlink).

**The Native Fix**: Clear all files from `.claude/skills|agents|commands|hooks`. 
Claude Code will still see everything via its auto-scan of `plugins/`, and other 
IDEs will still work via `.agents/`.

---

## Phase 5: Report

```
✅ optimize-context complete

Pass 1 — Skill deduplication:
  .claude/skills cleared : [N] entries removed
  .claude/agents cleared : [N] entries removed
  .claude/commands cleared: [N] entries removed
  Scanner result         : ✅ No filesystem duplicates

Pass 2 — Instruction files:
  CLAUDE.md   : [N] → [N] lines (-[N]%)   [skipped if absent]
  GEMINI.md   : [N] → [N] lines (-[N]%)   [skipped if absent]
  copilot-instructions.md: [N] → [N] lines [skipped if absent]

Pass 3 — Session efficiency: [skipped | N delegation candidates identified | practices applied]

Next: reload your IDE and check active context size
```

---

## Fallback Rules

- **`.claude/` empty already**: Skip Pass 1, report clean.
- **`plugins/` not found**: Skip scanner, report warning.
- **All instruction files already lean (≤ 80 lines each)**: Report as-is, suggest no changes.
- **User declines instruction file rewrite**: Skip Phase 3, complete Pass 1 only.
- **No instruction files found**: Report warning, skip Phase 3.

---

## References

- [`scripts/optimize_context.py`](../../scripts/optimize_context.py) — filesystem duplicate scanner
- [`references/acceptance-criteria.md`](references/acceptance-criteria.md) — structural pass/fail criteria
