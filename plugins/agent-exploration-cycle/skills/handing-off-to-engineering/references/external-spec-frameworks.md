# External Spec and Execution Frameworks (optional design constraints)

None of these is required or preferred. Exploration produces a framework-neutral package ([engineering-cycle-contract.md](engineering-cycle-contract.md)). Read this only when a receiving team already uses one and its conventions become design constraints on the handoff. For a structured workflow with this repository's own control plane, use the `os-control-intake` skill instead. Facts are as last surveyed (2026); check the source before relying on them.

## Layer 1: specification frameworks (what gets built)

| Framework | What it is | Fits when |
|---|---|---|
| GitHub Spec Kit | Open-source toolkit of templates and workflows for specify, plan, tasks, implement; many agent platforms | broad platform support and a low-friction start |
| Spec-Kitty | CLI-first, enforcing lifecycle with repository-native artifacts, worktree isolation per feature, a live plan, agent boundary rules and an orchestrator API | parallel features with strong boundary enforcement and auditability |
| OpenSpec | Lightweight, tool-agnostic spec layer; each change gets a folder with proposal, specs, design, tasks | structure without heavy workflow overhead |
| BMAD-Method | Multi-agent method with persona files for analyst, PM, architect, scrum master, PO, developer, QA; each role produces a verifiable artifact | complex greenfield work with clearly separated roles |

## Layer 2: agent SDKs (how the engineering agent thinks and coordinates)

| SDK | Notes | Fits when |
|---|---|---|
| Claude Agent SDK | Agent loop, tools and context management as a programmable SDK; native subagents with isolated context; deep MCP integration | Claude-first engineering agents |
| Microsoft Agent Framework | Built on Semantic Kernel; composes agents from several vendors in sequential, concurrent, handoff and group-chat patterns | Azure-hosted or multi-vendor environments |

## Layer 3: execution harnesses (how code is generated, tested and delivered safely)

| Harness | Notes | Fits when |
|---|---|---|
| obra/superpowers | Composable skills that keep an agent on spec-first, plan-then-execute behaviour (MIT licence) | Claude Code workflows needing a skill-driven discipline |
| GSD (get-shit-done) | Context-engineering and spec-driven system against context rot: fresh context per task, atomic commits per micro-task, stuck-loop detection, multi-provider | long sessions where context rot and milestone tracking are the main risk |
| Execution sandbox | Isolated containerised environment where generated code is deployed and integration-tested before delivery; built per deployment, not a third-party tool | any production code generation (always) |

The choice of SDK is driven by the target deployment environment, not preference; all operate against the same spec layer.
