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
python -c "import os; print('Found' if os.path.exists('.claude/commands/my-command.md') else 'Missing')"
```

**Automated validation script:**

```python
#!/usr/bin/env python
# validate_command.py
import sys
import os

command_file = sys.argv[1] if len(sys.argv) > 1 else ""

if not os.path.isfile(command_file):
    print(f"ERROR: File not found: {command_file}")
    sys.exit(1)

# Check .md extension
if not command_file.endswith(".md"):
    print("ERROR: File must have .md extension")
    sys.exit(1)

with open(command_file, 'r') as f:
    content = f.read()
    lines = content.splitlines()

# Validate YAML frontmatter if present
if lines and lines[0].strip() == "---":
    markers = content.count("\n---") + (1 if content.startswith("---") else 0)
    if markers < 2:
        print("ERROR: Invalid YAML frontmatter (need exactly 2 '---' markers)")
        sys.exit(1)
    print("✓ YAML frontmatter syntax valid")

# Check for empty file
if not content.strip():
    print("ERROR: File is empty")
    sys.exit(1)

print("✓ Command file structure valid")
```

### Level 2: Frontmatter Field Validation

**What to test:**
- Field types correct
- Values in valid ranges
- Required fields present (if any)

**Validation script:**
```python
#!/usr/bin/env python
# validate_frontmatter.py
import sys
import os
import re

command_file = sys.argv[1] if len(sys.argv) > 1 else ""

with open(command_file, 'r') as f:
    content = f.read()

# Extract YAML frontmatter
match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL | re.MULTILINE)
if not match:
    print("No frontmatter to validate")
    sys.exit(0)

frontmatter = match.group(1)

# Check 'model' field
model_match = re.search(r'^model:\s*(\S+)', frontmatter, re.MULTILINE)
if model_match:
    model = model_match.group(1)
    if model not in ("sonnet", "opus", "haiku"):
        print(f"ERROR: Invalid model '{model}' (must be sonnet, opus, or haiku)")
        sys.exit(1)
    print(f"✓ Model field valid: {model}")

# Check 'description' length
desc_match = re.search(r'^description:\s*(.*)', frontmatter, re.MULTILINE)
if desc_match:
    desc = desc_match.group(1)
    if len(desc) > 80:
        print(f"WARNING: Description length {len(desc)} (recommend < 60 chars)")
    else:
        print(f"✓ Description length acceptable: {len(desc)} chars")

print("✓ Frontmatter fields valid")
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
| Two args | `/cmd arg1 arg2` | $1 and $2 substituted |
| Extra args | `/cmd a b c d` | All captured or extras ignored appropriately |
| Special chars | `/cmd "arg with spaces"` | Quotes handled correctly |
| Empty arg | `/cmd ""` | Empty string handled |

**Test script:**

```python
#!/usr/bin/env python
# test_command_arguments.py
import sys

command = sys.argv[1] if len(sys.argv) > 1 else "unknown"

print(f"Testing argument handling for /{command}\n")

# Tests are documented here as manual steps for brevity, 
# but could be automated via subprocess calls.
print("Test 1: No arguments")
print(f"  Command: /{command}")
print("  Expected: [describe expected behavior]")
print("  Manual test required\n")

print("Test 2: Single argument")
print(f"  Command: /{command} test-value")
print("  Expected: 'test-value' appears in output\n")
```

### Level 5: File Reference Testing

**What to test:**
- @ syntax loads file contents
- Non-existent files handled
- Large files handled appropriately
- Multiple file references work

**Test procedure:**

```bash
# Create test files
echo "Test content" > /tmp/test-file.txt
echo "Second file" > /tmp/test-file-2.txt

# Test single file reference
> /my-command /tmp/test-file.txt
# Verify file content is read

# Test non-existent file
> /my-command /tmp/nonexistent.txt
# Verify graceful error handling

# Test multiple files
> /my-command /tmp/test-file.txt /tmp/test-file-2.txt
# Verify both files processed

# Test large file
dd if=/dev/zero of=/tmp/large-file.bin bs=1M count=100
> /my-command /tmp/large-file.bin
# Verify reasonable behavior (may truncate or warn)

# Cleanup
rm /tmp/test-file*.txt /tmp/large-file.bin
```

### Level 6: Bash Execution Testing

