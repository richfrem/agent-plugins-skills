---
name: optimize-agent-instructions
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
assistant: [triggers os-skill-improvement, not optimize-agent-instructions]
</example>

# optimize-agent-instructions

Audits and rewrites the AI agent instruction files in a repo. Works on any project —
not just agent-plugins-skills. The goal is files that are authoritative, concise, and
guide AI behavior through explicit principles rather than hoping for defaults.

---

## Phase 1 — Discovery

Before reading anything, ask:

1. **Which files to audit?** Default: all that exist. Check:
   ```bash
   ls CLAUDE.md GEMINI.md .github/copilot-instructions.md 2>/dev/null
   ```
2. **What platform(s) does the user work on?** (Claude Code, Copilot, Gemini CLI, all)
3. **Does the repo have a Super-RAG stack?** (rlm-factory, vector-db, obsidian-wiki-engine)
   — if yes, include the Super-RAG context retrieval protocol section
4. **Any existing project-specific rules to preserve?** (coding standards, ADRs, etc.)

If files are missing that should exist for active platforms, offer to create them.

---

## Phase 2 — Audit Each File

Read each file, then score it against the **Quality Checklist**:

### Quality Checklist

**Structure**
- [ ] Has a `## Purpose` section (what the repo does)
- [ ] Has a `## Key Commands` section (install, run, test)
- [ ] Has a `## Architecture` section (directory layout, key paths)
- [ ] Has a `## Behavior & Judgment` section with Karpathy's four principles
- [ ] Has a `## Coding Rules` section (project-specific constraints)

**Content quality**
- [ ] No stale AI-session artifacts ("Would you like X configured?", "Here is a summary of...")
- [ ] No foreign rules from other projects (spec-kitty constitution, unrelated frameworks)
- [ ] No self-referential framing ("this file reproduces CLAUDE.md...", "this is a copy of...")
- [ ] All paths and commands are current and correct
- [ ] Platform-specific notes are present where relevant (Windows caveats, tool name mapping)

**Karpathy Principles** — verify all four are present and specific to this repo:
- [ ] **Think Before Acting**: states what to clarify before starting, what to ask
- [ ] **Simplicity First**: gives concrete limits (e.g. "SKILL.md under 500 lines")
- [ ] **Surgical Changes**: clear rule about not touching adjacent code
- [ ] **Goal-Driven Execution**: defines success criteria pattern (evals before content, etc.)

**Platform-specific (if applicable)**
- [ ] Gemini: has tool name mapping table (Read→read_file, Bash→run_shell_command, etc.)
- [ ] Copilot: is authoritative (not framed as "a copy of CLAUDE.md")
- [ ] All: has Super-RAG context retrieval table (if stack is installed)

Report the audit score before rewriting. Example:
```
CLAUDE.md: 8/12 checks pass
  ✗ No Karpathy principles section
  ✗ Stale artifact at EOF
  ✗ References spec-kitty rules (foreign project)
  ✓ Key commands present
  ...
```

---

## Phase 3 — Rewrite Plan

For each file that scored below 10/12, propose changes:

- State what will be **removed** (foreign content, stale artifacts)
- State what will be **added** (Karpathy section, platform notes)
- State what will be **preserved** (valid project-specific rules)

Get confirmation before writing. Show the full proposed content for each file.

---

## Phase 4 — Write

Write each file using the canonical structure below. Adapt sections to what the
repo actually needs — do not add sections that don't apply.

### Canonical Structure

```markdown
# <Title>

> <One-line purpose — what is this file? Who is it for?>

## Purpose
<What the repo does. Why it exists. What makes it unusual.>

---

## Key Commands
<Install, run, test, deploy. Bash code blocks. Keep current.>

---

## Architecture
<Directory tree or prose. Explain the canonical source vs runtime distinction if applicable.>

---

## Behavior & Judgment (Karpathy Principles)
<The four principles, adapted to this repo's domain. Not generic — specific.>

### 1. Think Before Acting
### 2. Simplicity First
### 3. Surgical Changes
### 4. Goal-Driven Execution

---

## Coding Rules (always applied)
<Project-specific rules. Link to ADRs if they exist.>

---

## Skill/Component Standards (if applicable)
<Naming conventions, file limits, schema requirements.>

---

## Scratch Output
<Where to write temp files. "Never to project root.">

---

## Context Retrieval Protocol (if Super-RAG is installed)
<3-phase table: keyword → semantic → concept.>
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
2. All four Karpathy principles are present in each file
3. Platform-specific sections are correct
4. Files are authoritative — none frame themselves as copies of another

Report:
```
=== optimize-agent-instructions Complete ===

Files updated:
  ✓ CLAUDE.md       — 12/12 checks pass
  ✓ GEMINI.md       — 12/12 checks pass
  ✓ .github/copilot-instructions.md — 12/12 checks pass

Karpathy principles: ✓ all four present in all files
Stale artifacts removed: 2
Foreign content removed: 1
Platform sections added: Gemini tool mapping, Super-RAG protocol
```

---

## Rules

- Never remove valid project-specific rules — only remove foreign or stale content
- Never create files that don't exist (CLAUDE.md, GEMINI.md, copilot-instructions.md) unless the user explicitly asks
- Always read before writing — never write a file you haven't read this session
- Keep all three files in sync on shared content (Purpose, Architecture, Coding Rules)
- The Karpathy principles should be adapted to the repo's domain, not copy-pasted verbatim
- Gemini tool mapping only goes in GEMINI.md — not in CLAUDE.md or copilot-instructions.md

---

## Attribution

The four behavioral principles in this skill are derived from
[Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876)
on LLM coding pitfalls, as distilled by
[forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills).
