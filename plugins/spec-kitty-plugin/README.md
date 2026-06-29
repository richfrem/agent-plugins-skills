# Spec-Kitty Plugin 🐱 (DEPRECATED)

> ⚠️ **DEPRECATION NOTICE**: As of Spec Kitty v3.2.2+, this standalone repository-packaged plugin is **deprecated** in favor of native CLI-managed integration.
> 
> **Source of Truth & Documentation**: For the most up-to-date documentation, guides, and updates, refer directly to the upstream repository:
> 👉 **[Priivacy-ai/spec-kitty on GitHub](https://github.com/Priivacy-ai/spec-kitty)**
> 👉 **[Official Getting Started Guide](https://github.com/Priivacy-ai/spec-kitty/blob/main/docs/guides/getting-started.md)**

Spec Kitty natively supports all AI agent platforms (including Google Antigravity, Claude Code, Gemini CLI, Cursor, and Windsurf) and manages the setup of its 50+ skills and rules directly.

---

## What It Provides

| Need | Spec Kitty provides |
| :--- | :--- |
| **Start from intent** | Guided specify, plan, and tasks workflows |
| **Keep agents aligned** | Repository-native mission artifacts under `kitty-specs/` |
| **Split implementation** | Work packages with lifecycle lanes such as `planned`, `in_progress`, `for_review`, `approved`, and `done` |
| **Run agents in parallel** | Isolated git worktrees under `.worktrees/` |
| **Keep quality visible** | Review, accept, merge, and retrospective gates |
| **See progress** | Optional local kanban dashboard with `spec-kitty dashboard` |
| **Integrate agents** | Slash commands or skills for Claude Code, Codex, Cursor, Gemini, Copilot, Windsurf, OpenCode, and more |
| **Learn from missions** | Every completed mission generates a retrospective by default. Tune via `.kittify/config.yaml#retrospective` or charter. |

---

## 1. Install Spec Kitty

Install the CLI using your preferred tool. `pipx` is the preferred installer for the CLI because it keeps Spec Kitty in its own virtual environment and avoids `externally-managed-environment` errors:

```bash
# Preferred Method
pipx install spec-kitty-cli

# Alternative: Using uv
uv tool install spec-kitty-cli

# Alternative: Inside a virtual environment
python -m pip install spec-kitty-cli
```

Verify the installation:
```bash
spec-kitty --version
```

---

## 2. Initialize a Project

To initialize Spec Kitty natively in your repository:

```bash
spec-kitty init my-project --ai claude
cd my-project
spec-kitty verify-setup
```
*Replace `claude` with your agent key when needed. Common choices include: `antigravity`, `gemini`, `copilot`, `cursor`, `opencode`, `qwen`, `windsurf`, `kiro`, `vibe`, `pi`, and `letta`.*

---

## 3. The Core Workflow

The native workflow structure is:
```text
spec ➔ plan ➔ tasks ➔ next ➔ review ➔ accept ➔ merge
```

### Phase A: Setup & Specify
Open your AI coding agent in the project and run:
```text
/spec-kitty.charter
/spec-kitty.specify Build a small task list app.
```

### Phase B: Plan & Task Slicing
```text
/spec-kitty.plan
/spec-kitty.tasks
```

### Phase C: Autonomous Execution
Let the runtime choose the next action until the mission is ready:
```bash
spec-kitty next --agent <agent-key> --mission <mission-slug>
```

### Phase D: Close the Loop
Review, accept, merge, and close the loop:
```text
/spec-kitty.review
/spec-kitty.accept
/spec-kitty.merge --push
```
*After the merge completes, run `/spec-kitty-mission-review` from a checkout containing the landed changes.*

*Note: The mission's `retrospective.yaml` is authored during the runtime terminus. Once it exists, use `spec-kitty retrospect summary` for the cross-mission view and `spec-kitty agent retrospect synthesize --mission <mission-slug>` to apply any staged proposals (use `--apply` to mutate).*

---

## Everyday Commands

| Command | Purpose |
| :--- | :--- |
| `spec-kitty init . --ai <agent>` | Add Spec Kitty to the current repository |
| `spec-kitty verify-setup` | Check local installation and project wiring |
| `spec-kitty dashboard` | Open the local mission dashboard |
| `spec-kitty next --agent <agent> --mission <slug>` | Ask Spec Kitty what the agent should do next |
| `spec-kitty upgrade` | Update an existing project after upgrading the CLI |
| `spec-kitty --help` | Show all available commands |

---

## Troubleshooting

- **`spec-kitty: command not found`**: Reopen your shell, run `pipx ensurepath` if you installed with `pipx`, or reinstall via `pipx` or `uv`.
- **No `/spec-kitty.specify` command available**: Re-run `spec-kitty init . --ai <your-agent>` from the project root, then verify the setup with `spec-kitty verify-setup --diagnostics`.
- **`WAITING_FOR_DISCOVERY_INPUT`**: The command is paused for your answers; provide the requested details to continue.
