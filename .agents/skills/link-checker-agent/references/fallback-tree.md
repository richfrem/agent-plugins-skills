# Procedural Fallback Tree: Link Checker Agent

## 1. file_inventory.json Missing When Fixer Runs
If `smart_fix_links.py` is invoked but `file_inventory.json` does not exist:
- **Action**: HALT. Do NOT run the fixer with a missing inventory. Run `map_repository_files.py` first and verify `file_inventory.json` is created before retrying.

## 2. Fixer Reports Ambiguous Match (Multiple Candidates)
If `smart_fix_links.py` finds multiple files matching a broken link's basename:
- **Action**: Do NOT silently pick one. Report all candidates to the user with their full relative paths. Ask the user to specify the correct target. Never auto-select when ambiguous.

## 3. check_broken_paths.py Reports Remaining Broken Links After Fix
If `broken_links.log` contains unresolved links after running the full workflow:
- **Action**: Report each remaining broken link individually. Do NOT mark the audit as complete. Present options: (a) manual fix, (b) delete the dead reference. Await user decision per link.

## 4. Script Run from Wrong Directory (CWD Mismatch)
If any script produces errors about relative paths or produces an empty inventory:
- **Action**: Report that CWD must be the repository root. Print the current working directory and the expected root. Do NOT retry from the wrong directory.
