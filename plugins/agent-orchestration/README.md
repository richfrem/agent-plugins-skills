# Agent Orchestration & Multi-LLM Routing

A framework-agnostic execution and routing suite for AI agents. Combines structural execution topologies (deterministic state machines, DAG workflows, supervisor/worker loops, and parallel swarms) with multi-backend LLM task routing, governance sandboxing, and expert persona delegation.

---

## Skills

| Skill | Role | Description |
|---|---|---|
| `orchestrating-agent-work` | Master Orchestrator | Interactive intake and execution planner for DAGs, supervisor/worker loops, and parallel swarms. Analyzes incoming tasks, determines topology, plans artifacts, and coordinates execution. |
| `cli-agent` | Multi-LLM Router | Dispatches bounded tasks to six backends (`--cli claude\|codex\|copilot\|agy\|gemini\|llama`) via `run_agent.py`. Manages local llama-server setup, canonical model catalogs, project capability setup, and KV cache optimization. |
| `agt-security` | Governance & Sandboxing | Microsoft Agent Governance Toolkit (AGT) sandbox validation, boundary verification, and HMAC key rotation. |
| `maf-adapter` | Framework Adapter | Microsoft Agent Framework (MAF) manifest validation, adapter bindings, and local simulation harness. |

---

## Architecture & Execution Modes

### 1. Structural Orchestration (Loops & DAGs)
```
Task Trigger → orchestrating-agent-work
  ├── Topology: Directed Acyclic Graph (DAG)
  │     └── graph-manifest.json → graph_runner.py (isolated worktrees, receipts, rollback)
  └── Topology: Loop Pattern
        ├── Supervisor / Worker → agent_orchestrator.py (strategy packets, verification loop)
        └── Parallel Swarm → swarm_run.py (partitioned jobs, concurrent batching, merged results)
```

### 2. Multi-LLM Backend Routing
```
Mode A — Interactive Model Replacement (routing_proxy.py)
  Claude Code / Copilot / Agy / Codex → ANTHROPIC_BASE_URL=:4000
  → routing_proxy → llama-server :8089 (Gemma 4 12B)

Mode B — Task Delegation (run_agent.py — fast task router)
  Primary agent → run_agent.py cli=<backend>
  ├── cli=llama   → http://localhost:8089/v1/chat/completions  (direct, ~2s)
  ├── cli=copilot → GitHub Copilot CLI subprocess
  ├── cli=gemini  → Gemini CLI subprocess
  ├── cli=claude  → Claude CLI subprocess
  ├── cli=agy     → Antigravity CLI subprocess
  └── cli=codex   → Codex/OpenAI-compatible CLI subprocess
```

---

## 13 Expert Agent Personas (`agents/`)

Host sub-agents that also serve as persona templates passed to `run_agent.py`:

| Persona | Domain | Focus |
|---|---|---|
| `architect-review.md` | Architecture | C4/SOLID structural review, coupling, layer boundary compliance |
| `compliance-reviewer.md` | Governance | Repository conventions, coding standards, drift detection |
| `critical-auditor.md` | Adversarial | Failure-seeking audit of runtime contracts and assumptions |
| `debate-synthesizer.md` | Adversarial | Dialectical synthesis across conflicting agent proposals |
| `output-validator.md` | Safety | Output guardrail — hallucination, schema, and policy verification |
| `performance-analyst.md` | Performance | Bottleneck analysis — Big-O scaling, I/O amplification |
| `pr-reviewer.md` | Code Quality | Pull request diff review — correctness, blast radius, ship/hold |
| `red-team-reviewer.md` | Adversarial | Exploit scenarios, privilege escalation, attack surface analysis |
| `refactor-expert.md` | Code Quality | Code smell taxonomy, refactoring safety, SOLID/DRY cleanup |
| `security-auditor.md` | Security | OWASP vulnerability audit, risk severity classification |
| `self-critic.md` | Adversarial | Internal reflection loop — task-fit, completeness, blind spots |
| `tdd-contract-reviewer.md` | Testing | Specification testability and Red-Green contract verification |
| `test-writer.md` | Testing | Test suite generation — happy paths, boundaries, edge cases |

---

## Directory Structure

```text
agent-orchestration/
├── .claude-plugin/              # Claude Code plugin manifest
├── hooks/                       # Lifecycle hooks (closure enforcement via closure_guard.py)
├── plugin.yaml                  # Plugin manifest (skills, agents, tools, platforms)
├── requirements.in / .txt       # Standard library dependencies
├── README.md                    # This file
├── agents/                      # 13 host sub-agents & persona templates
├── references/                  # Plugin-wide acceptance criteria, fallback trees, evolution log
├── tests/                       # Plugin-level authoring and execution contract tests
└── skills/
    ├── orchestrating-agent-work/ # Unified DAG and loop orchestrator
    │   ├── SKILL.md             # Master router and execution planner
    │   ├── scripts/             # swarm_run.py, agent_orchestrator.py, graph_runner.py, etc.
    │   ├── assets/templates/    # Job, strategy packet, and retrospective templates
    │   └── references/          # Pattern guides, schemas, and architecture diagrams
    ├── cli-agent/               # Multi-LLM task router, local llama-server, and model catalog
    │   ├── SKILL.md             # Central dispatcher across 6 CLI backends
    │   ├── scripts/             # run_agent.py, run_server.py, routing_proxy.py, kv_cache_orchestrator.py
    │   └── references/          # Backend dispatch guides, catalogs, setup guides
    ├── agt-security/            # Microsoft Agent Governance Toolkit (AGT) sandboxing & HMAC
    └── maf-adapter/             # Microsoft Agent Framework (MAF) adapter & test harness
```

---

## Testing & Verification

```bash
# Plugin structure audit
python3 plugins/agent-extension-authoring/skills/authoring-plugins/scripts/audit_plugin_structure.py plugins/agent-orchestration

# Skill audits
python3 plugins/agent-extension-authoring/skills/authoring-skills/scripts/audit_skill.py plugins/agent-orchestration/skills/orchestrating-agent-work --mode source
python3 plugins/agent-extension-authoring/skills/authoring-skills/scripts/audit_skill.py plugins/agent-orchestration/skills/cli-agent --mode source

# Sub-agent audits
python3 plugins/agent-extension-authoring/skills/authoring-subagents/scripts/audit_sub_agent.py plugins/agent-orchestration --all

# Unit tests
python3 -m pytest plugins/agent-orchestration/skills/cli-agent/scripts -v
```
