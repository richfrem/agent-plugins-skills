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

Ask targeted questions based on context:

1. **Project Status**: Is this a brand-new project, or an existing repository with code/skills to retrofit?
2. **Active AI Tooling & LLM Clients**: Which tools are used in this workspace?
   - Claude Code CLI / VS Code extension
   - GitHub Copilot CLI / Chat
   - Gemini / Antigravity CLI (`agy`)
   - Codex / OpenAI-compatible CLI
   - Microsoft Agent Framework (MAF)
3. **Plugin Installation Preference**:
   - **`uvx` (Universal / Recommended)**: Instant setup without manual clone.
   - **Claude Code Marketplace**: `claude plugin add richfrem/agent-plugins-skills`.
   - **Local Monorepo / Worktree**: Local sync via `plugin_add.py`.

---

## Phase 2: Component Planning

Propose a component table before execution:

```markdown
| Component | Fresh Init | Retrofit Mode | Purpose |
|---|---|---|---|
| `CLAUDE.md` | Intelligent Seed | Context Blend & Reconcile | Authoritative project kernel |
| `GEMINI.md` | Create Mirror | Context Blend & Tool Mapping | Gemini CLI mirror with tool mappings |
| `.github/copilot-instructions.md` | Create Mirror | Context Blend & Header | Copilot CLI instructions header |
| `AGENTS.md` | Create Mirror | Context Blend | Cross-platform agent instructions |
| `wiki/` | Create | Create Index | Layer 2 Confirmed Knowledge Base |
| `references/map-debt.md` | Create | Create Ledger | Tier 3 Map Debt Tracking |
| `.git/hooks/pre-commit-evolution-guard` | Install | Install / Enable | Deterministic pre-commit evolution & map-debt gate |
| `.agent/learning/traces/` | Create | Create Ledger | Layer 3 Evolution Trace Manifests |
| `audit-skill --fix` | N/A | Run on custom skills | Auto-upgrades legacy skills to boolean evals schema |
```

---

## Phase 2.5 — Mandatory Intelligent Instruction Blending Protocol

> [!IMPORTANT]
> **No Blind Overwrites**: The AI Agent MUST NEVER blindly replace or overwrite existing agent instruction files (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`). Instead, the agent acts as an **intelligent context synthesizer**, blending template best practices with existing project domain rules:

1. **Inspect Existing Instruction Files**:
   - Read existing `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, and `.github/copilot-instructions.md`.
   - Identify project-specific sections (e.g. custom architecture diagrams, startup commands, ports, canonical scripts, and non-negotiable business rules).
2. **Blend with Agentic OS Standards**:
   - Merge the universal evolution infrastructure (3-Layer Memory, Map Debt Ledger, Pre-Commit Evolution Guard, and Turn-by-Turn Pre-Completion Gate) into the existing instructions.
   - Retain 100% of project-specific domain rules, terminology, and tool configurations.
3. **Present Proposed Markdown Diff**:
   - Present the synthesized diff to the user for confirmation before writing, or apply using `replace_file_content` surgically.

---

## Phase 3: Execution

Run `init_agentic_os.py` based on mode:

### Mode A: Fresh Project Setup
```bash
python3 .agents/skills/os-init/scripts/init_agentic_os.py --target <project-path> --sync-instructions
```

### Mode B: Retrofit Existing Repository
```bash
python3 .agents/skills/os-init/scripts/init_agentic_os.py --target <project-path> --retrofit
```

*Note: In both modes, `init_agentic_os.py` automatically installs `.git/hooks/pre-commit-evolution-guard` and configures the `Stop` turn hook.*

---

## Phase 4: Plugin Installation & Deployment

Provide the exact installation command tailored to the user's environment:

### Option 1: Universal `uvx` (Recommended for any project)
```bash
# Add all plugins
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills

# Or install specific plugin
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills/plugins/agent-agentic-os -y
```

### Option 2: Claude Code Marketplace
```bash
claude plugin add richfrem/agent-plugins-skills
```

### Option 3: Local Monorepo Sync
```bash
python3 plugins/plugin-manager/scripts/plugin_add.py --all -y
```

---

## Phase 5: Verification Checklist

1. **Verify 3-Layer Memory & Evolution Gates**:
   - Layer 1: `context/` in-prompt templates.
   - Layer 2: `wiki/index.md` and `references/map-debt.md`.
   - Layer 3: `.agent/learning/traces/cycle_manifests.jsonl`.
   - Pre-Commit Guard: `.git/hooks/pre-commit-evolution-guard` is executable (`chmod +x`).
2. **Verify Multi-Tool Instruction Mirrors**:
   - `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `AGENTS.md` are aligned.
3. **Verify Skills Compliance**:
   - Run `python3 .agents/skills/audit-skill/scripts/audit_skill.py <path-to-skill>` on any newly authored or migrated skills.
