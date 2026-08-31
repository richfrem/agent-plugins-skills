# Portability Audit Report

## ⚠️ Standard — Hardcoded Path References

> The following files contain hardcoded `plugins/` references or absolute machine paths.
> The `fix-plugin-paths` skill must run until this report returns zero violations
> by either neutralizing the path or updating `plugin_paths_whitelist.json`.

### [ ] .github/copilot-instructions.md
- Line `189`: `**Do not reference:** `plugins/claude-cli`, `plugins/copilot-cli`, `plugins/gemini-cli` — all deleted.`
- Line `199`: `**Do not reference:** `plugins/rlm-factory`, `plugins/vector-db`, `plugins/memory-management` — all deleted.`
- Line `209`: `**Do not reference:** `plugins/adr-manager`, `plugins/coding-conventions`, `plugins/context-bundler`,`
- Line `210`: ``plugins/huggingface-utils`, `plugins/link-checker`, `plugins/mermaid-to-png`,`
- Line `211`: ``plugins/task-manager`, `plugins/voice-writer` — all deleted.`

### [ ] GEMINI.md
- Line `188`: `**Do not reference:** `plugins/claude-cli`, `plugins/copilot-cli`, `plugins/gemini-cli` — all deleted.`
- Line `198`: `**Do not reference:** `plugins/rlm-factory`, `plugins/vector-db`, `plugins/memory-management` — all deleted.`
- Line `208`: `**Do not reference:** `plugins/adr-manager`, `plugins/coding-conventions`, `plugins/context-bundler`,`
- Line `209`: ``plugins/huggingface-utils`, `plugins/link-checker`, `plugins/mermaid-to-png`,`
- Line `210`: ``plugins/task-manager`, `plugins/voice-writer` — all deleted.`

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

### [ ] plugins/agent-agentic-os/references/meta/anthropic-official-docs.md
- Line `43`: `Source: [GitHub: claude-plugins-official/plugins/skill-creator](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator)`
- Line `62`: `Source: [GitHub: claude-plugins-official/plugins/plugin-dev](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/plugin-dev)`

### [ ] plugins/agent-agentic-os/scripts/evaluate.py
- Line `47`: `# evaluate.py lives at plugins/autoresearch-improvement/scripts/evaluate.py`

### [ ] plugins/agent-agentic-os/scripts/init_autoresearch.py
- Line `32`: `[--plugin-root .agents/plugins/autoresearch-improvement]`

### [ ] plugins/agent-agentic-os/skills/os-eval-runner/scripts/evaluate.py
- Line `47`: `# evaluate.py lives at plugins/autoresearch-improvement/scripts/evaluate.py`

### [ ] plugins/agent-agentic-os/skills/os-eval-runner/scripts/init_autoresearch.py
- Line `32`: `[--plugin-root .agents/plugins/autoresearch-improvement]`

### [ ] plugins/agent-agentic-os/skills/os-improvement-loop/scripts/evaluate.py
- Line `47`: `# evaluate.py lives at plugins/autoresearch-improvement/scripts/evaluate.py`

### [ ] plugins/agent-orchestration/scripts/swarm_run.py
- Line `34`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-orchestration/skills/agent-swarm/scripts/swarm_run.py
- Line `34`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-orchestration/skills/orchestrator/scripts/swarm_run.py
- Line `34`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-memory/assets/references/research/summary.md
- Line `59`: `*   **Discovery CLI:** Scripts within self-contained plugins/skills architecture (Recursive Scanner)`

### [ ] plugins/agent-memory/scripts/swarm_run.py
- Line `34`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-memory/skills/rlm-cleanup-agent/scripts/swarm_run.py
- Line `34`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-memory/skills/rlm-curator/scripts/swarm_run.py
- Line `34`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-memory/skills/rlm-distill-agent/scripts/swarm_run.py
- Line `34`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-memory/skills/rlm-init/scripts/swarm_run.py
- Line `34`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-memory/skills/rlm-search/SKILL.md
- Line `69`: `# Example: Search plugins/scripts cache`

