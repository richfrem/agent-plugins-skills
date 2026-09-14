---
name: os-init
plugin: agent-agentic-os
description: >
  Trigger: "set up agentic OS", "initialize agent harness", "init my project for AI agents",
  "retrofit repository", "upgrade project for evolution", "sync instruction files",
  "where do I put CLAUDE.md", "create my agent environment", "set up persistent memory".
  Guides users through discovery, initializes/retrofits 3-Layer Memory, mirrors multi-tool
  instruction files (CLAUDE/GEMINI/Copilot/AGENTS), and guides plugin installation.
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Agentic OS Init & Retrofit Guide

Bootstrap or retrofit the Agentic OS, 3-Layer Memory architecture, and multi-tool instructions in any repository.
Supports fresh setup as well as retrofitting established projects to comply with autonomous evolution standards.

## Installation-state protocol (run before choosing a mode)

Always perform a read-only preflight against the target before proposing or running setup. Classify
the target into exactly one state:

```bash
python3 .agents/skills/os-init/scripts/control_plane/installation_probe.py --target <project-path>
```

When running from the source checkout, use `plugins/agent-agentic-os/scripts/control_plane/installation_probe.py`.
The command emits JSON with `state` and diagnostic `missing` entries and never creates or migrates files.

| State | Classification evidence | Action |
|---|---|---|
| `FRESH` | No Agentic OS markers, control-plane database, or managed hooks | Propose full initialization. |
| `COMPLETE` | Required directories/files exist, control-plane schema initializes cleanly, and managed hooks/instruction markers are present | Report already initialized; do not rewrite setup files. Run only requested validation. |
| `PARTIAL_OR_DRIFTED` | Some markers exist but a required substrate is missing, stale, or fails schema/source parity | Propose idempotent `--retrofit`, showing the missing/drifted items first. |
| `BLOCKED` | Conflicting ownership, unsafe permissions, unapproved destructive change, or unrecoverable migration failure | Stop and explain the blocker and the smallest safe recovery action. |

The preflight is diagnostic, not an authorization bypass. Never infer permission to overwrite
customized `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, rules, hooks, or databases. A `COMPLETE` target
must not be routed through retrofit merely because the skill was invoked again. A
`PARTIAL_OR_DRIFTED` target may use retrofit only after presenting the concrete diff/repair scope.
After setup, repeat the same checks and report the resulting state. If source Python/YAML
definitions and SQLite transition/schema definitions differ, classify as `PARTIAL_OR_DRIFTED` and
recommend migration plus a read-only parity check; do not hand-edit SQLite rows.

---

## Execution Flow

1. **Installation-State Preflight**: Classify the target as `FRESH`, `COMPLETE`, `PARTIAL_OR_DRIFTED`, or `BLOCKED` before any write.
2. **Discovery & Environment Interview**: Identify project stack, active AI tools (Claude, Copilot, Gemini, Codex), and package manager (uvx, marketplace, local).
3. **Component & Retrofit Planning**: Present the state-specific plan (fresh initialization, no-op validation, or retrofit repair).
4. **Execution**: Run `init_agentic_os.py` with appropriate flags (`--retrofit`, `--sync-instructions`).
4. **Plugin Installation Guidance**: Guide installation based on user's tooling environment.
5. **Post-Init & Memory Validation**: Verify Layer 2 `wiki/`, `references/map-debt.md`, and instruction mirrors.

---

## Phase 1: Discovery & Tooling Interview

Identify project status (fresh setup vs. retrofit), active AI tools (Claude Code, Copilot CLI, Gemini/Antigravity, Codex, MAF), and installation preference (`uvx`, Claude marketplace, local).

---

## Phase 2: Component & Retrofit Planning

Propose a component plan before execution:
- Consult [retrofit-planning.md](references/retrofit-planning.md) for the component initialization and retrofit matrix.
- Verify `context/control_plane.db` SQLite initialization, Layer 2 `wiki/` playbooks, `references/map-debt.md`, and Git pre-commit evolution guards.

---

## Phase 2.5 — Mandatory Intelligent Architecture & Rule Synthesis Protocol

> [!IMPORTANT]
> **No Blind Overwrites**: The AI Agent MUST NEVER blindly replace existing architecture files (`architecture.md`), rules (`.agent/rules/*.md`), or instruction files (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`). This cannot be a pure rigid deterministic script — act as an **intelligent context synthesizer**, balancing Agentic OS principles with target project domain realities.

Follow the protocol in [instruction-blending.md](references/instruction-blending.md):
1. **Inspect Target Context**: Read existing `architecture.md`, `.agent/rules/`, and instruction files to discover project tech stack, constraints, and domain conventions.
2. **Synthesize Architecture**: If `architecture.md` exists, review and integrate Agentic OS substrates without disturbing system design; if absent, seed a tailored architecture blueprint.
3. **Blend Instructions & Rules**: Retain 100% of domain logic, reconcile rules non-destructively, and inject 3-Layer Memory, Map Debt Ledger, and Pre-Completion Gate.
4. **Present Diff**: Present proposed architectural and rule changes for confirmation before writing.

---

## Phase 3: Execution

Run `init_agentic_os.py` based on mode:

- **Mode A (Fresh Setup)**: `python3 .agents/skills/os-init/scripts/init_agentic_os.py --target <project-path> --sync-instructions`
- **Mode B (Retrofit Existing)**: `python3 .agents/skills/os-init/scripts/init_agentic_os.py --target <project-path> --retrofit`

*Note: In both modes, `init_agentic_os.py` automatically initializes `context/control_plane.db` with WAL mode, installs `.git/hooks/pre-commit-evolution-guard`, and configures the `Stop` turn hook.*

Retrofit mode must call every scaffolding substrate explicitly — it does not inherit them from
fresh setup. The `--retrofit` branch in `_execute_action()` is a separate, independently
maintained call list from `create_project_structure()`'s; when modifying either, diff their two
call lists against each other explicitly rather than assuming retrofit is a subset of fresh
setup. Full history and the invariant this guards against are in `references/detailed-reference.md`.

---

## Phase 4: Plugin Installation & Deployment

Provide the installation command tailored to the user's environment:
- **Universal `uvx` (Recommended)**: `uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills`
- **Claude Code Marketplace**: `claude plugin add richfrem/agent-plugins-skills`
- **Local Source Reinstall**: `python3 plugins/plugin-manager/scripts/plugin_add.py --all -y`

---

## Phase 5: Verification Checklist & System Health Check

1. **Verify 3-Layer Memory & Control Plane**: Check `context/control_plane.db`, Layer 2 `wiki/index.md`, and `references/map-debt.md`.
2. **Verify Multi-Tool Instruction Mirrors**: Ensure `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, and `AGENTS.md` are aligned.
3. **Verify Skills & Plugin Compliance**: Run `audit_skill.py` on new skills; check `references/evolution-log.md` stubs.
4. **Mandatory Post-Init Health Check**: Trigger `os-health-check` (or Phase 3.5 substrate check); if any substrate reports `MISSING`, re-run with `--retrofit`. Check commands in `references/detailed-reference.md`.

## Consumer Guidance & Upstream Contribution Protocol

When a bug or gap is found in an installed skill/script: prefer **Workflow A** (fix locally, port upstream via PR); use **Workflow B** (project-specific overrides in `.agent/rules/local-*`) for domain divergence; fall back to **Workflow C** (file upstream issue) if a PR isn't feasible. Full details in `references/detailed-reference.md`.