**What to test:**
- !` commands execute correctly
- Command output included in prompt
- Command failures handled
- Security: only allowed commands run

**Test procedure:**

```bash
# Create test command with bash execution
cat > .claude/commands/test-bash.md << 'EOF'
---
description: Test bash execution
allowed-tools: Bash(echo:*), Bash(date:*)
---

Current date: !`date`
Test output: !`echo "Hello from bash"`

Analysis of output above...
EOF

# Test in Claude Code
> /test-bash
# Verify:
# 1. Date appears correctly
# 2. Echo output appears
# 3. No errors in debug logs

# Test with disallowed command (should fail or be blocked)
cat > .claude/commands/test-forbidden.md << 'EOF'
---
description: Test forbidden command
allowed-tools: Bash(echo:*)
---

Trying forbidden: !`ls -la /`
EOF

> /test-forbidden
# Verify: Permission denied or appropriate error
```

### Level 7: Integration Testing

**What to test:**
- Commands work with other plugin components
- Commands interact correctly with each other
- State management works across invocations
- Workflow commands execute in sequence

**Test scenarios:**

**Scenario 1: Command + Hook Integration**

```bash
# Setup: Command that triggers a hook
# Test: Invoke command, verify hook executes

# Command: .claude/commands/risky-operation.md
# Hook: PreToolUse that validates the operation

> /risky-operation
# Verify: Hook executes and validates before command completes
```

**Scenario 2: Command Sequence**

```bash
# Setup: Multi-command workflow
> /workflow-init
# Verify: State file created

> /workflow-step2
# Verify: State file read, step 2 executes

> /workflow-complete
# Verify: State file cleaned up
```

**Scenario 3: Command + MCP Integration**

```bash
# Setup: Command uses MCP tools
# Test: Verify MCP server accessible

> /mcp-command
# Verify:
# 1. MCP server starts (if stdio)
# 2. Tool calls succeed
# 3. Results included in output
```

## Automated Testing Approaches

### Command Test Suite

Create a test suite script:

```bash
#!/bin/bash
# test-commands.sh - Command test suite

TEST_DIR=".claude/commands"
FAILED_TESTS=0

echo "Command Test Suite"
echo "=================="
echo

