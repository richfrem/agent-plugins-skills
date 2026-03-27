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
