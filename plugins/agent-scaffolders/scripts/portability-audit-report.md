# Portability Audit Report

## 🔴 CRITICAL — Python Runtime Path Constructions

> These lines hardcode `plugins/<name>` inside Python `Path()` variable assignments.
> They **cannot be whitelisted** — they must be fixed by replacing the hardcoded path
> with a relative `scripts/` reference or a `.agents/skills/` installed path.

### [ ] plugins/agent-agentic-os/tests/test_audit_map_debt.py
- Line `15` [CRITICAL]: `SCRIPT_DIR = REPO_ROOT / "plugins/agent-agentic-os/scripts"`

## ⚠️ Standard — Hardcoded Path References

> The following files contain hardcoded `plugins/` references or absolute machine paths.
> The `fix-plugin-paths` skill must run until this report returns zero violations
> by either neutralizing the path or updating `plugin_paths_whitelist.json`.

### [ ] .github/copilot-instructions.md
- Line `202`: `**spec-kitty is not installed or used in this repo.** `plugins/spec-kitty-plugin/` was removed on`
- Line `252`: `**Do not reference:** `plugins/claude-cli`, `plugins/copilot-cli`, `plugins/gemini-cli` — all deleted.`
- Line `262`: `**Do not reference:** `plugins/rlm-factory`, `plugins/vector-db`, `plugins/memory-management` — all deleted.`
- Line `273`: `**Do not reference:** `plugins/adr-manager`, `plugins/coding-conventions`, `plugins/context-bundler`,`
- Line `274`: ``plugins/huggingface-utils`, `plugins/link-checker`, `plugins/mermaid-to-png`,`
- Line `275`: ``plugins/task-manager`, `plugins/voice-writer` — all deleted.`
- Line `1709`: ``plugins/portfolio-advisor/scripts/daily_brief.py`, despite reporting a passing`

### [ ] .venv/lib/python3.14/site-packages/__editable___agent_plugins_0_1_0_finder.py
- Line `9`: `MAPPING: dict[str, str] = {'bootstrap': '/Users/richardfremmerlid/Projects/agent-plugins-skills/bootstrap'}`

### [ ] AGENTS.md
- Line `199`: `**spec-kitty is not installed or used in this repo.** `plugins/spec-kitty-plugin/` was removed on`
- Line `249`: `**Do not reference:** `plugins/claude-cli`, `plugins/copilot-cli`, `plugins/gemini-cli` — all deleted.`
- Line `259`: `**Do not reference:** `plugins/rlm-factory`, `plugins/vector-db`, `plugins/memory-management` — all deleted.`
- Line `270`: `**Do not reference:** `plugins/adr-manager`, `plugins/coding-conventions`, `plugins/context-bundler`,`
- Line `271`: ``plugins/huggingface-utils`, `plugins/link-checker`, `plugins/mermaid-to-png`,`
- Line `272`: ``plugins/task-manager`, `plugins/voice-writer` — all deleted.`
- Line `1706`: ``plugins/portfolio-advisor/scripts/daily_brief.py`, despite reporting a passing`

### [ ] GEMINI.md
- Line `199`: `**spec-kitty is not installed or used in this repo.** `plugins/spec-kitty-plugin/` was removed on`
- Line `249`: `**Do not reference:** `plugins/claude-cli`, `plugins/copilot-cli`, `plugins/gemini-cli` — all deleted.`
- Line `259`: `**Do not reference:** `plugins/rlm-factory`, `plugins/vector-db`, `plugins/memory-management` — all deleted.`
- Line `270`: `**Do not reference:** `plugins/adr-manager`, `plugins/coding-conventions`, `plugins/context-bundler`,`
- Line `271`: ``plugins/huggingface-utils`, `plugins/link-checker`, `plugins/mermaid-to-png`,`
- Line `272`: ``plugins/task-manager`, `plugins/voice-writer` — all deleted.`
- Line `1706`: ``plugins/portfolio-advisor/scripts/daily_brief.py`, despite reporting a passing`

### [ ] architecture.md
- Line `18`: `or agent list are installed **globally** via the Claude Code marketplace (`~/.claude/plugins/cache/`) —`
- Line `27`: ``plugins/spec-kitty-plugin` was removed 2026-09-05, never part of this count):`
- Line `187`: `- New plugins/skills should be scaffolded via `create-plugin` / `create-skill`, then validated with`

