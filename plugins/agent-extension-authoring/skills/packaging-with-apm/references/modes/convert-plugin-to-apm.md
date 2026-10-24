> Retired skill `convert-plugin-to-apm`, kept as the **convert-plugin-to-apm** mode of `packaging-with-apm`. Body unchanged apart from link targets, moved script/test paths and the compile verification command (`apm compile --validate`). Frontmatter removed.
>
> Original description: Activate when the user wants to convert an existing Claude/Copilot/agent plugin to APM, add APM package management to a plugin without changing its layout, migrate a plugin to APM-native format, or check that a plugin packages and installs cleanly with APM.

# Convert Plugin to APM (`convert-plugin-to-apm`)

Packages or converts an existing agent plugin repository for [APM](https://github.com/microsoft/apm), verifies the install across agent harnesses, and reports every misalignment with its standard fix. Behaviour below was verified with APM `0.33.0`.

## Contents

- [Critical Constraints](#critical-constraints)
- [Two Conversion Tracks](#two-conversion-tracks)
- [Track A: Interactive Modal Consolidation (Authoritative)](#track-a-interactive-modal-consolidation-authoritative)
- [Track B: Legacy Build Pipeline Overlay](#track-b-legacy-build-pipeline-overlay)
- [Authoring Rules for APM](#authoring-rules-for-apm)
- [Verification](#verification) · [References](#references)

## Critical Constraints

1. **Conduct Interactive Discovery First**: For complex repositories, never restructure files autonomously. Run the 5-point intake interview to uncover repo-specific documentation dependencies, customer data locations, and target design aspirations.
2. **Review Wave-by-Wave**: Review mapping plans one wave/plugin at a time with the operator before executing file operations.
3. **Deterministic Pre-Purge Accounting**: Run an automated comparison script verifying 100% of files exist at target locations before deleting legacy folders.
4. **Scope Discipline**: Domain-specific packages install project-locally; only universal agent OS infrastructure installs globally.

## Two Conversion Tracks

| Track | When to Choose | Key Characteristics | Reference |
| :--- | :--- | :--- | :--- |
| **Track A: Interactive Modal Consolidation** *(Authoritative)* | Complex multi-skill plugins, repos with copy manifests (`symlinks.json`), broken Windows symlinks, or downstream consumers | Retires copy manifests, collapses micro-skills into modal hubs (< 100 lines), interactive wave-by-wave review, 100% pre-purge accounting | [legacy-plugin-conversion-guide.md](../legacy-plugin-conversion-guide.md) |
| **Track B: Build Pipeline Overlay** | Simple, already-consolidated single plugins needing an APM package bundle without layout refactoring | Packages in staging under `build/`, tests install/uninstall, writes `.zip` bundle | Section below |

---

## Track A: Interactive Modal Consolidation (Authoritative)

Follow this 5-stage interactive lifecycle when migrating real-world plugin repositories:

### 1. Interactive Intake & Discovery (The 5 Dimensions)
Interview the operator to uncover unique repository context:
1. **Target Repo & Git Status**: Path, active branch, worktree clean status.
2. **Current Footprint**: Plugins count, micro-skills count, copy manifests (`symlinks.json`).
3. **Design Aspirations**: Single unified plugin (e.g. `@sharepoint/sharepoint-workbench`) vs multi-plugin; desired domain hubs.
4. **Repository Pitfalls & Caveats**: Workflow dependencies on legacy skill names (e.g. Oracle Forms), required runtimes (PowerShell 7+, Python, Node), or platform symlink text stubs.
5. **Downstream Consumers & Data Paths**: Projects that invoke these skills (e.g. `jag-csb-intranet`); proprietary paths to protect (`inventory/`, `config*.psd1`, `context/`).

### 2. Wave-by-Wave Mapping & Interactive Review Gate
Partition the migration into 4–8 logical waves. For each wave, formulate an explicit mapping table:

```markdown
| Legacy Micro-Skill | Consolidated Hub Skill | Target Mode | Absorbed Scripts / Assets | Caveats & Invariants |
|:---|:---|:---|:---|:---|
| `<old-skill>` | `<hub-skill>` | `<mode>` | `scripts/<script>.py` | Preserves parameter X |
```
Present the wave mapping to the human operator for review and approval before touching code.

### 3. Delegated Execution & Self-Contained Co-location
- Dispatch implementation tasks to a high-throughput worker (**Codex CLI** / Luna 6) with unconstrained workspace write access.
- Author modal `SKILL.md` (< 100 lines) routing to `references/modes/<mode>.md`.
- Co-locate scripts and assets directly in `skills/<hub-skill>/scripts/` as real Git-tracked files (Solution B).

### 4. Multi-Layer Deterministic Gates & Pre-Purge Accounting
- Run `audit_skill.py <path> --mode source` (verifies frontmatter, schemas, and relative links).
- Run unit test suites with `pytest`.
- Run automated pre-purge check verifying 100% of source files exist at target locations before executing `git rm -rf`.

### 5. Downstream Consumer Refactor Matrix & Scope Discipline
- Author a 1:1 transition matrix cheat sheet for consumer repositories.
- Configure `.gitignore` in consumer projects to exclude deployed client harnesses (`.agents/`, `.claude/skills/`, `.codex/`, `.github/agents/`, `apm_modules/`).

---

## Track B: Legacy Build Pipeline Overlay

For existing plugins undergoing overlay-based APM packaging without structural changes:

### Quick Start
```bash
python3 scripts/apm_build_pipeline.py --plugin plugins/<plugin-name> --apm <path-to-apm>
```
Add `--pack` to build the installable bundle, or `--skip-deploy` to validate without APM.

### Workflow
1. **Run the pipeline**: Stages: inspect, normalize, validate, package, test deploy, and (with `--pack`) pack.
   - Symlinks are read from the git index, handling Windows checkouts.
   - Legacy `symlinks.json` entries with `strategy: "copy"` become per-skill physical copies in staging only.
2. **Apply Findings**: Read `build/staging/<plugin>.report.json` and apply standard fixes (SF-1 to SF-11) from [apm-alignment-fixes.md](../apm-alignment-fixes.md).
3. **Verify Clean Deployment**: Re-run until validation and test deploy pass cleanly.

## Authoring Rules for APM

| Reference to | Write it as |
|---|---|
| Another skill or agent | Its name: "use the `managing-adrs` skill" |
| A file in the same skill | A path relative to the skill folder (`references/`, `scripts/`) |
| A document elsewhere in the plugin | A markdown link with a `../` path inside the plugin |
| A script the skill runs | Keep it inside the skill (`scripts/<script>.py`) |
| A hook script | `${CLAUDE_PLUGIN_ROOT}/hooks/x.py` in `hooks/hooks.json` |
| Another plugin's files | The other plugin's skill by name, never a path |

Never name an install folder (`.agents/`, `.claude/`, `~/.apm/`) in instructions; it differs by harness and by project versus global install.

## Verification

- **Track A (Modal Consolidation)**:
  ```bash
  python3 plugins/agent-extension-authoring/skills/authoring-skills/scripts/audit_skill.py <skill-path> --mode source
  pytest <skill-or-plugin-tests> -v
  ```
- **Track B (Overlay Pipeline)**:
  ```bash
  python3 scripts/apm_build_pipeline.py --plugin plugins/<name> --apm <path> --pack
  ```

## References

- [legacy-plugin-conversion-guide.md](../legacy-plugin-conversion-guide.md) — Authoritative interactive master playbook with 5-dimension intake questionnaire, wave mapping templates, and pre-purge accounting.
- [apm-alignment-fixes.md](../apm-alignment-fixes.md) — Standard fix for every pipeline finding (SF-1 to SF-11), with applied examples.
- [acceptance-criteria.md](../acceptance-criteria.md) — Acceptance criteria for the earlier overlay, hybrid and full conversion modes of `migrate_to_apm.py`.
- [fallback-tree.md](../fallback-tree.md) — Fallback resolution for mapping errors and validation rejections.