### [ ] plugins/agent-memory/skills/rlm-search/scripts/swarm_run.py
- Line `34`: `Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):`

### [ ] plugins/agent-scaffolders/commands/convert-plugin-to-apm.md
- Line `20`: `/convert-plugin-to-apm ./plugins/my-plugin --mode overlay --governance enterprise`

### [ ] plugins/agent-scaffolders/commands/mine-plugins.md
- Line `28`: `/mine-plugins claude-knowledgework-plugins/sales`
- Line `34`: `/mine-plugins plugins/legacy\ system`

### [ ] plugins/agent-scaffolders/commands/mine-skill.md
- Line `27`: `/mine-skill claude-knowledgework-plugins/sales/skills/call-prep`

### [ ] plugins/agent-scaffolders/references/examples/plugin-commands.md
- Line `548`: `@/home/user/.claude/plugins/my-plugin/config.json`

### [ ] plugins/agent-scaffolders/references/examples/plugin-features-reference.md
- Line `106`: `Read template: @/path/to/plugins/plugin-name/templates/report.md`

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
- Line `56`: `plugins/adr-manager/commands/adr-management.md  plugins/adr-manager/`
- Line `57`: `plugins/plugin-installer/hooks/hooks.json  plugins/plugin-installer/`
- Line `58`: `plugins/adr-manager/.claude-plugin/plugin.json  plugins/adr-manager/`
- Line `61`: `plugins/adr-manager/skills/adr-management/SKILL.md  None (skip)`
- Line `76`: `return Path(*parts[:idx+2])  # e.g., plugins/adr-manager/`

### [ ] plugins/agent-scaffolders/scripts/check_skill_boundaries.py
- Line `14`: `pythonheck_skill_boundaries.py temp/inventory.json --skill plugins/adr-manager/skills/adr-management`
- Line `62`: `r"re:/Users/.*",           # macOS absolute paths (e.g. /Users/robert/...)`
- Line `97`: `plugins/adr-manager/skills/adr-management/SKILL.md`
- Line `98`: `plugins/adr-manager/skills/adr-management/`
- Line `110`: `return Path(*parts[:idx+2])  # e.g., plugins/adr-manager/skills/adr-management`

### [ ] plugins/agent-scaffolders/scripts/fix_descriptions.py
- Line `14`: `"plugins/excel-to-csv/skills/excel-to-csv/SKILL.md"`
- Line `90`: `root_dir = '/Users/richardfremmerlid/Projects/agent-plugins-skills'`

### [ ] plugins/agent-scaffolders/scripts/fix_inside_plugin_symlinks.py
- Line `74`: `"""Extract plugin root from path like plugins/adr-manager/skills/adr-management/file.md"""`

### [ ] plugins/agent-scaffolders/scripts/fix_plugin_load_errors.py
- Line `25`: `NOTE: Claude Code scans ALL cached plugin versions under ~/.claude/plugins/cache/,`

### [ ] plugins/agent-scaffolders/scripts/path_reference_auditor.py
- Line `110`: `Walk all plugins/skills directories and find every ./reference.`

### [ ] plugins/agent-scaffolders/scripts/scaffold_agentic_workflow.py
- Line `365`: `Example: --plugin-dir plugins/my-plugin --mode ide`

### [ ] plugins/agent-scaffolders/scripts/validate_local_links.py
- Line `60`: `# Matches explicit strings like "plugins/my-plugin" or "plugins/rlm-factory/scripts"`

### [ ] plugins/agent-scaffolders/skills/analyze-plugin/references/003_plugin_skill_resource_sharing_via_mirrored_folder_structure_and_file_level_symlinks.md
- Line `117`: `- Real file at plugin root (e.g. `plugins/adr-manager/scripts/adr_manager.py`)`

