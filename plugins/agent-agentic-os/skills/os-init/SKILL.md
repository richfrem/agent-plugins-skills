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
> **Retrofit mode must call every scaffolding substrate explicitly — it does not inherit them
> from fresh setup.** `create_project_structure()` (the non-`--retrofit` path) calls
> `_scaffold_root_files()`, `_scaffold_context_dir()` (→ `_init_control_plane_db()`),
> `_scaffold_claude_dir()` (→ `.claude/hooks/hooks.json`, the Stop turn hook config), and
> `_validate_and_finalize()` (→ `.git/hooks/pre-commit-evolution-guard`) as one sequence. The
> `--retrofit` branch in `_execute_action()` is a **separate, independently-maintained list** —
> historically it only called `_scaffold_3layer_memory()` + instructions/rules/skills sync, so
> retrofit runs silently skipped `control_plane.db`, `.claude/hooks/hooks.json`, and the git
> pre-commit hook, all three, while this doc and the script's own completion banner claimed both
> modes initialize them. Fixed in two passes: `_init_control_plane_db()` first (found via a
> downstream consumer repo where `context/control_plane.db` was missing post-retrofit), then
> `_scaffold_claude_dir()` + `_validate_and_finalize()` (found immediately after, by auditing the
> rest of `create_project_structure()`'s call list against what `--retrofit` actually reaches).
> All three are idempotent (skip-if-exists / merge-not-clobber), so calling them unconditionally
> on every retrofit run is safe. **When modifying `_execute_action()` again, diff its two
> branches' call lists against each other explicitly** — do not assume retrofit is a subset of
> fresh-setup; every fresh-setup scaffolding call needs a deliberate yes/no decision for whether
> retrofit should also make it, not silent omission.

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
3. **Verify Skills & Plugin Compliance**: Run `audit_skill.py` on any newly authored or migrated skills. Verify all local plugins under `plugins/` have initialized `references/evolution-log.md` stubs.
4. **Mandatory Post-Init Health Check**: Immediately trigger the `os-health-check` skill (or run Phase 3.5 substrate check) to deterministically verify all substrates are active and operational:
   ```bash
   test -f context/control_plane.db && echo "OK control_plane.db" || echo "MISSING control_plane.db"
   test -f .claude/hooks/hooks.json && echo "OK hooks.json (Stop turn hook)" || echo "MISSING hooks.json"
   test -f .git/hooks/pre-commit-evolution-guard && echo "OK pre-commit-evolution-guard" || echo "MISSING pre-commit-evolution-guard"
   test -f .github/workflows/verify-evolution-integrity.yml && echo "OK verify-evolution-integrity.yml" || echo "MISSING verify-evolution-integrity.yml"
   ```
   If any report `MISSING`, re-run with `--retrofit`.

## Consumer Guidance & Upstream Contribution Protocol

When consuming plugins and skills from `agent-plugins-skills` (e.g. via `plugin-add` or direct clone):

1. **Maintainer vs. Consumer Separation**:
   - Consumers should **not** treat installed `.agents/skills/` or `plugins/` as unmaintainable black boxes.
   - If a bug, syntax error, or missing capability is detected in an installed skill or script, you have three primary workflows:

2. **Workflow A: Local Fix with Upstream Contribution (Recommended)**:
   - Identify the gap in the installed skill/script.
   - Test and verify the fix locally in your target repository.
   - Clone or checkout a feature branch in `richfrem/agent-plugins-skills`.
   - Port the fix, run `pytest plugins/agent-agentic-os/tests/`, and submit a Pull Request upstream.
   - Once merged, consuming projects can pull clean updates via `plugin-add -y` or `init_agentic_os.py --retrofit`.

3. **Workflow B: Project-Specific Overrides (Domain Divergence)**:
   - If your project requires rules or behavior specific to your domain (e.g., custom brokerage rules, private API endpoints), do **not** edit shared OS skills directly.
   - Place project-specific customizations in `.agent/rules/local-*` or define project-owned plugins under `plugins/<your-plugin>/`.
   - Shared OS rules in `CLAUDE.md`/`GEMINI.md` layer the fundamental control plane first; local rules layer on top without contradiction.

4. **Workflow C: Issue Reporting for Upstream Gaps**:
   - If unable to submit a PR directly, capture the exact reproduction trace, failure mode, and OS substrate versions, and log an issue in `https://github.com/richfrem/agent-plugins-skills/issues`.
   - Maintain the temporary local patch in `.agents/skills/` until the upstream fix is released and retrofitted.



