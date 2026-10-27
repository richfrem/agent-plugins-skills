---
description: Universal rules for APM-native plugin packaging, self-contained skills, cross-plugin boundaries, Python script organization, and install-location-independent references.
globs: ["plugins/**/.apm/**", "plugins/**/SKILL.md", "plugins/**/scripts/**/*.py", "plugins/**/*.md"]
---

# Plugin Architecture & Coupling Policy

Plugins are packaged and installed with [APM](https://github.com/microsoft/apm) (`0.33.0+`). Every plugin under `plugins/<plugin>/` uses the pure APM-native layout: primitives live inside `.apm/` (`.apm/skills/`, `.apm/agents/`, `.apm/hooks/`, `.apm/prompts/`, `.apm/instructions/`) and every skill is 100% self-contained in source and after install.

## 1. The Iron Law

Every skill in `plugins/<plugin>/.apm/skills/<skill>/` MUST be completely self-contained. All scripts, references, assets, tests, and evals live directly inside the owning skill directory as real files. Raw filesystem symlinks, transitional copy manifests (`symlinks.json`), and shared plugin-root `scripts/` hubs are forbidden.

## 2. Invariants & Forbidden Actions

1. **Pure APM-Native Plugin Layout**:
   - `plugins/<plugin>/apm.yml`: Primary package manifest specifying `name`, `version`, `description`, `author`, `license`, and `targets` (`claude,copilot,codex,antigravity`).
   - `plugins/<plugin>/.claude-plugin/plugin.json`: Claude Code manifest with `author` as an object `{"name": "...", "email": "..."}` and no primitive path arrays (`skills`, `agents`, `hooks`, `commands`).
   - `plugins/<plugin>/.apm/`: Single primitive root (`skills/`, `agents/`, `hooks/`, `prompts/`, `instructions/`). Never maintain duplicate root `skills/`, `agents/`, or `hooks/` folders alongside `.apm/`.
   - **Zero Legacy Plumbing**: `plugin.yaml`, `symlinks.json`, `plugin-sources.json`, `plugin-retention.json`, `skills-lock.json`, `gemini-extension.json`, and `.agents/ownership/` are retired and forbidden.
   - `lsp.json` (when present) must be a flat `{serverName: {command, ...}}` map (**SF-10**), never empty `{}` or wrapped in `{"languageServers": ...}`.

2. **Self-Contained Skills & Cross-Skill Delegation**:
   - **Zero Symlinks & Zero Climbing Paths**: Never create symlinks (`ln -s`) or reference parent paths in code blocks or inline code (`../../scripts/tool.py`, **SF-8**). Scripts run from their own skill boundary (`scripts/<tool>.py`).
   - **Pluggable Independence**: An installed skill must never depend at runtime on the source repository, another plugin, an external sibling Python package, or a specific harness install path.
   - **Cross-Skill & Cross-Plugin Delegation**: When capability lives in another skill or plugin, delegate by skill or agent name in natural language rather than cross-skill Python imports or relative script paths.
   - **Sub-Agent Mirrors Forbidden**: Files in `.apm/agents/<name>.md` must be standalone agent definitions and never symlinks or verbatim copies of a skill's `SKILL.md` (**SF-12**).

3. **Resource Placement by Purpose**:
   | Directory | Purpose |
   |---|---|
   | `.apm/skills/<skill>/references/` | Schemas, contracts, and documentation the agent reads on demand |
   | `.apm/skills/<skill>/scripts/` | Executable Python, validation, transformation, and helper scripts (cohesive subfolders allowed; no redundant `scripts/<plugin_name>/`) |
   | `.apm/skills/<skill>/assets/` | Templates and static resources copied, embedded, or rendered |
   | `.apm/skills/<skill>/tests/` & `evals/` | Unit test suites, fixtures, and evaluation scenarios |
   | `.apm/hooks/` | `hooks.json` and harness-neutral hook scripts referenced via `${CLAUDE_PLUGIN_ROOT}/.apm/hooks/<script>.py` |
   | `rules/` | Source governance rules (**not** deployed by APM per **SF-9**; copied to `.agent/rules/` during project setup and indexed in `AGENTS.md`) |

4. **Harness-Neutral Hooks (**SF-11**)**:
   Hook scripts execute under every target harness (`claude`, `copilot`, `codex`). They must locate sibling files via `Path(__file__).resolve()` and store project runtime state in harness-neutral directories (`context/`), never `.claude/` or `.agents/`.

## 3. Install-Location-Independent References

Installed primitives run from different directories per harness and scope (project `.claude/` / `.agents/` vs. global `~/.claude/` / `~/.agents/` / `~/.gemini/antigravity-cli/`).

| Reference Target | Required Authoring Form |
|---|---|
| Another skill or sub-agent | By name: *"use the `managing-adrs` skill"* |
| A file in the same skill | Skill-relative path: `scripts/tool.py`, `references/guide.md` |
| A sibling file in the same plugin | Relative Markdown link (`[text](../other-skill/SKILL.md)`) so APM rewrites or resolves it |
| Forbidden in `SKILL.md`, references, agents, or hooks | Machine paths, repo-root paths, or harness install paths (`.agents/`, `.claude/`, `~/.apm/`, `apm_modules/`) |

## 4. Evaluation Checklist

- [ ] Does `plugins/<plugin>/apm.yml` exist alongside a valid `.claude-plugin/plugin.json` (object `author`, no primitive arrays)?
- [ ] Do all skills, agents, and hooks reside exclusively under `plugins/<plugin>/.apm/` with zero root duplicates and zero symlinks?
- [ ] Are all script invocations inside `SKILL.md` and `references/` skill-relative (`scripts/...`) with zero `../` climbing paths in code blocks?
- [ ] Do hook commands use `${CLAUDE_PLUGIN_ROOT}/.apm/hooks/<script>.py` and avoid hardcoded `.claude/` or `.agents/` state paths?
- [ ] Do `audit_skill.py --mode source`, `audit_plugin_structure.py`, and `audit_rule.py --strict` pass with zero errors or warnings?
