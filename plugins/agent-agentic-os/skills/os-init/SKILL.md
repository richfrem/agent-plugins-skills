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

---

## Execution Flow

1. **Discovery & Environment Interview**: Identify project stack, active AI tools (Claude, Copilot, Gemini, Codex), and package manager (uvx, marketplace, local).
2. **Component & Retrofit Planning**: Present plan (fresh initialization vs. retrofit of existing custom skills).
3. **Execution**: Run `init_agentic_os.py` with appropriate flags (`--retrofit`, `--sync-instructions`).
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

> [!IMPORTANT]
> **Retrofit mode must call `_init_control_plane_db()` explicitly.** Only the fresh-setup path
> (`create_project_structure()` → `_scaffold_context_dir()`) calls `_init_control_plane_db()`
> implicitly. The `--retrofit` branch in `_execute_action()` scaffolds 3-Layer Memory and syncs
> instructions/rules/skills, but never touches `context/`, so a retrofit run silently skipped
> `control_plane.db` creation while still claiming (in this doc and in its own completion banner)
> that both modes initialize it. Fixed by calling `_init_control_plane_db(target, args.dry_run)`
> directly inside the `if args.retrofit:` branch — it's idempotent (skips if the DB already
> exists), so it's safe to call unconditionally on every retrofit run. When modifying
> `_execute_action()` again, verify both branches still reach every substrate listed in this
> Phase 3 note — retrofit is not a subset of fresh-setup and does not get scaffolding steps for
> free.

---

## Phase 4: Plugin Installation & Deployment

Provide the installation command tailored to the user's environment:
- **Universal `uvx` (Recommended)**: `uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills`
- **Claude Code Marketplace**: `claude plugin add richfrem/agent-plugins-skills`
- **Local Source Reinstall**: `python3 plugins/plugin-manager/scripts/plugin_add.py --all -y`

---

## Phase 5: Verification Checklist

1. **Verify 3-Layer Memory & Control Plane**: Check `context/control_plane.db`, Layer 2 `wiki/index.md`, and `references/map-debt.md`.
2. **Verify Multi-Tool Instruction Mirrors**: Ensure `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, and `AGENTS.md` are aligned.
3. **Verify Skills Compliance**: Run `audit_skill.py` on any newly authored or migrated skills.
