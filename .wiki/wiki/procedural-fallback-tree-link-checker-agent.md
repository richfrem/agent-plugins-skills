---
concept: procedural-fallback-tree-link-checker-agent
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/link-checker-agent/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.108322+00:00
cluster: fixer
content_hash: f168b3e3d296e8ec
---

# Procedural Fallback Tree: Link Checker Agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Link Checker Agent

## 1. file_inventory.json Missing When Fixer Runs
If `scripts/04_autofix_unique_links.py` is invoked but `file_inventory.json` does not exist:
- **Action**: HALT. Do NOT run the fixer with a missing inventory. Run `scripts/01_build_file_inventory.py` first and verify `file_inventory.json` is created before retrying.

## 2. broken_links.json Missing When Fixer Runs
If `scripts/04_autofix_unique_links.py` is invoked but `broken_links.json` does not exist:
- **Action**: WARN the user. The fixer will fall back to a full repo walk, which is slower and may fix links that were not actually flagged as broken. Strongly recommend running `scripts/03_audit_broken_links.py` first to produce `broken_links.json`, then re-running the fixer.

## 3. Fixer Reports Ambiguous Match (Multiple Candidates)
If `scripts/04_autofix_unique_links.py` finds multiple files matching a broken link's basename:
- **Action**: Do NOT silently pick one. Report all candidates to the user with their full relative paths. Ask the user to specify the correct target. Never auto-select when ambiguous.

## 4. Broken Links Remain After Fix (Step 5 Report Has Entries)
If `unfixable_links_report.md` contains unresolved links after running the full workflow:
- **Action**: Report each remaining broken link individually. Do NOT mark the audit as complete. Present options: (a) manual fix, (b) delete the dead reference. Await user decision per link.

## 5. Script Run from Wrong Directory (CWD Mismatch)
If any script produces errors about relative paths or produces an empty inventory:
- **Action**: Report that CWD must be the repository root. Print the current working directory and the expected root. Do NOT retry from the wrong directory.

## 6. Regex Corruption Suspected After Fix
If `git diff` shows unexpected changes after running the fixer (e.g., links inside code blocks were altered, or syntax was mangled):
- **Action**: HALT. Run `git restore .` (or `git checkout -- .`) to discard the changes. Report the issue to the user. Do NOT commit corrupted files.


## See Also

- [[procedural-fallback-tree-agent-swarm]]
- [[procedural-fallback-tree-create-azure-agent]]
- [[procedural-fallback-tree-create-sub-agent]]
- [[procedural-fallback-tree-claude-cli-agent]]
- [[procedural-fallback-tree-copilot-cli-agent]]
- [[procedural-fallback-tree-gemini-cli-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/link-checker-agent/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.108322+00:00
