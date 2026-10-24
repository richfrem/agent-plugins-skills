# APM Alignment: Standard Fixes

Every finding from `scripts/apm_build_pipeline.py` carries a `fix` id from this table. The same
misalignment with the APM model is always fixed the same way. The pipeline never edits the source
tree: it reports the fix (and, for SF-3, the exact replacement link), and the fix is applied as a
normal reviewed source change.

Direction for every fix: the APM migration plan (`docs/plans/apm_migration_plan.md` in the
source repository), Section 10.3. Each file lives in one canonical place; skills cite it with a relative markdown link;
no new symlinks and no duplicate copies.

| Fix | Finding(s) | Standard fix |
| :--- | :--- | :--- |
| **SF-1** | `broken_symlink` | The symlink points at a file that moved or no longer exists. Delete the dummy symlink file. If anything cites it, point that citation at the canonical file with a relative link. Remove its entry from `symlinks.json` if it has one. Do not repoint the symlink and do not copy the file in. |
| **SF-2** | `cross_plugin_symlink` | The symlink pulls a file from another plugin, which APM rejects (a link outside the package aborts the install) and ADR-001 forbids. Delete the symlink and its `symlinks.json` entry. Where the content is needed, reference the other plugin's skill or rule by name instead of copying it. |
| **SF-3** | `broken_relative_link`, `link_escapes_package` | APM copies only the skill folder, but rewrites **markdown links** that leave it to point into its package cache (`apm_modules/` in a project, `~/.apm/apm_modules/` globally), so links to sibling skills and plugin-root files work for every target and scope. Fix broken links so they resolve to a file inside the plugin. A link that leaves the plugin is not rewritten and breaks: reference the other plugin's skill by name instead. |
| **SF-4** | `symlink_in_package`, `sha256_mismatch` | Staging did not dereference a link. Re-run the pipeline. If it persists, the link is not tracked in git (normalize reads links from the git index); commit it or remove it. |
| **SF-5** | `frontmatter_name`, `frontmatter_description` | Set the `SKILL.md` frontmatter `name` to the skill folder name, and give it a third-person `description`. |
| **SF-6** | `skill_not_deployed`, `deployed_content_mismatch`, `uninstall_left_files` | Compare the staged package with the fixture install in `build/test-deploy/<plugin>/`. A skill without a valid `SKILL.md` is not deployed. If deployed content differs and its links do not resolve, record it as an APM issue. |
| **SF-7** | `apm_install_failed` | Read the APM error in the report's `test_deploy.steps`. Known case: the CLI accepts the target `agents`, but a package `apm.yml` accepts only `agent-skills`; the package stage maps it automatically. |
| **SF-8** | `path_not_rewritten` | APM rewrites only markdown links. Paths in inline code, code blocks or plain text that climb out of the skill folder (e.g. `python3 ../../scripts/x.py`) break after install. For documents, use a markdown link. For a script the skill tells the agent to run, keep the script inside that skill (`scripts/x.py`). |
| **SF-9** | `rules_not_deployed` (info) | APM does not install a plugin's `rules/` folder. Decision (2026-10-22): rules stay outside APM; setup copies the rules a project needs into `.agent/rules/`, and `AGENTS.md` lists them there. No change to the package. |
| **SF-10** | `lsp_config_invalid` | APM reads `lsp.json` as a flat map of server name to `{command, ...}`. A file shaped `{"languageServers": {}}` declares no servers and APM skips it with a warning: delete the empty file, or rewrite it in the flat format if servers are needed. |
| **SF-11** | `hook_script_harness_path` | Hook scripts run under every target harness (APM copies them into `.claude/hooks/`, `.agents/hooks/`, `.codex/hooks/`, `.github/hooks/scripts/`). A script that reads or writes `.claude/...` or `.agents/...` assumes one harness. Use `Path(__file__)` for the script's own files and a harness-neutral project path (e.g. `context/`) for state. |
| **SF-12** | `agent_mirrors_skill` | An `agents/<name>.md` file that is a symlink (or copy) of a skill's `SKILL.md` carries links written relative to the skill folder, which break once the file sits in `agents/` (and in each harness's agents folder after install). Write the agent as its own short definition that uses the skill by name. Changes agent behaviour, so review before applying. |
| none | `link_rewritten_by_apm` | Informational. APM rewrites cross-skill links in deployed markdown to point into `apm_modules/`, and they still resolve. |

## Examples already applied

- **SF-1**: six dangling links in `plugins/agent-extension-authoring/references/ADRs/` pointed at a root
  `ADRs/` folder that moved to `docs/ADRs/`. The dummy files were deleted; nothing cited them by path.
- **SF-2**: `plugins/agent-extension-authoring/skills/audit-plugin/references/destructive-action-guard.md`
  linked into `plugins/agent-agentic-os/rules/`. The symlink and its `symlinks.json` entry were removed.
- **SF-3**: `plugins/agent-extension-authoring/references/index.md` (deployed through
  `ecosystem-authoritative-sources` as a symlink) linked to a sibling that only exists next to the
  plugin-root original, so the link did not resolve from the skill. It now points at
  `../../create-skill/references/anthropic-skill-authoring-best-practices.md`.
