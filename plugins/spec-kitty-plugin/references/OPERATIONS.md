# Spec Kitty Dual Tri Bridge: Operations Guide

> **Status**: Active
> **Policy**: [ADR-0032 Dual Tri Bridge Architecture](ADRs/0032-dual-tri-bridge-architecture.md)

## 1. Overview
The **Dual Tri Bridge** system ensures that the **Antigravity Agent** configuration (`.agent/`) serves as the Single Source of Truth for:
1.  **Antigravity IDE** (Native)
2.  **Gemini CLI** (Hard Verification)
3.  **VS Code Copilot** (Contextual Assistance)

## 2. Synchronization
When you modify any Rule (`.agent/rules/*.md`) or Workflow (`.agent/workflows/*.md`), you must run the bridge script to propagate changes to Gemini and Copilot.

### Project Memory Strategy (Copilot)
The Bridge ensures Copilot has access to project memory (like Constitution) through two methods:
1.  **Context Injection**: Is extracted from `.agent/rules/` and compiled into `.github/copilot-instructions.md` (Global Context).
2.  **File Access**: Workflows referenced in Spec Kitty (e.g., `/spec-kitty.constitution`) may write to `.kittify/memory/`. Ensure this structure exists if using those workflows. Note that `.agent/rules/` is the Single Source of Truth; the Bridge handles synchronization.

### Triggering Sync
You can trigger the sync from any environment:

**Option A: Gemini CLI (Recommended)**
```bash
gemini run system-sync
```
*   *Default*: Runs BOTH Inbound and Outbound phases.

**Option B: Trigger via spec-kitty-plugin:spec-kitty-sync-plugin**
Ask the agent to trigger the `spec-kitty-plugin:spec-kitty-sync-plugin` skill with `--inbound` or `--outbound` phase as needed.

**Option C: Via Gemini / Agent Workflow**
```bash
# Run a specific workflow
gemini run codify-form

# Run Spec Kitty
gemini run spec-kitty.specify
```

### C. Installation & Configuration (WSL REQUIRED)

> [!WARNING]
> **DO NOT USE THE NPM VERSION.**
> The package `@google/gemini-cli` (installed via npm) is incompatible.
> It does not support file-based commands or the `config` schema required by this bridge.

**You MUST use the Python-based `gemini-agent` in WSL.**

```bash
# In WSL:
pip install gemini-agent
```

### D. Configuring Credentials
To use models (Claude Opus or Gemini Pro/Ultra via API):

1.  **Anthropic (Claude 3 Opus)**
    ```bash
    gemini config models.default claude-3-opus
    gemini config providers.anthropic.api_key sk-ant-...
    ```

2.  **Google (Gemini 1.5 Pro / Gemini 3 Preview)**
    To access Gemini 3 models, you must enable **Preview features**:
    *   Visit: [https://goo.gle/enable-preview-features](https://goo.gle/enable-preview-features)
    *   Command: `gemini settings` -> Select "Enable Preview features"
    
    ```bash
    gemini config models.default gemini-3-pro
    gemini config providers.gemini.api_key ...
    ```

## 3. Maintenance Workflows
To ingest new capabilities into the system:
3.  **Register Tools**:
    *   If you added new python scripts, trigger the `tool-inventory:tool-inventory` skill to register them.
4.  **Run System Sync**:
    *   Execute `gemini run system-sync` to broadcast these new capabilities to Copilot and Gemini CLI.

## 4. Verification
To verify that the system is synced:

**Step 1: Check Gemini**
Verify that a TOML wrapper exists for your workflow:
```bash
ls .gemini/commands/your_workflow.toml
```

**Step 2: Check Copilot**
Verify that a prompt file exists and `copilot-instructions.md` represents the latest rules:
```bash
ls .github/prompts/your-workflow.prompt.md
head .github/copilot-instructions.md
```

**Step 3: Automated Integrity Audit**
Trigger the `spec-kitty-plugin:spec-kitty-sync-plugin` skill to verify all Rules, Workflows, and Skills are correctly bridged.
