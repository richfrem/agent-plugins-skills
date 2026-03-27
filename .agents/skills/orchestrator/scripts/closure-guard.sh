#!/bin/bash

# Agent Loops: Closure Guard (Stop Hook)
# Prevents premature session exit when a learning loop is active.
# Inspired by the Ralph Loop stop-hook pattern.
#
# If an active loop state file exists and closure hasn't been completed,
# this hook blocks exit and reminds the agent to run the closure sequence.

set -euo pipefail

# Read hook input from stdin
HOOK_INPUT=$(cat)

# Check for active loop state file
LOOP_STATE_FILE=".claude/agent-loop-state.local.md"

if [[ ! -f "$LOOP_STATE_FILE" ]]; then
  # No active loop — allow exit
  exit 0
fi

# Parse frontmatter
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$LOOP_STATE_FILE")
ITERATION=$(echo "$FRONTMATTER" | grep '^iteration:' | sed 's/iteration: *//')
MAX_ITERATIONS=$(echo "$FRONTMATTER" | grep '^max_iterations:' | sed 's/max_iterations: *//')
CLOSURE_DONE=$(echo "$FRONTMATTER" | grep '^closure_done:' | sed 's/closure_done: *//')
PATTERN=$(echo "$FRONTMATTER" | grep '^pattern:' | sed 's/pattern: *//')

# If closure is already done, allow exit
if [[ "$CLOSURE_DONE" == "true" ]]; then
  rm "$LOOP_STATE_FILE"
  exit 0
fi

# Validate iteration counter
if [[ ! "$ITERATION" =~ ^[0-9]+$ ]]; then
  jq -n \
    --arg msg "⚠️  Agent loop: State file corrupted (iteration: '$ITERATION'). Please fix the state file." \
    '{
      "decision": "block",
      "reason": "Corrupted state file.",
      "systemMessage": $msg
    }'
  exit 0
fi

# Check max iterations
if [[ "$MAX_ITERATIONS" =~ ^[0-9]+$ ]] && [[ $MAX_ITERATIONS -gt 0 ]] && [[ $ITERATION -ge $MAX_ITERATIONS ]]; then
  jq -n \
    --arg msg "🛑 Agent loop: Max iterations ($MAX_ITERATIONS) reached. Forcing closure.\n\nYou MUST still complete the closure sequence:\n1. Seal (bundle session artifacts)\n2. Persist (append session traces)\n3. Retrospective (analyze what went right/wrong)\n4. Set closure_done: true in '$LOOP_STATE_FILE'" \
    '{
      "decision": "block",
      "reason": "Max iterations reached.",
      "systemMessage": $msg
    }'
  exit 0
fi

# Closure not done — block exit
PROMPT_TEXT=$(awk '/^---$/{i++; next} i>=2' "$LOOP_STATE_FILE")

# Update iteration
NEXT_ITERATION=$((ITERATION + 1))
TEMP_FILE="${LOOP_STATE_FILE}.tmp.$$"
sed "s/^iteration: .*/iteration: $NEXT_ITERATION/" "$LOOP_STATE_FILE" > "$TEMP_FILE"
mv "$TEMP_FILE" "$LOOP_STATE_FILE"

jq -n \
  --arg prompt "$PROMPT_TEXT" \
  --arg msg "🔄 Agent loop iteration $NEXT_ITERATION ($PATTERN) | Closure NOT complete — you must Seal → Persist → Retrospective before exiting." \
  '{
    "decision": "block",
    "reason": $prompt,
    "systemMessage": $msg
  }'

exit 0
