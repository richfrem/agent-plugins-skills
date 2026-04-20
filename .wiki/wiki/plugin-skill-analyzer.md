---
concept: plugin-skill-analyzer
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/analyze-plugin/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.711369+00:00
cluster: patterns
content_hash: d163225f31f45cd2
---

# Plugin & Skill Analyzer

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: analyze-plugin
description: >
  Systematically analyze agent plugins and skills to extract design patterns, architectural
  decisions, and reusable techniques. Trigger with "analyze this plugin", "mine patterns from",
  "review plugin structure", "extract learnings from", "what patterns does this plugin use",
  "check if this plugin is well-structured", "validate plugin compliance", or when examining
  any plugin or skill collection to understand its design. Use this skill even when the user
  just says "look at this plugin" or "tell me how this is structured."
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `../../requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Plugin & Skill Analyzer

Perform deep structural and content analysis on agent plugins and skills. Extract reusable
patterns that feed the virtuous cycle of continuous improvement.

## Two Analysis Modes

### Single Plugin Mode
Deep-dive into one plugin. Use when you want to fully understand a plugin's architecture.

### Comparative Mode
Analyze multiple plugins side-by-side. Use when looking for common patterns across a collection.

## Analysis Framework

Execute these phases sequentially. Do not skip phases.

### Phase 0: Quick Compliance Pre-Check

Before deep analysis, run a rapid compliance scan to surface blockers:

**Manifest check:**
```bash
# plugin.json must be in .claude-plugin/ (not root)
ls .claude-plugin/plugin.json && jq . .claude-plugin/plugin.json
```
- `name` present and kebab-case (no spaces, no uppercase)?
- `version` follows semver (X.Y.Z) if present?
- No unknown fields causing warnings?

**Structure check:**
- Component dirs (`commands/`, `agents/`, `skills/`, `hooks/`) at plugin ROOT (not inside `.claude-plugin/`)?
- All file names use kebab-case?
- `SKILL.md` (not `README.md`) inside each skill directory?

**Security scan:**
```bash
# Hardcoded credentials
grep -rn "password\|api_key\|secret" --include="*.md" --include="*.json" --include="*.sh" .

# Hardcoded paths (should use ${CLAUDE_PLUGIN_ROOT})
grep -rn "/Users/\|/home/" --include="*.json" --include="*.sh" .
```

Report Phase 0 findings before proceeding. If CRITICAL issues found (invalid JSON,
hardcoded credentials, missing required fields), flag them prominently in the final report.

### Phase 1: Inventory

Run the deterministic inventory script first:
```bash
python "scripts/inventory_plugin.py" --path <plugin-dir> --format json
```

If the script is unavailable, manually enumerate:
1. Walk the directory tree
2. Classify every file by type:
   - `SKILL.md` → Skill definition
   - `commands/*.md` → Command definition
   - `references/*.md` → Reference material (progressive disclosure)
   - `scripts/*.py` → Executable scripts
   - `README.md` → Plugin documentation
   - `plugin.json` → Plugin manifest
   - `*.json` → Configuration (MCP, hooks, etc.)
   - `*.yaml` / `*.yml` → Pipeline/config data
   - `*.html` → Artifact templates
   - `*.mmd` → Architecture diagrams
   - Other → ./assets/misc

3. Record for each file: path, type, line count, byte size
4. Output a structured inventory as a markdown checklist with one checkbox per file

### Phase 2: Structure Analysis

Evaluate the plugin's architectural decisions:

| Dimension | What to Look For |
|-----------|-----------------|
| **Layout** | How are skills/commands/references organized? Flat vs nested? |
| **Progressive Disclosure** | Is SKILL.md lean (<500 lines) with depth in `references/`? |
| **Component Ratios** | Skills vs commands vs scripts — what's the balance? |
| **Naming Patterns** | Are names descriptive? Follow kebab-case? Use gerund form? |
| **README Quality** | Does it have a file tree? Usage examples? Architecture diagram? |
| **Standalone vs 

*(content truncated)*

## See Also

- [[agent-plugin-analyzer]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[agent-plugin-analyzer---architecture]]
- [[red-team-review-agent-plugin-analyzer-meta-plugin]]
- [[round-2-red-team-review-refactored-agent-plugin-analyzer]]
- [[round-3-red-team-review-agent-plugin-analyzer-v3]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/analyze-plugin/SKILL.md`
- **Indexed:** 2026-04-17T06:42:09.711369+00:00