### [ ] plugins/agent-scaffolders/skills/audit-plugin-l5/SKILL.md
- Line `27`: `Before executing this skill, ensure you know the exact path or name of the plugin you wish to audit (e.g., `plugins/oracle-legacy-system-analysis/xml-to-markdown`).`

### [ ] plugins/agent-scaffolders/skills/audit-plugin-l5/references/003_plugin_skill_resource_sharing_via_mirrored_folder_structure_and_file_level_symlinks.md
- Line `117`: `- Real file at plugin root (e.g. `plugins/adr-manager/scripts/adr_manager.py`)`

### [ ] plugins/agent-scaffolders/skills/audit-plugin/SKILL.md
- Line `125`: ``~/.claude/plugins/cache/`, not just the active `installPath`. Fixing source files`

### [ ] plugins/agent-scaffolders/skills/audit-plugin/references/003_plugin_skill_resource_sharing_via_mirrored_folder_structure_and_file_level_symlinks.md
- Line `117`: `- Real file at plugin root (e.g. `plugins/adr-manager/scripts/adr_manager.py`)`

### [ ] plugins/agent-scaffolders/skills/create-agentic-workflow/scripts/scaffold_agentic_workflow.py
- Line `365`: `Example: --plugin-dir plugins/my-plugin --mode ide`

### [ ] plugins/agent-scaffolders/skills/create-github-action/scripts/scaffold_agentic_workflow.py
- Line `365`: `Example: --plugin-dir plugins/my-plugin --mode ide`

### [ ] plugins/agent-scaffolders/skills/create-plugin/references/003_plugin_skill_resource_sharing_via_mirrored_folder_structure_and_file_level_symlinks.md
- Line `117`: `- Real file at plugin root (e.g. `plugins/adr-manager/scripts/adr_manager.py`)`

### [ ] plugins/agent-scaffolders/skills/create-skill/references/003_plugin_skill_resource_sharing_via_mirrored_folder_structure_and_file_level_symlinks.md
- Line `117`: `- Real file at plugin root (e.g. `plugins/adr-manager/scripts/adr_manager.py`)`

### [ ] plugins/agent-scaffolders/skills/ecosystem-authoritative-sources/SKILL.md
- Line `25`: `- **Foundational Specification**: `https://github.com/anthropics/claude-plugins-official/tree/main/plugins/plugin-dev``
- Line `70`: `- Relative path (same-repo monorepo): `"source": "./plugins/my-plugin"` — resolved from repo root`

### [ ] plugins/agent-scaffolders/skills/fix-plugin-paths/SKILL.md
- Line `39`: ``PROJECT_ROOT / "plugins/other-plugin/..."` at runtime. Cross-plugin script references`

### [ ] plugins/agent-scaffolders/skills/fix-plugin-paths/references/fix-plugin-paths.prompt.md
- Line `4`: `If a file inside `plugins/A/` references `plugins/A/scripts/foo.py`, replace with `./scripts/foo.py`.`
- Line `30`: `**BEFORE:** `e.g. "/Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/link-checker"``
- Line `31`: `**AFTER:**  `e.g. "<USER_HOME>/Projects/agent-plugins-skills/plugins/link-checker"``
- Line `69`: `- **Generic placeholder examples**: `plugins/my-plugin`, `plugins/<plugin-name>`, `plugins/link-checker`.`

### [ ] plugins/agent-scaffolders/skills/l5-red-team-auditor/references/003_plugin_skill_resource_sharing_via_mirrored_folder_structure_and_file_level_symlinks.md
- Line `117`: `- Real file at plugin root (e.g. `plugins/adr-manager/scripts/adr_manager.py`)`

