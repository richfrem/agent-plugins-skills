---
name: obsidian-wiki-linter
description: Runs semantic health checks over the Obsidian LLM wiki using cheap LLM CLIs. Detects contradictions, missing concepts, stale articles, and connection candidates.
---

# Obsidian Wiki Linter (obsidian-wiki-linter)

Performs semantic health checks over the Obsidian LLM wiki to detect contradictions, knowledge gaps, and connection candidates.

## Contents
- [Critical Constraints](#critical-constraints)
- [Dependencies](#dependencies)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- The linter only writes analytical reports to `{wiki_root}/meta/lint-report.md`; never autonomously mutates concept nodes.
- Run semantic passes with low-cost mini/flash models (`gpt-5-mini`, `claude-haiku-4-5`).
- Limit checks to manageable node subsets on large wikis (`--sample 20`).

## Dependencies

Requires Python 3.8+ and at least one CLI installed: `copilot`, `claude`, or `gemini`.

## Quick start
```bash
# Run semantic health check with default engine
python3 plugins/obsidian-wiki-engine/scripts/lint_wiki.py --wiki-root <path>

# Sample specific number of nodes
python3 plugins/obsidian-wiki-engine/scripts/lint_wiki.py --wiki-root <path> --sample 30

# Dry run inspection
python3 plugins/obsidian-wiki-engine/scripts/lint_wiki.py --wiki-root <path> --dry-run
```

## Workflow
1. **Wiki Sampling**: Enumerate concept nodes and select target sample size.
2. **Diagnostic Analysis**: Check for contradictions, unlinked references, and thin nodes.
3. **Link Candidate Identification**: Recommend new `[[wikilinks]]` between semantically related concepts.
4. **Report Generation**: Write structured diagnostic findings to `{wiki_root}/meta/lint-report.md`.

## Verification
```bash
# Verify linter with dry run
python3 plugins/obsidian-wiki-engine/scripts/lint_wiki.py --wiki-root <path> --dry-run

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/obsidian-wiki-engine/skills/obsidian-wiki-linter --mode source
```

## References
- [wiki-linting-guide.md](references/wiki-linting-guide.md) - Report schemas, audit vs linting tradeoffs, and CLI flags.
