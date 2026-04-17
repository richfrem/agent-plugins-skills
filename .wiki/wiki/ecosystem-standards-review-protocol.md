---
concept: ecosystem-standards-review-protocol
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/ecosystem-standards/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.059690+00:00
cluster: skill
content_hash: d48c88cd36408bf6
---

# Ecosystem Standards Review Protocol

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: ecosystem-standards
description: Provides active execution protocols to rigorously audit how code, directory structures, and agent actions comply with the authoritative ecosystem specs. Trigger when validating new skills, plugins, or workflows.
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Ecosystem Standards Review Protocol

This skill details how to perform an audit on new or existing capabilities (Skills, Plugins, Workflows, Sub-Agents, and Hooks) against authoritative ecosystem specifications to ensure they are created, installed, and structured correctly.

## Instructions
When invoked to review a codebase component or a planned extension:

1.  **Identify the Component Type**: Determine if the subject is a Plugin boundary, an Agent Skill, an Antigravity Workflow/Rule, a Sub-Agent, or a Hook.
2.  **Recall the Specs**: Before reviewing, read the relevant specification file found in the `ecosystem-authoritative-sources` skill library.
    *   *Path:* `./references/*.md`
3.  **Perform Rigorous Audit**:
    *   **Structure**: Does the directory schema match the standard (`./plugin.json`, `my-skill/SKILL.md`)? Are all supporting files strictly organized into the official optional directories (`scripts/`, `references/`, `assets/`) rather than cluttering the skill root?
    *   **Manifest Schema**: Does `plugin.json` follow the authoritative schema? Check:
        - `name` is kebab-case (lowercase, hyphens, no spaces)
        - `version` uses semver (e.g., `0.1.0`, not `1.0`)
        - `author` is an object `{"name": "..."}`, NOT a string
        - No `author.url` field (not in spec)
        - No `commands_dir` or `skills_dir` fields (auto-discovered)
        - `skills`, `agents`, `hooks`, `commands`, `scripts`, `dependencies` arrays are documentation-only (ignored by runtime, OK to keep for human readability)
        - See `references/plugins.md` in `ecosystem-authoritative-sources` for the full schema
    *   **Naming**: Verify the skill name uses the **gerund form** (`verb + -ing`, e.g., `analyzing-spreadsheets`). Reject generic nouns. Ensure the `name` is 1-64 lowercase alphanumeric chars/hyphens only, contains NO consecutive hyphens (`--`), and EXACTLY matches the parent directory name.
    *   **Content**: Does the YAML frontmatter adhere precisely to rules (`description` 1-1024 chars, `compatibility` max 500 chars, `metadata` strictly string-to-string keys/values)? Provide the recommendation to run `skills-ref validate ./my-skill` to definitively catch parse errors.
    *   **Description Viewpoint**: Ensure the `description` is written strictly in the **third person** ("Extracts text", not "I extract text") and isn't overly vague.
    *   **Progressive Disclosure**: For Skills, is the `SKILL.md` file appropriately constrained (< 500 lines) with extraneous detail pushed to one-level deep reference files? **Reject deeply nested reference chains**.
    *   **Reference Paths**: Verify that all file references are strictly relative to the skill's root (e.g., `scripts/extract.py`), avoiding absolute paths outside the plugin boundaries.
    *   **Reference Readability**: Do reference files >100 lines contain a Table of Contents for partial-read navigation?
    *   **Script Quality**: Verify python utility scripts do **not** punt errors back to the LLM (e.g., failing silently), but instead handle exceptions safely or emit clear `stderr` messages. Ensure they don't use undocumented "magic numbers" (voodoo constants).
    *   **Multi-CLI Support**: When integrating agent CLI plugins, support exists for `claude-cli`, `gemini-cli`, and `copilot-cli`. Plugins must reflect the native CLI syntax in their system

*(content truncated)*

## See Also

- [[procedural-fallback-tree-ecosystem-standards-protocol]]
- [[procedural-fallback-tree-ecosystem-standards-protocol]]
- [[procedural-fallback-tree-ecosystem-standards-protocol]]
- [[acceptance-criteria-ecosystem-standards]]
- [[acceptance-criteria-ecosystem-standards]]
- [[acceptance-criteria-ecosystem-standards]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/ecosystem-standards/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.059690+00:00