### [ ] plugins/agent-scaffolders/skills/manage-marketplace/SKILL.md
- Line `46`: `{ "source": "./plugins/my-plugin-folder" }`
- Line `60`: `{ "source": { "source": "git-subdir", "url": "https://github.com/owner/repo", "path": "plugins/my-plugin" } }`
- Line `89`: `4.  Optional: use `metadata.pluginRoot` to shorten relative source paths. Setting `"pluginRoot": "./plugins"` lets you write `"source": "formatter"` instead of `"source": "./plugins/formatter"`.`

### [ ] plugins/agent-scaffolders/skills/manage-marketplace/acceptance-criteria.md
- Line `21`: `| **Hardcoded paths in hooks** | Plugin author guidance uses absolute host paths (e.g., `/home/user/.claude/plugins/my-plugin/run.sh`) instead of `${CLAUDE_PLUGIN_ROOT}`. |`

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

### [ ] plugins/agent-scaffolders/skills/path-reference-auditor/scripts/check_plugin_boundaries.py
- Line `14`: `pythonheck_plugin_boundaries.py temp/inventory.json --plugin plugins/adr-manager`
- Line `56`: `plugins/adr-manager/commands/adr-management.md  plugins/adr-manager/`
- Line `57`: `plugins/plugin-installer/hooks/hooks.json  plugins/plugin-installer/`
- Line `58`: `plugins/adr-manager/.claude-plugin/plugin.json  plugins/adr-manager/`
- Line `61`: `plugins/adr-manager/skills/adr-management/SKILL.md  None (skip)`
- Line `76`: `return Path(*parts[:idx+2])  # e.g., plugins/adr-manager/`

### [ ] plugins/agent-scaffolders/skills/path-reference-auditor/scripts/check_skill_boundaries.py
- Line `14`: `pythonheck_skill_boundaries.py temp/inventory.json --skill plugins/adr-manager/skills/adr-management`
- Line `62`: `r"re:/Users/.*",           # macOS absolute paths (e.g. /Users/robert/...)`
- Line `97`: `plugins/adr-manager/skills/adr-management/SKILL.md`
- Line `98`: `plugins/adr-manager/skills/adr-management/`
- Line `110`: `return Path(*parts[:idx+2])  # e.g., plugins/adr-manager/skills/adr-management`

### [ ] plugins/agent-scaffolders/skills/path-reference-auditor/scripts/fix_inside_plugin_symlinks.py
- Line `74`: `"""Extract plugin root from path like plugins/adr-manager/skills/adr-management/file.md"""`

### [ ] plugins/agent-scaffolders/skills/path-reference-auditor/scripts/path_reference_auditor.py
- Line `110`: `Walk all plugins/skills directories and find every ./reference.`

### [ ] plugins/cli-agents/references/routing_latency_findings.md
- Line `164`: `FROM /Users/richardfremmerlid/Projects/local-llm-bench/llama.cpp/models/gemma-4-12b-UD-Q4_K_XL.gguf`

### [ ] plugins/dev-utils/commands/create-sym-link.md
- Line `18`: `1. **Source path** — relative to repo root (e.g., `plugins/my-plugin/scripts/script.py`)`
- Line `19`: `2. **Destination path** — relative to repo root (e.g., `plugins/my-plugin/skills/my-skill/scripts/script.py`)`

### [ ] plugins/dev-utils/references/assistant_preferences.md
- Line `3`: `- Default project root for this user's task operations: /Users/richardfremmerlid/Projects/hermes-agent/tasks`

### [ ] plugins/dev-utils/references/per-user-tasks-default.md
- Line `15`: `/Users/richardfremmerlid/Projects/hermes-agent/tasks`

### [ ] plugins/dev-utils/references/user-hermes-tasks-root.md
- Line `4`: `/Users/richardfremmerlid/Projects/hermes-agent/tasks`
- Line `9`: `- CLI: python3 ./scripts/task_manager.py create "Title" --lane backlog --dir /Users/richardfremmerlid/Projects/hermes-agent/tasks`
- Line `10`: `- Env var convenience: export HERMES_TASKS_ROOT=/Users/richardfremmerlid/Projects/hermes-agent/tasks`

