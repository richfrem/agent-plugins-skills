# Agent Discovery and Publication Pattern

This document codifies the "Discovery-First Publication" pattern for agentic ecosystems. It explains how to bridge the gap between **Source of Truth** (in `plugins/`) and **Discovery Harness** (in `.github/agents/` or `.claude/agents/`).

## The Problem
Agents stored in `plugins/<name>/agents/` are authoritative for the codebase but are **not automatically visible** to agent hosts (like GitHub Copilot or Claude Code) until they are materialized into specific runtime directories.

## The Pattern: Materialization vs. Committal

### 1. The Source (The Authoritative File)
Always author your agents in the plugin source tree:
`plugins/<plugin-name>/agents/<agent-name>.md`

### 2. The Materialized Harness (The Local Face)
When you run `apm install` or `uvx plugin-add`, the agent is copied or symlinked into:
- `.github/agents/` (for GitHub/Copilot discovery)
- `.claude/agents/` (for Claude Code discovery)

### 3. The Discovery Exception (The Publication)
By default, these runtime directories should be in `.gitignore`. However, if you want a repository to **host its own agents publicly** on GitHub, you must implement the **Discovery Exception**:

#### Step A: Update `.gitignore`
Instead of ignoring the entire directory, ignore its contents but allow the subdirectory:
```gitignore
.github/*
!.github/agents/
```

#### Step B: Commit the "Face"
Commit the materialized agent file in `.github/agents/`. This ensures that when the repo is viewed on GitHub, the agent appears in the "Custom Agents" list for Copilot.

## Best Practices
- **Synchronized Updates**: Ensure that the "Face" in `.github/agents/` is always a byte-for-byte copy of the source in `plugins/`.
- **CI/CD Enforcement**: Use a GitHub Action (like the `update-ecosystem` workflow) to automatically re-materialize agents from source to harness if they drift.
- **Minimalist Harness**: Only commit agents to the root harness that are intended for public repo-level interaction. Keep internal utility agents as "Source-Only".
