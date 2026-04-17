---
concept: procedural-fallback-tree-adr-management
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/adr-management/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.708594+00:00
cluster: directory
content_hash: f58e85b1d3666531
---

# Procedural Fallback Tree: ADR Management

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: ADR Management

## 1. ADRs Directory Does Not Exist
If `adr_manager.py create` is run and the target directory (`ADRs/` or custom) does not exist:
- **Action**: The script creates the directory automatically on first run (per acceptance criteria). Report to the user that the directory was created. Do NOT fail silently.

## 2. ID Numbering Conflict (Duplicate Found)
If `../scripts/next_number.py` detects that the next sequential ID already exists as a file:
- **Action**: Report the conflict, showing the conflicting filename. Do NOT overwrite the existing file. Increment past the conflict and report the new ID used.

## 3. Existing ADR Not Found When Superseding
If instructed to mark an ADR as Superseded but the referenced ADR number does not exist in the directory:
- **Action**: Report the missing ADR number. List the available ADR IDs (via `adr_manager.py list`). Ask the user to confirm the correct ID before making any changes.

## 4. Template Sections Missing or Blank
If any of the 5 required sections (Status, Context, Decision, Consequences, Alternatives) would be left blank:
- **Action**: Extrapolate the missing sections from context using software engineering knowledge. If insufficient information is available, ask the user a targeted question for each blank section. Never create a skeleton ADR with empty sections.


## See Also

- [[procedural-fallback-tree-dependency-management]]
- [[procedural-fallback-tree-memory-management]]
- [[procedural-fallback-tree-dependency-management]]
- [[procedural-fallback-tree-dependency-management]]
- [[procedural-fallback-tree-memory-management]]
- [[procedural-fallback-tree-memory-management]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/adr-management/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:09.708594+00:00
