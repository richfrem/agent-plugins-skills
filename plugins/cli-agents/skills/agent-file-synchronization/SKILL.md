---
name: agent-file-synchronization
plugin: cli-agents
description: >
  Synchronizes project instruction files across AGENTS.md, CLAUDE.md, GEMINI.md, and
  .github/copilot-instructions.md while preserving platform-specific sections (GEMINI.md tool
  mapping, copilot authoritative header). Supports AGENTS.md or CLAUDE.md as primary source,
  and selective target syncing. Also reports drift between .agent/rules/ and matching
  plugins/*/rules/ sources. Triggers: "sync instructions", "sync CLAUDE.md to GEMINI.md",
  "sync AGENTS.md", "replicate instruction files", "mirror CLAUDE.md", "check rule drift".
allowed-tools: Bash, Read, Write
---

<example>
<commentary>User has edited instructions and wants specific agent files kept in sync.</commentary>
user: "sync instructions across my agent files"
assistant: [triggers agent-file-synchronization, runs sync_instruction_files.py --dry-run by default, reports the diff summary, then runs with --execute after user confirmation]
</example>

<example>
<commentary>User only uses AGENTS.md and GEMINI.md and wants selective target sync.</commentary>
user: "sync AGENTS.md to GEMINI.md"
assistant: [triggers agent-file-synchronization, runs sync_instruction_files.py --source AGENTS.md --targets GEMINI.md --dry-run]
</example>

<example>
<commentary>Negative — user wants a stylistic quality audit, not a mechanical sync.</commentary>
user: "audit my AGENTS.md against Karpathy's principles and rewrite it"
assistant: [triggers optimize-agent-instructions, not agent-file-synchronization — that skill owns content quality, this one owns mechanical replication]
</example>

# agent-file-synchronization

## Identity

You synchronize project instruction files across modern AI tooling environments.
Today, **AGENTS.md** is an open cross-tool standard (Codex, Cursor, Antigravity, and portable agents),
while **CLAUDE.md** is used by Claude Code, **GEMINI.md** is used by Gemini CLI, and
**.github/copilot-instructions.md** is used by GitHub Copilot.

A blind full-copy destroys platform-specific sections; this skill detects and re-preserves those
sections automatically instead of requiring a human to re-append them by hand. It also respects
repos that only want a subset of target files (via `--targets`) rather than forcing all 4 formats.

**Scope**: This skill owns *mechanical replication*. It does not own *content quality*
(`optimize-agent-instructions`) or *initial project scaffolding* (`project-setup`).

## What gets preserved per target

| Target | Preserved section | Detected via |
|---|---|---|
| `GEMINI.md` | `## Gemini CLI Tool Mapping` table, appended at end of file | Tail marker match |
| `.github/copilot-instructions.md` | `# Copilot Instructions for <repo>` header + authoritative blockquote | Header lines before the shared body's first line |
| `AGENTS.md` | Open cross-tool standard (preserves custom header lines before anchor if any) | Header lines before anchor |
| `CLAUDE.md` | Anthropic Claude Code standard | Header lines before anchor |

The shared body boundary is the fixed anchor line: *"Behavioral guidelines to reduce
common LLM coding mistakes. Merge with project-specific instructions as needed."* (or standard `# Project Name` / `# Purpose` anchors).

## Steps

1. **Dry-run first, always**:
   ```bash
   python3 ./scripts/sync_instruction_files.py --dry-run
   ```
   Or with selective source and targets:
   ```bash
   python3 ./scripts/sync_instruction_files.py --source AGENTS.md --targets GEMINI.md,CLAUDE.md --dry-run
   ```
   Reports per-target line-count deltas and preserved sections.

2. **If the dry-run summary looks right, execute**:
   ```bash
   python3 ./scripts/sync_instruction_files.py --execute
   ```

3. **Verify** — inspect target files (e.g. `tail -20 GEMINI.md`) to confirm preserved sections.

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
