# Agent Scaffolders: Spec + Factory

The interactive creation and compliance engine for the agent ecosystem. 
If `agent-orchestration` handles *execution*, and `agent-agentic-os` handles *improvement*, `agent-scaffolders` is the **Factory** that actually builds the components.

It provides a suite of generative and auditing tools to scaffold fully compliant Claude Code plugins, skills, hooks, sub-agents, commands, and MCP integrations from scratch using best-practice architectural patterns.

> **Scope:** Designed for developers building tools and agents. It writes the files, verifies compliance, and optimizes descriptions via the benchmarking stack.

---

## Is This For You?

**Good fit:**
- You want to build a new AI agent, skill, or plugin without manually writing boilerplate.
- You want to ensure your existing plugins comply with the L4/L5 architectural maturity matrices.
- You need to run headless evaluations to iteratively optimize a skill's routing accuracy.
- You want to mine existing plugins to extract reusable design patterns.

**Not a fit:**
- You are an end-user just trying to run a task (use the installed plugins directly).
- You want to execute a swarm or loop (use `agent-orchestration`).

---

## 🚀 Start Here

> **To build something new, use the creation suite:**
>
> ```bash
> /create-plugin
> # or
> /create-skill
> ```
>
> These interactive skills will conduct a discovery interview to understand your goals, and then automatically scaffold the complete directory structure, manifests, and `SKILL.md` files required to get started.

---

## What's in the Box

### 🏭 The Factory (Creation)

These skills build ecosystem-compliant components from scratch.

| Skill | Trigger | What it builds |
|-------|---------|----------------|
| `create-plugin` | "create a plugin" | Complete plugin structure (`plugin.json`, skills, commands, etc.) |
| `create-skill` | "scaffold a skill" | Full skill directory with `SKILL.md`, references, and evals |
| `create-sub-agent` | "add an agent" | Agent `.md` file with validated frontmatter and permission grants |
| `create-hook` | "add a PreToolUse hook" | Validated `hooks.json` entries or skill-scoped hook frontmatter |
| `create-mcp-integration` | "setup mcp server" | `.mcp.json` or plugin `mcpServers` block |
| `create-stateful-skill` | "stateful skill" | L4-pattern skill with epistemic trust and artifact lifecycle |
| `create-agentic-workflow`| "convert to copilot" | Custom Copilot agent (.agent.md), GitHub Agentic Workflow (gh-aw), or CI/CD Smart Failure agent |
| `create-github-action` | "scaffold CI workflow" | Deterministic GitHub Actions YAML |
| `create-docker-skill` | "docker skill" | Dockerfile and pre-flight security overrides |
| `create-azure-agent` | "azure ai foundry" | Azure AI Foundry agent boilerplate |

---

### 🛡️ The Auditors (Compliance & Repair)

These skills ensure your built components don't violate architectural constraints.

| Skill | Purpose |
|-------|---------|
| `audit-plugin` | Validates plugin structure, boundaries, and security compliance. |

---

### 🔬 The Analysts (Pattern Mining)

These skills extract knowledge from existing components.

| Skill | Purpose |
|-------|---------|

---

### ⚙️ Optimization & Benchmarking

The benchmarking stack (located in `scripts/benchmarking/`) supports the `agent-agentic-os` continuous improvement loop by providing the headless evaluation engine.

| Script | Purpose |
|--------|---------|
| `run_eval.py` | Triggers objective evaluation (live routing check) with train/test splits. |
| `improve_description.py`| Description optimization via selectable backend (`claude` or `copilot`). |
| `run_loop.py` | Closed-loop iterative optimization with persistent ledger output. |
| `aggregate_benchmark.py`| Statistical analysis (mean, stddev) across optimization runs. |

*Note: The actual looping mechanics are driven by `agent-agentic-os` and `agent-orchestration`. This plugin simply provides the scoring binaries.*

---

## Architecture & Constraints

This plugin follows universal plugin architecture principles for portability:

- **No Cross-Plugin Script Execution**: Cross-plugin coordination happens via natural-language agent skill delegation, never via hardcoded Python imports or subprocess calls to sibling plugins.
- **Hub-and-Spoke Shared Scripts**: Scripts shared across multiple skills live at the plugin root (`./scripts/`); individual skill directories contain only file-level symlinks pointing up to the plugin root.
- **File-Level Symlinks Only**: Only file-level symlinks are used (never directory-level). Plugin installers resolve symlinks into hard copies during deployment.
- **Full Self-Containment**: The plugin is fully portable and self-contained. Zero runtime dependencies on other plugins, external repository paths, or configuration files that won't exist in target installations.

---

## Part of the Plugin Triad

| Plugin | Role |
|--------|------|
| **`agent-scaffolders`** | **Spec + Factory — what ecosystem artifacts are and how to create them** |
| `agent-agentic-os` | Operations — eval-gated improvement loop, experiment log, memory |
| `agent-orchestration` | Execution patterns — the loop substrate used by the ecosystem |
