# Portability Audit Report

> ⚠️ **Action Required**: The following files contain hardcoded `plugins/` references or absolute machine paths.
> The `fix-plugin-paths` skill must run until this report returns zero violations by either neutralizing the path or updating `plugin_paths_whitelist.json`.

### [ ] CLAUDE.md
- Line `26`: `python plugins/plugin-manager/scripts/install_all_plugins.py`
- Line `29`: `python plugins/plugin-manager/scripts/install_all_plugins.py --dry-run`
- Line `38`: `python plugins/plugin-manager/scripts/plugin_add.py`
- Line `41`: `python plugins/plugin-manager/scripts/plugin_add.py richfrem/agent-plugins-skills`
- Line `115`: `All ecosystem management lives in `plugins/plugin-manager/scripts/`:`

### [ ] INSTALL.md
- Line `113`: `python plugins/plugin-manager/scripts/plugin_add.py --plugin <plugin-name>`
- Line `116`: `python plugins/plugin-manager/scripts/plugin_add.py --all`

### [ ] README.md
- Line `44`: `The `os-nightly-evolver` agent runs the INNER flywheel autonomously overnight — delegating mutation proposals to Gemini CLI (cheap/fast) while using `evaluate.py` as the locked KEEP/DISCARD gate. No h`
- Line `80`: `- [`os-guide`](plugins/agent-agentic-os/skills/os-guide/SKILL.md) — master orientation + skill taxonomy`
- Line `81`: `- [`os-improvement-loop`](plugins/agent-agentic-os/skills/os-improvement-loop/SKILL.md) — OUTER flywheel: 7-step session improvement protocol`
- Line `82`: `- [`os-eval-lab-setup`](plugins/agent-agentic-os/skills/os-eval-lab-setup/SKILL.md) — bootstrap eval experiment dir (evals.json, results.tsv, program.md)`
- Line `83`: `- [`os-eval-runner`](plugins/agent-agentic-os/skills/os-eval-runner/SKILL.md) — INNER flywheel gate: evaluate.py KEEP/DISCARD engine`
- Line `84`: `- [`os-skill-improvement`](plugins/agent-agentic-os/skills/os-skill-improvement/SKILL.md) — RED-GREEN-REFACTOR skill mutation`
- Line `85`: `- [`os-eval-backport`](plugins/agent-agentic-os/skills/os-eval-backport/SKILL.md) — backport approved improvements to master plugin sources`
- Line `86`: `- [`os-memory-manager`](plugins/agent-agentic-os/skills/os-memory-manager/SKILL.md) — Phase 6/7 learning promotion to persistent memory`
- Line `87`: `- [`os-improvement-report`](plugins/agent-agentic-os/skills/os-improvement-report/SKILL.md) — progress charts and score trajectory reports`
- Line `88`: `- [`os-init`](plugins/agent-agentic-os/skills/os-init/SKILL.md) — OS bootstrap and kernel initialization`
- Line `89`: `- [`os-clean-locks`](plugins/agent-agentic-os/skills/os-clean-locks/SKILL.md) — directory lock recovery`
- Line `90`: `- [`todo-check`](plugins/agent-agentic-os/skills/todo-check/SKILL.md) — session TODO hygiene`
- Line `93`: `- [`os-learning-loop`](plugins/agent-agentic-os/agents/os-learning-loop.md) — retrospective + friction analysis sub-agent`
- Line `94`: `- [`os-nightly-evolver`](plugins/agent-agentic-os/agents/os-nightly-evolver.md) — bounded autonomous overnight skill evolution (Gemini CLI mutations + evaluate.py gate)`
- Line `95`: `- [`os-health-check`](plugins/agent-agentic-os/agents/os-health-check.md) — OS liveness metrics`
- Line `96`: `- [`agentic-os-setup`](plugins/agent-agentic-os/agents/agentic-os-setup.md) — OS initialization agent`
- Line `102`: `- [`orchestrator`](plugins/agent-loops/skills/orchestrator/SKILL.md) — intelligent task router and lifecycle manager`
- Line `103`: `- [`learning-loop`](plugins/agent-loops/skills/learning-loop/SKILL.md) — research, contextual integration, memory persistence`
- Line `104`: `- [`dual-loop`](plugins/agent-loops/skills/dual-loop/SKILL.md) — inner execution / outer verification for multi-step tasks`
- Line `105`: `- [`agent-swarm`](plugins/agent-loops/skills/agent-swarm/SKILL.md) — parallelized concurrent sub-agents on independent worktrees`
- Line `106`: `- [`red-team-review`](plugins/agent-loops/skills/red-team-review/SKILL.md) — adversarial multi-agent evaluation`
- Line `112`: `- [`verification-before-completion`](plugins/agent-execution-disciplines/skills/verification-before-completion/SKILL.md) — forces shell verification before claiming completion *(35/40 HIGH — **autores`
- Line `113`: `- [`test-driven-development`](plugins/agent-execution-disciplines/skills/test-driven-development/SKILL.md) — RED-GREEN-REFACTOR compliance *(35/40 HIGH)*`
- Line `114`: `- [`using-git-worktrees`](plugins/agent-execution-disciplines/skills/using-git-worktrees/SKILL.md) — isolated worktree sandboxing *(33/40 HIGH — best DETERMINISTIC first loop candidate)*`
- Line `115`: `- [`systematic-debugging`](plugins/agent-execution-disciplines/skills/systematic-debugging/SKILL.md) — structured root cause analysis *(22/40 LOW)*`
- Line `116`: `- [`finishing-a-development-branch`](plugins/agent-execution-disciplines/skills/finishing-a-development-branch/SKILL.md) — safe git branch lifecycle *(16/40 LOW)*`
- Line `117`: `- [`requesting-code-review`](plugins/agent-execution-disciplines/skills/requesting-code-review/SKILL.md) — structured review request protocol *(28/40 MEDIUM)*`
- Line `123`: `- [`create-plugin`](plugins/agent-scaffolders/skills/create-plugin/SKILL.md) · [`create-skill`](plugins/agent-scaffolders/skills/create-skill/SKILL.md) · [`create-sub-agent`](plugins/agent-scaffolders`
- Line `124`: `- [`create-command`](plugins/agent-scaffolders/skills/create-command/SKILL.md) · [`create-hook`](plugins/agent-scaffolders/skills/create-hook/SKILL.md) · [`create-github-action`](plugins/agent-scaffol`
- Line `125`: `- [`create-agentic-workflow`](plugins/agent-scaffolders/skills/create-agentic-workflow/SKILL.md) · [`create-azure-agent`](plugins/agent-scaffolders/skills/create-azure-agent/SKILL.md)`
- Line `126`: `- [`create-docker-skill`](plugins/agent-scaffolders/skills/create-docker-skill/SKILL.md) · [`create-mcp-integration`](plugins/agent-scaffolders/skills/create-mcp-integration/SKILL.md)`
- Line `127`: `- [`create-stateful-skill`](plugins/agent-scaffolders/skills/create-stateful-skill/SKILL.md) · [`manage-marketplace`](plugins/agent-scaffolders/skills/manage-marketplace/SKILL.md)`
- Line `133`: `- [`l5-red-team-auditor`](plugins/agent-plugin-analyzer/skills/l5-red-team-auditor/SKILL.md) — 39-point L5 maturity matrix audit`
- Line `134`: `- [`audit-plugin`](plugins/agent-plugin-analyzer/skills/audit-plugin/SKILL.md) · [`audit-plugin-l5`](plugins/agent-plugin-analyzer/skills/audit-plugin-l5/SKILL.md)`
- Line `135`: `- [`analyze-plugin`](plugins/agent-plugin-analyzer/skills/analyze-plugin/SKILL.md) · [`self-audit`](plugins/agent-plugin-analyzer/skills/self-audit/SKILL.md) *(32/40 HIGH)*`
- Line `136`: `- [`mine-skill`](plugins/agent-plugin-analyzer/skills/mine-skill/SKILL.md) · [`mine-plugins`](plugins/agent-plugin-analyzer/skills/mine-plugins/SKILL.md)`
- Line `137`: `- [`path-reference-auditor`](plugins/agent-plugin-analyzer/skills/path-reference-auditor/SKILL.md) · [`synthesize-learnings`](plugins/agent-plugin-analyzer/skills/synthesize-learnings/SKILL.md)`
- Line `138`: `- [`eval-autoresearch-fit`](plugins/agent-plugin-analyzer/skills/eval-autoresearch-fit/SKILL.md) — score any skill for Karpathy autoresearch loop viability; update `summary-ranked-skills.json` *(25/40`
- Line `144`: `- [`claude-cli-agent`](plugins/claude-cli/skills/claude-cli-agent/SKILL.md) · [`claude-project-setup`](plugins/claude-cli/skills/claude-project-setup/SKILL.md)`
- Line `145`: `- [`copilot-cli-agent`](plugins/copilot-cli/skills/copilot-cli-agent/SKILL.md) — GPT-5 mini via Copilot CLI; used in autoresearch mutation delegation`
- Line `146`: `- [`gemini-cli-agent`](plugins/gemini-cli/skills/gemini-cli-agent/SKILL.md) · [`antigravity-project-setup`](plugins/gemini-cli/skills/antigravity-project-setup/SKILL.md)`
- Line `152`: `- [`coding-conventions-agent`](plugins/coding-conventions/skills/coding-conventions-agent/SKILL.md)`
- Line `158`: `- [`context-bundler`](plugins/context-bundler/skills/context-bundler/SKILL.md) *(29/40 MEDIUM)*`
- Line `159`: `- [`red-team-bundler`](plugins/context-bundler/skills/red-team-bundler/SKILL.md) — structured red team review payload generator`
- Line `165`: `- [`dependency-management`](plugins/dependency-management/skills/dependency-management/SKILL.md)`
- Line `171`: `- [`excel-to-csv`](plugins/excel-to-csv/skills/excel-to-csv/SKILL.md)`
- Line `177`: `- [`exploration-workflow`](plugins/exploration-cycle-plugin/skills/exploration-workflow/SKILL.md) · [`exploration-session-brief`](plugins/exploration-cycle-plugin/skills/exploration-session-brief/SKIL`
- Line `178`: `- [`business-requirements-capture`](plugins/exploration-cycle-plugin/skills/business-requirements-capture/SKILL.md) · [`business-workflow-doc`](plugins/exploration-cycle-plugin/skills/business-workflo`
- Line `179`: `- [`user-story-capture`](plugins/exploration-cycle-plugin/skills/user-story-capture/SKILL.md) · [`exploration-handoff`](plugins/exploration-cycle-plugin/skills/exploration-handoff/SKILL.md)`
- Line `180`: `- [`exploration-optimizer`](plugins/exploration-cycle-plugin/skills/exploration-optimizer/SKILL.md)`
- Line `183`: `- [`exploration-orchestrator`](plugins/exploration-cycle-plugin/skills/deferred/exploration-orchestrator/SKILL.md) — full-cycle orchestrator coordinating discovery agents end-to-end`
- Line `184`: `- [`prototype-builder`](plugins/exploration-cycle-plugin/skills/deferred/prototype-builder/SKILL.md) — builds exploratory prototypes to make ambiguous product direction concrete`
- Line `190`: `- [`spec-kitty-specify`](plugins/spec-kitty-plugin/skills/spec-kitty-specify/SKILL.md) · [`spec-kitty-plan`](plugins/spec-kitty-plugin/skills/spec-kitty-plan/SKILL.md) · [`spec-kitty-tasks`](plugins/s`
- Line `191`: `- [`spec-kitty-implement`](plugins/spec-kitty-plugin/skills/spec-kitty-implement/SKILL.md) · [`spec-kitty-review`](plugins/spec-kitty-plugin/skills/spec-kitty-review/SKILL.md) · [`spec-kitty-merge`](p`
- Line `192`: `- [`spec-kitty-analyze`](plugins/spec-kitty-plugin/skills/spec-kitty-analyze/SKILL.md) · [`spec-kitty-accept`](plugins/spec-kitty-plugin/skills/spec-kitty-accept/SKILL.md) · [`spec-kitty-clarify`](plu`
- Line `193`: `- [`spec-kitty-research`](plugins/spec-kitty-plugin/skills/spec-kitty-research/SKILL.md) · [`spec-kitty-dashboard`](plugins/spec-kitty-plugin/skills/spec-kitty-dashboard/SKILL.md) · [`spec-kitty-statu`
- Line `194`: `- [`spec-kitty-checklist`](plugins/spec-kitty-plugin/skills/spec-kitty-checklist/SKILL.md) · [`spec-kitty-constitution`](plugins/spec-kitty-plugin/skills/spec-kitty-constitution/SKILL.md)`
- Line `195`: `- [`spec-kitty-tasks-outline`](plugins/spec-kitty-plugin/skills/spec-kitty-tasks-outline/SKILL.md) · [`spec-kitty-tasks-finalize`](plugins/spec-kitty-plugin/skills/spec-kitty-tasks-finalize/SKILL.md) `
- Line `196`: `- [`spec-kitty-workflow`](plugins/spec-kitty-plugin/skills/spec-kitty-workflow/SKILL.md) · [`spec-kitty-sync-plugin`](plugins/spec-kitty-plugin/skills/spec-kitty-sync-plugin/SKILL.md)`
- Line `202`: `- [`link-checker-agent`](plugins/link-checker/skills/link-checker-agent/SKILL.md)`
- Line `208`: `- [`markdown-to-msword-converter`](plugins/markdown-to-msword-converter/skills/markdown-to-msword-converter/SKILL.md)`
- Line `214`: `- [`memory-management`](plugins/memory-management/skills/memory-management/SKILL.md)`
- Line `220`: `- [`convert-mermaid`](plugins/mermaid-to-png/skills/convert-mermaid/SKILL.md) *(autoresearch score: 30/40 MEDIUM)*`
- Line `226`: `- [`obsidian-init`](plugins/obsidian-integration/skills/obsidian-init/SKILL.md) · [`obsidian-vault-crud`](plugins/obsidian-integration/skills/obsidian-vault-crud/SKILL.md)`
- Line `227`: `- [`obsidian-canvas-architect`](plugins/obsidian-integration/skills/obsidian-canvas-architect/SKILL.md) · [`obsidian-graph-traversal`](plugins/obsidian-integration/skills/obsidian-graph-traversal/SKIL`
- Line `228`: `- [`obsidian-markdown-mastery`](plugins/obsidian-integration/skills/obsidian-markdown-mastery/SKILL.md) · [`obsidian-bases-manager`](plugins/obsidian-integration/skills/obsidian-bases-manager/SKILL.md`
- Line `234`: `- [`plugin-installer`](plugins/plugin-manager/skills/plugin-installer/SKILL.md) — local symlink deployment from source to agent environments`
- Line `235`: `- [`auto-update-plugins`](plugins/plugin-manager/skills/auto-update-plugins/SKILL.md) — pull-based sync via SessionStart hook`
- Line `236`: `- [`maintain-plugins`](plugins/plugin-manager/skills/maintain-plugins/SKILL.md)`
- Line `237`: `- [`replicate-plugin`](plugins/plugin-manager/skills/replicate-plugin/SKILL.md)`
- Line `243`: `- [`rlm-init`](plugins/rlm-factory/skills/rlm-init/SKILL.md) · [`rlm-curator`](plugins/rlm-factory/skills/rlm-curator/SKILL.md) · [`rlm-search`](plugins/rlm-factory/skills/rlm-search/SKILL.md)`
- Line `244`: `- [`rlm-distill-agent`](plugins/rlm-factory/skills/rlm-distill-agent/SKILL.md) · [`rlm-distill-ollama`](plugins/rlm-factory/skills/rlm-distill-ollama/SKILL.md) · [`rlm-cleanup-agent`](plugins/rlm-fact`
- Line `245`: `- [`ollama-launch`](plugins/rlm-factory/skills/ollama-launch/SKILL.md)`
- Line `251`: `- [`rsvp-reading`](plugins/rsvp-speed-reader/skills/rsvp-reading/SKILL.md) · [`rsvp-comprehension-agent`](plugins/rsvp-speed-reader/skills/rsvp-comprehension-agent/SKILL.md)`
- Line `257`: `- [`ecosystem-standards`](plugins/agent-skill-open-specifications/skills/ecosystem-standards/SKILL.md)`
- Line `258`: `- [`ecosystem-authoritative-sources`](plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/SKILL.md)`
- Line `264`: `- [`task-agent`](plugins/task-manager/skills/task-agent/SKILL.md)`
- Line `270`: `- [`tool-inventory`](plugins/tool-inventory/skills/tool-inventory/SKILL.md) · [`tool-inventory-init`](plugins/tool-inventory/skills/tool-inventory-init/SKILL.md)`
- Line `276`: `- [`vector-db-init`](plugins/vector-db/skills/vector-db-init/SKILL.md) · [`vector-db-launch`](plugins/vector-db/skills/vector-db-launch/SKILL.md)`
- Line `277`: `- [`vector-db-ingest`](plugins/vector-db/skills/vector-db-ingest/SKILL.md) · [`vector-db-search`](plugins/vector-db/skills/vector-db-search/SKILL.md)`
- Line `278`: `- [`vector-db-cleanup`](plugins/vector-db/skills/vector-db-cleanup/SKILL.md)`
- Line `284`: `- [`humanize`](plugins/voice-writer/skills/humanize/SKILL.md)`
- Line `290`: `- [`hf-init`](plugins/huggingface-utils/skills/hf-init/SKILL.md) · [`hf-upload`](plugins/huggingface-utils/skills/hf-upload/SKILL.md)`
- Line `296`: `- [`adr-management`](plugins/adr-manager/skills/adr-management/SKILL.md)`

### [ ] bootstrap.py
- Line `71`: `"plugins/plugin-manager/scripts/plugin_add.py",`
- Line `72`: `"plugins/plugin-manager/scripts/bridge_installer.py"`

### [ ] plugins/agent-agentic-os/references/vision.md
- Line `548`: `- `/Users/richardfremmerlid/Projects/manchurian-agent-poc` — full PoC with red team assessments from Gemini, Claude, and Copilot CLI`

### [ ] plugins/agent-agentic-os/scripts/evaluate.py
- Line `45`: `# evaluate.py lives at plugins/autoresearch-improvement/scripts/evaluate.py`

### [ ] plugins/agent-agentic-os/scripts/init_autoresearch.py
- Line `29`: `python plugins/autoresearch-improvement/scripts/init_autoresearch.py \\`
- Line `32`: `[--plugin-root plugins/autoresearch-improvement]`
- Line `60`: `# or inside the full plugin tree (plugins/agent-agentic-os/skills/os-eval-runner/).`
- Line `167`: `"Defaults to plugins/autoresearch-improvement."`

### [ ] plugins/agent-agentic-os/skills/os-eval-backport/SKILL.md
- Line `46`: `The canonical plugin path in `agent-plugins-skills` (e.g. `plugins/link-checker`).`

### [ ] plugins/agent-agentic-os/skills/os-eval-lab-setup/SKILL.md
- Line `49`: `The canonical plugin path in `agent-plugins-skills` (e.g. `plugins/link-checker`). This is`

### [ ] plugins/agent-agentic-os/skills/os-eval-runner/SKILL.md
- Line `455`: `| `.agents/skills/os-eval-runner/` (if patched) | Deployed Engine | `plugins/agent-agentic-os/skills/os-eval-runner/` |`

### [ ] plugins/agent-agentic-os/skills/os-eval-runner/scripts/evaluate.py
- Line `45`: `# evaluate.py lives at plugins/autoresearch-improvement/scripts/evaluate.py`

### [ ] plugins/agent-agentic-os/skills/os-eval-runner/scripts/init_autoresearch.py
- Line `29`: `python plugins/autoresearch-improvement/scripts/init_autoresearch.py \\`
- Line `32`: `[--plugin-root plugins/autoresearch-improvement]`
- Line `60`: `# or inside the full plugin tree (plugins/agent-agentic-os/skills/os-eval-runner/).`
- Line `167`: `"Defaults to plugins/autoresearch-improvement."`

### [ ] plugins/agent-agentic-os/skills/os-improvement-loop/scripts/evaluate.py
- Line `45`: `# evaluate.py lives at plugins/autoresearch-improvement/scripts/evaluate.py`

### [ ] plugins/agent-execution-disciplines/references/root-cause-tracing.md
- Line `36`: `Error: git init failed in /Users/jesse/project/packages/core`

### [ ] plugins/agent-execution-disciplines/skills/verification-before-completion/autoresearch/README.md
- Line `13`: `cd plugins/agent-execution-disciplines/skills/verification-before-completion`
- Line `105`: `Target skill: plugins/agent-execution-disciplines/skills/verification-before-completion`

### [ ] plugins/agent-plugin-analyzer/README.md
- Line `79`: `Analyze the sales plugin at claude-knowledgework-plugins/sales`

### [ ] plugins/agent-plugin-analyzer/commands/mine-plugins.md
- Line `28`: `/mine-plugins claude-knowledgework-plugins/sales`
- Line `34`: `/mine-plugins plugins/legacy\ system`

### [ ] plugins/agent-plugin-analyzer/commands/mine-skill.md
- Line `27`: `/mine-skill claude-knowledgework-plugins/sales/skills/call-prep`

### [ ] plugins/agent-plugin-analyzer/references/broken_symlinks_repair_report.md
- Line `5`: `| `plugins/agent-plugin-analyzer/references/patterns/evals.json` | `../../evals/evals.json` | ⚠️  Unknown target | ⚠️  Manual Fix |`
- Line `6`: `| `plugins/agent-plugin-analyzer/references/patterns/CONNECTORS.md` | `../../CONNECTORS.md` | ⚠️  Unknown target | ⚠️  Manual Fix |`
- Line `7`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/evals.json` | `../../../../references/audit-plugin/patterns/evals.json` | ⚠️  Unknown target | ⚠️  Manual Fix |`
- Line `8`: `| `plugins/agent-plugin-analyzer/skills/analyze-plugin/references/diagrams/analyze-plugin-flow.mmd` | `../../../../references/analyze-plugin/diagrams/analyze-plugin-flow.mmd` | Found elsewhere: plugin`
- Line `9`: `| `plugins/agent-plugin-analyzer/skills/analyze-plugin/assets/resources/analyze-plugin-flow.mmd` | `../../../../assets/resources/analyze-plugin-flow.mmd` | Found elsewhere: plugins/agent-plugin-analyz`
- Line `10`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin-l5/references/diagrams/audit-plugin-l5-flow.mmd` | `../../../../references/audit-plugin-l5/diagrams/audit-plugin-l5-flow.mmd` | Found elsewhere: pl`
- Line `11`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin-l5/assets/resources/audit-plugin-l5-flow.mmd` | `../../../../assets/resources/audit-plugin-l5-flow.mmd` | Found elsewhere: plugins/agent-plugin-ana`
- Line `12`: `| `.agents/skills/replicate-plugin/references/plugin_replicator_diagram.mmd` | `../../../../assets/diagrams/plugin_replicator_diagram.mmd` | Found elsewhere: plugins/plugin-manager/assets/diagrams/plu`
- Line `13`: `| `.agents/skills/replicate-plugin/assets/resources/plugin_replicator_diagram.mmd` | `../../../../assets/resources/plugin_replicator_diagram.mmd` | Found elsewhere: plugins/plugin-manager/assets/diagr`
- Line `14`: `| `.agents/skills/maintain-plugins/references/cleanup_flow.mmd` | `../../../../assets/diagrams/cleanup_flow.mmd` | Found elsewhere: plugins/plugin-manager/assets/diagrams/cleanup_flow.mmd | ⚠️  Manual`
- Line `15`: `| `.agents/skills/maintain-plugins/assets/resources/cleanup_flow.mmd` | `../../../../assets/resources/cleanup_flow.mmd` | Found elsewhere: plugins/plugin-manager/assets/diagrams/cleanup_flow.mmd | ⚠️ `
- Line `16`: `| `.agents/skills/plugin-installer/references/agent_bridge_diagram.mmd` | `../../../../assets/diagrams/agent_bridge_diagram.mmd` | Found elsewhere: plugins/plugin-manager/assets/diagrams/agent_bridge_`
- Line `17`: `| `.agents/skills/plugin-installer/references/ecosystem_system_bridge.mmd` | `../../../../assets/diagrams/ecosystem_system_bridge.mmd` | Found elsewhere: plugins/plugin-manager/assets/diagrams/ecosyst`
- Line `18`: `| `.agents/skills/tool-inventory/references/tool-inventory-workflow.mmd` | `../../../../assets/diagrams/tool-inventory-workflow.mmd` | Found elsewhere: plugins/tool-inventory/assets/diagrams/tool-inve`
- Line `19`: `| `.agents/skills/tool-inventory/references/diagrams/legacy-architecture/Tool_Architecture_Domain_Model.mmd` | `../../../../../references/tool-inventory/diagrams/legacy-architecture/Tool_Architecture_`
- Line `20`: `| `.agents/skills/tool-inventory/references/diagrams/legacy-architecture/Tool_Architecture_Domain_Model.png` | `../../../../../references/tool-inventory/diagrams/legacy-architecture/Tool_Architecture_`
- Line `21`: `| `.agents/skills/rsvp-reading/references/diagrams/rsvp-reading-flow.mmd` | `../../../../references/rsvp-reading/diagrams/rsvp-reading-flow.mmd` | Found elsewhere: plugins/rsvp-speed-reader/assets/dia`
- Line `23`: `| `.agents/skills/continuous-skill-optimizer/references/resources/continuous-skill-optimizer-flow.mmd` | `../../../../references/continuous-skill-optimizer/resources/continuous-skill-optimizer-flow.mm`
- Line `24`: `| `.agents/skills/continuous-skill-optimizer/references/diagrams/continuous-skill-optimizer-flow.mmd` | `../../../../references/continuous-skill-optimizer/diagrams/continuous-skill-optimizer-flow.mmd``
- Line `30`: `| `.agents/skills/manage-marketplace/manage-marketplace-flow.mmd` | `../../../assets/resources/manage-marketplace-flow.mmd` | Found elsewhere: plugins/agent-scaffolders/assets/diagrams/manage-marketpl`
- Line `43`: `| `.agents/skills/task-agent/references/task-manager-workflow.mmd` | `../../../../assets/diagrams/task-manager-workflow.mmd` | Found elsewhere: plugins/task-manager/assets/diagrams/task-manager-workfl`
- Line `44`: `| `plugins/rlm-factory/references/research/summary.md` | `../../../../assets/references/research/summary.md` | Found elsewhere: plugins/rlm-factory/assets/references/research/summary.md | ⚠️  Manual F`
- Line `45`: `| `plugins/rlm-factory/references/research/2512.24601v1.pdf` | `../../../../assets/references/research/2512.24601v1.pdf` | Found elsewhere: plugins/rlm-factory/assets/references/research/2512.24601v1.`
- Line `46`: `| `plugins/rlm-factory/references/examples/rlm_profiles.json` | `../../../../assets/references/examples/rlm_profiles.json` | Found elsewhere: plugins/rlm-factory/assets/references/examples/rlm_profile`
- Line `47`: `| `plugins/rlm-factory/references/examples/rlm_summary_cache_manifest.json` | `../../../../assets/references/examples/rlm_summary_cache_manifest.json` | Found elsewhere: plugins/rlm-factory/assets/ref`
- Line `48`: `| `plugins/rlm-factory/references/examples/rlm_tools_manifest.json` | `../../../../assets/references/examples/rlm_tools_manifest.json` | Found elsewhere: plugins/rlm-factory/assets/references/examples`
- Line `49`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm_mechanism_workflow.png` | `../../../../assets/references/diagrams/rlm_mechanism_workflow.png` | Found elsewhere: plugins/rlm-factory/assets/`
- Line `50`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm_late_binding_flow.mmd` | `../../../../assets/references/diagrams/rlm_late_binding_flow.mmd` | Found elsewhere: plugins/rlm-factory/assets/di`
- Line `51`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm-factory-architecture.png` | `../../../../assets/references/diagrams/rlm-factory-architecture.png` | Found elsewhere: plugins/rlm-factory/ass`
- Line `52`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm-factory-architecture.mmd` | `../../../../assets/references/diagrams/rlm-factory-architecture.mmd` | Found elsewhere: plugins/rlm-factory/ass`
- Line `53`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm_tool_enrichment_flow.mmd` | `../../../../assets/references/diagrams/rlm_tool_enrichment_flow.mmd` | Found elsewhere: plugins/rlm-factory/ass`
- Line `54`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm_mechanism_workflow.mmd` | `../../../../assets/references/diagrams/rlm_mechanism_workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/`
- Line `55`: `| `.agents/skills/rlm-distill-agent/references/diagrams/workflow.mmd` | `../../../../assets/references/diagrams/workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/workflow.mmd | ⚠️  `
- Line `56`: `| `.agents/skills/rlm-distill-agent/references/diagrams/logic.mmd` | `../../../../assets/references/diagrams/logic.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/logic.mmd | ⚠️  Manual Fi`
- Line `57`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm-factory-dual-path.mmd` | `../../../../assets/references/diagrams/rlm-factory-dual-path.mmd` | Found elsewhere: plugins/rlm-factory/assets/di`
- Line `58`: `| `.agents/skills/rlm-distill-agent/references/diagrams/unpacking.mmd` | `../../../../assets/references/diagrams/unpacking.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/unpacking.mmd | ⚠`
- Line `59`: `| `.agents/skills/rlm-distill-agent/references/diagrams/search_process.mmd` | `../../../../assets/references/diagrams/search_process.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/search_`
- Line `60`: `| `.agents/skills/rlm-distill-agent/references/diagrams/distillation_process.mmd` | `../../../../assets/references/diagrams/distillation_process.mmd` | Found elsewhere: plugins/rlm-factory/assets/diag`
- Line `61`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm-factory-dual-path.png` | `../../../../assets/references/diagrams/rlm-factory-dual-path.png` | Found elsewhere: plugins/rlm-factory/assets/di`
- Line `62`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm-factory-workflow.mmd` | `../../../../assets/references/diagrams/rlm-factory-workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diag`
- Line `63`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm_mechanism_workflow.png` | `../../../../assets/references/diagrams/rlm_mechanism_workflow.png` | Found elsewhere: plugins/rlm-factory/assets`
- Line `64`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm_late_binding_flow.mmd` | `../../../../assets/references/diagrams/rlm_late_binding_flow.mmd` | Found elsewhere: plugins/rlm-factory/assets/d`
- Line `65`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm-factory-architecture.png` | `../../../../assets/references/diagrams/rlm-factory-architecture.png` | Found elsewhere: plugins/rlm-factory/as`
- Line `66`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm-factory-architecture.mmd` | `../../../../assets/references/diagrams/rlm-factory-architecture.mmd` | Found elsewhere: plugins/rlm-factory/as`
- Line `67`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm_tool_enrichment_flow.mmd` | `../../../../assets/references/diagrams/rlm_tool_enrichment_flow.mmd` | Found elsewhere: plugins/rlm-factory/as`
- Line `68`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm_mechanism_workflow.mmd` | `../../../../assets/references/diagrams/rlm_mechanism_workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets`
- Line `69`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/workflow.mmd` | `../../../../assets/references/diagrams/workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/workflow.mmd | ⚠️ `
- Line `70`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/logic.mmd` | `../../../../assets/references/diagrams/logic.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/logic.mmd | ⚠️  Manual F`
- Line `71`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm-factory-dual-path.mmd` | `../../../../assets/references/diagrams/rlm-factory-dual-path.mmd` | Found elsewhere: plugins/rlm-factory/assets/d`
- Line `72`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/unpacking.mmd` | `../../../../assets/references/diagrams/unpacking.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/unpacking.mmd | `
- Line `73`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/search_process.mmd` | `../../../../assets/references/diagrams/search_process.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/search`
- Line `74`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/distillation_process.mmd` | `../../../../assets/references/diagrams/distillation_process.mmd` | Found elsewhere: plugins/rlm-factory/assets/dia`
- Line `75`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm-factory-dual-path.png` | `../../../../assets/references/diagrams/rlm-factory-dual-path.png` | Found elsewhere: plugins/rlm-factory/assets/d`
- Line `76`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm-factory-workflow.mmd` | `../../../../assets/references/diagrams/rlm-factory-workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/dia`
- Line `77`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm_mechanism_workflow.png` | `../../../../assets/references/diagrams/rlm_mechanism_workflow.png` | Found elsewhere: plugins/rlm-factory/assets/`
- Line `78`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm_late_binding_flow.mmd` | `../../../../assets/references/diagrams/rlm_late_binding_flow.mmd` | Found elsewhere: plugins/rlm-factory/assets/di`
- Line `79`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm-factory-architecture.png` | `../../../../assets/references/diagrams/rlm-factory-architecture.png` | Found elsewhere: plugins/rlm-factory/ass`
- Line `80`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm-factory-architecture.mmd` | `../../../../assets/references/diagrams/rlm-factory-architecture.mmd` | Found elsewhere: plugins/rlm-factory/ass`
- Line `81`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm_tool_enrichment_flow.mmd` | `../../../../assets/references/diagrams/rlm_tool_enrichment_flow.mmd` | Found elsewhere: plugins/rlm-factory/ass`
- Line `82`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm_mechanism_workflow.mmd` | `../../../../assets/references/diagrams/rlm_mechanism_workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/`
- Line `83`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/workflow.mmd` | `../../../../assets/references/diagrams/workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/workflow.mmd | ⚠️  `
- Line `84`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/logic.mmd` | `../../../../assets/references/diagrams/logic.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/logic.mmd | ⚠️  Manual Fi`
- Line `85`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm-factory-dual-path.mmd` | `../../../../assets/references/diagrams/rlm-factory-dual-path.mmd` | Found elsewhere: plugins/rlm-factory/assets/di`
- Line `86`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/unpacking.mmd` | `../../../../assets/references/diagrams/unpacking.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/unpacking.mmd | ⚠`
- Line `87`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/search_process.mmd` | `../../../../assets/references/diagrams/search_process.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/search_`
- Line `88`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/distillation_process.mmd` | `../../../../assets/references/diagrams/distillation_process.mmd` | Found elsewhere: plugins/rlm-factory/assets/diag`
- Line `89`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm-factory-dual-path.png` | `../../../../assets/references/diagrams/rlm-factory-dual-path.png` | Found elsewhere: plugins/rlm-factory/assets/di`
- Line `90`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm-factory-workflow.mmd` | `../../../../assets/references/diagrams/rlm-factory-workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diag`
- Line `91`: `| `.agents/skills/rlm-search/references/diagrams/rlm_mechanism_workflow.png` | `../../../../assets/references/diagrams/rlm_mechanism_workflow.png` | Found elsewhere: plugins/rlm-factory/assets/diagram`
- Line `92`: `| `.agents/skills/rlm-search/references/diagrams/rlm_late_binding_flow.mmd` | `../../../../assets/references/diagrams/rlm_late_binding_flow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/`
- Line `93`: `| `.agents/skills/rlm-search/references/diagrams/rlm-factory-architecture.png` | `../../../../assets/references/diagrams/rlm-factory-architecture.png` | Found elsewhere: plugins/rlm-factory/assets/dia`
- Line `94`: `| `.agents/skills/rlm-search/references/diagrams/rlm-factory-architecture.mmd` | `../../../../assets/references/diagrams/rlm-factory-architecture.mmd` | Found elsewhere: plugins/rlm-factory/assets/dia`
- Line `95`: `| `.agents/skills/rlm-search/references/diagrams/rlm_tool_enrichment_flow.mmd` | `../../../../assets/references/diagrams/rlm_tool_enrichment_flow.mmd` | Found elsewhere: plugins/rlm-factory/assets/dia`
- Line `96`: `| `.agents/skills/rlm-search/references/diagrams/rlm_mechanism_workflow.mmd` | `../../../../assets/references/diagrams/rlm_mechanism_workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagram`
- Line `97`: `| `.agents/skills/rlm-search/references/diagrams/workflow.mmd` | `../../../../assets/references/diagrams/workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/workflow.mmd | ⚠️  Manual `
- Line `98`: `| `.agents/skills/rlm-search/references/diagrams/logic.mmd` | `../../../../assets/references/diagrams/logic.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/logic.mmd | ⚠️  Manual Fix |`
- Line `99`: `| `.agents/skills/rlm-search/references/diagrams/rlm-factory-dual-path.mmd` | `../../../../assets/references/diagrams/rlm-factory-dual-path.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/`
- Line `100`: `| `.agents/skills/rlm-search/references/diagrams/unpacking.mmd` | `../../../../assets/references/diagrams/unpacking.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/unpacking.mmd | ⚠️  Manu`
- Line `101`: `| `.agents/skills/rlm-search/references/diagrams/search_process.mmd` | `../../../../assets/references/diagrams/search_process.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/search_process`
- Line `102`: `| `.agents/skills/rlm-search/references/diagrams/distillation_process.mmd` | `../../../../assets/references/diagrams/distillation_process.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/di`
- Line `103`: `| `.agents/skills/rlm-search/references/diagrams/rlm-factory-dual-path.png` | `../../../../assets/references/diagrams/rlm-factory-dual-path.png` | Found elsewhere: plugins/rlm-factory/assets/diagrams/`
- Line `104`: `| `.agents/skills/rlm-search/references/diagrams/rlm-factory-workflow.mmd` | `../../../../assets/references/diagrams/rlm-factory-workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/rl`
- Line `106`: `| `.agents/skills/link-checker-agent/references/link-checker-workflow.mmd` | `../../../../assets/diagrams/link-checker-workflow.mmd` | Found elsewhere: plugins/link-checker/assets/diagrams/link-checke`
- Line `107`: `| `.agents/skills/link-checker-agent/references/workflow.mmd` | `../../../../assets/diagrams/workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/workflow.mmd | ⚠️  Manual Fix |`
- Line `108`: `| `.agents/skills/link-checker-agent/references/logic.mmd` | `../../../../assets/diagrams/logic.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/logic.mmd | ⚠️  Manual Fix |`
- Line `109`: `| `.agents/skills/link-checker-agent/references/unpacking.mmd` | `../../../../assets/diagrams/unpacking.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/unpacking.mmd | ⚠️  Manual Fix |`
- Line `110`: `| `.agents/skills/link-checker-agent/references/link_checker_workflow.png` | `../../../../assets/diagrams/link_checker_workflow.png` | Found elsewhere: plugins/link-checker/assets/diagrams/link_checke`
- Line `111`: `| `.agents/skills/link-checker-agent/references/link_checker_workflow.mmd` | `../../../../assets/diagrams/link_checker_workflow.mmd` | Found elsewhere: plugins/link-checker/assets/diagrams/link_checke`
- Line `112`: `| `.agents/skills/agent-swarm/assets/resources/agent_swarm.mmd` | `../../../../assets/resources/agent_swarm.mmd` | Found elsewhere: plugins/agent-loops/assets/diagrams/agent_swarm.mmd | ⚠️  Manual Fix`
- Line `113`: `| `.agents/skills/dual-loop/references/diagrams/dual_loop_architecture.mmd` | `../../../../references/dual-loop/diagrams/dual_loop_architecture.mmd` | Found elsewhere: plugins/agent-loops/assets/diagr`
- Line `114`: `| `.agents/skills/red-team-review/assets/resources/red_team_review_loop.mmd` | `../../../../assets/resources/red_team_review_loop.mmd` | Found elsewhere: plugins/agent-loops/assets/diagrams/red_team_r`
- Line `156`: `| `.agents/skills/spec-kitty-specify/templates/spec-template.md` | `../../../../../assets/templates/.kittify/missions/software-dev/templates/spec-template.md` | Found elsewhere: plugins/spec-kitty-plu`
- Line `165`: `| `.agents/skills/spec-kitty-workflow/pure-spec-kitty-workflow.mmd` | `../../references/diagrams/pure-spec-kitty-workflow.mmd` | Found elsewhere: plugins/spec-kitty-plugin/assets/diagrams/pure-spec-ki`
- Line `167`: `| `.agents/skills/spec-kitty-workflow/references/diagrams/pure-spec-kitty-workflow.mmd` | `../../../../references/diagrams/pure-spec-kitty-workflow.mmd` | Found elsewhere: plugins/spec-kitty-plugin/as`
- Line `184`: `| `.agents/skills/convert-mermaid/references/mermaid-to-png-architecture.mmd` | `../../../../assets/diagrams/mermaid-to-png-architecture.mmd` | Found elsewhere: plugins/mermaid-to-png/assets/diagrams/`
- Line `185`: `| `.agents/skills/convert-mermaid/references/convert-mermaid-flow.mmd` | `../../../../assets/diagrams/convert-mermaid-flow.mmd` | Found elsewhere: plugins/mermaid-to-png/assets/diagrams/convert-mermai`
- Line `186`: `| `.agents/skills/convert-mermaid/references/convert-mermaid-flow.png` | `../../../../assets/diagrams/convert-mermaid-flow.png` | Found elsewhere: plugins/mermaid-to-png/assets/diagrams/convert-mermai`
- Line `187`: `| `.agents/skills/convert-mermaid/references/mermaid-to-png-architecture.png` | `../../../../assets/diagrams/mermaid-to-png-architecture.png` | Found elsewhere: plugins/mermaid-to-png/assets/diagrams/`
- Line `190`: `| `.agents/skills/agentic-os-init/assets/resources/agentic-os-init-flow.mmd` | `../../../../assets/resources/agentic-os-init-flow.mmd` | Found elsewhere: plugins/agent-agentic-os/assets/diagrams/agent`
- Line `191`: `| `.agents/skills/agentic-os-guide/references/diagrams/agentic-os-guide-flow.mmd` | `../../../../references/agentic-os-guide/diagrams/agentic-os-guide-flow.mmd` | Found elsewhere: plugins/agent-agenti`
- Line `192`: `| `.agents/skills/agentic-os-guide/assets/resources/agentic-os-guide-flow.mmd` | `../../../../assets/resources/agentic-os-guide-flow.mmd` | Found elsewhere: plugins/agent-agentic-os/assets/diagrams/ag`
- Line `193`: `| `.agents/skills/session-memory-manager/assets/resources/session-memory-manager-flow.mmd` | `../../../../assets/resources/session-memory-manager-flow.mmd` | Found elsewhere: plugins/agent-agentic-os/`
- Line `194`: `| `.agents/skills/memory-management/references/diagrams/architecture/memory_lookup_flow.mmd` | `../../../../../assets/resources/memory_lookup_flow.mmd` | Found elsewhere: plugins/memory-management/ass`
- Line `195`: `| `.agents/skills/memory-management/references/diagrams/architecture/memory_architecture.mmd` | `../../../../../assets/resources/memory_architecture.mmd` | Found elsewhere: plugins/memory-management/a`
- Line `196`: `| `.agents/skills/memory-management/references/diagrams/architecture/memory_session_lifecycle.mmd` | `../../../../../assets/resources/memory_session_lifecycle.mmd` | Found elsewhere: plugins/memory-ma`
- Line `197`: `| `.agents/skills/memory-management/assets/resources/memory_lookup_flow.mmd` | `../../../../assets/resources/memory_lookup_flow.mmd` | Found elsewhere: plugins/memory-management/assets/diagrams/memory`
- Line `198`: `| `.agents/skills/memory-management/assets/resources/memory_architecture.mmd` | `../../../../assets/resources/memory_architecture.mmd` | Found elsewhere: plugins/memory-management/assets/diagrams/memo`
- Line `199`: `| `.agents/skills/memory-management/assets/resources/memory_session_lifecycle.mmd` | `../../../../assets/resources/memory_session_lifecycle.mmd` | Found elsewhere: plugins/memory-management/assets/dia`
- Line `200`: `| `.agents/skills/dependency-management/references/python_dependency_workflow.mmd` | `../../../../assets/diagrams/python_dependency_workflow.mmd` | Found elsewhere: plugins/dependency-management/asset`
- Line `201`: `| `.agents/skills/vector-db-ingest/assets/resources/architecture_sequence.mmd` | `../../../../assets/resources/architecture_sequence.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/architect`
- Line `202`: `| `.agents/skills/vector-db-ingest/assets/resources/deployment_model.mmd` | `../../../../assets/resources/deployment_model.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/deployment_model.mm`
- Line `203`: `| `.agents/skills/vector-db-init/assets/resources/architecture_sequence.mmd` | `../../../../assets/resources/architecture_sequence.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/architectur`
- Line `204`: `| `.agents/skills/vector-db-init/assets/resources/deployment_model.mmd` | `../../../../assets/resources/deployment_model.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/deployment_model.mmd `
- Line `205`: `| `.agents/skills/vector-db-launch/assets/resources/architecture_sequence.mmd` | `../../../../assets/resources/architecture_sequence.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/architect`
- Line `206`: `| `.agents/skills/vector-db-launch/assets/resources/deployment_model.mmd` | `../../../../assets/resources/deployment_model.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/deployment_model.mm`
- Line `207`: `| `.agents/skills/vector-db-search/assets/resources/architecture_sequence.mmd` | `../../../../assets/resources/architecture_sequence.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/architect`
- Line `208`: `| `.agents/skills/vector-db-search/assets/resources/deployment_model.mmd` | `../../../../assets/resources/deployment_model.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/deployment_model.mm`
- Line `209`: `| `.agents/skills/vector-db-cleanup/assets/resources/architecture_sequence.mmd` | `../../../../assets/resources/architecture_sequence.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/architec`
- Line `210`: `| `.agents/skills/vector-db-cleanup/assets/resources/deployment_model.mmd` | `../../../../assets/resources/deployment_model.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/deployment_model.m`
- Line `212`: `| `.agents/skills/ecosystem-authoritative-sources/references/plugin-architecture.mmd` | `../../../../assets/diagrams/plugin-architecture.mmd` | Found elsewhere: plugins/agent-skill-open-specifications`
- Line `214`: `| `.agents/skills/ecosystem-authoritative-sources/references/skill-execution-flow.mmd` | `../../../../assets/diagrams/skill-execution-flow.mmd` | Found elsewhere: plugins/agent-skill-open-specificatio`
- Line `217`: `| `.agents/skills/ecosystem-authoritative-sources/references/diagrams/plugin-architecture.mmd` | `../../../../references/ecosystem-authoritative-sources/diagrams/plugin-architecture.mmd` | Found elsew`
- Line `218`: `| `.agents/skills/ecosystem-authoritative-sources/references/diagrams/plugin-architecture.png` | `../../../../references/ecosystem-authoritative-sources/diagrams/plugin-architecture.png` | Found elsew`
- Line `219`: `| `.agents/skills/ecosystem-authoritative-sources/references/diagrams/skill-execution-flow.mmd` | `../../../../references/ecosystem-authoritative-sources/diagrams/skill-execution-flow.mmd` | Found els`
- Line `220`: `| `.agents/skills/ecosystem-authoritative-sources/references/diagrams/skill-execution-flow.png` | `../../../../references/ecosystem-authoritative-sources/diagrams/skill-execution-flow.png` | Found els`
- Line `221`: `| `.agents/skills/ecosystem-authoritative-sources/references/reference/plugin-architecture.mmd` | `../../../../references/ecosystem-authoritative-sources/reference/plugin-architecture.mmd` | Found els`
- Line `222`: `| `.agents/skills/ecosystem-authoritative-sources/references/reference/plugin-architecture.png` | `../../../../references/ecosystem-authoritative-sources/reference/plugin-architecture.png` | Found els`
- Line `224`: `| `.agents/skills/ecosystem-authoritative-sources/references/reference/skill-execution-flow.mmd` | `../../../../references/ecosystem-authoritative-sources/reference/skill-execution-flow.mmd` | Found e`
- Line `225`: `| `.agents/skills/ecosystem-authoritative-sources/references/reference/skill-execution-flow.png` | `../../../../references/ecosystem-authoritative-sources/reference/skill-execution-flow.png` | Found e`
- Line `228`: `| `.agents/skills/ecosystem-authoritative-sources/assets/resources/plugin-architecture.mmd` | `../../../../assets/resources/plugin-architecture.mmd` | Found elsewhere: plugins/agent-skill-open-specifi`
- Line `229`: `| `.agents/skills/ecosystem-authoritative-sources/assets/resources/skill-execution-flow.mmd` | `../../../../assets/resources/skill-execution-flow.mmd` | Found elsewhere: plugins/agent-skill-open-speci`

### [ ] plugins/agent-plugin-analyzer/references/security-checks.md
- Line `34`: `| Undeclared dependencies | Plugin relies on other plugins/MCP servers not documented | Warning |`

### [ ] plugins/agent-plugin-analyzer/references/usage-guide.md
- Line `89`: `python3 ./check_skill_boundaries.py inventory.json --skill plugins/adr-manager/skills/adr-management`
- Line `97`: `RESOLVES TO: plugins/adr-manager/templates/adr-template.md  ❌ OUTSIDE!`
- Line `102`: `cd plugins/adr-manager/skills/adr-management`
- Line `119`: `python3 ./check_plugin_boundaries.py inventory.json --plugin plugins/plugin-installer`
- Line `124`: `FILE: plugins/adr-manager/commands/adr-management.md:8`
- Line `126`: `PLUGIN ROOT: plugins/adr-manager/`
- Line `132`: `cd plugins/adr-manager`

### [ ] plugins/agent-plugin-analyzer/scripts/audit_plugin_structure.py
- Line `14`: `python3 audit_plugin_structure.py plugins/agent-plugin-analyzer`

### [ ] plugins/agent-plugin-analyzer/scripts/auto_fix_local_links.py
- Line `47`: `# Group 2: The plugins prefix (plugins/plugin-name/...)`
- Line `85`: `# if the original string was plugins/agent-plugin-analyzer/scripts/foo.py`

### [ ] plugins/agent-plugin-analyzer/scripts/check_plugin_boundaries.py
- Line `14`: `python3 check_plugin_boundaries.py temp/inventory.json --plugin plugins/adr-manager`
- Line `56`: `plugins/adr-manager/commands/adr-management.md  plugins/adr-manager/`
- Line `57`: `plugins/plugin-installer/hooks/hooks.json  plugins/plugin-installer/`
- Line `58`: `plugins/adr-manager/.claude-plugin/plugin.json  plugins/adr-manager/`
- Line `61`: `plugins/adr-manager/skills/adr-management/SKILL.md  None (skip)`
- Line `76`: `return Path(*parts[:idx+2])  # e.g., plugins/adr-manager/`

### [ ] plugins/agent-plugin-analyzer/scripts/check_skill_boundaries.py
- Line `14`: `python3 check_skill_boundaries.py temp/inventory.json --skill plugins/adr-manager/skills/adr-management`
- Line `62`: `r"re:/Users/.*",           # macOS absolute paths (e.g. /Users/robert/...)`
- Line `97`: `plugins/adr-manager/skills/adr-management/SKILL.md`
- Line `98`: `plugins/adr-manager/skills/adr-management/`
- Line `110`: `return Path(*parts[:idx+2])  # e.g., plugins/adr-manager/skills/adr-management`

### [ ] plugins/agent-plugin-analyzer/scripts/fix_inside_plugin_symlinks.py
- Line `74`: `"""Extract plugin root from path like plugins/adr-manager/skills/adr-management/file.md"""`

### [ ] plugins/agent-plugin-analyzer/scripts/path_reference_auditor.py
- Line `110`: `Walk all plugins/skills directories and find every ./reference.`

### [ ] plugins/agent-plugin-analyzer/scripts/run_eval.py
- Line `13`: `python3 run_eval.py --eval-set eval_set.json --skill-path plugins/agent-plugin-analyzer/skills/audit-plugin`

### [ ] plugins/agent-plugin-analyzer/scripts/run_loop.py
- Line `14`: `python3 run_loop.py --eval-set eval_set.json --skill-path plugins/agent-plugin-analyzer/skills/audit-plugin`

### [ ] plugins/agent-plugin-analyzer/skills/analyze-plugin/references/security-checks.md
- Line `34`: `| Undeclared dependencies | Plugin relies on other plugins/MCP servers not documented | Warning |`

### [ ] plugins/agent-plugin-analyzer/skills/audit-plugin-l5/SKILL.md
- Line `26`: `Before executing this skill, ensure you know the exact path or name of the plugin you wish to audit (e.g., `plugins/oracle-legacy-system-analysis/xml-to-markdown`).`

### [ ] plugins/agent-plugin-analyzer/skills/audit-plugin/scripts/run_eval.py
- Line `13`: `python3 run_eval.py --eval-set eval_set.json --skill-path plugins/agent-plugin-analyzer/skills/audit-plugin`

### [ ] plugins/agent-plugin-analyzer/skills/audit-plugin/scripts/run_loop.py
- Line `14`: `python3 run_loop.py --eval-set eval_set.json --skill-path plugins/agent-plugin-analyzer/skills/audit-plugin`

### [ ] plugins/agent-plugin-analyzer/skills/fix-plugin-paths/references/fix-plugin-paths.prompt.md
- Line `4`: `If a file inside `plugins/A/` references `plugins/A/scripts/foo.py`, replace with `./scripts/foo.py`.`
- Line `6`: `**BEFORE:** `python3 plugins/agent-agentic-os/scripts/evaluate.py``
- Line `22`: `**BEFORE:** `plugins/copilot-cli/skills/copilot-cli-agent/references/foo.md``
- Line `30`: `**BEFORE:** `e.g. "/Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/link-checker"``
- Line `31`: `**AFTER:**  `e.g. "<USER_HOME>/Projects/agent-plugins-skills/plugins/link-checker"``
- Line `41`: `# (symlink → plugins/agent-agentic-os/assets/templates/...)`

### [ ] plugins/agent-plugin-analyzer/skills/fix-plugin-paths/references/program.md
- Line `17`: `- `plugins/agent-agentic-os/scripts/evaluate.py``
- Line `18`: `- `plugins/agent-agentic-os/scripts/eval_runner.py``
- Line `23`: `2. `python3 plugins/agent-agentic-os/skills/os-eval-runner/scripts/evaluate.py --skill plugins/agent-plugin-analyzer/skills/fix-plugin-paths --desc "what you changed"``

### [ ] plugins/agent-plugin-analyzer/skills/mine-plugins/SKILL.md
- Line `50`: `/mine-plugins claude-knowledgework-plugins/sales`
- Line `56`: `/mine-plugins plugins/legacy\ system`

### [ ] plugins/agent-plugin-analyzer/skills/mine-skill/SKILL.md
- Line `48`: `/mine-skill claude-knowledgework-plugins/sales/skills/call-prep`

### [ ] plugins/agent-plugin-analyzer/skills/path-reference-auditor/SKILL.md
- Line `35`: `- **Plugin-local**: References in `plugins/X/` (root level) stay within `X/``
- Line `111`: `FILE: plugins/adr-manager/commands/adr-management.md:8`
- Line `191`: `python3 ./scripts/bridge_installer.py plugins/agent-plugin-analyzer`
- Line `194`: `cp -r plugins/agent-plugin-analyzer /path/to/target/plugins/`
- Line `214`: `- `../../templates/file.md` → `plugins/X/templates/file.md` (outside skill) ❌`
- Line `219`: `cd plugins/X/skills/Y`
- Line `224`: `All file references **inside** `plugins/X/` (root level, non-skill files) must resolve **within** `X/`.`
- Line `227`: `- `./commands/file.md` → `plugins/X/commands/file.md` ✅`
- Line `231`: `- `../other-plugin/file.md` → `plugins/other-plugin/file.md` (sibling plugin) ❌`
- Line `236`: `cd plugins/X`

### [ ] plugins/agent-plugin-analyzer/skills/path-reference-auditor/references/broken_symlinks_repair_report.md
- Line `5`: `| `plugins/agent-plugin-analyzer/references/patterns/evals.json` | `../../evals/evals.json` | ⚠️  Unknown target | ⚠️  Manual Fix |`
- Line `6`: `| `plugins/agent-plugin-analyzer/references/patterns/CONNECTORS.md` | `../../CONNECTORS.md` | ⚠️  Unknown target | ⚠️  Manual Fix |`
- Line `7`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/stage-aware-feedback.md` | `../../../../references/audit-plugin/patterns/stage-aware-feedback.md` | ⚠️  Unknown target | ⚠️  Ma`
- Line `8`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/tainted-context-cleanser.md` | `../../../../references/audit-plugin/patterns/tainted-context-cleanser.md` | ⚠️  Unknown target `
- Line `9`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/iteration-directory-isolation.md` | `../../../../references/audit-plugin/patterns/iteration-directory-isolation.md` | ⚠️  Unkno`
- Line `10`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/multi-actor-operational-coordination-manifest.md` | `../../../../references/audit-plugin/patterns/multi-actor-operational-coord`
- Line `11`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/persistent-plugin-configuration.md` | `../../../../references/audit-plugin/patterns/persistent-plugin-configuration.md` | ⚠️  U`
- Line `12`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/escalation-taxonomy.md` | `../../../../references/audit-plugin/patterns/escalation-taxonomy.md` | ⚠️  Unknown target | ⚠️  Manu`
- Line `13`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/complexity-tiered-output.md` | `../../../../references/audit-plugin/patterns/complexity-tiered-output.md` | ⚠️  Unknown target `
- Line `14`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/anti-pattern-vaccination.md` | `../../../../references/audit-plugin/patterns/anti-pattern-vaccination.md` | ⚠️  Unknown target `
- Line `15`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/dual-register-communication-enforcement.md` | `../../../../references/audit-plugin/patterns/dual-register-communication-enforce`
- Line `16`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/graduated-autonomy.md` | `../../../../references/audit-plugin/patterns/graduated-autonomy.md` | ⚠️  Unknown target | ⚠️  Manual`
- Line `17`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/output-classification.md` | `../../../../references/audit-plugin/patterns/output-classification.md` | ⚠️  Unknown target | ⚠️  `
- Line `18`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/asynchronous-benchmark-metric-capture.md` | `../../../../references/audit-plugin/patterns/asynchronous-benchmark-metric-capture`
- Line `19`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/dual-mode-degradation.md` | `../../../../references/audit-plugin/patterns/dual-mode-degradation.md` | ⚠️  Unknown target | ⚠️  `
- Line `20`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/category-calibrated-benchmark-anchoring.md` | `../../../../references/audit-plugin/patterns/category-calibrated-benchmark-ancho`
- Line `21`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/negative-instruction-constraint.md` | `../../../../references/audit-plugin/patterns/negative-instruction-constraint.md` | ⚠️  U`
- Line `22`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/ui-degradation-constraint.md` | `../../../../references/audit-plugin/patterns/ui-degradation-constraint.md` | ⚠️  Unknown targe`
- Line `23`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/temporal-anchoring.md` | `../../../../references/audit-plugin/patterns/temporal-anchoring.md` | ⚠️  Unknown target | ⚠️  Manual`
- Line `24`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/source-authority.md` | `../../../../references/audit-plugin/patterns/source-authority.md` | ⚠️  Unknown target | ⚠️  Manual Fix`
- Line `25`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/conditional-step-inclusion.md` | `../../../../references/audit-plugin/patterns/conditional-step-inclusion.md` | ⚠️  Unknown tar`
- Line `26`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/passive-style-injection-payload.md` | `../../../../references/audit-plugin/patterns/passive-style-injection-payload.md` | ⚠️  U`
- Line `27`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/artifact-embedded-execution-audit-trail.md` | `../../../../references/audit-plugin/patterns/artifact-embedded-execution-audit-t`
- Line `28`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/cyclical-state-propagation-contract.md` | `../../../../references/audit-plugin/patterns/cyclical-state-propagation-contract.md``
- Line `29`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/delegated-constraint-verification-loop.md` | `../../../../references/audit-plugin/patterns/delegated-constraint-verification-lo`
- Line `30`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/zero-sum-addition-gate.md` | `../../../../references/audit-plugin/patterns/zero-sum-addition-gate.md` | ⚠️  Unknown target | ⚠️`
- Line `31`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/dual-mode-meta-skill.md` | `../../../../references/audit-plugin/patterns/dual-mode-meta-skill.md` | ⚠️  Unknown target | ⚠️  Ma`
- Line `32`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/multi-source-synthesis.md` | `../../../../references/audit-plugin/patterns/multi-source-synthesis.md` | ⚠️  Unknown target | ⚠️`
- Line `33`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/graduated-source-attributed-elicitation.md` | `../../../../references/audit-plugin/patterns/graduated-source-attributed-elicita`
- Line `34`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/evals.json` | `../../../../references/audit-plugin/patterns/evals.json` | ⚠️  Unknown target | ⚠️  Manual Fix |`
- Line `35`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/sub-action-multiplexing.md` | `../../../../references/audit-plugin/patterns/sub-action-multiplexing.md` | ⚠️  Unknown target | `
- Line `36`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/pre-committed-rollback-contract.md` | `../../../../references/audit-plugin/patterns/pre-committed-rollback-contract.md` | ⚠️  U`
- Line `37`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/structured-output-contracts.md` | `../../../../references/audit-plugin/patterns/structured-output-contracts.md` | ⚠️  Unknown t`
- Line `38`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/artifact-generation-xss-compliance-gate.md` | `../../../../references/audit-plugin/patterns/artifact-generation-xss-compliance-`
- Line `39`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/anti-symptom-triage.md` | `../../../../references/audit-plugin/patterns/anti-symptom-triage.md` | ⚠️  Unknown target | ⚠️  Manu`
- Line `40`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/category-semantic-deferred-tool-binding.md` | `../../../../references/audit-plugin/patterns/category-semantic-deferred-tool-bin`
- Line `41`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/population-normative-distribution-constraint.md` | `../../../../references/audit-plugin/patterns/population-normative-distribut`
- Line `42`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/rigorous-benchmarking-loop.md` | `../../../../references/audit-plugin/patterns/rigorous-benchmarking-loop.md` | ⚠️  Unknown tar`
- Line `43`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/multi-dimensional-tone.md` | `../../../../references/audit-plugin/patterns/multi-dimensional-tone.md` | ⚠️  Unknown target | ⚠️`
- Line `44`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/connector-placeholders.md` | `../../../../references/audit-plugin/patterns/connector-placeholders.md` | ⚠️  Unknown target | ⚠️`
- Line `45`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/artifact-state-interrogative-routing.md` | `../../../../references/audit-plugin/patterns/artifact-state-interrogative-routing.m`
- Line `46`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/chained-command-invocation.md` | `../../../../references/audit-plugin/patterns/chained-command-invocation.md` | ⚠️  Unknown tar`
- Line `47`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/priority-ordered-scanning.md` | `../../../../references/audit-plugin/patterns/priority-ordered-scanning.md` | ⚠️  Unknown targe`
- Line `48`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/tiered-source-authority.md` | `../../../../references/audit-plugin/patterns/tiered-source-authority.md` | ⚠️  Unknown target | `
- Line `49`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/embedded-deterministic-scoring-formula.md` | `../../../../references/audit-plugin/patterns/embedded-deterministic-scoring-formu`
- Line `50`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/source-transparency.md` | `../../../../references/audit-plugin/patterns/source-transparency.md` | ⚠️  Unknown target | ⚠️  Manu`
- Line `51`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/lifecycle-aware-knowledge.md` | `../../../../references/audit-plugin/patterns/lifecycle-aware-knowledge.md` | ⚠️  Unknown targe`
- Line `52`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/multi-modal-routing.md` | `../../../../references/audit-plugin/patterns/multi-modal-routing.md` | ⚠️  Unknown target | ⚠️  Manu`
- Line `53`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/chained-commands.md` | `../../../../references/audit-plugin/patterns/chained-commands.md` | ⚠️  Unknown target | ⚠️  Manual Fix`
- Line `54`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/local-interactive-output-viewer-loop.md` | `../../../../references/audit-plugin/patterns/local-interactive-output-viewer-loop.m`
- Line `55`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/action-forcing-output-with-deadline-attribution.md` | `../../../../references/audit-plugin/patterns/action-forcing-output-with-`
- Line `56`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/explicit-seed-anchored-determinism.md` | `../../../../references/audit-plugin/patterns/explicit-seed-anchored-determinism.md` |`
- Line `57`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/audience-segmented-information-filtering.md` | `../../../../references/audit-plugin/patterns/audience-segmented-information-fil`
- Line `58`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/severity-stratified-output.md` | `../../../../references/audit-plugin/patterns/severity-stratified-output.md` | ⚠️  Unknown tar`
- Line `59`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/artifact-lifecycle.md` | `../../../../references/audit-plugin/patterns/artifact-lifecycle.md` | ⚠️  Unknown target | ⚠️  Manual`
- Line `60`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/adversarial-objectivity-constraint.md` | `../../../../references/audit-plugin/patterns/adversarial-objectivity-constraint.md` |`
- Line `61`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/client-side-compute-sandbox-constraint.md` | `../../../../references/audit-plugin/patterns/client-side-compute-sandbox-constrai`
- Line `62`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/pre-execution-workflow-commitment-diagram.md` | `../../../../references/audit-plugin/patterns/pre-execution-workflow-commitment`
- Line `63`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/mode-invariant-compliance-gate.md` | `../../../../references/audit-plugin/patterns/mode-invariant-compliance-gate.md` | ⚠️  Unk`
- Line `64`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/pre-execution-input-manifest.md` | `../../../../references/audit-plugin/patterns/pre-execution-input-manifest.md` | ⚠️  Unknown`
- Line `65`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/highly-procedural-fallback-trees.md` | `../../../../references/audit-plugin/patterns/highly-procedural-fallback-trees.md` | ⚠️ `
- Line `66`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/quantification-enforcement.md` | `../../../../references/audit-plugin/patterns/quantification-enforcement.md` | ⚠️  Unknown tar`
- Line `67`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/mandatory-counterfactual-scenario-templating.md` | `../../../../references/audit-plugin/patterns/mandatory-counterfactual-scena`
- Line `68`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/skill-command-two-tier.md` | `../../../../references/audit-plugin/patterns/skill-command-two-tier.md` | ⚠️  Unknown target | ⚠️`
- Line `69`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/trigger-description-optimization-loop.md` | `../../../../references/audit-plugin/patterns/trigger-description-optimization-loop`
- Line `70`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/dynamic-specification-fetching.md` | `../../../../references/audit-plugin/patterns/dynamic-specification-fetching.md` | ⚠️  Unk`
- Line `71`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin/references/patterns/multi-variant-trigger-optimizer.md` | `../../../../references/audit-plugin/patterns/multi-variant-trigger-optimizer.md` | ⚠️  U`
- Line `72`: `| `plugins/agent-plugin-analyzer/skills/analyze-plugin/references/diagrams/analyze-plugin-flow.mmd` | `../../../../references/analyze-plugin/diagrams/analyze-plugin-flow.mmd` | Found elsewhere: plugin`
- Line `73`: `| `plugins/agent-plugin-analyzer/skills/analyze-plugin/assets/resources/analyze-plugin-flow.mmd` | `../../../../assets/resources/analyze-plugin-flow.mmd` | Found elsewhere: plugins/agent-plugin-analyz`
- Line `74`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin-l5/references/diagrams/audit-plugin-l5-flow.mmd` | `../../../../references/audit-plugin-l5/diagrams/audit-plugin-l5-flow.mmd` | Found elsewhere: pl`
- Line `75`: `| `plugins/agent-plugin-analyzer/skills/audit-plugin-l5/assets/resources/audit-plugin-l5-flow.mmd` | `../../../../assets/resources/audit-plugin-l5-flow.mmd` | Found elsewhere: plugins/agent-plugin-ana`
- Line `76`: `| `.agents/skills/replicate-plugin/references/plugin_replicator_diagram.mmd` | `../../../../assets/diagrams/plugin_replicator_diagram.mmd` | Found elsewhere: plugins/plugin-manager/assets/diagrams/plu`
- Line `77`: `| `.agents/skills/replicate-plugin/assets/resources/plugin_replicator_diagram.mmd` | `../../../../assets/resources/plugin_replicator_diagram.mmd` | Found elsewhere: plugins/plugin-manager/assets/diagr`
- Line `78`: `| `.agents/skills/maintain-plugins/references/cleanup_flow.mmd` | `../../../../assets/diagrams/cleanup_flow.mmd` | Found elsewhere: plugins/plugin-manager/assets/diagrams/cleanup_flow.mmd | ⚠️  Manual`
- Line `79`: `| `.agents/skills/maintain-plugins/assets/resources/cleanup_flow.mmd` | `../../../../assets/resources/cleanup_flow.mmd` | Found elsewhere: plugins/plugin-manager/assets/diagrams/cleanup_flow.mmd | ⚠️ `
- Line `80`: `| `.agents/skills/plugin-installer/references/agent_bridge_diagram.mmd` | `../../../../assets/diagrams/agent_bridge_diagram.mmd` | Found elsewhere: plugins/plugin-manager/assets/diagrams/agent_bridge_`
- Line `81`: `| `.agents/skills/plugin-installer/references/ecosystem_system_bridge.mmd` | `../../../../assets/diagrams/ecosystem_system_bridge.mmd` | Found elsewhere: plugins/plugin-manager/assets/diagrams/ecosyst`
- Line `82`: `| `.agents/skills/tool-inventory/references/tool-inventory-workflow.mmd` | `../../../../assets/diagrams/tool-inventory-workflow.mmd` | Found elsewhere: plugins/tool-inventory/assets/diagrams/tool-inve`
- Line `83`: `| `.agents/skills/tool-inventory/references/diagrams/legacy-architecture/Tool_Architecture_Domain_Model.mmd` | `../../../../../references/tool-inventory/diagrams/legacy-architecture/Tool_Architecture_`
- Line `84`: `| `.agents/skills/tool-inventory/references/diagrams/legacy-architecture/Tool_Architecture_Domain_Model.png` | `../../../../../references/tool-inventory/diagrams/legacy-architecture/Tool_Architecture_`
- Line `85`: `| `.agents/skills/rsvp-reading/references/diagrams/rsvp-reading-flow.mmd` | `../../../../references/rsvp-reading/diagrams/rsvp-reading-flow.mmd` | Found elsewhere: plugins/rsvp-speed-reader/assets/dia`
- Line `87`: `| `.agents/skills/continuous-skill-optimizer/references/resources/continuous-skill-optimizer-flow.mmd` | `../../../../references/continuous-skill-optimizer/resources/continuous-skill-optimizer-flow.mm`
- Line `88`: `| `.agents/skills/continuous-skill-optimizer/references/diagrams/continuous-skill-optimizer-flow.mmd` | `../../../../references/continuous-skill-optimizer/diagrams/continuous-skill-optimizer-flow.mmd``
- Line `94`: `| `.agents/skills/manage-marketplace/manage-marketplace-flow.mmd` | `../../../assets/resources/manage-marketplace-flow.mmd` | Found elsewhere: plugins/agent-scaffolders/assets/diagrams/manage-marketpl`
- Line `107`: `| `.agents/skills/task-agent/references/task-manager-workflow.mmd` | `../../../../assets/diagrams/task-manager-workflow.mmd` | Found elsewhere: plugins/task-manager/assets/diagrams/task-manager-workfl`
- Line `108`: `| `plugins/rlm-factory/references/research/summary.md` | `../../../../assets/references/research/summary.md` | Found elsewhere: plugins/rlm-factory/assets/references/research/summary.md | ⚠️  Manual F`
- Line `109`: `| `plugins/rlm-factory/references/research/2512.24601v1.pdf` | `../../../../assets/references/research/2512.24601v1.pdf` | Found elsewhere: plugins/rlm-factory/assets/references/research/2512.24601v1.`
- Line `110`: `| `plugins/rlm-factory/references/examples/rlm_profiles.json` | `../../../../assets/references/examples/rlm_profiles.json` | Found elsewhere: plugins/rlm-factory/assets/references/examples/rlm_profile`
- Line `111`: `| `plugins/rlm-factory/references/examples/rlm_summary_cache_manifest.json` | `../../../../assets/references/examples/rlm_summary_cache_manifest.json` | Found elsewhere: plugins/rlm-factory/assets/ref`
- Line `112`: `| `plugins/rlm-factory/references/examples/rlm_tools_manifest.json` | `../../../../assets/references/examples/rlm_tools_manifest.json` | Found elsewhere: plugins/rlm-factory/assets/references/examples`
- Line `113`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm_mechanism_workflow.png` | `../../../../assets/references/diagrams/rlm_mechanism_workflow.png` | Found elsewhere: plugins/rlm-factory/assets/`
- Line `114`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm_late_binding_flow.mmd` | `../../../../assets/references/diagrams/rlm_late_binding_flow.mmd` | Found elsewhere: plugins/rlm-factory/assets/di`
- Line `115`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm-factory-architecture.png` | `../../../../assets/references/diagrams/rlm-factory-architecture.png` | Found elsewhere: plugins/rlm-factory/ass`
- Line `116`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm-factory-architecture.mmd` | `../../../../assets/references/diagrams/rlm-factory-architecture.mmd` | Found elsewhere: plugins/rlm-factory/ass`
- Line `117`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm_tool_enrichment_flow.mmd` | `../../../../assets/references/diagrams/rlm_tool_enrichment_flow.mmd` | Found elsewhere: plugins/rlm-factory/ass`
- Line `118`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm_mechanism_workflow.mmd` | `../../../../assets/references/diagrams/rlm_mechanism_workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/`
- Line `119`: `| `.agents/skills/rlm-distill-agent/references/diagrams/workflow.mmd` | `../../../../assets/references/diagrams/workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/workflow.mmd | ⚠️  `
- Line `120`: `| `.agents/skills/rlm-distill-agent/references/diagrams/logic.mmd` | `../../../../assets/references/diagrams/logic.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/logic.mmd | ⚠️  Manual Fi`
- Line `121`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm-factory-dual-path.mmd` | `../../../../assets/references/diagrams/rlm-factory-dual-path.mmd` | Found elsewhere: plugins/rlm-factory/assets/di`
- Line `122`: `| `.agents/skills/rlm-distill-agent/references/diagrams/unpacking.mmd` | `../../../../assets/references/diagrams/unpacking.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/unpacking.mmd | ⚠`
- Line `123`: `| `.agents/skills/rlm-distill-agent/references/diagrams/search_process.mmd` | `../../../../assets/references/diagrams/search_process.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/search_`
- Line `124`: `| `.agents/skills/rlm-distill-agent/references/diagrams/distillation_process.mmd` | `../../../../assets/references/diagrams/distillation_process.mmd` | Found elsewhere: plugins/rlm-factory/assets/diag`
- Line `125`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm-factory-dual-path.png` | `../../../../assets/references/diagrams/rlm-factory-dual-path.png` | Found elsewhere: plugins/rlm-factory/assets/di`
- Line `126`: `| `.agents/skills/rlm-distill-agent/references/diagrams/rlm-factory-workflow.mmd` | `../../../../assets/references/diagrams/rlm-factory-workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diag`
- Line `127`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm_mechanism_workflow.png` | `../../../../assets/references/diagrams/rlm_mechanism_workflow.png` | Found elsewhere: plugins/rlm-factory/assets`
- Line `128`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm_late_binding_flow.mmd` | `../../../../assets/references/diagrams/rlm_late_binding_flow.mmd` | Found elsewhere: plugins/rlm-factory/assets/d`
- Line `129`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm-factory-architecture.png` | `../../../../assets/references/diagrams/rlm-factory-architecture.png` | Found elsewhere: plugins/rlm-factory/as`
- Line `130`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm-factory-architecture.mmd` | `../../../../assets/references/diagrams/rlm-factory-architecture.mmd` | Found elsewhere: plugins/rlm-factory/as`
- Line `131`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm_tool_enrichment_flow.mmd` | `../../../../assets/references/diagrams/rlm_tool_enrichment_flow.mmd` | Found elsewhere: plugins/rlm-factory/as`
- Line `132`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm_mechanism_workflow.mmd` | `../../../../assets/references/diagrams/rlm_mechanism_workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets`
- Line `133`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/workflow.mmd` | `../../../../assets/references/diagrams/workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/workflow.mmd | ⚠️ `
- Line `134`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/logic.mmd` | `../../../../assets/references/diagrams/logic.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/logic.mmd | ⚠️  Manual F`
- Line `135`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm-factory-dual-path.mmd` | `../../../../assets/references/diagrams/rlm-factory-dual-path.mmd` | Found elsewhere: plugins/rlm-factory/assets/d`
- Line `136`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/unpacking.mmd` | `../../../../assets/references/diagrams/unpacking.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/unpacking.mmd | `
- Line `137`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/search_process.mmd` | `../../../../assets/references/diagrams/search_process.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/search`
- Line `138`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/distillation_process.mmd` | `../../../../assets/references/diagrams/distillation_process.mmd` | Found elsewhere: plugins/rlm-factory/assets/dia`
- Line `139`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm-factory-dual-path.png` | `../../../../assets/references/diagrams/rlm-factory-dual-path.png` | Found elsewhere: plugins/rlm-factory/assets/d`
- Line `140`: `| `.agents/skills/rlm-distill-ollama/references/diagrams/rlm-factory-workflow.mmd` | `../../../../assets/references/diagrams/rlm-factory-workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/dia`
- Line `141`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm_mechanism_workflow.png` | `../../../../assets/references/diagrams/rlm_mechanism_workflow.png` | Found elsewhere: plugins/rlm-factory/assets/`
- Line `142`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm_late_binding_flow.mmd` | `../../../../assets/references/diagrams/rlm_late_binding_flow.mmd` | Found elsewhere: plugins/rlm-factory/assets/di`
- Line `143`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm-factory-architecture.png` | `../../../../assets/references/diagrams/rlm-factory-architecture.png` | Found elsewhere: plugins/rlm-factory/ass`
- Line `144`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm-factory-architecture.mmd` | `../../../../assets/references/diagrams/rlm-factory-architecture.mmd` | Found elsewhere: plugins/rlm-factory/ass`
- Line `145`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm_tool_enrichment_flow.mmd` | `../../../../assets/references/diagrams/rlm_tool_enrichment_flow.mmd` | Found elsewhere: plugins/rlm-factory/ass`
- Line `146`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm_mechanism_workflow.mmd` | `../../../../assets/references/diagrams/rlm_mechanism_workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/`
- Line `147`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/workflow.mmd` | `../../../../assets/references/diagrams/workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/workflow.mmd | ⚠️  `
- Line `148`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/logic.mmd` | `../../../../assets/references/diagrams/logic.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/logic.mmd | ⚠️  Manual Fi`
- Line `149`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm-factory-dual-path.mmd` | `../../../../assets/references/diagrams/rlm-factory-dual-path.mmd` | Found elsewhere: plugins/rlm-factory/assets/di`
- Line `150`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/unpacking.mmd` | `../../../../assets/references/diagrams/unpacking.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/unpacking.mmd | ⚠`
- Line `151`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/search_process.mmd` | `../../../../assets/references/diagrams/search_process.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/search_`
- Line `152`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/distillation_process.mmd` | `../../../../assets/references/diagrams/distillation_process.mmd` | Found elsewhere: plugins/rlm-factory/assets/diag`
- Line `153`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm-factory-dual-path.png` | `../../../../assets/references/diagrams/rlm-factory-dual-path.png` | Found elsewhere: plugins/rlm-factory/assets/di`
- Line `154`: `| `.agents/skills/rlm-cleanup-agent/references/diagrams/rlm-factory-workflow.mmd` | `../../../../assets/references/diagrams/rlm-factory-workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diag`
- Line `155`: `| `.agents/skills/rlm-search/references/diagrams/rlm_mechanism_workflow.png` | `../../../../assets/references/diagrams/rlm_mechanism_workflow.png` | Found elsewhere: plugins/rlm-factory/assets/diagram`
- Line `156`: `| `.agents/skills/rlm-search/references/diagrams/rlm_late_binding_flow.mmd` | `../../../../assets/references/diagrams/rlm_late_binding_flow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/`
- Line `157`: `| `.agents/skills/rlm-search/references/diagrams/rlm-factory-architecture.png` | `../../../../assets/references/diagrams/rlm-factory-architecture.png` | Found elsewhere: plugins/rlm-factory/assets/dia`
- Line `158`: `| `.agents/skills/rlm-search/references/diagrams/rlm-factory-architecture.mmd` | `../../../../assets/references/diagrams/rlm-factory-architecture.mmd` | Found elsewhere: plugins/rlm-factory/assets/dia`
- Line `159`: `| `.agents/skills/rlm-search/references/diagrams/rlm_tool_enrichment_flow.mmd` | `../../../../assets/references/diagrams/rlm_tool_enrichment_flow.mmd` | Found elsewhere: plugins/rlm-factory/assets/dia`
- Line `160`: `| `.agents/skills/rlm-search/references/diagrams/rlm_mechanism_workflow.mmd` | `../../../../assets/references/diagrams/rlm_mechanism_workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagram`
- Line `161`: `| `.agents/skills/rlm-search/references/diagrams/workflow.mmd` | `../../../../assets/references/diagrams/workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/workflow.mmd | ⚠️  Manual `
- Line `162`: `| `.agents/skills/rlm-search/references/diagrams/logic.mmd` | `../../../../assets/references/diagrams/logic.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/logic.mmd | ⚠️  Manual Fix |`
- Line `163`: `| `.agents/skills/rlm-search/references/diagrams/rlm-factory-dual-path.mmd` | `../../../../assets/references/diagrams/rlm-factory-dual-path.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/`
- Line `164`: `| `.agents/skills/rlm-search/references/diagrams/unpacking.mmd` | `../../../../assets/references/diagrams/unpacking.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/unpacking.mmd | ⚠️  Manu`
- Line `165`: `| `.agents/skills/rlm-search/references/diagrams/search_process.mmd` | `../../../../assets/references/diagrams/search_process.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/search_process`
- Line `166`: `| `.agents/skills/rlm-search/references/diagrams/distillation_process.mmd` | `../../../../assets/references/diagrams/distillation_process.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/di`
- Line `167`: `| `.agents/skills/rlm-search/references/diagrams/rlm-factory-dual-path.png` | `../../../../assets/references/diagrams/rlm-factory-dual-path.png` | Found elsewhere: plugins/rlm-factory/assets/diagrams/`
- Line `168`: `| `.agents/skills/rlm-search/references/diagrams/rlm-factory-workflow.mmd` | `../../../../assets/references/diagrams/rlm-factory-workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/rl`
- Line `170`: `| `.agents/skills/link-checker-agent/references/link-checker-workflow.mmd` | `../../../../assets/diagrams/link-checker-workflow.mmd` | Found elsewhere: plugins/link-checker/assets/diagrams/link-checke`
- Line `171`: `| `.agents/skills/link-checker-agent/references/workflow.mmd` | `../../../../assets/diagrams/workflow.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/workflow.mmd | ⚠️  Manual Fix |`
- Line `172`: `| `.agents/skills/link-checker-agent/references/logic.mmd` | `../../../../assets/diagrams/logic.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/logic.mmd | ⚠️  Manual Fix |`
- Line `173`: `| `.agents/skills/link-checker-agent/references/unpacking.mmd` | `../../../../assets/diagrams/unpacking.mmd` | Found elsewhere: plugins/rlm-factory/assets/diagrams/unpacking.mmd | ⚠️  Manual Fix |`
- Line `174`: `| `.agents/skills/link-checker-agent/references/link_checker_workflow.png` | `../../../../assets/diagrams/link_checker_workflow.png` | Found elsewhere: plugins/link-checker/assets/diagrams/link_checke`
- Line `175`: `| `.agents/skills/link-checker-agent/references/link_checker_workflow.mmd` | `../../../../assets/diagrams/link_checker_workflow.mmd` | Found elsewhere: plugins/link-checker/assets/diagrams/link_checke`
- Line `176`: `| `.agents/skills/agent-swarm/assets/resources/agent_swarm.mmd` | `../../../../assets/resources/agent_swarm.mmd` | Found elsewhere: plugins/agent-loops/assets/diagrams/agent_swarm.mmd | ⚠️  Manual Fix`
- Line `177`: `| `.agents/skills/dual-loop/references/diagrams/dual_loop_architecture.mmd` | `../../../../references/dual-loop/diagrams/dual_loop_architecture.mmd` | Found elsewhere: plugins/agent-loops/assets/diagr`
- Line `178`: `| `.agents/skills/red-team-review/assets/resources/red_team_review_loop.mmd` | `../../../../assets/resources/red_team_review_loop.mmd` | Found elsewhere: plugins/agent-loops/assets/diagrams/red_team_r`
- Line `220`: `| `.agents/skills/spec-kitty-specify/templates/spec-template.md` | `../../../../../assets/templates/.kittify/missions/software-dev/templates/spec-template.md` | Found elsewhere: plugins/spec-kitty-plu`
- Line `229`: `| `.agents/skills/spec-kitty-workflow/pure-spec-kitty-workflow.mmd` | `../../references/diagrams/pure-spec-kitty-workflow.mmd` | Found elsewhere: plugins/spec-kitty-plugin/assets/diagrams/pure-spec-ki`
- Line `231`: `| `.agents/skills/spec-kitty-workflow/references/diagrams/pure-spec-kitty-workflow.mmd` | `../../../../references/diagrams/pure-spec-kitty-workflow.mmd` | Found elsewhere: plugins/spec-kitty-plugin/as`
- Line `248`: `| `.agents/skills/convert-mermaid/references/mermaid-to-png-architecture.mmd` | `../../../../assets/diagrams/mermaid-to-png-architecture.mmd` | Found elsewhere: plugins/mermaid-to-png/assets/diagrams/`
- Line `249`: `| `.agents/skills/convert-mermaid/references/convert-mermaid-flow.mmd` | `../../../../assets/diagrams/convert-mermaid-flow.mmd` | Found elsewhere: plugins/mermaid-to-png/assets/diagrams/convert-mermai`
- Line `250`: `| `.agents/skills/convert-mermaid/references/convert-mermaid-flow.png` | `../../../../assets/diagrams/convert-mermaid-flow.png` | Found elsewhere: plugins/mermaid-to-png/assets/diagrams/convert-mermai`
- Line `251`: `| `.agents/skills/convert-mermaid/references/mermaid-to-png-architecture.png` | `../../../../assets/diagrams/mermaid-to-png-architecture.png` | Found elsewhere: plugins/mermaid-to-png/assets/diagrams/`
- Line `254`: `| `.agents/skills/agentic-os-init/assets/resources/agentic-os-init-flow.mmd` | `../../../../assets/resources/agentic-os-init-flow.mmd` | Found elsewhere: plugins/agent-agentic-os/assets/diagrams/agent`
- Line `255`: `| `.agents/skills/agentic-os-guide/references/diagrams/agentic-os-guide-flow.mmd` | `../../../../references/agentic-os-guide/diagrams/agentic-os-guide-flow.mmd` | Found elsewhere: plugins/agent-agenti`
- Line `256`: `| `.agents/skills/agentic-os-guide/assets/resources/agentic-os-guide-flow.mmd` | `../../../../assets/resources/agentic-os-guide-flow.mmd` | Found elsewhere: plugins/agent-agentic-os/assets/diagrams/ag`
- Line `257`: `| `.agents/skills/session-memory-manager/assets/resources/session-memory-manager-flow.mmd` | `../../../../assets/resources/session-memory-manager-flow.mmd` | Found elsewhere: plugins/agent-agentic-os/`
- Line `258`: `| `.agents/skills/memory-management/references/diagrams/architecture/memory_lookup_flow.mmd` | `../../../../../assets/resources/memory_lookup_flow.mmd` | Found elsewhere: plugins/memory-management/ass`
- Line `259`: `| `.agents/skills/memory-management/references/diagrams/architecture/memory_architecture.mmd` | `../../../../../assets/resources/memory_architecture.mmd` | Found elsewhere: plugins/memory-management/a`
- Line `260`: `| `.agents/skills/memory-management/references/diagrams/architecture/memory_session_lifecycle.mmd` | `../../../../../assets/resources/memory_session_lifecycle.mmd` | Found elsewhere: plugins/memory-ma`
- Line `261`: `| `.agents/skills/memory-management/assets/resources/memory_lookup_flow.mmd` | `../../../../assets/resources/memory_lookup_flow.mmd` | Found elsewhere: plugins/memory-management/assets/diagrams/memory`
- Line `262`: `| `.agents/skills/memory-management/assets/resources/memory_architecture.mmd` | `../../../../assets/resources/memory_architecture.mmd` | Found elsewhere: plugins/memory-management/assets/diagrams/memo`
- Line `263`: `| `.agents/skills/memory-management/assets/resources/memory_session_lifecycle.mmd` | `../../../../assets/resources/memory_session_lifecycle.mmd` | Found elsewhere: plugins/memory-management/assets/dia`
- Line `264`: `| `.agents/skills/dependency-management/references/python_dependency_workflow.mmd` | `../../../../assets/diagrams/python_dependency_workflow.mmd` | Found elsewhere: plugins/dependency-management/asset`
- Line `265`: `| `.agents/skills/vector-db-ingest/assets/resources/architecture_sequence.mmd` | `../../../../assets/resources/architecture_sequence.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/architect`
- Line `266`: `| `.agents/skills/vector-db-ingest/assets/resources/deployment_model.mmd` | `../../../../assets/resources/deployment_model.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/deployment_model.mm`
- Line `267`: `| `.agents/skills/vector-db-init/assets/resources/architecture_sequence.mmd` | `../../../../assets/resources/architecture_sequence.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/architectur`
- Line `268`: `| `.agents/skills/vector-db-init/assets/resources/deployment_model.mmd` | `../../../../assets/resources/deployment_model.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/deployment_model.mmd `
- Line `269`: `| `.agents/skills/vector-db-launch/assets/resources/architecture_sequence.mmd` | `../../../../assets/resources/architecture_sequence.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/architect`
- Line `270`: `| `.agents/skills/vector-db-launch/assets/resources/deployment_model.mmd` | `../../../../assets/resources/deployment_model.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/deployment_model.mm`
- Line `271`: `| `.agents/skills/vector-db-search/assets/resources/architecture_sequence.mmd` | `../../../../assets/resources/architecture_sequence.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/architect`
- Line `272`: `| `.agents/skills/vector-db-search/assets/resources/deployment_model.mmd` | `../../../../assets/resources/deployment_model.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/deployment_model.mm`
- Line `273`: `| `.agents/skills/vector-db-cleanup/assets/resources/architecture_sequence.mmd` | `../../../../assets/resources/architecture_sequence.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/architec`
- Line `274`: `| `.agents/skills/vector-db-cleanup/assets/resources/deployment_model.mmd` | `../../../../assets/resources/deployment_model.mmd` | Found elsewhere: plugins/vector-db/assets/diagrams/deployment_model.m`
- Line `276`: `| `.agents/skills/ecosystem-authoritative-sources/references/plugin-architecture.mmd` | `../../../../assets/diagrams/plugin-architecture.mmd` | Found elsewhere: plugins/agent-skill-open-specifications`
- Line `278`: `| `.agents/skills/ecosystem-authoritative-sources/references/skill-execution-flow.mmd` | `../../../../assets/diagrams/skill-execution-flow.mmd` | Found elsewhere: plugins/agent-skill-open-specificatio`
- Line `281`: `| `.agents/skills/ecosystem-authoritative-sources/references/diagrams/plugin-architecture.mmd` | `../../../../references/ecosystem-authoritative-sources/diagrams/plugin-architecture.mmd` | Found elsew`
- Line `282`: `| `.agents/skills/ecosystem-authoritative-sources/references/diagrams/plugin-architecture.png` | `../../../../references/ecosystem-authoritative-sources/diagrams/plugin-architecture.png` | Found elsew`
- Line `283`: `| `.agents/skills/ecosystem-authoritative-sources/references/diagrams/skill-execution-flow.mmd` | `../../../../references/ecosystem-authoritative-sources/diagrams/skill-execution-flow.mmd` | Found els`
- Line `284`: `| `.agents/skills/ecosystem-authoritative-sources/references/diagrams/skill-execution-flow.png` | `../../../../references/ecosystem-authoritative-sources/diagrams/skill-execution-flow.png` | Found els`
- Line `285`: `| `.agents/skills/ecosystem-authoritative-sources/references/reference/plugin-architecture.mmd` | `../../../../references/ecosystem-authoritative-sources/reference/plugin-architecture.mmd` | Found els`
- Line `286`: `| `.agents/skills/ecosystem-authoritative-sources/references/reference/plugin-architecture.png` | `../../../../references/ecosystem-authoritative-sources/reference/plugin-architecture.png` | Found els`
- Line `288`: `| `.agents/skills/ecosystem-authoritative-sources/references/reference/skill-execution-flow.mmd` | `../../../../references/ecosystem-authoritative-sources/reference/skill-execution-flow.mmd` | Found e`
- Line `289`: `| `.agents/skills/ecosystem-authoritative-sources/references/reference/skill-execution-flow.png` | `../../../../references/ecosystem-authoritative-sources/reference/skill-execution-flow.png` | Found e`
- Line `292`: `| `.agents/skills/ecosystem-authoritative-sources/assets/resources/plugin-architecture.mmd` | `../../../../assets/resources/plugin-architecture.mmd` | Found elsewhere: plugins/agent-skill-open-specifi`
- Line `293`: `| `.agents/skills/ecosystem-authoritative-sources/assets/resources/skill-execution-flow.mmd` | `../../../../assets/resources/skill-execution-flow.mmd` | Found elsewhere: plugins/agent-skill-open-speci`

### [ ] plugins/agent-plugin-analyzer/skills/path-reference-auditor/references/check_plugin_boundaries.py
- Line `14`: `python3 check_plugin_boundaries.py temp/inventory.json --plugin plugins/adr-manager`
- Line `56`: `plugins/adr-manager/commands/adr-management.md  plugins/adr-manager/`
- Line `57`: `plugins/plugin-installer/hooks/hooks.json  plugins/plugin-installer/`
- Line `58`: `plugins/adr-manager/.claude-plugin/plugin.json  plugins/adr-manager/`
- Line `61`: `plugins/adr-manager/skills/adr-management/SKILL.md  None (skip)`
- Line `76`: `return Path(*parts[:idx+2])  # e.g., plugins/adr-manager/`

### [ ] plugins/agent-plugin-analyzer/skills/path-reference-auditor/references/check_skill_boundaries.py
- Line `14`: `python3 check_skill_boundaries.py temp/inventory.json --skill plugins/adr-manager/skills/adr-management`
- Line `62`: `r"re:/Users/.*",           # macOS absolute paths (e.g. /Users/robert/...)`
- Line `97`: `plugins/adr-manager/skills/adr-management/SKILL.md`
- Line `98`: `plugins/adr-manager/skills/adr-management/`
- Line `110`: `return Path(*parts[:idx+2])  # e.g., plugins/adr-manager/skills/adr-management`

### [ ] plugins/agent-plugin-analyzer/skills/path-reference-auditor/references/path_reference_auditor.py
- Line `110`: `Walk all plugins/skills directories and find every ./reference.`

### [ ] plugins/agent-plugin-analyzer/skills/path-reference-auditor/references/usage-guide.md
- Line `89`: `python3 ./check_skill_boundaries.py inventory.json --skill plugins/adr-manager/skills/adr-management`
- Line `97`: `RESOLVES TO: plugins/adr-manager/templates/adr-template.md  ❌ OUTSIDE!`
- Line `102`: `cd plugins/adr-manager/skills/adr-management`
- Line `119`: `python3 ./check_plugin_boundaries.py inventory.json --plugin plugins/plugin-installer`
- Line `124`: `FILE: plugins/adr-manager/commands/adr-management.md:8`
- Line `126`: `PLUGIN ROOT: plugins/adr-manager/`
- Line `132`: `cd plugins/adr-manager`

### [ ] plugins/agent-plugin-analyzer/skills/path-reference-auditor/scripts/check_plugin_boundaries.py
- Line `14`: `python3 check_plugin_boundaries.py temp/inventory.json --plugin plugins/adr-manager`
- Line `56`: `plugins/adr-manager/commands/adr-management.md  plugins/adr-manager/`
- Line `57`: `plugins/plugin-installer/hooks/hooks.json  plugins/plugin-installer/`
- Line `58`: `plugins/adr-manager/.claude-plugin/plugin.json  plugins/adr-manager/`
- Line `61`: `plugins/adr-manager/skills/adr-management/SKILL.md  None (skip)`
- Line `76`: `return Path(*parts[:idx+2])  # e.g., plugins/adr-manager/`

### [ ] plugins/agent-plugin-analyzer/skills/path-reference-auditor/scripts/check_skill_boundaries.py
- Line `14`: `python3 check_skill_boundaries.py temp/inventory.json --skill plugins/adr-manager/skills/adr-management`
- Line `62`: `r"re:/Users/.*",           # macOS absolute paths (e.g. /Users/robert/...)`
- Line `97`: `plugins/adr-manager/skills/adr-management/SKILL.md`
- Line `98`: `plugins/adr-manager/skills/adr-management/`
- Line `110`: `return Path(*parts[:idx+2])  # e.g., plugins/adr-manager/skills/adr-management`

### [ ] plugins/agent-plugin-analyzer/skills/path-reference-auditor/scripts/fix_inside_plugin_symlinks.py
- Line `74`: `"""Extract plugin root from path like plugins/adr-manager/skills/adr-management/file.md"""`

### [ ] plugins/agent-plugin-analyzer/skills/path-reference-auditor/scripts/path_reference_auditor.py
- Line `110`: `Walk all plugins/skills directories and find every ./reference.`

### [ ] plugins/agent-scaffolders/references/examples/plugin-features-reference.md
- Line `106`: `Read template: @/path/to/plugins/plugin-name/templates/report.md`

### [ ] plugins/agent-scaffolders/references/plugin-features-reference.md
- Line `106`: `Read template: @/path/to/plugins/plugin-name/templates/report.md`

### [ ] plugins/agent-scaffolders/skills/create-command/references/examples/plugin-features-reference.md
- Line `106`: `Read template: @/path/to/plugins/plugin-name/templates/report.md`

### [ ] plugins/agent-scaffolders/skills/create-command/references/plugin-features-reference.md
- Line `106`: `Read template: @/path/to/plugins/plugin-name/templates/report.md`

### [ ] plugins/agent-scaffolders/skills/manage-marketplace/SKILL.md
- Line `78`: `4.  Optional: use `metadata.pluginRoot` to shorten relative source paths. Setting `"pluginRoot": "./plugins"` lets you write `"source": "formatter"` instead of `"source": "./plugins/formatter"`.`

### [ ] plugins/agent-skill-open-specifications/references/marketplace.md
- Line `23`: `- `metadata.pluginRoot`: Base directory prepended to relative plugin source paths. Setting `"./plugins"` lets entries use `"source": "formatter"` instead of `"source": "./plugins/formatter"`.`
- Line `119`: `- **Submit to official marketplace**: Claude.ai: `claude.ai/settings/plugins/submit` · Console: `platform.claude.com/plugins/submit`.`

### [ ] plugins/agent-skill-open-specifications/references/plugins.md
- Line `25`: `- **Plugin Cache:** Installed marketplace plugins are copied to a cache (`~/.claude/plugins/cache`).`
- Line `26`: `- **`plugins`:** Always use this environment variable inside `hooks.json`, `.mcp.json`, and scripts to reference the absolute path of your plugin (e.g. `"plugins/scripts/execute.sh"`).`

### [ ] plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/references/marketplace.md
- Line `23`: `- `metadata.pluginRoot`: Base directory prepended to relative plugin source paths. Setting `"./plugins"` lets entries use `"source": "formatter"` instead of `"source": "./plugins/formatter"`.`
- Line `119`: `- **Submit to official marketplace**: Claude.ai: `claude.ai/settings/plugins/submit` · Console: `platform.claude.com/plugins/submit`.`

### [ ] plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/references/plugins.md
- Line `25`: `- **Plugin Cache:** Installed marketplace plugins are copied to a cache (`~/.claude/plugins/cache`).`
- Line `26`: `- **`plugins`:** Always use this environment variable inside `hooks.json`, `.mcp.json`, and scripts to reference the absolute path of your plugin (e.g. `"plugins/scripts/execute.sh"`).`

### [ ] plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/references/reference/marketplace.md
- Line `23`: `- `metadata.pluginRoot`: Base directory prepended to relative plugin source paths. Setting `"./plugins"` lets entries use `"source": "formatter"` instead of `"source": "./plugins/formatter"`.`
- Line `119`: `- **Submit to official marketplace**: Claude.ai: `claude.ai/settings/plugins/submit` · Console: `platform.claude.com/plugins/submit`.`

### [ ] plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/references/reference/plugins.md
- Line `25`: `- **Plugin Cache:** Installed marketplace plugins are copied to a cache (`~/.claude/plugins/cache`).`
- Line `26`: `- **`plugins`:** Always use this environment variable inside `hooks.json`, `.mcp.json`, and scripts to reference the absolute path of your plugin (e.g. `"plugins/scripts/execute.sh"`).`

### [ ] plugins/exploration-cycle-plugin/references/spec-kitty-skill-optimizer-program.md
- Line `235`: `<USER_HOME>/Projects/agent-plugins-skills/plugins/spec-kitty-plugin/agents/spec-kitty-agent.md`

### [ ] plugins/exploration-cycle-plugin/skills/exploration-optimizer/references/spec-kitty-skill-optimizer-program.md
- Line `235`: `<USER_HOME>/Projects/agent-plugins-skills/plugins/spec-kitty-plugin/agents/spec-kitty-agent.md`

### [ ] plugins/obsidian-integration/scripts/obsidian-parser/tests/test_parser.py
- Line `11`: `python3 -m unittest plugins/obsidian-integration/scripts/obsidian-parser/tests/test_parser.py`

### [ ] plugins/plugin-manager/README.md
- Line `98`: `| **[maintain-plugins](skills/maintain-plugins/SKILL.md)** | Audit structure, sync agent environments, scaffold READMEs, clean orphans | `sync_with_inventory.py`, `audit_structure.py` |`
- Line `99`: `| **[auto-update-plugins](skills/auto-update-plugins/SKILL.md)** | SessionStart hook that auto-syncs from GitHub sources on every session | `check_and_sync.py` |`

### [ ] plugins/plugin-manager/references/cleanup_process.md
- Line `3`: `This document explains the logic used by `../scripts/sync_with_inventory.py` to manage plugin lifecycles in consuming repositories. It is invoked via the **[maintain-plugins](../skills/maintain-plugin`

### [ ] plugins/plugin-manager/references/installer-bootstrap-architecture.md
- Line `95`: `We publish a tiny stub package to NPM (`@agent-plugins/cli`) whose ONLY job is to execute a `fetch()` call, download the Python `plugin_add.py` script to a temp folder, and spawn `python3 temp_script.`
- Line `98`: `npx @agent-plugins/cli add richfrem/agent-plugins-skills`

### [ ] plugins/plugin-manager/references/plugin_replicator_overview.md
- Line `10`: `--dest <USER_HOME>/Projects/Project_Sanctuary/plugins/rlm-factory`
- Line `18`: `--source <USER_HOME>/Projects/agent-plugins-skills/plugins/rlm-factory \`
- Line `19`: `--dest <PROJECT_ROOT>/plugins/rlm-factory \`

### [ ] plugins/plugin-manager/scripts/audit_structure.py
- Line `14`: `python3 plugins/plugin-manager/scripts/audit_structure.py`
- Line `37`: `- plugins/agent-skill-open-specifications/skills/ecosystem-standards/SKILL.md`

### [ ] plugins/plugin-manager/scripts/clean_orphans.py
- Line `12`: `python3 plugins/plugin-manager/scripts/clean_orphans.py [--dry-run]`

### [ ] plugins/plugin-manager/scripts/cleanup_targets.py
- Line `12`: `python3 plugins/plugin-manager/scripts/cleanup_targets.py`

### [ ] plugins/plugin-manager/scripts/generate_readmes.py
- Line `12`: `python3 plugins/plugin-manager/scripts/generate_readmes.py [--apply]`
- Line `47`: `PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent  # repo-root/plugins/plugin-manager/scripts/ → 3 levels up`

### [ ] plugins/plugin-manager/scripts/install_all_plugins.py
- Line `12`: `python3 plugins/plugin-manager/scripts/install_all_plugins.py`
- Line `13`: `python3 plugins/plugin-manager/scripts/install_all_plugins.py --plugins-dir "temp/agent-plugins-skills/plugins"`

### [ ] plugins/plugin-manager/scripts/plugin_add.py
- Line `24`: `python plugins/plugin-manager/scripts/plugin_add.py`
- Line `27`: `python plugins/plugin-manager/scripts/plugin_add.py richfrem/agent-plugins-skills`
- Line `30`: `python plugins/plugin-manager/scripts/plugin_add.py richfrem/agent-plugins-skills --all -y`
- Line `33`: `python plugins/plugin-manager/scripts/plugin_add.py --dry-run`
- Line `245`: `anthropics/knowledge-work-plugins/engineering       → ("anthropics/knowledge-work-plugins", "engineering")`

### [ ] plugins/plugin-manager/scripts/plugin_bootstrap.py
- Line `12`: `python3 plugins/plugin-manager/scripts/plugin_bootstrap.py`

### [ ] plugins/plugin-manager/scripts/plugin_inventory.py
- Line `15`: `python3 plugins/plugin-manager/scripts/plugin_inventory.py [--root <project_root>] [--output <file.json>]`

### [ ] plugins/plugin-manager/scripts/sync_with_inventory.py
- Line `12`: `python3 plugins/plugin-manager/scripts/sync_with_inventory.py [--dry-run]`
- Line `68`: `BRIDGE_INSTALLER = PROJECT_ROOT / "plugins/plugin-manager/scripts/plugin_installer.py"`

### [ ] plugins/plugin-manager/scripts/update_agent_system.py
- Line `13`: `plugins/spec-kitty-plugin/commands/ (the auto-generated layer).`
- Line `20`: `python3 plugins/plugin-manager/scripts/update_agent_system.py`
- Line `29`: `SPEC_KITTY_SYNC = ROOT / "plugins/spec-kitty-plugin/skills/spec-kitty-agent/scripts/sync_configuration.py"`
- Line `30`: `PLUGIN_INSTALLER = ROOT / "plugins/plugin-manager/scripts/install_all_plugins.py"`
- Line `62`: `# Converts fresh .windsurf/workflows/*.md into plugins/spec-kitty-plugin/commands/`

### [ ] plugins/plugin-manager/skills/auto-update-plugins/scripts/check_and_sync.py
- Line `73`: `Path(__file__).resolve().parent.parent.parent / "plugins/plugin-manager/scripts/plugin_add.py",`
- Line `74`: `PROJECT_ROOT / "plugins/plugin-manager/scripts/plugin_add.py",`
- Line `161`: `"Run `python plugins/plugin-manager/scripts/plugin_add.py` manually.")`

### [ ] plugins/plugin-manager/skills/maintain-plugins/references/cleanup_process.md
- Line `3`: `This document explains the logic used by `../scripts/sync_with_inventory.py` to manage plugin lifecycles in consuming repositories. It is invoked via the **[maintain-plugins](../skills/maintain-plugin`

### [ ] plugins/plugin-manager/skills/maintain-plugins/scripts/audit_structure.py
- Line `14`: `python3 plugins/plugin-manager/scripts/audit_structure.py`
- Line `37`: `- plugins/agent-skill-open-specifications/skills/ecosystem-standards/SKILL.md`

### [ ] plugins/plugin-manager/skills/maintain-plugins/scripts/generate_readmes.py
- Line `12`: `python3 plugins/plugin-manager/scripts/generate_readmes.py [--apply]`
- Line `47`: `PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent  # repo-root/plugins/plugin-manager/scripts/ → 3 levels up`

### [ ] plugins/plugin-manager/skills/maintain-plugins/scripts/plugin_bootstrap.py
- Line `12`: `python3 plugins/plugin-manager/scripts/plugin_bootstrap.py`

### [ ] plugins/plugin-manager/skills/maintain-plugins/scripts/plugin_inventory.py
- Line `15`: `python3 plugins/plugin-manager/scripts/plugin_inventory.py [--root <project_root>] [--output <file.json>]`

### [ ] plugins/plugin-manager/skills/maintain-plugins/scripts/sync_with_inventory.py
- Line `12`: `python3 plugins/plugin-manager/scripts/sync_with_inventory.py [--dry-run]`
- Line `68`: `BRIDGE_INSTALLER = PROJECT_ROOT / "plugins/plugin-manager/scripts/plugin_installer.py"`

### [ ] plugins/plugin-manager/skills/plugin-installer/SKILL.md
- Line `184`: `| `anthropics/knowledge-work-plugins/engineering` | Clone repo, drill into `engineering/` as a single plugin |`
- Line `204`: `python ./scripts/plugin_add.py anthropics/knowledge-work-plugins/engineering`

### [ ] plugins/rlm-factory/assets/references/research-summary.md
- Line `59`: `*   **Discovery CLI:** Scripts within self-contained plugins/skills architecture (Recursive Scanner)`

### [ ] plugins/rlm-factory/assets/references/research/summary.md
- Line `59`: `*   **Discovery CLI:** Scripts within self-contained plugins/skills architecture (Recursive Scanner)`

### [ ] plugins/rlm-factory/commands/rlm-search.md
- Line `74`: `# Search plugins/scripts cache`

### [ ] plugins/rlm-factory/references/research/summary.md
- Line `59`: `*   **Discovery CLI:** Scripts within self-contained plugins/skills architecture (Recursive Scanner)`

### [ ] plugins/rlm-factory/skills/rlm-cleanup-agent/references/research-summary.md
- Line `59`: `*   **Discovery CLI:** Scripts within self-contained plugins/skills architecture (Recursive Scanner)`

### [ ] plugins/rlm-factory/skills/rlm-cleanup-agent/references/research/summary.md
- Line `59`: `*   **Discovery CLI:** Scripts within self-contained plugins/skills architecture (Recursive Scanner)`

### [ ] plugins/rlm-factory/skills/rlm-curator/references/research-summary.md
- Line `59`: `*   **Discovery CLI:** Scripts within self-contained plugins/skills architecture (Recursive Scanner)`

### [ ] plugins/rlm-factory/skills/rlm-distill-agent/references/research-summary.md
- Line `59`: `*   **Discovery CLI:** Scripts within self-contained plugins/skills architecture (Recursive Scanner)`

### [ ] plugins/rlm-factory/skills/rlm-distill-agent/references/research/summary.md
- Line `59`: `*   **Discovery CLI:** Scripts within self-contained plugins/skills architecture (Recursive Scanner)`

### [ ] plugins/rlm-factory/skills/rlm-distill-ollama/references/research-summary.md
- Line `59`: `*   **Discovery CLI:** Scripts within self-contained plugins/skills architecture (Recursive Scanner)`

### [ ] plugins/rlm-factory/skills/rlm-distill-ollama/references/research/summary.md
- Line `59`: `*   **Discovery CLI:** Scripts within self-contained plugins/skills architecture (Recursive Scanner)`

### [ ] plugins/rlm-factory/skills/rlm-search/SKILL.md
- Line `74`: `# Search plugins/scripts cache`

### [ ] plugins/rlm-factory/skills/rlm-search/references/research-summary.md
- Line `59`: `*   **Discovery CLI:** Scripts within self-contained plugins/skills architecture (Recursive Scanner)`

### [ ] plugins/rlm-factory/skills/rlm-search/references/research/summary.md
- Line `59`: `*   **Discovery CLI:** Scripts within self-contained plugins/skills architecture (Recursive Scanner)`

### [ ] plugins/rlm-factory/tests/test_rlm_config.py
- Line `11`: `pytest plugins/rlm-factory/tests/test_rlm_config.py`

### [ ] plugins/rsvp-speed-reader/README.md
- Line `34`: `cd plugins/rsvp-speed-reader`

### [ ] plugins/rsvp-speed-reader/scripts/execute.py
- Line `11`: `python3 plugins/rsvp-speed-reader/scripts/execute.py [--example value]`

### [ ] plugins/rsvp-speed-reader/skills/rsvp-reading/scripts/execute.py
- Line `11`: `python3 plugins/rsvp-speed-reader/scripts/execute.py [--example value]`

### [ ] plugins/spec-kitty-plugin/assets/templates/documentation/templates/plan-template.md
- Line `175`: `"plugins": ["plugins/markdown"]`

### [ ] plugins/spec-kitty-plugin/assets/templates/research/command-templates/tasks.md
- Line `43`: `**CRITICAL**: The command returns JSON with `feature_dir` as an ABSOLUTE path (e.g., `/Users/robert/Code/project/kitty-specs/015-research-topic`).`

### [ ] plugins/spec-kitty-plugin/assets/templates/software-dev/command-templates/tasks.md
- Line `88`: `**CRITICAL**: The command returns JSON with `feature_dir` as an ABSOLUTE path (e.g., `/Users/robert/Code/new_specify/kitty-specs/001-feature-name`).`
- Line `93`: `feature_dir = "/Users/robert/Code/new_specify/kitty-specs/001-a-simple-hello"`

### [ ] plugins/spec-kitty-plugin/assets/templates/tasks.md
- Line `43`: `**CRITICAL**: The command returns JSON with `feature_dir` as an ABSOLUTE path (e.g., `/Users/robert/Code/project/kitty-specs/015-research-topic`).`

### [ ] plugins/spec-kitty-plugin/references/LLM_UNPACKAGING_INSTRUCTIONS.md
- Line `24`: `Access `bridge/plugins/tool_inventory.json` (included in this bundle) to see the list of tools available for registration in your agent's configuration.`

### [ ] plugins/spec-kitty-plugin/rules/AGENTS.md
- Line `15`: `- `/Users/robert/Code/myproject/kitty-specs/001-feature/spec.md``

### [ ] plugins/spec-kitty-plugin/scripts/sync_configuration.py
- Line `186`: `print("   The local repository is now synced. Ask the user if they want to use their ecosystem's plugin bridge to install or update `plugins/spec-kitty-plugin` for their active AI environment.")`

### [ ] plugins/spec-kitty-plugin/scripts/verify_workflow_state.py
- Line `12`: `python3 plugins/spec-kitty-plugin/scripts/verify_workflow_state.py --feature SLUG --phase specify`

### [ ] plugins/spec-kitty-plugin/skills/spec-kitty-analyze/tasks.md
- Line `43`: `**CRITICAL**: The command returns JSON with `feature_dir` as an ABSOLUTE path (e.g., `/Users/robert/Code/project/kitty-specs/015-research-topic`).`

### [ ] plugins/spec-kitty-plugin/skills/spec-kitty-checklist/templates/tasks.md
- Line `43`: `**CRITICAL**: The command returns JSON with `feature_dir` as an ABSOLUTE path (e.g., `/Users/robert/Code/project/kitty-specs/015-research-topic`).`

### [ ] plugins/spec-kitty-plugin/skills/spec-kitty-implement/scripts/sync_configuration.py
- Line `186`: `print("   The local repository is now synced. Ask the user if they want to use their ecosystem's plugin bridge to install or update `plugins/spec-kitty-plugin` for their active AI environment.")`

### [ ] plugins/spec-kitty-plugin/skills/spec-kitty-merge/scripts/sync_configuration.py
- Line `186`: `print("   The local repository is now synced. Ask the user if they want to use their ecosystem's plugin bridge to install or update `plugins/spec-kitty-plugin` for their active AI environment.")`

### [ ] plugins/spec-kitty-plugin/skills/spec-kitty-plan/scripts/sync_configuration.py
- Line `186`: `print("   The local repository is now synced. Ask the user if they want to use their ecosystem's plugin bridge to install or update `plugins/spec-kitty-plugin` for their active AI environment.")`

### [ ] plugins/spec-kitty-plugin/skills/spec-kitty-plan/tasks.md
- Line `43`: `**CRITICAL**: The command returns JSON with `feature_dir` as an ABSOLUTE path (e.g., `/Users/robert/Code/project/kitty-specs/015-research-topic`).`

### [ ] plugins/spec-kitty-plugin/skills/spec-kitty-review/scripts/sync_configuration.py
- Line `186`: `print("   The local repository is now synced. Ask the user if they want to use their ecosystem's plugin bridge to install or update `plugins/spec-kitty-plugin` for their active AI environment.")`

### [ ] plugins/spec-kitty-plugin/skills/spec-kitty-specify/scripts/sync_configuration.py
- Line `186`: `print("   The local repository is now synced. Ask the user if they want to use their ecosystem's plugin bridge to install or update `plugins/spec-kitty-plugin` for their active AI environment.")`

### [ ] plugins/spec-kitty-plugin/skills/spec-kitty-sync-plugin/scripts/sync_configuration.py
- Line `186`: `print("   The local repository is now synced. Ask the user if they want to use their ecosystem's plugin bridge to install or update `plugins/spec-kitty-plugin` for their active AI environment.")`

### [ ] plugins/spec-kitty-plugin/skills/spec-kitty-tasks-finalize/tasks.md
- Line `43`: `**CRITICAL**: The command returns JSON with `feature_dir` as an ABSOLUTE path (e.g., `/Users/robert/Code/project/kitty-specs/015-research-topic`).`

### [ ] plugins/spec-kitty-plugin/skills/spec-kitty-tasks-outline/tasks.md
- Line `43`: `**CRITICAL**: The command returns JSON with `feature_dir` as an ABSOLUTE path (e.g., `/Users/robert/Code/project/kitty-specs/015-research-topic`).`

### [ ] plugins/spec-kitty-plugin/skills/spec-kitty-tasks-packages/tasks.md
- Line `43`: `**CRITICAL**: The command returns JSON with `feature_dir` as an ABSOLUTE path (e.g., `/Users/robert/Code/project/kitty-specs/015-research-topic`).`

### [ ] plugins/spec-kitty-plugin/skills/spec-kitty-tasks/tasks.md
- Line `43`: `**CRITICAL**: The command returns JSON with `feature_dir` as an ABSOLUTE path (e.g., `/Users/robert/Code/project/kitty-specs/015-research-topic`).`

### [ ] plugins/spec-kitty-plugin/skills/spec-kitty-workflow/tasks.md
- Line `43`: `**CRITICAL**: The command returns JSON with `feature_dir` as an ABSOLUTE path (e.g., `/Users/robert/Code/project/kitty-specs/015-research-topic`).`

### [ ] plugins/tool-inventory/scripts/audit_plugins.py
- Line `12`: `python3 plugins/tool-inventory/scripts/audit_plugins.py`

### [ ] plugins/tool-inventory/scripts/fix_inventory_paths.py
- Line `12`: `python3 plugins/tool-inventory/scripts/fix_inventory_paths.py [--apply]`

### [ ] plugins/tool-inventory/scripts/generate_tools_manifest.py
- Line `12`: `python3 plugins/tool-inventory/scripts/generate_tools_manifest.py`
- Line `13`: `python3 plugins/tool-inventory/scripts/generate_tools_manifest.py --output plugins/tools_manifest.json`
- Line `25`: `- `plugins/tools_manifest.json` (Json list of discovered scripts)`
- Line `83`: `parser.add_argument("--output", default="plugins/tools_manifest.json", help="Output path")`

### [ ] plugins/tool-inventory/scripts/manage_tool_inventory.py
- Line `536`: `# Ignore plugins/investment-screener UNLESS it is in backend/py_services`
- Line `539`: `if rel.startswith("plugins/investment-screener"):`

### [ ] plugins/tool-inventory/scripts/rebuild_inventory.py
- Line `7`: `Scans the plugins directory and rebuilds plugins/tool_inventory.json from scratch.`
- Line `13`: `python3 plugins/tool-inventory/scripts/rebuild_inventory.py`
- Line `22`: `- plugins/tool_inventory.json (rebuilt from scratch)`
- Line `28`: `- plugins/tool-inventory/scripts/manage_tool_inventory.py`
- Line `37`: `# This script is at plugins/tool-inventory/scripts/rebuild_inventory.py`

### [ ] plugins/tool-inventory/scripts/sync_inventory_descriptions.py
- Line `14`: `python3 plugins/tool-inventory/scripts/sync_inventory_descriptions.py`
- Line `33`: `- plugins/tool-inventory/scripts/manage_tool_inventory.py`

### [ ] plugins/tool-inventory/scripts/tool_chroma.py
- Line `16`: `tc.upsert("plugins/example_script.py", "CLI router", {"category": "orchestrator"})`
- Line `20`: `python3 plugins/tool-inventory/scripts/tool_chroma.py stats`
- Line `21`: `python3 plugins/tool-inventory/scripts/tool_chroma.py search "query cache"`
- Line `22`: `python3 plugins/tool-inventory/scripts/tool_chroma.py list`
- Line `23`: `python3 plugins/tool-inventory/scripts/tool_chroma.py import-json .agents/learning/rlm_tool_cache.json`
- Line `38`: `- Persistent ChromaDB collection at plugins/tool-inventory/data/chroma/`

### [ ] plugins/tool-inventory/scripts/tool_inventory_init.py
- Line `14`: `python3 plugins/tool-inventory/scripts/tool_inventory_init.py`

### [ ] plugins/tool-inventory/skills/tool-inventory-init/scripts/manage_tool_inventory.py
- Line `536`: `# Ignore plugins/investment-screener UNLESS it is in backend/py_services`
- Line `539`: `if rel.startswith("plugins/investment-screener"):`

### [ ] plugins/tool-inventory/skills/tool-inventory-init/scripts/tool_inventory_init.py
- Line `14`: `python3 plugins/tool-inventory/scripts/tool_inventory_init.py`

### [ ] plugins/tool-inventory/skills/tool-inventory/references/manage_tool_inventory.py
- Line `536`: `# Ignore plugins/investment-screener UNLESS it is in backend/py_services`
- Line `539`: `if rel.startswith("plugins/investment-screener"):`

### [ ] plugins/tool-inventory/skills/tool-inventory/scripts/audit_plugins.py
- Line `12`: `python3 plugins/tool-inventory/scripts/audit_plugins.py`

### [ ] plugins/tool-inventory/skills/tool-inventory/scripts/fix_inventory_paths.py
- Line `12`: `python3 plugins/tool-inventory/scripts/fix_inventory_paths.py [--apply]`

### [ ] plugins/tool-inventory/skills/tool-inventory/scripts/generate_tools_manifest.py
- Line `12`: `python3 plugins/tool-inventory/scripts/generate_tools_manifest.py`
- Line `13`: `python3 plugins/tool-inventory/scripts/generate_tools_manifest.py --output plugins/tools_manifest.json`
- Line `25`: `- `plugins/tools_manifest.json` (Json list of discovered scripts)`
- Line `83`: `parser.add_argument("--output", default="plugins/tools_manifest.json", help="Output path")`

### [ ] plugins/tool-inventory/skills/tool-inventory/scripts/manage_tool_inventory.py
- Line `536`: `# Ignore plugins/investment-screener UNLESS it is in backend/py_services`
- Line `539`: `if rel.startswith("plugins/investment-screener"):`

### [ ] plugins/tool-inventory/skills/tool-inventory/scripts/rebuild_inventory.py
- Line `7`: `Scans the plugins directory and rebuilds plugins/tool_inventory.json from scratch.`
- Line `13`: `python3 plugins/tool-inventory/scripts/rebuild_inventory.py`
- Line `22`: `- plugins/tool_inventory.json (rebuilt from scratch)`
- Line `28`: `- plugins/tool-inventory/scripts/manage_tool_inventory.py`
- Line `37`: `# This script is at plugins/tool-inventory/scripts/rebuild_inventory.py`

### [ ] plugins/tool-inventory/skills/tool-inventory/scripts/sync_inventory_descriptions.py
- Line `14`: `python3 plugins/tool-inventory/scripts/sync_inventory_descriptions.py`
- Line `33`: `- plugins/tool-inventory/scripts/manage_tool_inventory.py`

### [ ] plugins/tool-inventory/skills/tool-inventory/scripts/tool_chroma.py
- Line `16`: `tc.upsert("plugins/example_script.py", "CLI router", {"category": "orchestrator"})`
- Line `20`: `python3 plugins/tool-inventory/scripts/tool_chroma.py stats`
- Line `21`: `python3 plugins/tool-inventory/scripts/tool_chroma.py search "query cache"`
- Line `22`: `python3 plugins/tool-inventory/scripts/tool_chroma.py list`
- Line `23`: `python3 plugins/tool-inventory/scripts/tool_chroma.py import-json .agents/learning/rlm_tool_cache.json`
- Line `38`: `- Persistent ChromaDB collection at plugins/tool-inventory/data/chroma/`

### [ ] plugins/vector-db/scripts/cleanup.py
- Line `13`: `python3 plugins/vector-db/scripts/cleanup.py`
- Line `14`: `python3 plugins/vector-db/scripts/cleanup.py --profile knowledge`
- Line `33`: `- plugins/vector-db/scripts/vector_config.py`
- Line `34`: `- plugins/vector-db/scripts/operations.py`

### [ ] plugins/vector-db/scripts/ingest.py
- Line `47`: `rlm_script_dir = PROJECT_ROOT / "plugins/rlm-factory/skills/rlm-curator/scripts"`

### [ ] plugins/vector-db/scripts/query.py
- Line `16`: `# File is at: plugins/vector-db/scripts/query.py`

### [ ] plugins/vector-db/scripts/vector_config.py
- Line `17`: `# The script is in plugins/vector-db/scripts/, so root is 3 levels up`

### [ ] plugins/vector-db/skills/vector-db-cleanup/scripts/cleanup.py
- Line `13`: `python3 plugins/vector-db/scripts/cleanup.py`
- Line `14`: `python3 plugins/vector-db/scripts/cleanup.py --profile knowledge`
- Line `33`: `- plugins/vector-db/scripts/vector_config.py`
- Line `34`: `- plugins/vector-db/scripts/operations.py`

### [ ] plugins/vector-db/skills/vector-db-cleanup/scripts/query.py
- Line `16`: `# File is at: plugins/vector-db/scripts/query.py`

### [ ] plugins/vector-db/skills/vector-db-cleanup/scripts/vector_config.py
- Line `17`: `# The script is in plugins/vector-db/scripts/, so root is 3 levels up`

### [ ] plugins/vector-db/skills/vector-db-ingest/scripts/ingest.py
- Line `47`: `rlm_script_dir = PROJECT_ROOT / "plugins/rlm-factory/skills/rlm-curator/scripts"`

### [ ] plugins/vector-db/skills/vector-db-ingest/scripts/query.py
- Line `16`: `# File is at: plugins/vector-db/scripts/query.py`

### [ ] plugins/vector-db/skills/vector-db-ingest/scripts/vector_config.py
- Line `17`: `# The script is in plugins/vector-db/scripts/, so root is 3 levels up`

### [ ] plugins/vector-db/skills/vector-db-init/scripts/query.py
- Line `16`: `# File is at: plugins/vector-db/scripts/query.py`

### [ ] plugins/vector-db/skills/vector-db-launch/scripts/query.py
- Line `16`: `# File is at: plugins/vector-db/scripts/query.py`

### [ ] plugins/vector-db/skills/vector-db-search/scripts/ingest.py
- Line `47`: `rlm_script_dir = PROJECT_ROOT / "plugins/rlm-factory/skills/rlm-curator/scripts"`

### [ ] plugins/vector-db/skills/vector-db-search/scripts/query.py
- Line `16`: `# File is at: plugins/vector-db/scripts/query.py`

### [ ] plugins/vector-db/skills/vector-db-search/scripts/vector_config.py
- Line `17`: `# The script is in plugins/vector-db/scripts/, so root is 3 levels up`

### [ ] tasks/backlog/0010-bl-007-bridge-plugin-not-copying-assets-directory-during-plugin-install.md
- Line `4`: `plugins/task-manager/assets/templates/task-template.md exists in source but is missing from .agent/skills/task-agent/ after plugin-installer install. plugin-installer SKILL.md maps skills/ commands/ r`

### [ ] tasks/backlog/0015-standardize-all-plugin-templates-to-jinja-format.md
- Line `15`: `- **Reference pattern:** `plugins/agent-plugin-analyzer/assets/templates/README.md.jinja` is the target convention.`

### [ ] tasks/in-progress/0011-bl-008-task-agent-skill-md-unclear-on-which-script-path-to-use-agents-use-wrong-path.md
- Line `4`: `task-agent SKILL.md does not clearly specify whether to call scripts from plugins/task-manager/skills/task-agent/scripts/ or .agent/skills/task-agent/scripts/. This session used the .agent/ installed `

### [ ] temp_gemini_propose.py
- Line `4`: `skill_path = "plugins/gemini-cli/skills/gemini-cli-agent/SKILL.md"`
- Line `5`: `evals_path = "plugins/gemini-cli/skills/gemini-cli-agent/evals/evals.json"`

