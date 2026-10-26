# AGENTS.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

## Overview

This is the authoritative instruction file for agents working in this repository. Preserve the project-specific rules below while applying behavioral guidelines and platform-specific conventions.

For local planning, backlog status, and current task handoffs, consult `docs/plans/start-here.md` (a local-only, gitignored planning file; if absent on fresh clones, start directly with the `running-control-plane` skill (intake mode)).

---

## Contents

- [The Iron Laws & Critical Constraints](#the-iron-laws--critical-constraints)
- [Quick Start & Verification Tooling](#quick-start--verification-tooling)
- [Governing Rules & Modular References](#governing-rules--modular-references)
- [Pre-Completion Verification Gate](#pre-completion-verification-gate)

---

## The Iron Laws & Critical Constraints

1. **Adversarial Reasoning Before Agreement**:
   No significant architecture decision, schema design, code refactor, deletion plan, or migration proposal may be accepted without an adversarial pass first. Agreement must be earned; challenge premises and identify critical assumptions.
2. **Destructive Action & Skill Deletion Guard**:
   Never delete a skill directory, its `SKILL.md`, or its evals because you believe it is redundant, absorbed, consolidated, or superseded. Skill deletions are hard-gated and require explicit user instructions naming the exact path.
3. **Cryptographic Human Gates (CIBA/RAR Lineage)**:
   Three pipeline transitions are cryptographic: spec approval (`Gate 1`), worktree exit review (`Gate 3`), and task closure (`DONE`). Only an out-of-band OpenSSH signature from a human-held key can advance them. Agents must never run signing commands, manipulate keys, or synthesize approval proofs.
4. **Hub-First Architecture & Loose Coupling**:
   Shared resources reside at plugin roots (`plugins/<plugin>/scripts/`, etc.) as canonical authorities; never create symlinks. There is no copy manifest or build step: skills live in each plugin's `.apm/skills/` and APM installs them directly. Installed skills must be self-contained ([plugin-architecture-policy](.agent/rules/plugin-architecture-policy.md) Section 5).
5. **Verifier Sovereignty & Proposal Mode**:
   Implementation agents cannot modify acceptance tests, evaluation baselines, or verification scripts. Pre-execution verifier hashes are locked. In Stage 1 (`PLAN`), workspace files are strictly read-only.
6. **Config-Driven Constants Over Hardcoding**:
   Never introduce magic string literals or answer sequences. All domain constants must be imported from `constants.py`. SQL queries must use `?` bind parameters.
7. **Three-Attempt Maximum & Map Debt Logging**:
   Autonomous repair attempts are capped at 3. Every friction event must update the map (playbooks, rules, references), log `Status: RESOLVED` in `references/map-debt.md` if fixed inline, or record an open debt entry if deferred.
8. **Only Installed Skills Exist at Runtime**:
   `plugins/` is source; only what is installed in your active runtime environment can run. Depending on whether installed locally or globally (via APM or legacy):
   - Local project harnesses: `.claude/skills/<name>` (Claude) or `.agents/skills/<name>` (Copilot, Codex, Antigravity)
   - Global workstation profile: `~/.claude/skills/<name>` (Claude) or `~/.agents/skills/<name>` (Copilot, Codex, Antigravity)
   A skill present in `plugins/` may be disabled or uninstalled to save context. Before recommending, routing to, or writing a handoff to any skill or agent, verify it is installed in your active runtime harness or global profile; never route through an uninstalled one. If the right target is not installed, say so and ask. The `mode` workflow of `running-control-plane` (`control_plane_mode.py enable | disable | status`) switches commit and push gating on or off for one clone, through `context/control-plane-mode` and the two git guards; it does not install or remove any skill, and it says nothing about other skills.
   Install or update packages with `apm install <pkg> [--global] --target claude,copilot,codex,antigravity`. Never edit installed skill copies by hand.
   Before working with the Agentic OS, read the [Agentic OS Skill Map](plugins/agent-agentic-os/skills/running-control-plane/references/agentic-os-skill-map.md) (the three skills, their modes and how they relate) and [Two Improvement Paths](plugins/agent-agentic-os/skills/improving-skills-in-lab/references/two-improvement-paths.md) (control plane vs improvement lab).

---

## Quick Start & Verification Tooling

Run standard deterministic verification scripts to validate compliance:

```bash
# Audit individual or repository skills
python3 plugins/agent-extension-authoring/skills/authoring-skills/scripts/audit_skill.py <skill-path> --mode source

# Audit sub-agent specifications
python3 plugins/agent-extension-authoring/skills/authoring-subagents/scripts/audit_sub_agent.py plugins --all

# Audit rule policy invariants
python3 plugins/agent-extension-authoring/skills/authoring-instructions/scripts/audit_rule.py plugins --all

# Install all plugins globally from the root apm.yml, then check what is installed
apm install --global "$PWD" --target claude,copilot,codex,agy --parallel-downloads 0
apm deps list --global
```

---

## Governing Rules & Modular References

Detailed domain rules and behavioral invariants are maintained as modular documents in `.agent/rules/` and read on demand:

### Core Governance & Safety
- [Adversarial Reasoning](.agent/rules/adversarial-reasoning-before-agreement-rule.md): Anti-sycophancy heuristics and assumption testing.
- [Destructive Action Guard](.agent/rules/destructive-action-guard.md): Verification protocol before file deletions or stand-in conversions.
- [Skill Deletion Guard](.agent/rules/skill-deletion-guard.md): Hard gate prohibiting autonomous skill directory removal.
- [Cryptographic Human Gates](.agent/rules/cryptographic-human-gates.md): CIBA/RAR OpenSSH signing requirements and agent prohibitions.
- [Background Document Priority](.agent/rules/background-document-priority.md): Reading local prompt, issue, and handoff documents before asking redundant questions.

### Architecture & Engineering Lifecycle
- [Engineering Lifecycle Policy](.agent/rules/engineering-lifecycle-policy.md): Control-plane task state machine, proposal mode, and verifier contracts.
- [Plugin Architecture Policy](.agent/rules/plugin-architecture-policy.md): Hub-and-spoke resource layout, script organization, and packaging boundaries.
- [State Transition Guidance](.agent/rules/state-transition-guidance-compliance.md): Strict compliance with transition guidance templates.
- [Self-Evolution Policy](.agent/rules/self-evolution-policy.md): 3-Layer filesystem memory and self-healing friction tiers.
- [Config-Driven Constants](.agent/rules/config-driven-constants-over-hardcoding.md): Prohibition of string literals and SQL parameterization rules.

### Development & Operational Standards
- [Test-Driven Development](.agent/rules/test-driven-development.md): Red-Green-Refactor cycles and test isolation invariants.
- [Test-Driven Wave Deployment](.agent/rules/test-driven-wave-deployment.md): Layer-by-layer verification across multi-service deployments.
- [Spec-Driven Development](.agent/rules/spec-driven-development-policy.md): Specification authoring standards and schema definitions.
- [Coding Conventions](.agent/rules/coding-conventions.md): Language conventions, typing, docstrings, and naming rules.
- [Dependency Management](.agent/rules/dependency-management.md): Locked requirements workflow (`pip-compile`) and tiered dependencies.
- [Git Operations](.agent/rules/git-operations.md): Worktree boundaries, commit hygiene, and forbidden branch manipulations.
- [Worktree Lifecycle Management](.agent/rules/worktree-lifecycle-management.md): Native worktree allocation, locking, and teardown protocols.
- [Worktree Sub-Agent Leak Detection](.agent/rules/worktree-subagent-leak-detection.md): Verification preventing background child process leaks.
- [GitHub Issue Logging Policy](.agent/rules/github-issue-logging-policy.md): Decision matrix and dry-run deduplication for logging friction.
- [Cross-Platform Symlinks](.agent/rules/symlink-cross-platform.md): Superseded by the copy manifest; no new symlinks.
- [Pre-Push Audit](.agent/rules/pre-push-audit.md): Pre-push pipeline completion checks and review gates.

---

## Pre-Completion Verification Gate

Before claiming any task is complete, emit this verification block verbatim:

```
PRE-COMPLETION GATE:
  Capability check: Did I verify whether an existing repo capability was intended for this task? [YES/NO]
  1. Did any existing capability fail, get bypassed, or get manually replaced?  [YES/NO - 1 line if YES]
  2. Did I guess, assume, or get corrected on a repeatable process?              [YES/NO - 1 line if YES]
  3. Did I notice something the next agent will hit again if not fixed?          [YES/NO - 1 line if YES]

If any YES: action taken -> FIX / MAP_DEBT / ESCALATE
```
