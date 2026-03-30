# Gemini CLI Command Reference & Workflows

**Authoritative Sources:**
- Context & Memory: `https://geminicli.com/docs/cli/tutorials/memory-management/`
- Sessions & History: `https://geminicli.com/docs/cli/tutorials/session-management/`
- CLI Cheatsheet: `https://geminicli.com/docs/cli/cli-reference/`

## Memory Management (`/memory`)

Gemini CLI uses a hierarchical context system rooted in `GEMINI.md` files:
1. **Global:** `~/.gemini/GEMINI.md`
2. **Project Root:** `./GEMINI.md`
3. **Subdirectories:** `./src/GEMINI.md` (JIT Context)

- `/memory show`: Displays the full, concatenated content of the active memory.
- `/memory reload`: Forces a re-scan of all `GEMINI.md` files on disk.
- `/memory add <text>`: Saves a fact to your global memory.
- **Natural Language:** "Save the fact that..." automatically uses the `save_memory` tool.
- **Memory Import Processor:** You can modularize `GEMINI.md` files by importing other Markdown files using the `@filepath.md` syntax. Supports relative (`@./components/file.md`, `@../shared.md`) and absolute paths. Circular imports are automatically prevented.

## Session Management (`/resume`, `/rewind`)

- **Resuming:** `gemini -r` (or `gemini --resume`) restores the last session. `/resume` opens an interactive browser.
- **Deleting:** `gemini --delete-session <ID>` or pressing `x` in the `/resume` browser.
- **Rewind (Ctrl+Z):** `/rewind` or pressing `Esc` twice allows undoing mistakes. Options:
  1. Rewind conversation (removes chat history, leaves files).
  2. Revert code changes (undo file edits, keep chat).
  3. Rewind both.
- **Forking:** `/resume save <point>` followed by `/resume resume <point>` allows branching the conversation.

## Core CLI Commands

- `gemini -p "query"`: Headless execution (piping).
- `gemini -m <model>`: Force specific models (`gemini-3.1-pro-preview`, `gemini-2.5-pro`, `flash`, `flash-lite`).
- `/model`: Opens the interactive model selection (Auto, Pro, Manual).
- `/stats model`: Checks current session token usage and overall API quota.
- `/skills reload`: Reloads capabilities located in `.agents/skills/`.
- `/mcp reload`: Reloads MCP servers.

## Configuration & Settings

**Settings Precedence:** `.gemini/settings.json` (Project) > `~/.gemini/settings.json` (User) > System Defaults.

**Key Environment Variables (`.env`):**
- `GEMINI_MODEL`: Override default execution model (e.g., `export GEMINI_MODEL="gemini-3.1-pro-preview"`).
- `GEMINI_API_KEY`, `GOOGLE_CLOUD_PROJECT`: Authentication provisioning.
- `GEMINI_SANDBOX`: Enable secure tool sandboxing (`true`, `docker`, `podman`).

**Important Run Flags:**
- `--approval-mode <default|auto_edit|yolo|plan>`: Control tool confirmation prompts.
- `--yolo`: Automatically approve all tool calls (equivalent to `--approval-mode yolo`).
- `-s` or `--sandbox`: Execute potentially unsafe operations in an isolated container.

## Policy Engine (`.gemini/policies/*.toml`)

Controls tool execution permissions (`allow`, `deny`, `ask_user`) across User, Workspace, and Admin tiers.
- **Workspace Policies:** Put `.toml` files in `.gemini/policies/`.
- **Key Syntax:** `toolName`, `commandPrefix`, `mcpName` (Recommended for MCP), `decision`, and `priority`.
- **Security:** Setting `decision = "deny"` completely removes the tool from the LLM's context window.

## Built-in Tools & Shorthand (`/tools`)

The CLI acts as a runtime for a native tool registry (File System, Memory, Web Search, MCP).
- **List Tools:** `/tools` (shows active tools) or `/tools desc` (shows full descriptions).
- **Manual Execution Flags:**
  - `@/path/to/file`: Directly inject file content (triggers `read_many_files`).
  - `!npm test`: Directly execute shell commands (triggers `run_shell_command`).