for cmd_file in "$TEST_DIR"/*.md; do
  cmd_name=$(basename "$cmd_file" .md)
  echo "Testing: $cmd_name"

  # Validate structure
  if python validate_command.py "$cmd_file"; then
    echo "  ✓ Structure valid"
  else
    echo "  ✗ Structure invalid"
    ((FAILED_TESTS++))
  fi
  # Validate frontmatter
  if python validate_frontmatter.py "$cmd_file"; then
    echo "  ✓ Frontmatter valid"
  else
    echo "  ✗ Frontmatter invalid"
    ((FAILED_TESTS++))
  fi

  echo
done

echo "=================="
echo "Tests complete"
echo "Failed: $FAILED_TESTS"

exit $FAILED_TESTS
```

### Pre-Commit Hook

Validate commands before committing:

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Validating commands..."

COMMANDS_CHANGED=$(git diff --cached --name-only | grep "\.claude/commands/.*\.md")

if [ -z "$COMMANDS_CHANGED" ]; then
  echo "No commands changed"
  exit 0
fi

for cmd in $COMMANDS_CHANGED; do
  echo "Checking: $cmd"
  if ! python scripts/validate_command.py "$cmd"; then
    echo "ERROR: Command validation failed: $cmd"
    exit 1
  fi
done

echo "✓ All commands valid"
```

### Continuous Testing

Test commands in CI/CD:

```yaml
# .github/workflows/test-commands.yml
name: Test Commands

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Validate command structure
        run: |
          for cmd in .claude/commands/*.md; do
            python scripts/validate_command.py "$cmd"
          done
      - name: Validate frontmatter
        run: |
          for cmd in .claude/commands/*.md; do
            python scripts/validate_frontmatter.py "$cmd"
          done

      - name: Check for TODOs
        run: |
          if grep -r "TODO" .claude/commands/; then
            echo "ERROR: TODOs found in commands"
            exit 1
          fi
```

## Edge Case Testing

### Test Edge Cases

**Empty arguments:**
```bash
> /cmd ""
> /cmd '' ''
```

**Special characters:**
```bash
> /cmd "arg with spaces"
> /cmd arg-with-dashes
> /cmd arg_with_underscores
> /cmd arg/with/slashes
> /cmd 'arg with "quotes"'
```

**Long arguments:**
```bash
> /cmd $(python -c "print('a' * 10000)")
```

**Unusual file paths:**
```bash
> /cmd ./file
> /cmd ../file
> /cmd ~/file
> /cmd "/path with spaces/file"
```

**Bash command edge cases:**
```markdown
# Commands that might fail
!`exit 1`
!`false`
!`command-that-does-not-exist`

# Commands with special output
!`echo ""`
!`cat /dev/null`
!`yes | head -n 1000000`
```

## Performance Testing

### Response Time Testing

```bash
#!/bin/bash
# test_command_performance.py
# (Conversion to Python-based performance metrics)
# Acceptable threshold: < 3 seconds for fast commands
```

### Resource Usage Testing

```bash
# Monitor Claude Code during command execution
# In terminal 1:
claude --debug

# In terminal 2:
watch -n 1 'ps aux | grep claude'

# Execute command and observe:
# - Memory usage
# - CPU usage
# - Process count
```

## User Experience Testing

### Usability Checklist

- [ ] Command name is intuitive
- [ ] Description is clear in `/help`
- [ ] Arguments are well-documented
- [ ] Error messages are helpful
- [ ] Output is formatted readably
- [ ] Long-running commands show progress
- [ ] Results are actionable
- [ ] Edge cases have good UX

### User Acceptance Testing

Recruit testers:

```markdown
# Testing Guide for Beta Testers

## Command: /my-new-command

### Test Scenarios

1. **Basic usage:**
   - Run: `/my-new-command`
   - Expected: [describe]
   - Rate clarity: 1-5

2. **With arguments:**
   - Run: `/my-new-command arg1 arg2`
   - Expected: [describe]
   - Rate usefulness: 1-5

3. **Error case:**
   - Run: `/my-new-command invalid-input`
   - Expected: Helpful error message
   - Rate error message: 1-5

### Feedback Questions

1. Was the command easy to understand?
2. Did the output meet your expectations?
3. What would you change?
4. Would you use this command regularly?
```

## Testing Checklist

Before releasing a command:

### Structure
- [ ] File in correct location
- [ ] Correct .md extension
- [ ] Valid YAML frontmatter (if present)
- [ ] Markdown syntax correct

### Functionality
- [ ] Command appears in `/help`
- [ ] Description is clear
- [ ] Command executes without errors
- [ ] Arguments work as expected
- [ ] File references work
- [ ] Bash execution works (if used)

### Edge Cases
- [ ] Missing arguments handled
- [ ] Invalid arguments detected
- [ ] Non-existent files handled
- [ ] Special characters work
- [ ] Long inputs handled

### Integration
- [ ] Works with other commands
- [ ] Works with hooks (if applicable)
- [ ] Works with MCP (if applicable)
- [ ] State management works

### Quality
- [ ] Performance acceptable
- [ ] No security issues
- [ ] Error messages helpful
- [ ] Output formatted well
- [ ] Documentation complete

### Distribution
- [ ] Tested by others
- [ ] Feedback incorporated
- [ ] README updated
- [ ] Examples provided

## Debugging Failed Tests

### Common Issues and Solutions

**Issue: Command not appearing in /help**

```bash
# Check file location
ls -la .claude/commands/my-command.md

# Check permissions
chmod 644 .claude/commands/my-command.md

# Check syntax
head -n 20 .claude/commands/my-command.md

# Restart Claude Code
claude --debug
```

**Issue: Arguments not substituting**

```bash
# Verify syntax
grep '\$1' .claude/commands/my-command.md
grep '\$ARGUMENTS' .claude/commands/my-command.md

# Test with simple command first
echo "Test: \$1 and \$2" > .claude/commands/test-args.md
```

**Issue: Bash commands not executing**

```bash
# Check allowed-tools
grep "allowed-tools" .claude/commands/my-command.md

# Verify command syntax
grep '!\`' .claude/commands/my-command.md

# Test command manually
date
echo "test"
```

**Issue: File references not working**

```bash
# Check @ syntax
grep '@' .claude/commands/my-command.md

# Verify file exists
ls -la /path/to/referenced/file

# Check permissions
chmod 644 /path/to/referenced/file
```

## Best Practices

1. **Test early, test often**: Validate as you develop
2. **Automate validation**: Use scripts for repeatable checks
3. **Test edge cases**: Don't just test the happy path
4. **Get feedback**: Have others test before wide release
5. **Document tests**: Keep test scenarios for regression testing
6. **Monitor in production**: Watch for issues after release
7. **Iterate**: Improve based on real usage data
