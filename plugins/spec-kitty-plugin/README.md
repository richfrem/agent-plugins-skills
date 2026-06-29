# Spec-Kitty Plugin 🐱 (DEPRECATED)

> ⚠️ **DEPRECATION NOTICE**: As of Spec Kitty v3.2.2+, this standalone repository-packaged plugin is **deprecated**. 
> Spec Kitty now has first-class native support for AI agent workspaces (including Google Antigravity, Claude Code, Codex CLI, Gemini CLI, Cursor, and Windsurf) and automatically manages the setup of its 50+ skills and rules directly when you run `spec-kitty init`.

## Why This Plugin is Deprecated
1. **Native agent support**: The upstream `spec-kitty` package now installs its own skills and command surfaces dynamically directly to `.agents/skills/` at init time.
2. **Simplified integration**: Local workflow mapping configuration files (like `sync_configuration.py`) are legacy/redundant. No sync script execution is needed anymore.
3. **Always up-to-date**: Running `spec-kitty init` ensures you always have the latest upstream skills and bug fixes directly from the CLI tool without having to update the monorepo first.

---

## Migration Guide (How to use Native Spec-Kitty)

To transition to native Spec Kitty:

### 1. Install or Upgrade the CLI
Install `spec-kitty-cli` globally (virtual env / pipx recommended):
```bash
pip install --upgrade spec-kitty-cli
```
Verify version is **v3.2.2+**:
```bash
spec-kitty --version
```

### 2. Initialize in your Target Repository
Run the native initialization command in your target project directory (where your code is):

```bash
# For Google Antigravity
spec-kitty init . --ai antigravity

# For Claude Code
spec-kitty init . --ai claude

# For multiple agents
spec-kitty init . --ai antigravity,claude
```

This will automatically create:
- `.agent/` (for Antigravity) or `.claude/` directories with orientation files.
- `.kittify/` project configurations (rules, memory configs, canonical event logs).
- `.agents/skills/` directory containing all 50+ dynamic `spk-*` skills automatically!

### 3. Run directly
Start using the commands natively:
- `/spec-kitty.specify` to specify a mission
- `/spec-kitty.plan` to generate plans
- `/spec-kitty.tasks` to create work packages
- `spec-kitty next` to run the mission loops
