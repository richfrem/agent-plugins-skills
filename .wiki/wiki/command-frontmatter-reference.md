---
concept: command-frontmatter-reference
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-command/references/frontmatter-reference.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.803235+00:00
cluster: tools
content_hash: db1ea175ca4b0bb7
---

# Command Frontmatter Reference

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Command Frontmatter Reference

Complete reference for YAML frontmatter fields in slash commands.

## Frontmatter Overview

YAML frontmatter is optional metadata at the start of command files:

```markdown
---
description: Brief description
allowed-tools: Read, Write
model: sonnet
argument-hint: [arg1] [arg2]
---

Command prompt content here...
```

All fields are optional. Commands work without any frontmatter.

## Field Specifications

### description

**Type:** String
**Required:** No
**Default:** First line of command prompt
**Max Length:** ~60 characters recommended for `/help` display

**Purpose:** Describes what the command does, shown in `/help` output

**Examples:**
```yaml
description: Review code for security issues
```
```yaml
description: Deploy to staging environment
```
```yaml
description: Generate API documentation
```

**Best practices:**
- Keep under 60 characters for clean display
- Start with verb (Review, Deploy, Generate)
- Be specific about what command does
- Avoid redundant "command" or "slash command"

**Good:**
- ✅ "Review PR for code quality and security"
- ✅ "Deploy application to specified environment"
- ✅ "Generate comprehensive API documentation"

**Bad:**
- ❌ "This command reviews PRs" (unnecessary "This command")
- ❌ "Review" (too vague)
- ❌ "A command that reviews pull requests for code quality, security issues, and best practices" (too long)

### allowed-tools

**Type:** String or Array of strings
**Required:** No
**Default:** Inherits from conversation permissions

**Purpose:** Restrict or specify which tools command can use

**Formats:**

**Single tool:**
```yaml
allowed-tools: Read
```

**Multiple tools (comma-separated):**
```yaml
allowed-tools: Read, Write, Edit
```

**Multiple tools (array):**
```yaml
allowed-tools:
  - Read
  - Write
  - Bash(git:*)
```

**Tool Patterns:**

**Specific tools:**
```yaml
allowed-tools: Read, Grep, Edit
```

**Bash with command filter:**
```yaml
allowed-tools: Bash(git:*)           # Only git commands
allowed-tools: Bash(npm:*)           # Only npm commands
allowed-tools: Bash(docker:*)        # Only docker commands
```

**All tools (not recommended):**
```yaml
allowed-tools: "*"
```

**When to use:**

1. **Security:** Restrict command to safe operations
   ```yaml
   allowed-tools: Read, Grep  # Read-only command
   ```

2. **Clarity:** Document required tools
   ```yaml
   allowed-tools: Bash(git:*), Read
   ```

3. **Bash execution:** Enable bash command output
   ```yaml
   allowed-tools: Bash(git status:*), Bash(git diff:*)
   ```

**Best practices:**
- Be as restrictive as possible
- Use command filters for Bash (e.g., `git:*` not `*`)
- Only specify when different from conversation permissions
- Document why specific tools are needed

### model

**Type:** String
**Required:** No
**Default:** Inherits from conversation
**Values:** `sonnet`, `opus`, `haiku`

**Purpose:** Specify which Claude model executes the command

**Examples:**
```yaml
model: haiku    # Fast, efficient for simple tasks
```
```yaml
model: sonnet   # Balanced performance (default)
```
```yaml
model: opus     # Maximum capability for complex tasks
```

**When to use:**

**Use `haiku` for:**
- Simple, formulaic commands
- Fast execution needed
- Low complexity tasks
- Frequent invocations

```yaml
---
description: Format code file
model: haiku
---
```

**Use `sonnet` for:**
- Standard commands (default)
- Balanced speed/quality
- Most common use cases

```yaml
---
description: Review code changes
model: sonnet
---
```

**Use `opus` for:**
- Complex analysis
- Architectural decisions
- Deep code understanding
- Critical tasks

```yaml
---
description: Analyze system architecture
model: opus
---
```

**Best practices:**
- Omit unless specific need
- Use `haiku` for speed when possible
- Reserve `opus` for genuinely complex tasks
- Test with different models to find right balance

### argument-hint

**Type:** String
**Required:** No
**Default:** None

**Purpose:** Document expected a

*(content truncated)*

## See Also

- [[plugin-specific-command-features-reference]]
- [[plugin-specific-command-features-reference]]
- [[gemini-cli-command-reference-workflows]]
- [[gemini-cli-command-reference-workflows]]
- [[plugin-specific-command-features-reference]]
- [[plugin-specific-command-features-reference]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-command/references/frontmatter-reference.md`
- **Indexed:** 2026-04-17T06:42:09.803235+00:00
