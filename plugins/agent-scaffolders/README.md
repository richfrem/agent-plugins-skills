# Agent Scaffolders: Spec + Factory

The interactive creation and compliance engine for the agent ecosystem. 
If `agent-loops` handles *execution*, and `agent-agentic-os` handles *improvement*, `agent-scaffolders` is the **Factory** that actually builds the components.

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
- You want to execute a swarm or loop (use `agent-loops`).

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
| `create-command` | "add a slash command" | Slash command with bash or prompt-driven argument handling |
| `create-hook` | "add a PreToolUse hook" | Validated `hooks.json` entries or skill-scoped hook frontmatter |
| `create-mcp-integration` | "setup mcp server" | `.mcp.json` or plugin `mcpServers` block |
| `create-stateful-skill` | "stateful skill" | L4-pattern skill with epistemic trust and artifact lifecycle |
| `create-agentic-workflow`| "convert to copilot" | GitHub Agentic Workflow files (IDE or CI/CD) |
| `create-github-action` | "scaffold CI workflow" | Deterministic GitHub Actions YAML |
| `create-docker-skill` | "docker skill" | Dockerfile and pre-flight security overrides |
| `create-azure-agent` | "azure ai foundry" | Azure AI Foundry agent boilerplate |

---

### 🛡️ The Auditors (Compliance & Repair)

These skills ensure your built components don't violate architectural constraints.

| Skill | Purpose |
|-------|---------|
| `audit-plugin` | Validates plugin structure, boundaries, and security compliance. |
| `audit-plugin-l5` | Runs the rigorous L5 Enterprise Red Team Audit against the 39-point matrix. |
| `path-reference-auditor` | Scans for broken internal references in your markdown documentation. |
| `fix-plugin-paths` | Automatically repairs broken `plugins/` paths to ensure portability. |
| `self-audit` | Regression test for the analyzer tools. |

---

### 🔬 The Analysts (Pattern Mining)

These skills extract knowledge from existing components.

| Skill | Purpose |
|-------|---------|
| `mine-plugins` | Systematically analyzes an entire plugin directory to extract design patterns. |
| `mine-skill` | Targeted analysis on a single skill folder. |
| `synthesize-learnings`| Converts raw analysis results into actionable improvement recommendations. |

---

### ⚙️ Optimization & Benchmarking

The benchmarking stack (located in `scripts/benchmarking/`) supports the `agent-agentic-os` continuous improvement loop by providing the headless evaluation engine.

| Script | Purpose |
|--------|---------|
| `run_eval.py` | Triggers objective evaluation (live routing check) with train/test splits. |
| `improve_description.py`| Description optimization via selectable backend (`claude` or `copilot`). |
| `run_loop.py` | Closed-loop iterative optimization with persistent ledger output. |
| `aggregate_benchmark.py`| Statistical analysis (mean, stddev) across optimization runs. |

*Note: The actual looping mechanics are driven by `agent-agentic-os` and `agent-loops`. This plugin simply provides the scoring binaries.*

---

## Architecture & Constraints

This plugin strictly adheres to the ecosystem ADRs (Architecture Decision Records):

- **ADR-001**: No cross-plugin script execution at runtime — use Agent Skill Delegation instead.
- **ADR-002**: Scripts shared across multiple skills live at `./scripts/`; skill directories contain file-level symlinks pointing up to the plugin root.
- **ADR-003**: File-level symlinks only — directory-level symlinks are silently dropped by installers.
- **ADR-004**: Plugin is fully self-contained — no runtime dependencies on other plugins.

---

## Part of the Plugin Triad

| Plugin | Role |
|--------|------|
| **`agent-scaffolders`** | **Spec + Factory — what ecosystem artifacts are and how to create them** |
| `agent-agentic-os` | Operations — eval-gated improvement loop, experiment log, memory |
| `agent-loops` | Execution patterns — the loop substrate used by the ecosystem |
