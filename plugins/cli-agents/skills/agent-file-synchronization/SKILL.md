---
name: agent-file-synchronization
plugin: cli-agents
description: >
  Replicates CLAUDE.md into GEMINI.md, .github/copilot-instructions.md, and AGENTS.md
  as full-copy mirrors while preserving platform-specific sections (GEMINI.md tool mapping,
  copilot authoritative header). Also reports drift between .agent/rules/ and matching
  plugins/*/rules/ sources. Use when syncing, replicating, or mirroring CLAUDE.md into agent
  files, or checking rule drift. Different from optimize-agent-instructions (content audit) and
  project-setup (initial scaffold). Triggers: "sync CLAUDE.md to GEMINI.md", "replicate CLAUDE.md
  to agent files", "propagate CLAUDE.md changes", "mirror CLAUDE.md", "check rule drift".
allowed-tools: Bash, Read, Write
---

<example>
<commentary>User has just edited CLAUDE.md and wants the other instruction files kept in sync.</commentary>
user: "sync CLAUDE.md to the other agent files"
assistant: [triggers agent-file-synchronization, runs sync_instruction_files.py (dry-run by default), reports the diff summary, then --execute after confirmation]
</example>

<example>
<commentary>Negative — user wants a stylistic quality audit, not a mechanical sync.</commentary>
user: "audit my CLAUDE.md against Karpathy's principles and rewrite it"
assistant: [triggers optimize-agent-instructions, not agent-file-synchronization — that skill owns content quality, this one owns mechanical replication]
</example>

<example>
<commentary>Negative — user is setting up a brand-new project's agent config, not replicating an existing CLAUDE.md.</commentary>
user: "scaffold Claude and Gemini config for this new repo"
assistant: [triggers project-setup, not agent-file-synchronization — no CLAUDE.md exists yet to sync from]
</example>

# agent-file-synchronization

## Identity

You keep GEMINI.md, `.github/copilot-instructions.md`, and AGENTS.md as accurate mirrors of
CLAUDE.md — the single source of truth for this repo's agent instructions. A blind full-copy
destroys each target's platform-specific section; this skill detects and re-preserves those
sections automatically instead of requiring a human to notice and re-append them by hand.

**Scope**: This skill owns *mechanical replication*. It does not own *content quality*
(`optimize-agent-instructions`) or *initial project scaffolding* (`project-setup`).

## What gets preserved per target

| Target | Preserved section | Detected via |
|---|---|---|
| `GEMINI.md` | `## Gemini CLI Tool Mapping` table, appended at end of file | Tail marker match |
| `.github/copilot-instructions.md` | `# Copilot Instructions for <repo>` header + authoritative blockquote | Header lines before the shared body's first line |
| `AGENTS.md` | None currently required — verified fresh each run, not assumed | Header lines before the shared body's first line (empty if none) |

The shared body boundary is CLAUDE.md's fixed opening line: *"Behavioral guidelines to reduce
common LLM coding mistakes. Merge with project-specific instructions as needed."* Everything in
a target file between its own title and that line is treated as a preserved header. Everything
after a known tail marker (currently only GEMINI.md's table) is treated as a preserved tail.

## Steps

1. **Dry-run first, always**:
   ```bash
   python3 ./scripts/sync_instruction_files.py (no flags, dry-run is the default)
   ```
   Reports per-target line-count deltas and how many header/tail lines were detected and
   will be preserved. Review this before writing anything.

2. **If the dry-run summary looks right, execute**:
   ```bash
   python3 ./scripts/sync_instruction_files.py --execute
   ```

3. **Verify** — read at least one target file's tail (`tail -20 GEMINI.md`) to confirm the
   preserved section actually landed, don't just trust the script's own summary line.

4. **Reinstall + audit** per this repo's standing rules — sync only touches root-level docs,
   not `plugins/` source, so no plugin reinstall is needed for *this* step. But if the CLAUDE.md
   edit that triggered the sync also touched a skill/script, reinstall that plugin separately.

## Checking `.agent/rules/` drift against plugin rule sources

`.agent/rules/*.md` and `plugins/<plugin>/rules/*.md` are a **separate pairing** from the
CLAUDE.md-family mirrors above — same filename, but drift direction isn't reliably one-way
(either side can be the one that's stale), so this mode never writes:

```bash
python3 ./scripts/sync_instruction_files.py --check-rules
```

Reports per rule file: `IDENTICAL`, `DIFFERS` (with a unified diff), or
`NO PLUGIN COUNTERPART FOUND` (a `.agent/rules/`-only file with no matching plugin source —
not necessarily a problem, just worth knowing). On `DIFFERS`, read both files and manually
apply the fix on whichever side is actually behind — do not assume the plugin copy always wins.

## Common Failures

- **New platform section added to CLAUDE.md's own required structure**: if a future target needs
  a *new* kind of preserved section (not a header-before-anchor or tail-after-marker), the script's
  `TARGETS` list and marker-detection logic need a code change — this skill does not invent new
  preservation strategies on its own.
- **Anchor line changed or removed from CLAUDE.md**: the script hard-fails rather than guessing at
  the body boundary — if this happens, check whether CLAUDE.md's opening line changed and update
  `ANCHOR_LINE` in `scripts/sync_instruction_files.py` to match.
- **Target file has stray content between title and header that isn't actually platform-specific**:
  the script will treat it as preserved-header and keep re-appending it forever. Manually clean the
  target once; subsequent syncs will then preserve the cleaned version correctly.

## References

- [`acceptance-criteria.md`](references/acceptance-criteria.md)
- `CLAUDE.md` — "Instruction File Mirrors" section documents the same preservation rules this skill automates
- `optimize-agent-instructions` (agent-agentic-os) — deep content-quality audit, complementary not overlapping
