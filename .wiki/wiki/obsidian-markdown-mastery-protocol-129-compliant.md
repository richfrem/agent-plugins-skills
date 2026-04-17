---
concept: obsidian-markdown-mastery-protocol-129-compliant
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/obsidian-markdown-mastery/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.128401+00:00
cluster: plugin-code
content_hash: 48f52376b2c6b711
---

# Obsidian Markdown Mastery (Protocol 129 COMPLIANT)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: obsidian-markdown-mastery
description: "Core markdown syntax skill for Obsidian. Enforces strict parsing and authoring of Obsidian proprietary syntax (Wikilinks, Blocks, Headings, Aliases, Embeds, Callouts). Use when reading, writing, or validating Obsidian-flavored markdown."
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
# Obsidian Markdown Mastery (Protocol 129 COMPLIANT)

**Status:** Active
**Author:** Obsidian Integration Plugin
**Domain:** Obsidian Integration

## Core Mandate

The `obsidian-markdown-mastery` skill is responsible for the exact formatting, extraction, and validation of Obsidian-flavoured Markdown. It provides the low-level string manipulation that allows higher-order agents (like the Graph Traverser or JSON Canvas Architect) to safely interpret relational links without breaking the `.md` Vault.

> **CRITICAL ARCHITECTURAL RULE:**
> All vault data manipulation MUST occur through deterministic Python scripts rather than agent-prompted regex. This skill defines the `obsidian-parser` module that performs these deterministic actions.
> 
> *Agnosticism Enforcement*: This module knows NOTHING about project-specific protocols, persistence layers, or external services. It only knows how to parse text into valid Obsidian links and block-quotes. Project-specific configuration (vault paths, injection points) is managed via the `OBSIDIAN_VAULT_PATH` environment variable.

## Available Commands

### Analyze Markdown Content
Extracts all Obsidian-specific metadata (links, embeds, blocks) from a given markdown file or string.
**Command**: `python ./parser.py analyze --file <path_to_md>`

### Inject Callout
Wraps a target text block in an Obsidian-flavored callout.
**Command**: `python ./parser.py callout --type <type> --title <title> --text <content>`

## The Parsed Syntax (Data Dictionary)

When manipulating strings via this module, the following formats are enforced:

### 1. Linking and Aliasing
*   **Standard Link**: `[[Note Name]]`
*   **Heading Link**: `[[Note Name#Heading Name]]`
*   **Block Link**: `[[Note Name#^block-id]]`
*   **Aliased Link**: `[[Note Name|Display Text]]`

### 2. Transclusion (Embeds)
*   **Standard Embed**: `![[Note Name]]` (Note the leading `!`)
*   *(The parser specifically categorizes these differently so graph mappers know they are transclusions, not semantic links).*

### 3. Callouts
*   **Syntax**:
    ```markdown
    > [!type] Title
    > Content block goes here.
    ```
*   **Supported Types**: `info`, `warning`, `error`, `success`, `note`.

## Configuration Environment Variable
Other tools (such as `protocol-manager` and `chronicle-manager`) rely on the unified `OBSIDIAN_VAULT_PATH` environment variable to discover where the root of the Obsidian Vault resides. If missing, it defaults to the project root.


## See Also

- [[acceptance-criteria-obsidian-markdown-mastery]]
- [[procedural-fallback-tree-obsidian-markdown-mastery]]
- [[acceptance-criteria-obsidian-markdown-mastery]]
- [[procedural-fallback-tree-obsidian-markdown-mastery]]
- [[acceptance-criteria-obsidian-markdown-mastery]]
- [[procedural-fallback-tree-obsidian-markdown-mastery]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/obsidian-markdown-mastery/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.128401+00:00
