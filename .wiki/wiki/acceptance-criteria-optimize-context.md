---
concept: acceptance-criteria-optimize-context
source: plugin-code
source_file: claude-cli/skills/optimize-context/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.538801+00:00
cluster: skill
content_hash: 81cec7823d902d45
---

# Acceptance Criteria: optimize-context

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: optimize-context

## Structural Requirements

| Criterion | Pass condition |
|---|---|
| SKILL.md present | File exists at `skills/optimize-context/SKILL.md` |
| SKILL.md frontmatter | `name`, `description` (≤ 1024 chars), `allowed-tools` all present |
| Python script present | `scripts/optimize_context.py` exists at plugin root |
| Python-only | No `.sh` scripts anywhere in this skill |
| Evals present | `evals/evals.json` with ≥ 2 positive and ≥ 2 negative cases |
| Schema compliance | All eval entries use `should_trigger: true/false` (not `expected_behavior`) |
| Acceptance criteria | This file exists at `references/acceptance-criteria.md` |

## Behavioural Requirements

| Criterion | Pass condition |
|---|---|
| Canonical preference | Plugin-installed skills always win; `.agents/skills/` copies are suppressed |
| Idempotent patching | Running twice does not add duplicate lines to `.claudeignore` |
| Dry-run safety | `--dry-run` flag never writes to disk |
| Managed block header | `.claudeignore` additions are enclosed in the sentinel comment block |
| Relative paths | Suppression entries written as relative paths from project root |
| Exit codes | 0 = clean, 1 = error, 2 = dry-run with duplicates found |
| No silent errors | Python tracebacks are always surfaced to the user |

## Routing Accuracy Requirements (evaluated by os-eval-runner)

- **Positive triggers**: phrases containing "optimize claude context",
  "deduplicate skills", "fix duplicate skill definitions", "why are my skills
  loading twice", "remove duplicate context", "clean up claudeignore"
- **Negative triggers**: "create a new skill", "set up .claude directory",
  "install plugin", "improve skill routing" — these must NOT trigger
  optimize-context

## Script Quality Requirements

The Python script must conform to project coding conventions:

- Module-level docstring with Purpose, Layer, Usage Examples, Key Functions,
  Script Dependencies, Consumed by sections
- All public functions have Google-style docstrings (Args, Returns, Raises)
- `main()` entry point gated by `if __name__ == "__main__"`
- No hardcoded absolute paths (`/Users/...`)
- `pathlib.Path` used for all filesystem operations
- No third-party dependencies beyond Python stdlib


## See Also

- [[acceptance-criteria-context-bundler]]
- [[acceptance-criteria-context-bundler]]
- [[acceptance-criteria-adr-manager]]
- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-guide]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `claude-cli/skills/optimize-context/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:09.538801+00:00
