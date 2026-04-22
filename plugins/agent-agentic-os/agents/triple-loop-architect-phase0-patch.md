<!-- PATCH: Replacement for ## Phase 0: Resolve & Prepare in triple-loop-architect.md -->
<!-- Replace from the "## Phase 0: Resolve & Prepare" heading through the end of "### 0.3 Check evals state" block. -->

## Phase 0: Resolve & Prepare

### 0.0 Check for Intake Config

```bash
APS_ROOT=$(pwd)
if [ -f "$APS_ROOT/improvement/run-config.json" ]; then
  echo "[Architect] Intake config found — reading variables from improvement/run-config.json"
  TARGET_SKILL=$(jq -r '.target_skill' $APS_ROOT/improvement/run-config.json)
  PARTITION_ID=$(jq -r '.partition_id' $APS_ROOT/improvement/run-config.json)
  RUN_DEPTH=$(jq -r '.run_depth.label' $APS_ROOT/improvement/run-config.json)
  DISPATCH=$(jq -r '.dispatch_strategy' $APS_ROOT/improvement/run-config.json)

  # Derive PLUGIN_NAME and SKILL_NAME from target_skill (format: plugin-name/skills/skill-name)
  PLUGIN_NAME=$(echo "$TARGET_SKILL" | cut -d'/' -f1)
  SKILL_NAME=$(echo "$TARGET_SKILL" | cut -d'/' -f3)
  SKILL_PATH="plugins/$PLUGIN_NAME/skills/$SKILL_NAME"
  LAB_PATH="$HOME/Projects/test-${SKILL_NAME}-eval"
  SKILL_EVAL_SOURCE="$LAB_PATH/.agents/skills/os-eval-runner"

  echo "Config-sourced variables:"
  echo "  PLUGIN_NAME=$PLUGIN_NAME  SKILL_NAME=$SKILL_NAME"
  echo "  SKILL_PATH=$SKILL_PATH"
  echo "  LAB_PATH=$LAB_PATH"
  echo "  RUN_DEPTH=$RUN_DEPTH  DISPATCH=$DISPATCH"
  echo "Skipping steps 0.1 and 0.2 — variables set from intake config."
  # Jump to 0.3
else
  echo "[Architect] No intake config found — proceeding with user-prompted variable resolution (steps 0.1 and 0.2)"
fi
```

### 0.1 Resolve the skill path

> Skip this step if variables were set in 0.0 from intake config.

**If the user's prompt explicitly names both the skill AND the plugin, skip this step entirely.**
Set `SKILL_NAME` and `PLUGIN_NAME` directly from what the user provided and go to 0.2.

Only run the find if the skill name alone was given (plugin unknown):
```bash
find plugins -type d -name "<skill-name>" | grep "skills/"
# Example result: plugins/mermaid-to-png/skills/convert-mermaid
```
If multiple matches: show them and ask which one. If zero: "Skill not found — give me the full path."

### 0.2 Compute key variables from the find result

> Skip this step if variables were set in 0.0 from intake config.

The find result has the form: `plugins/<plugin-folder>/skills/<skill-folder>`

Parse it explicitly — do NOT use "plugins" as the PLUGIN_NAME:
```bash
APS_ROOT=$(pwd)

# From find result: plugins/mermaid-to-png/skills/convert-mermaid
FIND_RESULT="plugins/mermaid-to-png/skills/convert-mermaid"   # substitute actual result

# Extract the 2nd path segment (the plugin folder, NOT "plugins")
PLUGIN_NAME=$(echo "$FIND_RESULT" | cut -d'/' -f2)            # → mermaid-to-png
SKILL_NAME=$(echo "$FIND_RESULT" | cut -d'/' -f4)             # → convert-mermaid
SKILL_PATH="plugins/$PLUGIN_NAME/skills/$SKILL_NAME"           # → plugins/mermaid-to-png/skills/convert-mermaid

LAB_PATH="$HOME/Projects/test-${SKILL_NAME}-eval"
SKILL_EVAL_SOURCE="$LAB_PATH/.agents/skills/os-eval-runner"

# Confirm before proceeding:
echo "PLUGIN_NAME=$PLUGIN_NAME  SKILL_NAME=$SKILL_NAME"
echo "SKILL_PATH=$SKILL_PATH"
echo "LAB_PATH=$LAB_PATH"
echo "SKILL_EVAL_SOURCE=$SKILL_EVAL_SOURCE"
```

> ⚠️ `PLUGIN_NAME` is the **plugin folder** (e.g. `mermaid-to-png`), NOT the word `plugins`.
> Always double-check the echo output before continuing.

### 0.3 Check evals state
```bash
ls $APS_ROOT/$SKILL_PATH/evals/evals.json 2>/dev/null && echo "exists" || echo "missing"
```

### 0.4 Seed Lab with Gotchas and Invariants

Run AFTER the lab is initialized and plugin files are copied (after Phase 1.2).

```bash
# Seed gotchas from intake config (if any)
SEED_COUNT=$(jq '.seed_gotchas | length' $APS_ROOT/improvement/run-config.json 2>/dev/null || echo 0)
if [ "$SEED_COUNT" -gt 0 ]; then
  echo "## Seed Gotchas (human_authored — from intake)" > $LAB_PATH/gotchas.md
  jq -r '.seed_gotchas[]' $APS_ROOT/improvement/run-config.json | while read gotcha; do
    echo "- $gotcha (discovery_source: human_authored)" >> $LAB_PATH/gotchas.md
  done
  echo "[Architect] Seeded $SEED_COUNT gotchas into $LAB_PATH/gotchas.md"
else
  echo "[Architect] No seed gotchas — gotchas.md will be created by orchestrator on first circuit-break exit"
fi

# Write invariants.json into lab for orchestrator to reference
cat > $LAB_PATH/invariants.json << 'INVARIANTS_EOF'
{
  "single_active_executor": "At most one RUNNING agent per partition_id",
  "no_unvalidated_promotion": "PROMOTING only if previously VALIDATING AND validation_passed == true",
  "execution_freeze": "No proposals accepted when circuit_break_scope is set in context/os-state.json",
  "memory_bounding": "Memory store size must be <= MAX_SIZE before GC triggers",
  "lease_sovereignty": "Only confirmed lease_owner_id may extend an active lease",
  "transition_triggered_learning": "Every CIRCUIT_BREAK or DEGRADED exit MUST emit gotcha to target SKILL.md before RECOVERY is permitted"
}
INVARIANTS_EOF
echo "[Architect] Invariants written to $LAB_PATH/invariants.json"
```
