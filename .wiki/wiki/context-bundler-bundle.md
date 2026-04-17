---
concept: context-bundler-bundle
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/context-bundler_bundle.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.319578+00:00
cluster: phase
content_hash: 5eff251de4cdf8bb
---

# Context Bundler Bundle

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: bundle
description: Interactively package project files into a Markdown (.md) or ZIP archive.
argument-hint: "[target-directory or scope]"
allowed-tools: Bash, Read, Write
---

Follow the `context-bundler` skill workflow to package project context for sharing.

## Inputs

- `$ARGUMENTS` — optional target directory, specific files, or a brief scope description (e.g., "auth logic") to seed the discovery phase.

## Steps

1. **Phase 1: Discovery** — If `$ARGUMENTS` is vague, ask targeted questions to confirm the specific directories/files and the desired output format (.md or .zip).
2. **Phase 2: Recap & Confirm** — Present a proposed "Context Bundle Plan" listing the files and format. Wait for user approval.
3. **Phase 3: Build Manifest** — Formulate the `file-manifest.json` using recursive directory paths where possible.
4. **Phase 4: Execute & Handoff** — Invoke `bundle.py` (for .md) or `bundle_zip.py` (for .zip) using the created manifest.
5. Report the generated bundle path and provide instructions for use (e.g., copy/paste for Markdown).

## Output

A single file: either a structured Markdown document (`.md`) containing the source code and metadata, or a compressed Archive (`.zip`) for portability.

## Edge Cases

- **Token Limits:** If the target scope is too large for a single Markdown bundle, suggest splitting it or switching to ZIP.
- **Large Directories:** Use directory-level paths in the manifest instead of individual file entries to stay efficient.
- **Exclusions:** Respect `.gitignore` and common noise patterns (node_modules, .git).

## See Also

- [[context-bundler-plugin]]
- [[context-bundler-skill]]
- [[acceptance-criteria-context-bundler]]
- [[procedural-fallback-tree-context-bundler-markdown]]
- [[context-bundler-skill]]
- [[acceptance-criteria-context-bundler]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/context-bundler_bundle.md`
- **Indexed:** 2026-04-17T06:42:10.319578+00:00
