---
concept: command-testing-strategies
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-command/references/testing-strategies.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.827496+00:00
cluster: test
content_hash: e6ccf78d85c23bc5
---

# Command Testing Strategies

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Command Testing Strategies

Comprehensive strategies for testing slash commands before deployment and distribution.

## Overview

Testing commands ensures they work correctly, handle edge cases, and provide good user experience. A systematic testing approach catches issues early and builds confidence in command reliability.

## Testing Levels

### Level 1: Syntax and Structure Validation

**What to test:**
- YAML frontmatter syntax
- Markdown format
- File location and naming

**How to test:**

```bash
# Validate YAML frontmatter
head -n 20 .claude/commands/my-command.md | grep -A 10 "^---"

# Check for closing frontmatter marker
head -n 20 .claude/commands/my-command.md | grep -c "^---" # Should be 2

# Verify file has .md extension
ls .claude/commands/*.md

# Check file is in correct location
test -f .claude/commands/my-command.md && echo "Found" || echo "Missing"
```

**Automated validation script:**

```bash
#!/bin/bash
# validate-command.sh

COMMAND_FILE="$1"

if [ ! -f "$COMMAND_FILE" ]; then
  echo "ERROR: File not found: $COMMAND_FILE"
  exit 1
fi

# Check .md extension
if [[ ! "$COMMAND_FILE" =~ \.md$ ]]; then
  echo "ERROR: File must have .md extension"
  exit 1
fi

# Validate YAML frontmatter if present
if head -n 1 "$COMMAND_FILE" | grep -q "^---"; then
  # Count frontmatter markers
  MARKERS=$(head -n 50 "$COMMAND_FILE" | grep -c "^---")
  if [ "$MARKERS" -ne 2 ]; then
    echo "ERROR: Invalid YAML frontmatter (need exactly 2 '---' markers)"
    exit 1
  fi
  echo "✓ YAML frontmatter syntax valid"
fi

# Check for empty file
if [ ! -s "$COMMAND_FILE" ]; then
  echo "ERROR: File is empty"
  exit 1
fi

echo "✓ Command file structure valid"
```

### Level 2: Frontmatter Field Validation

**What to test:**
- Field types correct
- Values in valid ranges
- Required fields present (if any)

**Validation script:**

```bash
#!/bin/bash
# validate-frontmatter.sh

COMMAND_FILE="$1"

# Extract YAML frontmatter
FRONTMATTER=$(sed -n '/^---$/,/^---$/p' "$COMMAND_FILE" | sed '1d;$d')

if [ -z "$FRONTMATTER" ]; then
  echo "No frontmatter to validate"
  exit 0
fi

# Check 'model' field if present
if echo "$FRONTMATTER" | grep -q "^model:"; then
  MODEL=$(echo "$FRONTMATTER" | grep "^model:" | cut -d: -f2 | tr -d ' ')
  if ! echo "sonnet opus haiku" | grep -qw "$MODEL"; then
    echo "ERROR: Invalid model '$MODEL' (must be sonnet, opus, or haiku)"
    exit 1
  fi
  echo "✓ Model field valid: $MODEL"
fi

# Check 'allowed-tools' field format
if echo "$FRONTMATTER" | grep -q "^allowed-tools:"; then
  echo "✓ allowed-tools field present"
  # Could add more sophisticated validation here
fi

# Check 'description' length
if echo "$FRONTMATTER" | grep -q "^description:"; then
  DESC=$(echo "$FRONTMATTER" | grep "^description:" | cut -d: -f2-)
  LENGTH=${#DESC}
  if [ "$LENGTH" -gt 80 ]; then
    echo "WARNING: Description length $LENGTH (recommend < 60 chars)"
  else
    echo "✓ Description length acceptable: $LENGTH chars"
  fi
fi

echo "✓ Frontmatter fields valid"
```

### Level 3: Manual Command Invocation

**What to test:**
- Command appears in `/help`
- Command executes without errors
- Output is as expected

**Test procedure:**

```bash
# 1. Start Claude Code
claude --debug

# 2. Check command appears in help
> /help
# Look for your command in the list

# 3. Invoke command without arguments
> /my-command
# Check for reasonable error or behavior

# 4. Invoke with valid arguments
> /my-command arg1 arg2
# Verify expected behavior

# 5. Check debug logs
tail -f ~/.claude/debug-logs/latest
# Look for errors or warnings
```

### Level 4: Argument Testing

**What to test:**
- Positional arguments work ($1, $2, etc.)
- $ARGUMENTS captures all arguments
- Missing arguments handled gracefully
- Invalid arguments detected

**Test matrix:**

| Test Case | Command | Expected Result |
|-----------|---------|-----------------|
| No args | `/cmd` | Graceful handling or useful message |
| One arg | `/cmd arg1` | $1 substituted correctly |
| Two arg

*(content truncated)*

## See Also

- [[os-init-command]]
- [[os-loop-command]]
- [[os-memory-command]]
- [[testing-anti-patterns]]
- [[chained-command-invocation-via-offer-next-steps-blocks]]
- [[sub-action-command-multiplexing]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-command/references/testing-strategies.md`
- **Indexed:** 2026-04-17T06:42:09.827496+00:00
