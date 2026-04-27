---
name: optimize-agent-instructions
plugin: agent-agentic-os
description: >
  Audits and rewrites AI agent instruction files (CLAUDE.md, GEMINI.md,
  .github/copilot-instructions.md) in any repo. Strips stale or foreign content,
  applies Karpathy's four behavioral principles, ensures platform-specific sections,
  and makes each file authoritative rather than a copy of another.
  Trigger when the user says "optimize my CLAUDE.md", "audit agent instructions",
  "improve my CLAUDE.md", "apply Karpathy principles to my agent files", "clean up
  my copilot instructions", "review my GEMINI.md", or "update my AI instruction files".
allowed-tools: Read, Write, Bash
---

<example>
<commentary>User wants their agent instruction files to follow best practices.</commentary>
user: "Optimize my CLAUDE.md with Karpathy principles"
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
ls CLAUDE.md GEMINI.md .github/copilot-instructions.md 2>/dev/null
```

**2. Ask the user:**
- What platform(s) they use (Claude Code, Copilot, Gemini CLI) — determines which files to touch
- Any project-specific rules to preserve (coding standards, ADRs, naming conventions)

If instruction files are missing for active platforms, offer to create them.

---

## Phase 2 — Audit Each File

Read each file, then score it against the **Quality Checklist**:

### Quality Checklist

**Structure**
- [ ] Merges Karpathy's behavioral guidelines with project-specific instructions as needed
- [ ] No stale AI-session artifacts ("Would you like X configured?", "Here is a summary of...")
- [ ] No foreign rules from other projects (spec-kitty constitution, unrelated frameworks)
- [ ] No self-referential framing ("this file reproduces CLAUDE.md...", "this is a copy of...")
- [ ] All paths and commands are current and correct
- [ ] Platform-specific notes are present where relevant (Windows caveats, tool name mapping)

**Karpathy Principles** — verify all four are present:
- [ ] **1. Think Before Coding**: States what to clarify before starting, what to ask. Surfacing tradeoffs.
- [ ] **2. Simplicity First**: Minimum code that solves the problem. Nothing speculative.
- [ ] **3. Surgical Changes**: Touch only what you must. Clean up only your own mess. Match existing style.
- [ ] **4. Goal-Driven Execution**: Define success criteria. Loop until verified. Verify goals.

**Platform-specific (if applicable)**
- [ ] Gemini: has tool name mapping table (Read→read_file, Bash→run_shell_command, etc.)
- [ ] Copilot: is authoritative (not framed as "a copy of CLAUDE.md")

Report the audit score before rewriting. Example:
```
CLAUDE.md: 6/8 checks pass
  ✗ No Karpathy principles section
  ✗ Stale artifact at EOF
  ✓ No self-referential framing
  ...
```

---

## Phase 3 — Rewrite Plan

For each file that scored poorly, propose changes:

- State what will be **removed** (foreign content, stale artifacts)
- State what will be **added** (Karpathy section, platform notes)
- State what will be **preserved** (valid project-specific rules)

Get confirmation before writing. Show the full proposed content for each file.

---

## Phase 4 — Write

Before rewriting any files, read the Karpathy principles example at `references/sample-claude-md`. This file contains the authoritative representation of the principles derived from [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills/blob/main/CLAUDE.md).

Write each file using the canonical structure below.

### Canonical Structure

```markdown
# <Title (e.g., CLAUDE.md or Copilot Instructions)>

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
` ` `
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
` ` `
(Note: Do not escape backticks in actual file, use regular markdown codeblock formatting)

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

---

## Project-Specific Rules
<Project-specific rules. Keep existing rules from previous versions, or omit section if none exist.>
```

### Platform-Specific Sections

**For GEMINI.md only** — append after the main content:
```markdown
## Gemini CLI Tool Mapping

| Claude Code | Gemini CLI equivalent |
|:------------|:----------------------|
| `Read`      | `read_file`           |
| `Write`     | `write_file`          |
| `Edit`      | `replace_in_file`     |
| `Bash`      | `run_shell_command`   |
| `Glob`      | `glob`                |
| `Grep`      | `grep`                |

Skills in `.agents/skills/` use Claude Code tool names in their SKILL.md files.
When executing skills via Gemini, translate tool references using the table above.
```

**For .github/copilot-instructions.md** — title line should be authoritative:
```
# Copilot Instructions for <repo-name>

> Authoritative rules for all AI agents (Claude Code, Copilot, Gemini) working in this repo.
> Mirrors CLAUDE.md — keep in sync.
```

---

## Phase 5 — Verify

After writing, re-run the Quality Checklist mentally. Confirm:

1. No stale artifacts remain
2. All four Karpathy principles are present exactly as prescribed
3. Platform-specific sections are correct
4. Files are authoritative — none frame themselves as copies of another

Report:
```
=== optimize-agent-instructions Complete ===

Files updated:
  ✓ CLAUDE.md       — 8/8 checks pass
  ✓ GEMINI.md       — 8/8 checks pass
  ✓ .github/copilot-instructions.md — 8/8 checks pass

Karpathy principles: ✓ all four present in all files
Stale artifacts removed: 2
Foreign content removed: 1
Platform sections added: Gemini tool mapping
```

---

## Rules

- Never remove valid project-specific rules — move them to `## Project-Specific Rules`.
- Never create files that don't exist (CLAUDE.md, GEMINI.md, copilot-instructions.md) unless the user explicitly asks
- Always read before writing — never write a file you haven't read this session
- Keep all three files in sync on shared content (Karpathy principles, Project-specific rules)
- Gemini tool mapping only goes in GEMINI.md — not in CLAUDE.md or copilot-instructions.md

---

## Attribution

The four behavioral principles in this skill are derived from
[Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876)
on LLM coding pitfalls, as distilled by
[forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills).
