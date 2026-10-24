# Obsidian Wiki Builder (obsidian-wiki-builder)

Transforms raw source files into structured LLM wiki concept nodes, cluster pages, indices, and tables of contents.

## Contents
- [Critical Constraints](#critical-constraints)
- [Dependencies](#dependencies)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Scope limitation: Default discovery searches project root only; obtain explicit confirmation for external directory scans.
- Concept merging: Multiple source documents describing the same entity must merge into a single authoritative node (`multi_source: true`).
- Every compiled concept page must include complete YAML frontmatter (concept, source, cluster, timestamp).

## Dependencies

Requires `pyyaml` and Python 3.8+. Wiki construction is standalone; RLM ledger and vector retrieval are optional.

## Quick start
```bash
# Build wiki nodes from all registered sources
python3 scripts/wiki_builder.py --wiki-root <path>

# Build from single named source
python3 scripts/wiki_builder.py --wiki-root <path> --source arch-docs

# Dry run inspection
python3 scripts/wiki_builder.py --wiki-root <path> --dry-run
```

## Workflow
1. **Source Registration**: Read sources from `meta/wiki_sources.json` or ingest new directories.
2. **Concept Extraction**: Parse source markdown files into atomic concepts and link relationships.
3. **Node Synthesis**: Generate concept pages (`{concept}.md`), cluster summaries (`_{cluster}.md`), and root index.
4. **Graph Linking**: Insert bidirectional `[[wikilinks]]` between related concept nodes.

## Verification
```bash
# Validate build execution with dry run
python3 scripts/wiki_builder.py --wiki-root <path> --dry-run

```

## References
- [wiki-builder-guide.md](wiki-builder-guide.md) - Pipeline stages, multi-source merging, and markdown schemas.