### [ ] context/experiment-log/2026-04-25-verifier-2026-04-25-round1.md
- Line `74`: `│ cat > /Users/richardfremmerlid/Projects/agent-plugins-skills/temp/os-evolu`
- Line `508`: `python3 plugins/copilot-cli/scripts/run_agent.py \`
- Line `513`: `python3 plugins/copilot-cli/scripts/run_agent.py \`

### [ ] context/experiment-log/2026-04-26-planner-2026-04-26-ecosystem-validation.md
- Line `358`: `python3 plugins/copilot-cli/scripts/run_agent.py \`
- Line `363`: `python3 plugins/copilot-cli/scripts/run_agent.py \`

### [ ] docs/MAF-research-analysis/maf-hands-on-experiment-analysis.md
- Line `4`: `**Source:** `/Users/richardfremmerlid/Projects/MicrosoftAgentFramework/01_Basics``

### [ ] docs/superpowers/plans/2026-05-30-hardened-control-plane.md
- Line `98`: `cd /Users/richardfremmerlid/Projects/agent-plugins-skills`

### [ ] handoffs/task_packet_lean_memory_evolution.md
- Line `4`: `**Target Monorepo:** `/Users/richardfremmerlid/Projects/agent-plugins-skills``
- Line `7`: `**Ratified Plan:** [`temp/plans/lean-3-layer-memory-evolution-plan.md`](file:///Users/richardfremmerlid/Projects/agent-plugins-skills/temp/plans/lean-3-layer-memory-evolution-plan.md)`
- Line `8`: `**Execution Prompt:** [`temp/plans/gemini-agy-implementation-prompt.md`](file:///Users/richardfremmerlid/Projects/agent-plugins-skills/temp/plans/gemini-agy-implementation-prompt.md)`

### [ ] plugins/agent-agentic-os/references/map-debt.md
- Line `21`: `- Live repro: created worktree `../worktree-live-pass-1788153987` via `git worktree add -b evolution/<cid> ... HEAD`, applied a real Kelvin-broadening fix to `evo-smoketest/SKILL.md` inside that workt`

### [ ] plugins/agent-agentic-os/references/meta/anthropic-official-docs.md
- Line `43`: `Source: [GitHub: claude-plugins-official/plugins/skill-creator](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator)`
- Line `62`: `Source: [GitHub: claude-plugins-official/plugins/plugin-dev](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/plugin-dev)`

### [ ] plugins/agent-agentic-os/scripts/evaluate.py
- Line `51`: `# evaluate.py lives at plugins/autoresearch-improvement/scripts/evaluate.py`

### [ ] plugins/agent-agentic-os/scripts/init_autoresearch.py
- Line `32`: `[--plugin-root .agents/plugins/autoresearch-improvement]`

### [ ] plugins/agent-agentic-os/skills/os-eval-runner/scripts/evaluate.py
- Line `51`: `# evaluate.py lives at plugins/autoresearch-improvement/scripts/evaluate.py`

### [ ] plugins/agent-agentic-os/skills/os-eval-runner/scripts/init_autoresearch.py
- Line `32`: `[--plugin-root .agents/plugins/autoresearch-improvement]`

### [ ] plugins/agent-agentic-os/skills/os-improvement-loop/scripts/evaluate.py
- Line `51`: `# evaluate.py lives at plugins/autoresearch-improvement/scripts/evaluate.py`

### [ ] plugins/agent-agentic-os/skills/self-evolution/references/map-debt.md
- Line `21`: `- Live repro: created worktree `../worktree-live-pass-1788153987` via `git worktree add -b evolution/<cid> ... HEAD`, applied a real Kelvin-broadening fix to `evo-smoketest/SKILL.md` inside that workt`

### [ ] plugins/agent-agentic-os/tests/test_evolution_scripts.py
- Line `434`: `"--exit-code", "0", "--paths-affected", "plugins/test.py", "--repo-dir", str(test_git_repo)],`
- Line `443`: `"--exit-code", "0", "--paths-affected", "plugins/test.py", "--repo-dir", str(test_git_repo)],`

### [ ] plugins/agent-agentic-os/tests/test_graph_state_machine.py
- Line `66`: `"target_files": ["plugins/code.py"]`
- Line `82`: `subprocess.run([sys.executable, str(record_script), "append", "--cycle-id", cycle_id, "--node", "EXECUTE", "--event-type", "mutation.completed", "--paths-affected", "plugins/code.py", "--repo-dir", st`
- Line `139`: `"target_files": ["plugins/code.py"]`

### [ ] plugins/agent-memory/assets/references/research/summary.md
- Line `59`: `*   **Discovery CLI:** Scripts within self-contained plugins/skills architecture (Recursive Scanner)`

### [ ] plugins/agent-memory/scripts/swarm_run.py
- Line `40`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-memory/skills/rlm-cleanup-agent/scripts/swarm_run.py
- Line `40`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-memory/skills/rlm-curator/scripts/swarm_run.py
- Line `40`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-memory/skills/rlm-distill-agent/scripts/swarm_run.py
- Line `40`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-memory/skills/rlm-init/scripts/swarm_run.py
- Line `40`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-memory/skills/rlm-search/SKILL.md
- Line `69`: `# Example: Search plugins/scripts cache`

### [ ] plugins/agent-memory/skills/rlm-search/scripts/swarm_run.py
- Line `40`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-orchestration/scripts/swarm_run.py
- Line `46`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-orchestration/skills/agent-swarm/scripts/swarm_run.py
- Line `46`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-orchestration/skills/orchestrator/scripts/swarm_run.py
- Line `46`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-scaffolders/references/examples/plugin-commands.md
- Line `548`: `@/home/user/.claude/plugins/my-plugin/config.json`

### [ ] plugins/agent-scaffolders/references/examples/plugin-features-reference.md
- Line `106`: `Read template: @/path/to/plugins/plugin-name/templates/report.md`

### [ ] plugins/agent-scaffolders/references/fix-plugin-paths.prompt.md
- Line `4`: `If a file inside `plugins/A/` references `plugins/A/scripts/foo.py`, replace with `./scripts/foo.py`.`
- Line `30`: `**BEFORE:** `e.g. "/Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/link-checker"``
- Line `31`: `**AFTER:**  `e.g. "<USER_HOME>/Projects/agent-plugins-skills/plugins/link-checker"``
- Line `69`: `- **Generic placeholder examples**: `plugins/my-plugin`, `plugins/<plugin-name>`, `plugins/link-checker`.`

### [ ] plugins/agent-scaffolders/references/marketplace-architecture.md
- Line `17`: `A marketplace entry with `"source": "./plugins/my-plugin"` resolves the path relative to the marketplace repository root. This only works when the marketplace was added via a Git clone or local filesy`

### [ ] plugins/agent-scaffolders/references/marketplace-schema.md
- Line `29`: `| Relative Path | String | `"./plugins/my-plugin"` |`

### [ ] plugins/agent-scaffolders/references/marketplace.md
- Line `23`: `- `metadata.pluginRoot`: Base directory prepended to relative plugin source paths. Setting `"./plugins"` lets entries use `"source": "formatter"` instead of `"source": "./plugins/formatter"`.`
- Line `29`: `- Relative Path: `"./plugins/my-plugin"` — must start with `./`. Only works when marketplace added via Git clone, not direct URL.`
- Line `32`: `- Git subdirectory (sparse clone): `{"source": "git-subdir", "url": "https://github.com/owner/repo", "path": "plugins/my-plugin", "ref": "main"}`. Field is `path` not `subdir`.`
- Line `130`: `- **Submit to official marketplace**: Claude.ai: `claude.ai/settings/plugins/submit` · Console: `platform.claude.com/plugins/submit`.`

### [ ] plugins/agent-scaffolders/references/plugin-features-reference.md
- Line `106`: `Read template: @/path/to/plugins/plugin-name/templates/report.md`

### [ ] plugins/agent-scaffolders/references/plugins.md
- Line `25`: `- **Plugin Cache:** Installed marketplace plugins are copied to a cache (`~/.claude/plugins/cache`).`
- Line `26`: `- **`plugins`:** Always use this environment variable inside `hooks.json`, `.mcp.json`, and scripts to reference the absolute path of your plugin (e.g. `"plugins/scripts/execute.py"`).`

### [ ] plugins/agent-scaffolders/references/security-checks.md
- Line `34`: `| Undeclared dependencies | Plugin relies on other plugins/MCP servers not documented | Warning |`

### [ ] plugins/agent-scaffolders/references/usage-guide.md
- Line `89`: `python ./check_skill_boundaries.py inventory.json --skill plugins/adr-manager/skills/adr-management`
- Line `97`: `RESOLVES TO: plugins/adr-manager/templates/adr-template.md  ❌ OUTSIDE!`
- Line `102`: `cd plugins/adr-manager/skills/adr-management`
- Line `119`: `python ./check_plugin_boundaries.py inventory.json --plugin plugins/plugin-installer`
- Line `124`: `FILE: plugins/adr-manager/commands/adr-management.md:8`
- Line `126`: `PLUGIN ROOT: plugins/adr-manager/`
- Line `132`: `cd plugins/adr-manager`

### [ ] plugins/agent-scaffolders/scripts/auto_fix_local_links.py
- Line `47`: `# Group 2: The plugins prefix (plugins/plugin-name/...)`

### [ ] plugins/agent-scaffolders/scripts/check_plugin_boundaries.py
- Line `14`: `pythonheck_plugin_boundaries.py temp/inventory.json --plugin plugins/adr-manager`
- Line `52`: `r"re:.*Users/.*",           # macOS absolute paths (e.g. /Users/robert/...)`
- Line `91`: `plugins/adr-manager/commands/adr-management.md  plugins/adr-manager/`
- Line `92`: `plugins/plugin-installer/hooks/hooks.json  plugins/plugin-installer/`
- Line `93`: `plugins/adr-manager/.claude-plugin/plugin.json  plugins/adr-manager/`
- Line `96`: `plugins/adr-manager/skills/adr-management/SKILL.md  None (skip)`
- Line `111`: `return Path(*parts[:idx+2])  # e.g., plugins/adr-manager/`

### [ ] plugins/agent-scaffolders/scripts/check_skill_boundaries.py
- Line `14`: `pythonheck_skill_boundaries.py temp/inventory.json --skill plugins/adr-manager/skills/adr-management`
- Line `62`: `r"re:/Users/.*",           # macOS absolute paths (e.g. /Users/robert/...)`
- Line `98`: `plugins/adr-manager/skills/adr-management/SKILL.md`
- Line `99`: `plugins/adr-manager/skills/adr-management/`
- Line `111`: `return Path(*parts[:idx+2])  # e.g., plugins/adr-manager/skills/adr-management`

### [ ] plugins/agent-scaffolders/scripts/fix_descriptions.py
- Line `43`: `"plugins/excel-to-csv/skills/excel-to-csv/SKILL.md"`

### [ ] plugins/agent-scaffolders/scripts/fix_inside_plugin_symlinks.py
- Line `75`: `"""Extract plugin root from path like plugins/adr-manager/skills/adr-management/file.md"""`

### [ ] plugins/agent-scaffolders/scripts/fix_plugin_load_errors.py
- Line `25`: `NOTE: Claude Code scans ALL cached plugin versions under ~/.claude/plugins/cache/,`

### [ ] plugins/agent-scaffolders/scripts/path_reference_auditor.py
- Line `111`: `Walk all plugins/skills directories and find every ./reference.`

### [ ] plugins/agent-scaffolders/scripts/scaffold_agentic_workflow.py
- Line `412`: `Example: --plugin-dir plugins/my-plugin --mode ide`

### [ ] plugins/agent-scaffolders/scripts/validate_local_links.py
- Line `60`: `# Matches explicit strings like "plugins/my-plugin" or "plugins/rlm-factory/scripts"`

### [ ] plugins/agent-scaffolders/skills/analyze-plugin/references/security-checks.md
- Line `34`: `| Undeclared dependencies | Plugin relies on other plugins/MCP servers not documented | Warning |`

### [ ] plugins/agent-scaffolders/skills/audit-plugin-l5/SKILL.md
- Line `27`: `Before executing this skill, ensure you know the exact path or name of the plugin you wish to audit (e.g., `plugins/oracle-legacy-system-analysis/xml-to-markdown`).`

### [ ] plugins/agent-scaffolders/skills/audit-plugin/SKILL.md
- Line `119`: ``~/.claude/plugins/cache/`, not just the active `installPath`. Fixing source files`

### [ ] plugins/agent-scaffolders/skills/create-agentic-workflow/scripts/scaffold_agentic_workflow.py
- Line `412`: `Example: --plugin-dir plugins/my-plugin --mode ide`

### [ ] plugins/agent-scaffolders/skills/create-command/references/examples/plugin-commands.md
- Line `548`: `@/home/user/.claude/plugins/my-plugin/config.json`

### [ ] plugins/agent-scaffolders/skills/create-command/references/examples/plugin-features-reference.md
- Line `106`: `Read template: @/path/to/plugins/plugin-name/templates/report.md`

### [ ] plugins/agent-scaffolders/skills/create-command/references/plugin-features-reference.md
- Line `106`: `Read template: @/path/to/plugins/plugin-name/templates/report.md`

### [ ] plugins/agent-scaffolders/skills/create-github-action/scripts/scaffold_agentic_workflow.py
- Line `412`: `Example: --plugin-dir plugins/my-plugin --mode ide`

### [ ] plugins/agent-scaffolders/skills/ecosystem-authoritative-sources/SKILL.md
- Line `25`: `- **Foundational Specification**: `https://github.com/anthropics/claude-plugins-official/tree/main/plugins/plugin-dev``
- Line `70`: `- Relative path (same-repo monorepo): `"source": "./plugins/my-plugin"` — resolved from repo root`

### [ ] plugins/agent-scaffolders/skills/ecosystem-authoritative-sources/references/marketplace.md
- Line `23`: `- `metadata.pluginRoot`: Base directory prepended to relative plugin source paths. Setting `"./plugins"` lets entries use `"source": "formatter"` instead of `"source": "./plugins/formatter"`.`
- Line `29`: `- Relative Path: `"./plugins/my-plugin"` — must start with `./`. Only works when marketplace added via Git clone, not direct URL.`
- Line `32`: `- Git subdirectory (sparse clone): `{"source": "git-subdir", "url": "https://github.com/owner/repo", "path": "plugins/my-plugin", "ref": "main"}`. Field is `path` not `subdir`.`
- Line `130`: `- **Submit to official marketplace**: Claude.ai: `claude.ai/settings/plugins/submit` · Console: `platform.claude.com/plugins/submit`.`

### [ ] plugins/agent-scaffolders/skills/ecosystem-authoritative-sources/references/plugins.md
- Line `25`: `- **Plugin Cache:** Installed marketplace plugins are copied to a cache (`~/.claude/plugins/cache`).`
- Line `26`: `- **`plugins`:** Always use this environment variable inside `hooks.json`, `.mcp.json`, and scripts to reference the absolute path of your plugin (e.g. `"plugins/scripts/execute.py"`).`

### [ ] plugins/agent-scaffolders/skills/fix-plugin-paths/SKILL.md
- Line `39`: ``PROJECT_ROOT / "plugins/other-plugin/..."` at runtime. Cross-plugin script references`

### [ ] plugins/agent-scaffolders/skills/fix-plugin-paths/references/fix-plugin-paths.prompt.md
- Line `4`: `If a file inside `plugins/A/` references `plugins/A/scripts/foo.py`, replace with `./scripts/foo.py`.`
- Line `30`: `**BEFORE:** `e.g. "/Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/link-checker"``
- Line `31`: `**AFTER:**  `e.g. "<USER_HOME>/Projects/agent-plugins-skills/plugins/link-checker"``
- Line `69`: `- **Generic placeholder examples**: `plugins/my-plugin`, `plugins/<plugin-name>`, `plugins/link-checker`.`

### [ ] plugins/agent-scaffolders/skills/manage-marketplace/SKILL.md
- Line `46`: `{ "source": "./plugins/my-plugin-folder" }`
- Line `60`: `{ "source": { "source": "git-subdir", "url": "https://github.com/owner/repo", "path": "plugins/my-plugin" } }`
- Line `89`: `4.  Optional: use `metadata.pluginRoot` to shorten relative source paths. Setting `"pluginRoot": "./plugins"` lets you write `"source": "formatter"` instead of `"source": "./plugins/formatter"`.`

### [ ] plugins/agent-scaffolders/skills/manage-marketplace/acceptance-criteria.md
- Line `21`: `| **Hardcoded paths in hooks** | Plugin author guidance uses absolute host paths (e.g., `/home/user/.claude/plugins/my-plugin/run.sh`) instead of `${CLAUDE_PLUGIN_ROOT}`. |`

### [ ] plugins/agent-scaffolders/skills/manage-marketplace/references/marketplace-schema.md
- Line `29`: `| Relative Path | String | `"./plugins/my-plugin"` |`

### [ ] plugins/agent-scaffolders/skills/mine-plugins/SKILL.md
- Line `51`: `/mine-plugins claude-knowledgework-plugins/sales`
- Line `57`: `/mine-plugins plugins/legacy\ system`

### [ ] plugins/agent-scaffolders/skills/mine-skill/SKILL.md
- Line `49`: `/mine-skill claude-knowledgework-plugins/sales/skills/call-prep`

### [ ] plugins/agent-scaffolders/skills/path-reference-auditor/SKILL.md
- Line `36`: `- **Plugin-local**: References in `plugins/X/` (root level) stay within `X/``
- Line `112`: `FILE: plugins/adr-manager/commands/adr-management.md:8`
- Line `215`: `- `../../templates/file.md` → `plugins/X/templates/file.md` (outside skill) ❌`
- Line `220`: `cd plugins/X/skills/Y`
- Line `225`: `All file references **inside** `plugins/X/` (root level, non-skill files) must resolve **within** `X/`.`
- Line `228`: `- `./commands/file.md` → `plugins/X/commands/file.md` ✅`
- Line `232`: `- `../other-plugin/file.md` → `plugins/other-plugin/file.md` (sibling plugin) ❌`
- Line `237`: `cd plugins/X`

### [ ] plugins/agent-scaffolders/skills/path-reference-auditor/references/usage-guide.md
- Line `89`: `python ./check_skill_boundaries.py inventory.json --skill plugins/adr-manager/skills/adr-management`
- Line `97`: `RESOLVES TO: plugins/adr-manager/templates/adr-template.md  ❌ OUTSIDE!`
- Line `102`: `cd plugins/adr-manager/skills/adr-management`
- Line `119`: `python ./check_plugin_boundaries.py inventory.json --plugin plugins/plugin-installer`
- Line `124`: `FILE: plugins/adr-manager/commands/adr-management.md:8`
- Line `126`: `PLUGIN ROOT: plugins/adr-manager/`
- Line `132`: `cd plugins/adr-manager`

### [ ] plugins/agent-scaffolders/skills/path-reference-auditor/scripts/check_plugin_boundaries.py
- Line `14`: `pythonheck_plugin_boundaries.py temp/inventory.json --plugin plugins/adr-manager`
- Line `52`: `r"re:.*Users/.*",           # macOS absolute paths (e.g. /Users/robert/...)`
- Line `91`: `plugins/adr-manager/commands/adr-management.md  plugins/adr-manager/`
- Line `92`: `plugins/plugin-installer/hooks/hooks.json  plugins/plugin-installer/`
- Line `93`: `plugins/adr-manager/.claude-plugin/plugin.json  plugins/adr-manager/`
- Line `96`: `plugins/adr-manager/skills/adr-management/SKILL.md  None (skip)`
- Line `111`: `return Path(*parts[:idx+2])  # e.g., plugins/adr-manager/`

### [ ] plugins/agent-scaffolders/skills/path-reference-auditor/scripts/check_skill_boundaries.py
- Line `14`: `pythonheck_skill_boundaries.py temp/inventory.json --skill plugins/adr-manager/skills/adr-management`
- Line `62`: `r"re:/Users/.*",           # macOS absolute paths (e.g. /Users/robert/...)`
- Line `98`: `plugins/adr-manager/skills/adr-management/SKILL.md`
- Line `99`: `plugins/adr-manager/skills/adr-management/`
- Line `111`: `return Path(*parts[:idx+2])  # e.g., plugins/adr-manager/skills/adr-management`

### [ ] plugins/agent-scaffolders/skills/path-reference-auditor/scripts/fix_inside_plugin_symlinks.py
- Line `75`: `"""Extract plugin root from path like plugins/adr-manager/skills/adr-management/file.md"""`

### [ ] plugins/agent-scaffolders/skills/path-reference-auditor/scripts/path_reference_auditor.py
- Line `111`: `Walk all plugins/skills directories and find every ./reference.`

### [ ] plugins/cli-agents/references/routing_latency_findings.md
- Line `164`: `FROM /Users/richardfremmerlid/Projects/local-llm-bench/llama.cpp/models/gemma-4-12b-UD-Q4_K_XL.gguf`

### [ ] plugins/dev-utils/references/assistant_preferences.md
- Line `3`: `- Default project root for this user's task operations: /Users/richardfremmerlid/Projects/hermes-agent/tasks`

### [ ] plugins/dev-utils/references/per-user-tasks-default.md
- Line `15`: `/Users/richardfremmerlid/Projects/hermes-agent/tasks`

### [ ] plugins/dev-utils/references/user-hermes-tasks-root.md
- Line `4`: `/Users/richardfremmerlid/Projects/hermes-agent/tasks`
- Line `9`: `- CLI: python3 ./scripts/task_manager.py create "Title" --lane backlog --dir /Users/richardfremmerlid/Projects/hermes-agent/tasks`
- Line `10`: `- Env var convenience: export HERMES_TASKS_ROOT=/Users/richardfremmerlid/Projects/hermes-agent/tasks`

### [ ] plugins/dev-utils/skills/task-agent/SKILL.md
- Line `51`: `- Default Hermes Agent project root: For this user, prefer creating and managing tasks under the Hermes Agent project's tasks directory: /Users/richardfremmerlid/Projects/hermes-agent/tasks. The task_`
- Line `57`: `python3 ./scripts/task_manager.py create "Short Title" --lane backlog --dir /Users/richardfremmerlid/Projects/hermes-agent/tasks`
- Line `60`: `export HERMES_TASKS_ROOT=/Users/richardfremmerlid/Projects/hermes-agent/tasks`
- Line `107`: `If a user preference exists for which repository should host kanban tasks, prefer honoring that explicit per-user preference. On this host the user prefers the Hermes Agent project root as the canonic`
- Line `111`: `- Honor explicit `--dir` overrides. If a caller provides `--dir`, always use it. Example: `python3 ./scripts/task_manager.py --dir /Users/richardfremmerlid/Projects/hermes-agent/tasks create "Title" -`
- Line `155`: `- Default project root override for this user's environment: /Users/richardfremmerlid/Projects/hermes-agent/tasks`
- Line `159`: `python3 ./scripts/task_manager.py --dir /Users/richardfremmerlid/Projects/hermes-agent/tasks create "Short Title" --lane backlog --objective "..." --acceptance "..."`

### [ ] plugins/dev-utils/skills/task-agent/references/assistant_preferences.md
- Line `3`: `- Default project root for this user's task operations: /Users/richardfremmerlid/Projects/hermes-agent/tasks`

### [ ] plugins/dev-utils/skills/task-agent/references/per-user-tasks-default.md
- Line `15`: `/Users/richardfremmerlid/Projects/hermes-agent/tasks`

### [ ] plugins/dev-utils/skills/task-agent/references/user-hermes-tasks-root.md
- Line `4`: `/Users/richardfremmerlid/Projects/hermes-agent/tasks`
- Line `9`: `- CLI: python3 ./scripts/task_manager.py create "Title" --lane backlog --dir /Users/richardfremmerlid/Projects/hermes-agent/tasks`
- Line `10`: `- Env var convenience: export HERMES_TASKS_ROOT=/Users/richardfremmerlid/Projects/hermes-agent/tasks`

### [ ] plugins/exploration-cycle-plugin/agents/runtime-observer-agent.md
- Line `45`: `1.  **Absolute paths:** Strip Unix paths like `/Users/username/` and Windows paths like `C:\Users\`.`
- Line `83`: `"offending_value": "/Users/richardfremmerlid/Projects/agent-plugins-skills/...",`

### [ ] plugins/exploration-cycle-plugin/assets/resources/design-thinking/03-Exploration-and-Design/dashboard-pattern-refactor/superpowers-copilot-sonnet-orchestration.md
- Line `14`: ``/Users/richardfremmerlid/Projects/AI-Research/07-Opportunities/03-Exploration-and-Design/dashboard-pattern-refactor/sme-orchestrator-implementation-plan.md``

### [ ] plugins/exploration-cycle-plugin/assets/resources/design-thinking/03-Exploration-and-Design/design-artifacts/superpowers-copilot-sonnet-orchestration.md
- Line `28`: `| Copilot CLI skill | `/Users/richardfremmerlid/Projects/AI-Research/.agents/skills/copilot-cli-agent/SKILL.md` |`
- Line `29`: `| superpowers analysis | `/Users/richardfremmerlid/Projects/AI-Research/01-Research/harnesses/superpowers/superpowers-analysis.md` |`
- Line `30`: `| Opp 3 design plan | `/Users/richardfremmerlid/Projects/AI-Research/07-Opportunities/03-Exploration-and-Design/exploration-cycle-plugin-design-plan.md` |`
- Line `38`: `2. Read the Copilot CLI skill: `/Users/richardfremmerlid/Projects/AI-Research/.agents/skills/copilot-cli-agent/SKILL.md``
- Line `43`: `python /Users/richardfremmerlid/Projects/AI-Research/.agents/skills/copilot-cli-agent/scripts/run_agent.py \`
- Line `420`: `cd /Users/richardfremmerlid/Projects/agent-plugins-skills`

### [ ] plugins/exploration-cycle-plugin/tests/test_technical_diagnostic_engine.py
- Line `25`: `target_paths=["plugins/foo/bar.py", "plugins/foo/scripts/baz.py"],`
- Line `28`: `cross_plugin_symlinks=["plugins/foo/skills/bar/scripts/baz.py"],`
- Line `52`: `assert "`plugins/foo/bar.py`" in brief`

### [ ] plugins/obsidian-wiki-engine/scripts/obsidian-parser/tests/test_parser.py
- Line `11`: `python -m unittest plugins/obsidian-integration/scripts/obsidian-parser/tests/test_parser.py`

### [ ] plugins/obsidian-wiki-engine/skills/obsidian-wiki-builder/SKILL.md
- Line `80`: `- The installer and helper agents should ask for and confirm the repository or filesystem scope before running discovery. By default prefer searching the project root only (e.g. /Users/you/projects/ag`
- Line `150`: `"wiki_root": "/Users/me/vault/wiki-root",`
- Line `153`: `"path": "/Users/me/vault/notes",`
- Line `160`: `"path": "/Users/me/docs/architecture",`

### [ ] plugins/plugin-manager/references/installer-bootstrap-architecture.md
- Line `95`: `We publish a tiny stub package to NPM (`@agent-plugins/cli`) whose ONLY job is to execute a `fetch()` call, download the Python `plugin_add.py` script to a temp folder, and spawn `python temp_script.p`
- Line `98`: `npx @agent-plugins/cli add richfrem/agent-plugins-skills`

### [ ] plugins/plugin-manager/references/locating_skills.md
- Line `49`: `/Users/me/projects/agent-plugins-skills — proceed? (Y/n)".`

### [ ] plugins/plugin-manager/scripts/plugin_add.py
- Line `298`: `anthropics/knowledge-work-plugins/engineering       → ("anthropics/knowledge-work-plugins", "engineering")`

### [ ] plugins/plugin-manager/scripts/plugin_remove.py
- Line `463`: `interactive TUI (or uses --plugins/--all for headless mode), calls`

### [ ] plugins/plugin-manager/skills/plugin-installer/SKILL.md
- Line `141`: `"skillPath": "plugins/my-plugin/skills/my-skill",`
- Line `193`: `| `anthropics/knowledge-work-plugins/engineering` | Clone repo, drill into `engineering/` as a single plugin |`
- Line `213`: `python ./scripts/plugin_add.py anthropics/knowledge-work-plugins/engineering`
- Line `243`: `--plugin plugins/my-plugin`
- Line `249`: `--plugin plugins/my-plugin --dry-run`
- Line `263`: `- When the user requests a search or install, confirm the filesystem scope before running any discovery. Present the chosen path in plain text and ask for explicit approval (e.g. "Search only /Users/m`
- Line `280`: `- **Plugin**: plugins/my-plugin (v1.2.0)`

### [ ] plugins/plugin-manager/skills/plugin-installer/references/locating_skills.md
- Line `49`: `/Users/me/projects/agent-plugins-skills — proceed? (Y/n)".`

### [ ] plugins/plugin-manager/skills/plugin-installer/scripts/plugin_add.py
- Line `298`: `anthropics/knowledge-work-plugins/engineering       → ("anthropics/knowledge-work-plugins", "engineering")`

### [ ] plugins/plugin-manager/skills/plugin-remover/scripts/plugin_remove.py
- Line `463`: `interactive TUI (or uses --plugins/--all for headless mode), calls`