### [ ] plugins/dev-utils/skills/symlink-manager/references/003_plugin_skill_resource_sharing_via_mirrored_folder_structure_and_file_level_symlinks.md
- Line `117`: `- Real file at plugin root (e.g. `plugins/adr-manager/scripts/adr_manager.py`)`

### [ ] plugins/dev-utils/skills/task-agent/SKILL.md
- Line `47`: `- Default Hermes Agent project root: For this user, prefer creating and managing tasks under the Hermes Agent project's tasks directory: /Users/richardfremmerlid/Projects/hermes-agent/tasks. The task_`
- Line `53`: `python3 ./scripts/task_manager.py create "Short Title" --lane backlog --dir /Users/richardfremmerlid/Projects/hermes-agent/tasks`
- Line `56`: `export HERMES_TASKS_ROOT=/Users/richardfremmerlid/Projects/hermes-agent/tasks`
- Line `103`: `If a user preference exists for which repository should host kanban tasks, prefer honoring that explicit per-user preference. On this host the user prefers the Hermes Agent project root as the canonic`
- Line `107`: `- Honor explicit `--dir` overrides. If a caller provides `--dir`, always use it. Example: `python3 ./scripts/task_manager.py --dir /Users/richardfremmerlid/Projects/hermes-agent/tasks create "Title" -`
- Line `151`: `- Default project root override for this user's environment: /Users/richardfremmerlid/Projects/hermes-agent/tasks`
- Line `155`: `python3 ./scripts/task_manager.py --dir /Users/richardfremmerlid/Projects/hermes-agent/tasks create "Short Title" --lane backlog --objective "..." --acceptance "..."`

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

### [ ] plugins/plugin-manager/scripts/plugin_add.py
- Line `251`: `anthropics/knowledge-work-plugins/engineering       → ("anthropics/knowledge-work-plugins", "engineering")`

### [ ] plugins/plugin-manager/skills/plugin-installer/SKILL.md
- Line `137`: `"skillPath": "plugins/my-plugin/skills/my-skill",`
- Line `189`: `| `anthropics/knowledge-work-plugins/engineering` | Clone repo, drill into `engineering/` as a single plugin |`
- Line `209`: `python ./scripts/plugin_add.py anthropics/knowledge-work-plugins/engineering`
- Line `239`: `--plugin plugins/my-plugin`
- Line `245`: `--plugin plugins/my-plugin --dry-run`
- Line `259`: `- When the user requests a search or install, confirm the filesystem scope before running any discovery. Present the chosen path in plain text and ask for explicit approval (e.g. "Search only /Users/m`
- Line `276`: `- **Plugin**: plugins/my-plugin (v1.2.0)`

### [ ] plugins/plugin-manager/skills/plugin-installer/references/locating_skills.md
- Line `49`: `/Users/me/projects/agent-plugins-skills — proceed? (Y/n)".`

### [ ] plugins/plugin-manager/skills/plugin-installer/scripts/plugin_add.py
- Line `251`: `anthropics/knowledge-work-plugins/engineering       → ("anthropics/knowledge-work-plugins", "engineering")`

### [ ] plugins/spec-kitty-plugin/assets/templates/tasks.md
- Line `43`: `**CRITICAL**: The command returns JSON with `feature_dir` as an ABSOLUTE path (e.g., `/Users/robert/Code/project/kitty-specs/015-research-topic`).`

### [ ] plugins/spec-kitty-plugin/references/LLM_UNPACKAGING_INSTRUCTIONS.md
- Line `24`: `Access `bridge/plugins/tool_inventory.json` (included in this bundle) to see the list of tools available for registration in your agent's configuration.`

### [ ] plugins/spec-kitty-plugin/rules/AGENTS.md
- Line `15`: `- `/Users/robert/Code/myproject/kitty-specs/001-feature/spec.md``

