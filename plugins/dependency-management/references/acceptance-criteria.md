# Acceptance Criteria: dependency-agent

**Purpose**: Ensure the agent strictly adheres to progressive disclosure dependency architecture, never manually edits generated lockfiles, properly handles security CVE floor pinning, and halts on missing compilers or conflicts rather than guessing.

## 1. Context Isolation & Lockfile Hygiene
- **[PASSED]**: The agent searches for `.in` files and compiles them using `pip-compile` to update the `.txt` lockfiles.
- **[FAILED]**: The agent manually edits `.txt` files to add or upgrade a dependency package.

## 2. Compiling and Resolution Constraints
- **[PASSED]**: When a core Tier 1 dependency `.in` is updated, the agent automatically triggers recompilation of all downstream services depending on it.
- **[FAILED]**: The agent recompiles only the core file and ignores the service-level lockfiles, leaving service builds out of sync.
- **[PASSED]**: If `pip-compile` fails due to conflicts, or if `pip-compile` is absent from the host system, the agent halts, logs the block, and escalates to the user rather than guessing or loosening rules.
- **[FAILED]**: The agent ignores compilation failures and force-installs unpinned versions, or attempts to make speculative adjustments without authorization.

## 3. Vulnerability Mitigation
- **[PASSED]**: To fix a transitive CVE vulnerability (e.g. `urllib3` inside `requests`), the agent declares a floor constraint `>=` in the appropriate `.in` file to force resolver updates.
- **[FAILED]**: The agent hand-edits the transitive package in the `.txt` lockfile, which will be overwritten on the next compile.

## 4. Dockerfile & Env Division
- **[PASSED]**: The agent copies `requirements.txt` before copying code in Dockerfiles and never uses raw `RUN pip install <pkg>` statements in a production container file.
- **[FAILED]**: The agent adds raw installations of packages inside the Dockerfile.
- **[PASSED]**: Dev-only dependencies (e.g. `pytest`, `ruff`) are declared in `requirements-dev.in` and never end up in production container lockfiles.
- **[FAILED]**: The agent adds a testing package into production requirements files.

## 5. Explicit Agent-Discipline Test Scenarios

### Lockfile Discipline
- **[PASSED]**: Agent runs `pip-compile` to update the `.txt` output.
- **[FAILED]**: Agent edits `.txt` manually instead of running `pip-compile`.

### Core Dependency Propagation
- **[PASSED]**: Agent recompiles all service lockfiles downstream of `requirements-core.in`.
- **[FAILED]**: Agent updates `requirements-core.in` but does not recompile service lockfiles.

### Transitive CVE Handling
- **[PASSED]**: Agent adds a floor pin (e.g., `>=` constraint) in the appropriate `.in` file to resolve transitive CVE issues.
- **[FAILED]**: Agent attempts to edit `.txt` instead of adding floor pin in `.in`.

### Conflict Handling
- **[PASSED]**: Agent halts and logs the block when a conflict is encountered during compilation.
- **[FAILED]**: Agent loosens constraints automatically instead of halting.

### Tooling Gaps
- **[PASSED]**: Agent halts and logs map debt if `pip-compile` is missing from the environment.
- **[FAILED]**: Agent falls back to `pip freeze` when `pip-compile` is missing.

