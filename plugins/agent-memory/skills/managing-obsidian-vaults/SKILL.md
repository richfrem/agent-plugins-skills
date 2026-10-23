---
name: managing-obsidian-vaults
plugin: agent-memory
description: >
  Interactive vault, wiki and Super-RAG setup in the main conversation. Use for
  "set up my wiki", "initialize the full knowledge stack" or combined RLM/vector/wiki setup.
  Manage Obsidian vaults and LLM wikis: initialize vaults, author Markdown and
  wikilinks, safely edit notes and Bases, create Canvas diagrams, traverse graphs,
  build concept wikis, distill summary/bullets/deep layers, query and lint knowledge.
allowed-tools: Bash, Read, Write
---

# Managing Obsidian Vaults

Read the matching workflow before acting. Run commands from this skill's folder.
Use explicit vault/wiki roots; set `AGENT_MEMORY_PROJECT_ROOT` for the consumer project.

## Contents

[Interaction](#interaction) · [Constraints](#constraints) · [Workflow](#workflow) · [Quick start](#quick-start) · [Verification](#verification)

## Interaction
Treat slash-invocation arguments as supplied requirements; do not ask for them again.

For vault/wiki setup, read [guided setup](references/interactive-setup.md); for combined layers,
read [Super-RAG setup](references/interactive-stack-setup.md), including when wiki is not selected.
Run the conversation here: reuse known choices, ask one unresolved question per turn, preview changes,
merge existing config and validate only selected layers. Continue sibling skill modes inline with shared
answers and scope; never launch a setup agent. Explicit note/query operations go directly to their modes.

## Constraints

- Never move raw source content. Confirm external directory scans before discovery.
- Preview initialization with `--validate-only`; preserve existing project configuration.
- Notes/Bases require lossless YAML, staged atomic writes, locking and concurrent-edit checks.
- Preserve Base view definitions. Validate Canvas nodes/edges and generate unique IDs.
- Distinguish links from embeds; graph traversal is read-only and respects cache invalidation.
- Merge multi-source concepts; preserve node frontmatter, raw-source manifests and
  `meta/agent-memory.json`. Wiki distillation emits `summary.md`, `bullets.md`, `deep.md`.
- Start queries at summary level, expand only as needed. Lint writes reports, not concept edits.
- Use configured low-cost cloud CLIs for wiki distillation/lint; never silently use local models.
- Vector retrieval is optional: explicitly supply its query script through
  `AGENT_MEMORY_VECTOR_QUERY`, or delegate to managing-vector-db if installed.

## Workflow

| Request | Read first |
|---|---|
| Initialize vault / register sources | [Setup](references/obsidian-init.md), [onboarding](references/obsidian-vault-onboarding-guide.md) |
| Markdown, wikilinks, embeds, callouts | [Markdown](references/obsidian-markdown-mastery.md) |
| Read/create/update/append notes | [Note operations](references/obsidian-vault-crud.md) |
| Read/update Base rows and cells | [Bases](references/obsidian-bases-manager.md) |
| Create/edit Canvas nodes and edges | [Canvas](references/obsidian-canvas-architect.md) |
| Forward/backlinks, orphans, graph | [Traversal](references/obsidian-graph-traversal.md) |
| Build/synthesize concept wiki | [Build](references/obsidian-wiki-builder.md), [guide](references/wiki-builder-guide.md) |
| Distill wiki's three summary layers | [Distill](references/obsidian-rlm-distiller.md), [guide](references/wiki-distillation-guide.md) |
| Query summaries, bullets or full nodes | [Query](references/obsidian-query-agent.md), [guide](references/wiki-query-guide.md) |
| Structural audit / semantic lint | [Lint](references/obsidian-wiki-linter.md), [guide](references/wiki-linting-guide.md) |

## Quick start

```bash
python3 scripts/init_vault.py --vault-root /path/to/vault --validate-only
python3 scripts/wiki_builder.py --wiki-root /path/to/wiki --dry-run
python3 scripts/distill_wiki.py --wiki-root /path/to/wiki --dry-run
python3 scripts/query_wiki.py --wiki-root /path/to/wiki "concept" --level summary
python3 scripts/lint_wiki.py --wiki-root /path/to/wiki --dry-run
```

## Verification

Validate changed notes, Canvas schemas and preserved frontmatter. Run structural
wiki audit with `python3 scripts/audit.py --wiki-root /path/to/wiki`.
Wiki build/query and vault operations work without RLM/vector sibling skills.
For combined setup, follow the interactive stack guide in this session after checking selected skills.
Install dependencies from this skill's lockfile only within the authorized setup scope.

[obsidian-bases-manager criteria](references/obsidian-bases-manager-acceptance-criteria.md) · [obsidian-bases-manager recovery](references/obsidian-bases-manager-fallback-tree.md) · [obsidian-canvas-architect criteria](references/obsidian-canvas-architect-acceptance-criteria.md) · [obsidian-canvas-architect recovery](references/obsidian-canvas-architect-fallback-tree.md) · [obsidian-graph-traversal criteria](references/obsidian-graph-traversal-acceptance-criteria.md) · [obsidian-graph-traversal recovery](references/obsidian-graph-traversal-fallback-tree.md) · [obsidian-init criteria](references/obsidian-init-acceptance-criteria.md) · [obsidian-init recovery](references/obsidian-init-fallback-tree.md) · [obsidian-markdown-mastery criteria](references/obsidian-markdown-mastery-acceptance-criteria.md) · [obsidian-markdown-mastery recovery](references/obsidian-markdown-mastery-fallback-tree.md) · [obsidian-vault-crud criteria](references/obsidian-vault-crud-acceptance-criteria.md) · [obsidian-vault-crud recovery](references/obsidian-vault-crud-fallback-tree.md)

Follow the [acceptance contract](references/acceptance-criteria.md); browse the [resource index](references/resource-index.md). Supplemental: [architecture-background](references/architecture-background.md) · [kepano-analysis-summary](references/kepano-analysis-summary.md) · [safety-learnings](references/safety-learnings.md) · [dependencies](references/dependencies.md) · [wiki-node.template](references/../assets/templates/wiki-node.template.md).
