---
concept: procedural-fallback-tree-dependency-management
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/dependency-management/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.028346+00:00
cluster: version
content_hash: 2d9e11ab34e3ce4d
---

# Procedural Fallback Tree: Dependency Management

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Dependency Management

## 1. pip-compile Not Installed
If `pip-compile` command is not found when attempting to lock dependencies:
- **Action**: HALT. Do NOT fall back to `pip freeze` or manual editing of .txt files. Report the missing tool and provide the install command: `pip install pip-tools`. Never manually edit a .txt lockfile.

## 2. pip-compile Resolution Conflict
If `pip-compile` fails with a dependency conflict:
- **Action**: Report the conflicting package names and their version constraints. Do NOT auto-resolve by loosening constraints. Present the conflict to the user and ask which constraint should take priority. Only run pip-compile again after the user specifies the resolution.

## 3. Transitive Dependency Has No Patched Version
If a CVE affects a transitive dependency and no patched version exists:
- **Action**: Document the advisory by adding a comment to the .in file explaining the known risk and mitigations. Do NOT pin to a vulnerable version without documentation. Flag to the user that manual mitigation may be required.

## 4. Service Lockfile Out of Sync After Core Change
If a core .in change was compiled but service lockfiles were not recompiled:
- **Action**: Detect the out-of-date services by checking if their .txt files still reference the old version. Report each affected service. Do NOT commit until all downstream services are recompiled and verified.


## See Also

- [[procedural-fallback-tree-adr-management]]
- [[procedural-fallback-tree-memory-management]]
- [[procedural-fallback-tree-adr-management]]
- [[procedural-fallback-tree-memory-management]]
- [[procedural-fallback-tree-memory-management]]
- [[procedural-fallback-tree-agent-swarm]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/dependency-management/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.028346+00:00
