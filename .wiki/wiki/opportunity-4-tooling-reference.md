---
concept: opportunity-4-tooling-reference
source: plugin-code
source_file: exploration-cycle-plugin/assets/resources/design-thinking/04-Engineering-Cycle-Execution/tooling-reference.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.576844+00:00
cluster: agent
content_hash: 12a52c3e35b836f4
---

# Opportunity 4: Tooling Reference

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Opportunity 4: Tooling Reference

A reference guide to the three-layer stack used in Opportunity 4 execution. Each tool is linked to its source and described in terms of what it contributes to the pipeline.

---

## Layer 1 — Spec-Kits (Specification Driven Design)

These frameworks define *what gets built* and enforce the structure and constraints the engineering agent must follow. They translate human-validated intent into machine-consumable specifications that serve as the agent's contract.

---

### GitHub Spec-Kit
**[github/spec-kit](https://github.com/github/spec-kit)** · Open source · 72,000+ GitHub stars

GitHub's official open-source toolkit for spec-driven development. Provides templates and workflows for the full specify → plan → tasks → implement cycle. Supports over 22 AI agent platforms out of the box including Claude Code, GitHub Copilot, Amazon Q, and Gemini CLI. Cross-platform (shell scripts for Unix, PowerShell for Windows).

The most widely adopted SDD framework in the ecosystem. A good starting point for teams new to spec-driven development before introducing more opinionated tooling.

**Best for:** Teams wanting broad platform support and a low-friction entry point into SDD with minimal setup.

---

### Spec-Kitty
**[Priivacy-ai/spec-kitty](https://github.com/Priivacy-ai/spec-kitty)** · Open source · `pip install spec-kitty-cli`

A CLI-first workflow for spec-driven development built for serious agentic execution. Takes the spec → plan → tasks → implement → review → merge lifecycle and enforces it with repository-native artifacts, a live Kanban dashboard, git worktree isolation per feature, and automated merge workflows.

Key distinction from Spec-Kit: Spec-Kitty is opinionated and enforcing. It maintains a live `implementation_plan.md` that tracks progress in real time, uses `.clinerules` to set strict agent boundary constraints, and exposes an orchestrator API (`spec-kitty orchestrator-api`) for multi-agent coordination. The dashboard auto-starts and shows which agents are working on which work packages.

Current stable release is the 3.x line. Integrates directly with Claude Code, Cursor, Gemini, and Codex.

**Best for:** Teams running parallel agentic work across multiple features, needing strong boundary enforcement and auditability.

---

### OpenSpec
**[Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)** · Open source · Stable as of January 2026

A lightweight spec layer that adds structure to the agreement between human and agent before any code is written. Each change gets its own folder containing a proposal, specs, design document, and tasks — allowing fluid iteration without rigid phase gates.

Designed to be tool-agnostic: supports 20+ AI coding tools including Claude, Cursor, Cline, Codex, GitHub Copilot, Kiro, and Windsurf. Entry point is `/opsx:propose "your idea"` which creates the full proposal scaffold.

The explicit goal is eliminating "vibe coding" — unstructured natural language conversations where requirements scatter across chat logs with no persistence or systematization.

**Best for:** Teams wanting a lightweight, tool-agnostic spec layer that doesn't impose a heavy workflow overhead.

---

### BMAD-Method
**[bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)** · Open source · [docs.bmad-method.org](https://docs.bmad-method.org)

Breakthrough Method for Agile AI-Driven Development. A multi-agent framework where specialized AI agents — each defined by a self-contained Markdown persona file — handle distinct roles across the full development lifecycle: Analyst, Product Manager, Architect, Scrum Master, Product Owner, Developer, and QA.

The key architectural distinction: every agent produces a verifiable artifact (PRD, architecture diagram, test plan, sprint stories), not just a chat response. These persistent documents can be reviewed, versioned, and handed off between agents as structured work products. Current release is v6 Alpha, with a Scale A

*(content truncated)*

## See Also

- [[opportunity-4-engineering-cycleexecution]]
- [[optimizer-engine-patterns-reference-design]]
- [[project-setup-reference-guide]]
- [[optimizer-engine-patterns-reference-design]]
- [[analysis-framework-reference]]
- [[path-reference-auditor---usage-guide]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/assets/resources/design-thinking/04-Engineering-Cycle-Execution/tooling-reference.md`
- **Indexed:** 2026-04-17T06:42:09.576844+00:00
