---
concept: optimize-agent-instructions
source: plugin-code
source_file: agent-agentic-os/skills/optimize-agent-instructions/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.704668+00:00
cluster: files
content_hash: f286b2104224fe85
---

# optimize-agent-instructions

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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

**2. Which Super-RAG layers are installed?** Check `.agents/skills/` only — NOT `plugins/`.
Files in `plugins/` are the source repo and are inactive until installed via `plugin_add.py` or `uvx`.
```bash
ls .agents/skills/rlm-init/              2>/dev/null && echo "rlm-factory: INSTALLED"           || echo "rlm-factory: NOT INSTALLED"
ls .agents/skills/vector-db-init/        2>/dev/null && echo "vector-db: INSTALLED"             || echo "vector-db: NOT INSTALLED"
ls .agents/skills/obsidian-wiki-builder/ 2>/dev/null && echo "obsidian-wiki-engine: INSTALLED"  || echo "obsidian-wiki-engine: NOT INSTALLED"
```

Store which layers are installed. The Super-RAG protocol section in the output files will
**only include phases for installed layers**. If none are installed, omit the section entirely.

**3. Ask the user:**
- What platform(s) they use (Claude Code, Copilot, Gemini CLI) — determines which files to touch
- Any project-specific rules to preserve (coding standards, ADRs, naming conventions)

If instruction files are missing for active platforms, offer to create them.

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

**Karpathy Principles** — verify all four ar

*(content truncated)*

## See Also

- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[agent-agentic-os-hooks]]
- [[agent-bridge]]
- [[agent-harness-learning-layer]]
- [[agent-loops-execution-primitives]]
- [[agent-loops-hooks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/skills/optimize-agent-instructions/SKILL.md`
- **Indexed:** 2026-04-27T05:21:03.704668+00:00
