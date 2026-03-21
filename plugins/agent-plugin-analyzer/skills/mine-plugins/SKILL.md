---
user-invocable: true
argument-hint: "[path-to-plugin-or-directory]"
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---

# Mine Plugins

Run the full analysis pipeline on a plugin or collection of plugins. This is the one-shot command for the virtuous cycle.

## What This Command Does

1. **Inventory** — Enumerate and classify every file in the target
2. **Analyze** — Deep structural and content analysis using the `analyze-plugin` skill
3. **Extract** — Identify all design patterns (known and novel)
4. **Synthesize** — Generate improvement recommendations using the `synthesize-learnings` skill
5. **Report** — Produce a comprehensive analysis report

## Usage

```
/mine-plugins <path-to-plugin-or-directory>
```

### Examples

```
# Analyze a single plugin
/mine-plugins claude-knowledgework-plugins/sales

# Analyze an entire collection
/mine-plugins claude-knowledgework-plugins/

# Analyze our own plugins
/mine-plugins plugins/legacy\ system
```

## Execution Steps

### Step 1: Determine Scope

Check if `$ARGUMENTS` points to:
- A **single plugin** (contains `./plugin.json` or `skills/` directory) → Single Plugin Mode
- A **directory of plugins** (contains multiple subdirectories with plugins) → Comparative Mode
- A **single skill** (contains `SKILL.md`) → Single Skill Mode

### Step 2: Run Inventory

For each plugin in scope, run:
```bash
python3 "scripts/inventory_plugin.py" --path "$ARGUMENTS" --format json
```

> **Security scanning is enabled by default.** The inventory script runs credential detection,
> network call detection, and environment variable access checks on every script file.
> Pass `--no-security` only if you want to suppress the security scan output.

If the script fails, perform manual inventory per the `analyze-plugin` skill Phase 1.

### Step 3: Deep Analysis

For each plugin, execute the full 6-phase `analyze-plugin` framework:
1. Inventory (done)
2. Structure Analysis
3. Content Analysis — **read every file completely**, do not skip or summarize prematurely
4. Pattern Extraction
5. Anti-Pattern Detection
6. Synthesis

### Step 4: Cross-Plugin Synthesis

If analyzing multiple plugins, identify:
- Universal patterns (in all plugins)
- Common patterns (in most)
- Unique innovations (in one — with attribution)
- Consistency gaps

### Step 5: Generate Improvement Recommendations

Invoke the `synthesize-learnings` skill to produce targeted recommendations for:
1. `agent-scaffolders` — template and scaffold improvements
2. `agent-skill-open-specifications` — standards and spec updates
3. `agent-plugin-analyzer` — self-improvement of this analyzer
4. Domain plugins (e.g., `legacy system`) — transferable patterns for legacy code analysis

### Step 6: Deliver Report

Present the full analysis as a structured markdown artifact. Include:
- Executive summary
- Per-plugin analysis summaries
- Pattern catalog additions
- Prioritized improvement recommendations
- Next steps