### [ ] tasks/backlog/0010-bl-007-bridge-plugin-not-copying-assets-directory-during-plugin-install.md
- Line `4`: `plugins/task-manager/assets/templates/task-template.md exists in source but is missing from .agent/skills/task-agent/ after plugin-installer install. plugin-installer SKILL.md maps skills/ commands/ r`

### [ ] tasks/backlog/0011-bl-008-task-agent-skill-md-unclear-on-which-script-path-to-use-agents-use-wrong-path.md
- Line `4`: `task-agent SKILL.md does not clearly specify whether to call scripts from plugins/task-manager/skills/task-agent/scripts/ or .agent/skills/task-agent/scripts/. This session used the .agent/ installed `

### [ ] tasks/backlog/0015-standardize-all-plugin-templates-to-jinja-format.md
- Line `15`: `- **Reference pattern:** `plugins/agent-plugin-analyzer/assets/templates/README.md.jinja` is the target convention.`

### [ ] tasks/backlog/0021-finetuning-plugin-plan.md
- Line `65`: `| WS-A | Scaffold plugin shell | `plugins/agent-finetuning/README.md`, `CHANGELOG.md`, `.claude-plugin/plugin.json`, `evals/evals.json` |`
- Line `66`: `| WS-B | `setup-cuda-env` skill | `plugins/agent-finetuning/skills/setup-cuda-env/SKILL.md`, `evals.json` |`
- Line `67`: `| WS-C | `forge-dataset` skill | `plugins/agent-finetuning/skills/forge-dataset/SKILL.md`, `evals.json` |`
- Line `68`: `| WS-D | `run-finetuning` skill | `plugins/agent-finetuning/skills/run-finetuning/SKILL.md`, `evals.json` |`
- Line `69`: `| WS-E | `merge-and-export` skill | `plugins/agent-finetuning/skills/merge-and-export/SKILL.md`, `evals.json` |`
- Line `70`: `| WS-F | `finetuning-orchestrator` sub-agent | `plugins/agent-finetuning/agents/finetuning-orchestrator.md` |`
- Line `71`: `| WS-G | `hooks/session_end.py` | `plugins/agent-finetuning/hooks/session_end.py` |`

### [ ] tasks/backlog/2026-04-26-ecosystem-validation-plan.md
- Line `582`: `python3 plugins/copilot-cli/scripts/run_agent.py \`
- Line `588`: `python3 plugins/copilot-cli/scripts/run_agent.py \`

### [ ] tasks/backlog/copilot_prompt_0021-finetuning-plugin.md
- Line `8`: `3. **Paths**: Scaffold the plugin in `plugins/agent-finetuning/`. Update `huggingface-utils` in `plugins/huggingface-utils/`.`
- Line `15`: `Create `plugins/agent-finetuning/.claude-plugin/plugin.json`:`
- Line `33`: `Create `plugins/agent-finetuning/README.md` summarizing the generic fine-tuning pipeline (Setup -> Dataset -> Train -> Export).`
- Line `38`: `Path: `plugins/agent-finetuning/skills/setup-cuda-env/SKILL.md``
- Line `39`: `Path: `plugins/agent-finetuning/skills/setup-cuda-env/evals.json``
- Line `53`: `Path: `plugins/agent-finetuning/skills/forge-dataset/SKILL.md``
- Line `54`: `Path: `plugins/agent-finetuning/skills/forge-dataset/evals.json``
- Line `66`: `Path: `plugins/agent-finetuning/skills/run-finetuning/SKILL.md``
- Line `67`: `Path: `plugins/agent-finetuning/skills/run-finetuning/evals.json``
- Line `78`: `Path: `plugins/agent-finetuning/skills/merge-and-export/SKILL.md``
- Line `79`: `Path: `plugins/agent-finetuning/skills/merge-and-export/evals.json``
- Line `92`: `Path: `plugins/agent-finetuning/agents/finetuning-orchestrator.md``
- Line `107`: `1. **Review/Update `hf-init`**: Ensure `plugins/huggingface-utils/skills/hf-init/SKILL.md` is generic enough to initialize repo paths for model uploads, not just datasets.`
- Line `109`: `- Path: `plugins/huggingface-utils/skills/hf-model-upload/SKILL.md``
- Line `110`: `- Path: `plugins/huggingface-utils/skills/hf-model-upload/evals.json``

### [ ] tasks/backlog/copilot_prompt_0027_rsvp_speed_reader_lab.md
- Line `7`: `Run the `os-eval-lab-setup` skill to create a sibling evaluation repository for `plugins/rsvp-speed-reader`.`

### [ ] tasks/backlog/obsidian-rlm-llm-wiki/plan.md
- Line `14`: `| Migration strategy | Rename + retrofit `plugins/obsidian-integration` in place | Preserve all 6 existing skills, add 3 new ones |`
- Line `52`: `"wiki_root": "/Users/me/vaults/my-vault/wiki-root",`
- Line `54`: `{ "path": "/Users/me/vaults/my-vault/notes", "label": "daily-notes" },`
- Line `55`: `{ "path": "/Users/me/docs/architecture", "label": "arch-docs" },`
- Line `56`: `{ "path": "/Users/me/research", "label": "research" }`

### [ ] tasks/done/0020-os-architect-round2-fixes.md
- Line `22`: `Correct source path confirmed working: `plugins/copilot-cli/scripts/run_agent.py`.`

### [ ] tasks/done/copilot_prompt_0017.md
- Line `147`: `FIND_RESULT="plugins/mermaid-to-png/skills/convert-mermaid"  # substitute actual`

