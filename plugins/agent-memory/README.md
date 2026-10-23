# Agent Memory & Knowledge

Four self-contained skills for filesystem memory, summary ledgers, vector retrieval
and Obsidian knowledge. Version 2 consolidates the former agent-memory and
obsidian-wiki-engine plugins.

| Skill | Use it for | Dependencies |
|---|---|---|
| [managing-rlm-cache](skills/managing-rlm-cache/SKILL.md) | Configure, search, distill, audit and prune summary ledgers | Standard library for lookup/injection; PyYAML for batch jobs; selected CLI/service for model calls |
| [managing-vector-db](skills/managing-vector-db/SKILL.md) | Configure, ingest, query, audit and clean ChromaDB indexes | Its own requirements.in/txt, Python SQLite runtime; embeddings may need model downloads |
| [managing-obsidian-vaults](skills/managing-obsidian-vaults/SKILL.md) | Notes, Bases, Canvas, Markdown, graphs, wiki build/distill/query/lint | Its own requirements.txt; chosen CLI for semantic distillation/lint |
| [memory-management](skills/memory-management/SKILL.md) | Filesystem memory and session continuity | Standard library and filesystem tools |

Each skill owns its executable scripts, references and assets as real source files.
There is no materialization step for this plugin. Interactive setup and operation run directly in the main conversation through
the owning skills. Dedicated agents and command wrappers are removed.

## Target layout

```text
agent-memory/
  ├── references/                  # plugin governance
  └── skills/
      ├── managing-rlm-cache/         # scripts, references, assets, evals, dependencies
      ├── managing-vector-db/         # scripts, references, assets, evals, dependencies
      ├── managing-obsidian-vaults/   # scripts, references, assets, evals, dependencies
      └── memory-management/         # scripts, references and evals
```

## Install

From a checkout of this repository:

```bash
apm install ./plugins/agent-memory --target claude,copilot,codex,antigravity
```

Select one skill independently when the other layers are unnecessary:

```bash
apm install ./plugins/agent-memory --skill managing-obsidian-vaults --target claude,copilot,codex,antigravity
```

No installation or model execution occurs merely by reading the skills. Run scripts
from the owning skill folder and set `AGENT_MEMORY_PROJECT_ROOT` to the consumer
project, especially with global installs. Scripts otherwise discover the project
from the caller's working directory, including Git worktrees.

## Profiles and interoperability

Existing project data remains unchanged: `.agent/learning/rlm_profiles.json`,
`vector_profiles.json`, `rlm_wiki_raw_sources_manifest.json`, the configured caches,
and wiki `meta/agent-memory.json`. Read and merge existing configuration.

RLM ledgers retain their one-summary-per-file format. Wiki distillation separately
retains `summary.md`, `bullets.md` and `deep.md`; its engine is co-located with the wiki
linter so a wiki-only install works. RLM routes wiki requests to the Obsidian skill
by name. Optional vector enrichment reads consumer cache data without importing RLM.
For wiki semantic retrieval, explicitly set `AGENT_MEMORY_VECTOR_QUERY` to the
selected vector skill's query.py; otherwise wiki lookup uses its local search.

The skills conduct their own setup interviews. managing-obsidian-vaults also
provides a combined-stack conversation for any selected combination, including
RLM+vector without a wiki. Existing answers and authorizations carry across skill
modes in the main session; no layer is forced on.

## Migration

The former six rlm-* workflows are modes of managing-rlm-cache; six vector-db-*
workflows are modes of managing-vector-db; all ten obsidian-* workflows are modes
of managing-obsidian-vaults. Each former workflow is preserved in the owning
skill's references folder; evals/legacy preserves original evaluation evidence.
Former agent workflows now run directly in the skills; old agent names and command
wrappers are retired. Invoke /managing-rlm-cache, /managing-vector-db or
/managing-obsidian-vaults with the request and its arguments. Consumer skill selections
must use those names. Runtime reinstall and retirement of deployed legacy folders are separate
operations after source review.

## Verification

From the repository root: `python3 -m pytest plugins/agent-memory -q`.
The parser/model tests moved byte-for-byte with their scripts. The memory-layer test
now lives with memory-management; its repository locator is independently adapted
for relocation while its assertions remain unchanged. Skill audits
and isolated runtime probes supplement these tests; static eval preservation alone
does not establish routing accuracy.
