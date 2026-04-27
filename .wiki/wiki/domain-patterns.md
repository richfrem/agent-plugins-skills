---
concept: domain-patterns
source: plugin-code
source_file: agent-agentic-os/references/domain-patterns/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.692613+00:00
cluster: failure
content_hash: 95bd242817b0eab2
---

# Domain Patterns

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Domain Patterns

Curated library of escape strategies for recurring skill-improvement failure types.
Each file covers one skill category and documents mutations that have produced confirmed KEEPs.

## What domain patterns are

When `os-improvement-loop` encounters a failure type it has seen before, it can apply
a proven escape strategy instead of generating a fresh hypothesis from scratch.
This reduces wasted iterations on already-solved problems and accelerates convergence.

Patterns are discovered during improvement runs. Human authors may also contribute
patterns from manual improvement sessions.

## When to read them

`os-improvement-loop` checks this directory at **Phase 1 Step A** — before formulating a hypothesis.
If the current failure type matches a known pattern, apply that pattern's documented escape
as the Step B proposal. Only fall back to a novel hypothesis if no pattern matches.

## How to contribute a new pattern

1. A novel KEEP occurs and the failure type was not in any existing pattern file.
2. `os-improvement-loop` logs: `"Novel failure — tracking as candidate pattern."` in the run log.
3. After a **2nd KEEP confirmation** on the same failure type (in any run), promote the entry:
   - Add it under `## Novel Candidates` in the relevant file first.
   - After the 2nd confirmation, move it to `## Known Successful Mutations`.
4. Include: failure type, root cause, escape steps, and confirmed KEEP count.

## File naming convention

`<skill-category>.md` — name by the primary evaluation axis of the skill type:

| File | Covers |
|:-----|:-------|
| `routing-skill.md` | Skills evaluated on trigger/no-trigger routing accuracy |
| `python-script.md` | Skills that produce or modify Python scripts |
| `config-file.md` | Skills that generate structured config (JSON, YAML, TOML) |


## See Also

- [[domain-patterns-exploration-cycle]]
- [[domain-patterns-exploration-session-failures]]
- [[domain-patterns-routing-skills]]
- [[architectural-patterns-adapted-from-obrasuperpowers-mit-httpsgithubcomobrasuperpowers]]
- [[fix-patterns-like-or]]
- [[patterns-to-find-file-references-in-code]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/references/domain-patterns/README.md`
- **Indexed:** 2026-04-27T05:21:03.692613+00:00
