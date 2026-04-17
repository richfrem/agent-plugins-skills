---
concept: procedural-fallback-tree-context-bundler-markdown
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/context-bundler/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.751365+00:00
cluster: file
content_hash: 6234a259f4180d77
---

# Procedural Fallback Tree: Context Bundler (Markdown)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Context Bundler (Markdown)

## 1. File Not Found During Aggregation
If the agent attempts to read a file specified by the user and it does not exist:
- **Action**: Insert the explicit failure placeholder (`🔴 **NOT INCLUDED**`) into the Markdown bundle for that specific file path. Continue aggregating the rest of the files. Do NOT halt the entire bundling process.

## 2. File Unreadable (Permissions/Encoding)
If `view_file` or `cat` fails on a binary or permission-locked file:
- **Action**: Treat it exactly like a missing file. Insert the failure placeholder explaining that the file could not be read. Continue processing.

## 3. Bundle Exceeds Target Size (e.g. Output Too Large)
If compiling the bundle results in a massive Markdown file that exceeds output limits or takes too long to generate:
- **Action**: STOP. Report to the user that the requested bundle size is unmanageable as a single Markdown file. Suggest switching to `zip-bundling` or explicitly removing broad directories from the index.

## 4. User Provides Vague Request
If the user says "bundle the logic" without specifying files:
- **Action**: Perform a quick codebase search to identify 3-5 high-value files (e.g., `main.py`, standard architecture docs). Present the proposed manifest to the user for confirmation BEFORE generating the bundle.


## See Also

- [[procedural-fallback-tree-red-team-bundler]]
- [[procedural-fallback-tree-markdown-to-ms-word-conversion]]
- [[procedural-fallback-tree-obsidian-markdown-mastery]]
- [[procedural-fallback-tree-markdown-to-ms-word-conversion]]
- [[procedural-fallback-tree-markdown-to-ms-word-conversion]]
- [[procedural-fallback-tree-obsidian-markdown-mastery]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/context-bundler/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:09.751365+00:00
