---
name: optimize-agent-instructions
plugin: agent-agentic-os
description: >
  Audits and rewrites AI agent instruction files (AGENTS.md, CLAUDE.md, GEMINI.md,
  .github/copilot-instructions.md) in any repo. Strips stale or foreign content,
  applies Karpathy's four behavioral principles, ensures platform-specific sections,
  and makes each file authoritative rather than a copy of another.
  Trigger when the user says "optimize my CLAUDE.md", "audit agent instructions",
  "improve my AGENTS.md", "apply Karpathy principles to my agent files", "clean up
  my copilot instructions", "review my GEMINI.md", or "update my AI instruction files".
allowed-tools: Read, Write, Bash
---

<example>
<commentary>User wants their agent instruction files to follow best practices.</commentary>
user: "Optimize my AGENTS.md with Karpathy principles"
assistant: [triggers optimize-agent-instructions, reads files, audits against checklist, rewrites]
</example>

<example>
<commentary>User has stale auto-generated content in their instruction files.</commentary>
user: "My GEMINI.md has a bunch of stuff that doesn't belong — can you clean it up?"
assistant: [triggers optimize-agent-instructions, identifies foreign content, strips and rewrites]
</example>

<example>
<commentary>Negative — user wants to update a specific skill, not instruction files.</commentary>
user: "Improve the trigger description for my link-checker skill"
assistant: [triggers os-improvement-loop, not optimize-agent-instructions]
</example>

# optimize-agent-instructions

Audits and rewrites the AI agent instruction files in a repo. Works on any project —
not just agent-plugins-skills. The goal is files that are authoritative, concise, and
guide AI behavior through explicit principles rather than hoping for defaults.

---

## Phase 1 — Discovery

Run these checks silently before asking anything:

**1. Which instruction files exist?**
```bash
ls AGENTS.md CLAUDE.md GEMINI.md .github/copilot-instructions.md 2>/dev/null
```

**2. Ask the user:**
- What platform(s) they use (AGENTS.md open standard / Cursor / Codex / Antigravity, Claude Code, Copilot, Gemini CLI) — determines which files to touch
- Any project-specific rules to preserve (coding standards, ADRs, naming conventions)

If instruction files are missing for active platforms, offer to create them.

---

## Phase 2 — Audit Each File

Read each file, then score it against the Quality Checklist: structure (Karpathy + project rules
merged, no stale AI-session artifacts, no foreign rules from other projects, no self-referential
"copy of X" framing, current paths/commands, platform notes present), all four Karpathy
Principles present, and platform-specific checks (Gemini tool-mapping table; Copilot file is
authoritative, not framed as a copy). Full checklist and the audit-score report format are in
`references/detailed-reference.md`. Report the score before rewriting.

---

## Phase 3 — Rewrite Plan

For each file that scored poorly, propose changes:

- State what will be **removed** (foreign content, stale artifacts)
- State what will be **added** (Karpathy section, platform notes)
- State what will be **preserved** (valid project-specific rules)

Get confirmation before writing. Show the full proposed content for each file.

---

## Phase 4 — Write

Read the Karpathy principles at `references/sample-claude-md`. Write each file using the
canonical structure (tradeoff note, the four Karpathy sections, working-if footer, project rules)
plus platform-specific sections (Gemini CLI Tool Mapping table; copilot-instructions.md
authoritative title + "Mirrors CLAUDE.md" note). Full templates in `references/detailed-reference.md`.

## Phase 5 — Verify & Rules

Verify all four Karpathy principles are present, platform sections match, and files are
authoritative. Never remove valid project rules (move to `## Project-Specific Rules`), never
create unrequested instruction files, and always read files before writing. Full verification
report format, rules, and Karpathy attribution are in `references/detailed-reference.md`.
