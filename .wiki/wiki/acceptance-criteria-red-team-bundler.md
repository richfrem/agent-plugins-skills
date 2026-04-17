---
concept: acceptance-criteria-red-team-bundler
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/red-team-bundler/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.191730+00:00
cluster: agent
content_hash: 96ebbe0338e8d65b
---

# Acceptance Criteria: Red Team Bundler

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: Red Team Bundler

The red-team-bundler skill must meet the following criteria to be considered operational:

## 1. Workspace Isolation
- [ ] The agent accurately creates an isolated temporary directory (e.g., `temp/red-team-review-[topic]`) for the exercise.

## 2. Prompt Engineering
- [ ] The agent writes a `prompt.md` file that explicitly assigns a "Red Team / Security Auditor" persona.
- [ ] The prompt includes clear rules of engagement (e.g., output formats, severity levels, exploit scenarios).

## 3. Manifest Ordering
- [ ] **Critical:** The generated `file-manifest.json` MUST list `prompt.md` as the very first item in the `files` array. This guarantees the receiving AI reads the instructions before the codebase.

## 4. Output Handoff
- [ ] The agent successfully delegates to the standard Markdown bundler script to compile the final `.md` file.
- [ ] The agent explicitly tells the user the bundle is ready for export to an external LLM.

## See Also

- [[acceptance-criteria-red-team-review]]
- [[acceptance-criteria-red-team-review]]
- [[acceptance-criteria-red-team-review]]
- [[acceptance-criteria-context-bundler]]
- [[red-team-bundler-skill]]
- [[procedural-fallback-tree-red-team-bundler]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/red-team-bundler/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.191730+00:00
