# optimize-agent-instructions — Detailed Reference

Extracted from SKILL.md per Layer-1 procedural-core line budget (issue #551).

## Phase 2 — Quality Checklist (full)

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

## Phase 4 — Canonical Structure (full template)

Before rewriting any files, read the Karpathy principles example at `references/sample-claude-md`. This file contains the authoritative representation of the principles derived from [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills/blob/main/CLAUDE.md).

Write each file using the canonical structure below.

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

## Phase 5 — Verify report format

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

## Attribution

The four behavioral principles in this skill are derived from
[Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876)
on LLM coding pitfalls, as distilled by
[forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills).