### [ ] tasks/done/copilot_prompt_0019b.md
- Line `161`: `python3 plugins/copilot-cli/scripts/run_agent.py \`
- Line `349`: `python3 plugins/copilot-cli/scripts/run_agent.py \`
- Line `355`: `python3 plugins/copilot-cli/scripts/run_agent.py \`
- Line `454`: `python3 plugins/copilot-cli/scripts/run_agent.py \`
- Line `458`: `python3 plugins/copilot-cli/scripts/run_agent.py \`

### [ ] tasks/done/copilot_prompt_0020.md
- Line `59`: `path is `plugins/copilot-cli/scripts/run_agent.py`.`
- Line `67`: `python3 plugins/copilot-cli/scripts/run_agent.py`
- Line `221`: `WS-B: python3 plugins/copilot-cli/scripts/run_agent.py appears in architect agent (grep confirm) — [ ]`

### [ ] tasks/done/copilot_prompt_0025-agentic-os-simplification.md
- Line `23`: ``/Users/richardfremmerlid/Projects/agent-plugins-skills``

### [ ] tasks/done/copilot_prompt_0026-agent-orchestration/stration/-simplification.md
- Line `36`: ``/Users/richardfremmerlid/Projects/agent-plugins-skills``

### [ ] tasks/done/copilot_prompt_0027-stale-refs-and-diagrams-cleanup.md
- Line `30`: ``/Users/richardfremmerlid/Projects/agent-plugins-skills``

### [ ] tasks/done/copilot_prompt_readme-update.md
- Line `27`: ``/Users/richardfremmerlid/Projects/agent-plugins-skills``

### [ ] tasks/done/obsidian-rlm-llm-wiki/plan.md
- Line `14`: `| Migration strategy | Rename + retrofit `plugins/obsidian-integration` in place | Preserve all 6 existing skills, add 3 new ones |`
- Line `52`: `"wiki_root": "/Users/me/vaults/my-vault/wiki-root",`
- Line `54`: `{ "path": "/Users/me/vaults/my-vault/notes", "label": "daily-notes" },`
- Line `55`: `{ "path": "/Users/me/docs/architecture", "label": "arch-docs" },`
- Line `56`: `{ "path": "/Users/me/research", "label": "research" }`

