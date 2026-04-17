---
concept: plugin-command-examples
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-command/references/plugin-commands.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.825252+00:00
cluster: plugin-code
content_hash: a8505adc4f311343
---

# Plugin Command Examples

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Plugin Command Examples

Practical examples of commands designed for Claude Code plugins, demonstrating plugin-specific patterns and features.

## Table of Contents

1. [Simple Plugin Command](#1-simple-plugin-command)
2. [Script-Based Analysis](#2-script-based-analysis)
3. [Template-Based Generation](#3-template-based-generation)
4. [Multi-Script Workflow](#4-multi-script-workflow)
5. [Configuration-Driven Deployment](#5-configuration-driven-deployment)
6. [Agent Integration](#6-agent-integration)
7. [Skill Integration](#7-skill-integration)
8. [Multi-Component Workflow](#8-multi-component-workflow)
9. [Validated Input Command](#9-validated-input-command)
10. [Environment-Aware Command](#10-environment-aware-command)

---

## 1. Simple Plugin Command

**Use case:** Basic command that uses plugin script

**File:** `commands/analyze.md`

```markdown
---
description: Analyze code quality using plugin tools
argument-hint: [file-path]
allowed-tools: Bash(node:*), Read
---

Analyze @$1 using plugin's quality checker:

!`node ${CLAUDE_PLUGIN_ROOT}/scripts/quality-check.js $1`

Review the analysis output and provide:
1. Summary of findings
2. Priority issues to address
3. Suggested improvements
4. Code quality score interpretation
```

**Key features:**
- Uses `${CLAUDE_PLUGIN_ROOT}` for portable path
- Combines file reference with script execution
- Simple single-purpose command

---

## 2. Script-Based Analysis

**Use case:** Run comprehensive analysis using multiple plugin scripts

**File:** `commands/full-audit.md`

```markdown
---
description: Complete code audit using plugin suite
argument-hint: [directory]
allowed-tools: Bash(*)
model: sonnet
---

Running complete audit on $1:

**Security scan:**
!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/security-scan.sh $1`

**Performance analysis:**
!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/perf-analyze.sh $1`

**Best practices check:**
!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/best-practices.sh $1`

Analyze all results and create comprehensive report including:
- Critical issues requiring immediate attention
- Performance optimization opportunities
- Security vulnerabilities and fixes
- Overall health score and recommendations
```

**Key features:**
- Multiple script executions
- Organized output sections
- Comprehensive workflow
- Clear reporting structure

---

## 3. Template-Based Generation

**Use case:** Generate documentation following plugin template

**File:** `commands/gen-api-docs.md`

```markdown
---
description: Generate API documentation from template
argument-hint: [api-file]
---

Template structure: @${CLAUDE_PLUGIN_ROOT}/templates/api-documentation.md

API implementation: @$1

Generate complete API documentation following the template format above.

Ensure documentation includes:
- Endpoint descriptions with HTTP methods
- Request/response schemas
- Authentication requirements
- Error codes and handling
- Usage examples with curl commands
- Rate limiting information

Format output as markdown suitable for README or docs site.
```

**Key features:**
- Uses plugin template
- Combines template with source file
- Standardized output format
- Clear documentation structure

---

## 4. Multi-Script Workflow

**Use case:** Orchestrate build, test, and deploy workflow

**File:** `commands/release.md`

```markdown
---
description: Execute complete release workflow
argument-hint: [version]
allowed-tools: Bash(*), Read
---

Executing release workflow for version $1:

**Step 1 - Pre-release validation:**
!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/pre-release-check.sh $1`

**Step 2 - Build artifacts:**
!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/build-release.sh $1`

**Step 3 - Run test suite:**
!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/run-tests.sh`

**Step 4 - Package release:**
!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/package.sh $1`

Review all step outputs and report:
1. Any failures or warnings
2. Build artifacts location
3. Test results summary
4. Next steps for deployment
5. Rollback plan if needed
```

**Key featur

*(content truncated)*

## See Also

- [[plugin-specific-command-features-reference]]
- [[simple-command-examples]]
- [[plugin-specific-command-features-reference]]
- [[plugin-specific-command-features-reference]]
- [[simple-command-examples]]
- [[plugin-specific-command-features-reference]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-command/references/plugin-commands.md`
- **Indexed:** 2026-04-17T06:42:09.825252+00:00
