# Guided RLM setup

Run this workflow in the main conversation. Do not dispatch an initialization agent.
Reuse user answers, existing configuration and already-authorized scope. An explicit
search/audit/distillation request uses its mode directly; do not restart this wizard.

## Contents

- [Choose scope](#choose-scope)
- [Interview](#interview)
- [Profiles and manifests](#profiles-and-manifests)
- [Apply and validate](#apply-and-validate)
- [Continue or resume](#continue-or-resume)

## Choose scope

Inspect the consumer root and existing .agent/learning/rlm_profiles.json first.
Check other skills by name in the active runtime, not by searching install folders.
Only ask if the requested combination is not already clear:

| Choice | Provision | Availability |
|---|---|---|
| A: RLM only (default) | project/tools summary ledgers | This skill |
| B: RLM + vector | Ledgers, then selected vector profiles | managing-vector-db |
| C: RLM + wiki | Ledgers and selected wiki source setup | managing-obsidian-vaults |
| D: Full Super-RAG | Ledgers, vector profiles and wiki | Both sibling skills |

Mark unavailable combinations. If a required skill is missing, explain the gap and
let the user choose an available subset or an APM install; do not install or change
the chosen scope silently. Never provision the wiki profile for A/B.

## Interview

Ask one unresolved question per turn, with a recommended default where appropriate.
Skip inputs already supplied. Retain answers across same-session skill transitions:

1. Consumer project root and project/profile namespace.
2. Directories/files for project documentation (suggest README.md and docs/).
3. Directories/files for tools (suggest the actual discovered source/skill roots).
4. Included extensions, additional exclusions, and cache destinations.
5. For distillation: files or batch scope, engine/model and budget if not configured.

Inspect before proposing paths. Keep discovery within the project unless the user
has authorized an external source. Never move raw files. Separate configuring a
profile from authorizing a model run or an optional dependency installation.

## Profiles and manifests

Read-and-merge existing configuration. Preserve unknown fields and existing profiles.
For a conflicting profile, show the diff and ask whether to merge, rename or cancel;
never overwrite by default. Reuse an existing suitable profile instead of duplicating it.
Show the complete proposed JSON/diff before applying the authorized changes.

Use the examples in assets/examples/ as schema templates. A minimal profile is:

```json
{
  "version": 1,
  "default_profile": "project",
  "profiles": {
    "project": {
      "description": "Project documentation",
      "manifest": ".agent/learning/rlm_manifest.json",
      "cache": ".agent/learning/rlm_summary_cache.json",
      "extensions": [".md", ".txt", ".rst"],
      "parser": "directory_glob"
    },
    "tools": {
      "description": "Source and skill documentation",
      "manifest": ".agent/learning/rlm_tools_manifest.json",
      "cache": ".agent/learning/rlm_tool_cache.json",
      "extensions": [".py", ".md"],
      "parser": "directory_glob"
    }
  }
}
```

Carry over a configured llm_model; for a new model-backed profile use the current
model catalog and the selected engine. Lookup/injection need no model or daemon.
Each profile manifest has flat include/exclude/recursive fields:

```json
{
  "include": ["README.md", "docs/**/*.md"],
  "exclude": ["node_modules", "__pycache__", ".git"],
  "recursive": true
}
```

Create the tools manifest with the selected source patterns. For C/D, use a separate
flat rlm_wiki_manifest.json for the wiki ledger's source paths. The wiki's nested
rlm_wiki_raw_sources_manifest.json is a different schema and cannot be passed to the
RLM directory-glob collector. If an existing profile points there, show a repair
proposal before changing it. Preserve the distinction between per-file ledger
summaries and the wiki's summary.md/bullets.md/deep.md concept layers.

## Apply and validate

Set AGENT_MEMORY_PROJECT_ROOT to the consumer project. Run scripts from this skill's
folder; never edit generated ledgers directly. Preview writes, apply the authorized
profile/manifest changes, then run inventory for each selected profile:

```bash
python3 scripts/inventory.py --profile project
python3 scripts/inventory.py --profile tools
```

Report configured files separately from cache coverage. If initial distillation is
in scope, use the distillation/curation modes, read complete sources and inject via
the scripts. For batch work, use scripts/swarm_run.py and its assets/jobs template;
retain the chosen engine/workers and audit coverage afterward. Dependency checks and
model calls are separate from core setup. If missing, name the prerequisite and do
not report that validation passed.

## Continue or resume

For B/D continue managing-vector-db setup inline, carrying root, selected scope,
namespace and prior answers. For C/D continue managing-obsidian-vaults setup inline.
Do not launch a child agent or ask the combination again. Provision only the chosen
layers. A user who later adds a layer gets an incremental preview, not a fresh reset.

When asked to provision retrieval guidance, describe only installed/configured layers
in the project's authoritative instructions. Preserve thin instruction bridges and
unrelated content; do not append duplicate guidance to every harness file.

Finish with the selected mode, actual files changed, profiles, measured coverage,
validation results and the next named skill mode. On cancel, stop the pending change
and state any earlier writes already applied; do not continue into other layers.
