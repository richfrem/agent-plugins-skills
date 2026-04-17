---
concept: procedural-fallback-tree-red-team-bundler
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/red-team-bundler/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.192033+00:00
cluster: user
content_hash: 15a87080b6f9ec13
---

# Procedural Fallback Tree: Red Team Bundler

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Red Team Bundler

## 1. User Fails to Specify a Topic
If the user says "Prep a red team review" without specifying what code to look at:
- **Action**: STOP. Ask the user what specific module, feature, or folder they want reviewed so you can draft an accurate prompt and name the temp directory appropriately.

## 2. Temp Directory Already Exists
If `temp/red-team-review-[topic]` already exists from a previous run:
- **Action**: Do not halt. Either safely overwrite the existing `prompt.md`, `file-manifest.json`, and output `.md` file, or append a timestamp to the new directory name to prevent collisions.

## 3. Missing Core Context Files
If the user asks to review a specific feature, but you cannot find the core logic files:
- **Action**: Draft the prompt and manifest using whatever related documentation you *can* find, but explicitly warn the user that the core implementation files appear missing and ask if they want to manually add paths to the manifest before bundling.

## See Also

- [[procedural-fallback-tree-red-team-review]]
- [[procedural-fallback-tree-l5-red-team-auditor]]
- [[procedural-fallback-tree-l5-red-team-auditor]]
- [[procedural-fallback-tree-l5-red-team-auditor]]
- [[procedural-fallback-tree-red-team-review]]
- [[procedural-fallback-tree-red-team-review]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/red-team-bundler/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.192033+00:00
