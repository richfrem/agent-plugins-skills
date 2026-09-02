# Agentic Package Manager (APM) Capability Management

This document outlines the strategic approach to managing AI agent capabilities through **Plugin Marketplaces**, **`npx skills`**, and **Microsoft's Agentic Package Manager (APM)**. The core principle is to maintain **portable, repo-owned assets** while using enterprise-grade tools for **governed distribution**.

## 1. Key Resources

| Resource | URL |
| :--- | :--- |
| Official Website | https://microsoft.github.io/apm/ |
| Quick Start | https://microsoft.github.io/apm/quickstart/ |
| First Package Tutorial | https://microsoft.github.io/apm/getting-started/first-package/ |
| Package Anatomy | https://microsoft.github.io/apm/concepts/package-anatomy/ |
| Pack & Distribute | https://microsoft.github.io/apm/guides/pack/ |
| Plugin Authoring | https://microsoft.github.io/apm/guides/plugins/ |
| Plugin Schema | https://json.schemastore.org/claude-code-plugin.json |
| Sample Package | `apm install microsoft/apm-sample-package#v1.0.0` |

---

## 2. APM Governance Principle

APM is treated as an optional enterprise packaging, audit, policy, and distribution **overlay** — not as a mandatory replacement for existing plugin structures.

> **Overlay-First Rule**: When an existing plugin already has a valid plugin-native structure, do not move its primitives by default. Plugins remain the package primitive. Marketplaces remain the discovery primitive. APM adds optional manifest, lockfile, audit, policy, and multi-runtime deployment governance.

### Integration Modes

| Mode | Use Case | Implementation |
|------|----------|----------------|
| **Overlay** | Existing plugins | Add `apm.yml` to root; do not move files. |
| **Hybrid** | Evolving plugins | Keep layout; add `.apm/` for new governance assets. |
| **Full** | Native APM packages | Author primitives directly in `.apm/`. |

### Governance Lanes

- **experimental**: Minimal documentation; no enterprise policy enforcement; local use only.
- **team**: `README.md` and `docs/governance.md` required; standard metadata.
- **enterprise**: Full validation report required; `apm-policy.yml` optional; no dual-source-of-truth.

---

## 3. Executive Summary


The agentic ecosystem is moving from ad-hoc tool installation toward a professional supply-chain model. The goal is to avoid vendor lock-in by keeping agent instructions (skills, agents, prompts) in open formats, while using tools like Microsoft APM to provide the reproducibility and governance required by enterprise organizations.

> **Key Principle**: Don't "convert" every plugin into a specific vendor format. Repackage useful agent assets into a repo-owned, portable APM package, then use APM as the governed distribution layer.

APM's mental model mirrors `npm` by design:
- `apm install` → deploys primitives (like `npm install`)
- `apm update` → refreshes dependencies
- `apm install --frozen` → lockfile-only CI install (like `npm ci`)
- `apm self-update` → upgrades the CLI binary

---

## 3. Tool Comparison Matrix

| Feature | Plugin Marketplaces (MCP) | `npx skills` / Installer | Microsoft APM |
| :--- | :--- | :--- | :--- |
| **Primary Goal** | Ecosystem discovery & seamless integration. | CLI-driven skill fetching for developer convenience. | Enterprise-grade dependency management & governance. |
| **Package Unit** | Plugins (Skills, Agents, Hooks, MCP). | Skill packages (centered around `SKILL.md`). | APM Packages (Skills, Prompts, Agents, Hooks, MCP). |
| **Registry Model** | Centralized & Third-party catalogs. | GitHub-native (owner/repo). | Registry-agnostic (Git, Azure DevOps, etc.). |
| **Portability** | Works with Claude, Copilot, Cursor, etc. | Multi-client support. | Universal (Copilot, Claude, Cursor, Gemini, etc.). |
| **Governance** | Individual trust. | Source-based trust. | **Policy-driven** (Audits, Scanning, Allowed-lists). |
| **Best For** | Discovery and one-off utility. | Rapid local prototyping. | **Governed enterprise distribution.** |

---

## 4. Installation (Windows)

```powershell
# Install APM binary (downloads, verifies checksum, adds to PATH)
irm https://aka.ms/apm-windows | iex
```

Verify install:
```powershell
apm --version
apm targets   # inspect what APM detects in the current directory
```

---

## 5. Your First Package — Step by Step

> In about ten minutes you can scaffold a package, add a skill, add a custom agent, deploy both locally, and publish to GitHub.

### Step 1 — Scaffold

```bash
apm init -y team-skills
cd team-skills
```

`apm init` creates exactly **one file** — the manifest. The `.apm/` source tree is yours to author.

```text
team-skills/
+-- apm.yml
```

Open `apm.yml` and give it a real description:

```yaml
# apm.yml
name: team-skills
version: 1.0.0
description: Skills and agents for our team's review workflow
author: your-handle
dependencies:
  apm: []
  mcp: []
includes: auto
scripts: {}
```

> **`includes: auto`** is what makes `apm install` walk your local `.apm/` tree and deploy what it finds. Set `includes: []` (or omit it) and local content stops deploying.

---

### Step 2 — Add a Skill

A **skill** is a chunk of expertise the runtime activates **automatically** based on its description. No slash command, no manual selection — the agent sees the description, decides the skill is relevant, and pulls it in. That auto-activation is what separates skills from prompts.

```markdown
<!-- .apm/skills/pr-description/SKILL.md -->
---
name: pr-description
description: >-
  Activate when the user asks for a pull-request description, a summary of
  uncommitted changes, or release notes. Use when preparing to open a PR or
  when the user says "draft a PR description for me".
---
# PR Description Skill

Produce a PR description with these sections, in order:

## Summary
One sentence. What changes and why. No file lists, no implementation detail.

## Motivation
Two to four sentences. The problem this solves or the capability it adds.
Link to the issue or design doc if one exists.

## Changes
Bullet list grouped by area (e.g. "API", "Tests", "Docs"). One bullet per
logical change, not per file.

## Risk and rollback
Note any breaking changes, migrations required, or feature flags.
Mention how to revert if something breaks.

## Testing
How you verified the change. Commands run, environments tested.
```

> The frontmatter `description` is a **contract with the runtime**: write it as "activate when …". The body is the operating manual the agent reads when the skill fires.

---

### Step 3 — Add a Custom Agent

A **custom agent** (`.agent.md`) is a named expert your runtime can invoke directly. While skills auto-activate based on context, agents are **summoned on demand** — typically with `@agent-name`.

```markdown
<!-- .apm/agents/team-reviewer.agent.md -->
---
name: team-reviewer
description: Senior reviewer that critiques diffs against team standards before PR submission.
---
# Team Reviewer

You are a senior engineer reviewing a teammate's diff before it becomes
a pull request. Your job is to catch the things that waste reviewer time downstream.

## What to check, in order

1. **Correctness.** Does the code do what its commit message claims?
2. **Tests.** Are the changed code paths covered?
3. **Naming and clarity.** Are names accurate? Would a new contributor understand this?
4. **Surface area.** Does this change export anything new? Is it documented?

## Output format

Group findings by severity: **Blocking**, **Should fix**, **Nit**.
For each finding, cite the file and line. End with a one-line verdict:
"Ready to ship", "Address blockers then ship", or "Needs another pass".

Do not rewrite the code yourself. Point and explain.
```

---

### Step 4 — Deploy and Use

```bash
apm install
```

Expected output:
```
[+] <project root> (local)
|-- 1 agents integrated -> .github/agents/
|-- 1 skill(s) integrated -> .agents/skills/
[i] Added apm_modules/ to .gitignore
```

Your tree now has **source on the left** and **runtime-ready output on the right**:

```text
team-skills/
+-- .apm/                              # source you edit
|   +-- skills/
|   |   +-- pr-description/SKILL.md
|   +-- agents/
|       +-- team-reviewer.agent.md
+-- .agents/                           # generated — cross-client skills
|   +-- skills/
|       +-- pr-description/SKILL.md
+-- .github/                           # generated — runtime-specific (Copilot)
|   +-- agents/
|       +-- team-reviewer.agent.md
+-- apm_modules/                       # generated — dependency cache
|   +-- _local/                        # symlinks to local packages
|   +-- microsoft/                     # downloaded packages
+-- apm.yml                            # source manifest
+-- apm.lock.yaml                      # generated lockfile (commit this!)
```

> **Never edit files under `.agents/`, `.github/`, `.claude/`, or `.cursor/` directly.** Edit the source under `.apm/` and re-run `apm install`.

Now open Copilot or Claude in this project. Ask "draft a PR description for my last commit" — the skill activates on its own. To get the review pass: `@team-reviewer review my staged changes`.

#### Target Resolution Priority Chain

`apm install` resolves which harness directories to populate in this order:

1. `--target` flag (e.g., `apm install --target claude`)
2. `targets:` in `apm.yml` (e.g., `targets: [copilot, claude]`)
3. **Auto-detect** from filesystem signals:

| Signal File / Directory | Detected Harness |
| :--- | :--- |
| `.claude/` or `CLAUDE.md` | Claude Code |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `.cursor/` | Cursor |
| `.gemini/` | Gemini |
| `.codex/` | Codex |
| `.opencode/` | OpenCode |
| `.windsurf/` | Windsurf |

> With **no signal at all**, `apm install` exits with code 2 and a teaching message instead of silently picking a target.

#### Skills vs. Agents: Where They Land

| Primitive | Lands in | Access pattern |
| :--- | :--- | :--- |
| **Skills** | `.agents/skills/` (cross-client) | Auto-activated by context |
| **Skills** (Claude exception) | `.claude/skills/` | Auto-activated by context |
| **Agents** | `.github/agents/` (Copilot dir) | Summoned via `@agent-name` |

#### What about `apm compile`?

`apm compile` is a separate concern: it generates merged `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` files for tools that read a top-level context document (Codex, Gemini, plain agents-protocol hosts). Copilot, Claude Code, and Cursor read per-skill directories directly — **no compile step needed** for those.

---

### Step 5 — Publish as a Package

```bash
git init
git add apm.yml .apm/
git commit -m "Initial team-skills package"
git remote add origin https://github.com/your-handle/team-skills.git
git push -u origin main
```

In any other project's `apm.yml`:

```yaml
dependencies:
  apm:
    - your-handle/team-skills
```

Then `apm install` — consumers get the same skill and agent in their runtime dirs, with version pinning recorded in `apm.lock.yaml`.

---

### Step 6 — Ship as a Plugin (Optional)

```bash
apm pack
```

Output (`build/` directory, plugin format by default):

```text
build/team-skills-1.0.0/
+-- plugin.json        # synthesized, schema-conformant
+-- apm.lock.yaml      # enriched with bundle_files manifest
+-- agents/
|   +-- team-reviewer.agent.md
+-- skills/
    +-- pr-description/SKILL.md
```

No `apm.yml`, no `apm_modules/`, no `.apm/` — just primitives in plugin-native layout. Convention dirs (`agents/`, `skills/`, `commands/`, `instructions/`) are auto-discovered by Claude Code, so the synthesized `plugin.json` does not need to list them.

> To scaffold with plugin support from day one: `apm init --plugin team-skills`

---

## 6. Package Anatomy

### The Minimal Package

Three files on disk is enough:

```text
my-pkg/
+-- apm.yml
+-- .apm/
    +-- skills/hello/SKILL.md
```

`name` and `version` in `apm.yml` are the only required fields.

### Full Source Tree

```text
my-pkg/
+-- apm.yml                       # The manifest. Required.
+-- apm.lock.yaml                 # Resolved versions + content hashes. Generated.
+-- apm_modules/                  # Installed dependencies. Generated. Gitignore.
+-- .apm/                         # Source primitives you author.
|   +-- instructions/             # Always-on rules attached to file globs.
|   +-- skills/                   # Multi-file capabilities (SKILL.md + assets).
|   +-- prompts/                  # Reusable prompt templates.
|   +-- agents/                   # Named agents (model + system prompt + tools).
|   +-- chatmodes/                # Chat-mode configurations.
|   +-- context/                  # Shared context fragments.
|   +-- hooks/                    # Lifecycle hooks (pre/post events).
+-- .github/                      # Compiled output for Copilot. Generated.
+-- .claude/                      # Compiled output for Claude Code. Generated.
+-- .cursor/                      # Compiled output for Cursor. Generated.
+-- .codex/                       # Compiled output for Codex. Generated.
+-- AGENTS.md                     # Cross-tool spec read by OpenCode, Gemini, Codex.
+-- apm-policy.yml                # Optional org/repo policy.
+-- scripts/                      # Optional helper scripts you author.
+-- tests/                        # Optional tests for your primitives.
```

### `.apm/` Primitive Types

| Directory | Purpose | How It Ships |
| :--- | :--- | :--- |
| `instructions/` | Always-on rules attached to file globs (e.g. "for every `*.py`, follow PEP 8"). One `.md` file per rule. | Compiled into `.github/instructions/`, `.cursor/rules/`, etc. |
| `skills/<name>/SKILL.md` | Multi-file capabilities. `SKILL.md` is the entry point; sibling files (templates, scripts, references) ship alongside it. | Loaded on demand by the harness. |
| `prompts/` | Reusable prompt templates. One `.prompt.md` per prompt. | Invocable via `apm run <script>` or harness CLI. |
| `agents/` | Named agent definitions: model choice, system prompt, tool whitelist. One `.agent.md` per agent. | Summoned via `@agent-name`. |
| `chatmodes/` | Chat-mode configurations for harnesses that expose modes (e.g. Copilot Chat). | Harness-specific. |
| `context/` | Shared context fragments that other primitives can reference. Not loaded standalone. | Referenced, not deployed directly. |
| `hooks/` | Lifecycle hooks fired on pre/post install, compile, or run events. | Executed by APM lifecycle. |

### Package Layout Options

APM recognizes three layouts — pick the one that matches what you are shipping:

| Layout | When to Use | Structure |
| :--- | :--- | :--- |
| **Single Skill (Hybrid)** | One focused capability. | `SKILL.md` at repo root; optional `agents/`, `assets/`, `scripts/` alongside. Add `apm.yml` for dependency management. |
| **Multiple Primitives** | A collection of skills, agents, prompts. | `.apm/` directory with `skills/`, `agents/`, `instructions/` subdirs. APM hoists each primitive individually. |
| **Claude Plugin** | Already have a `plugin.json`. | APM can consume `plugin.json` directly without restructuring. |

---

## 7. `apm.yml` Field Reference

### APM Manifest (apm.yml) Schema

```yaml
name: agent-orchestration/
version: 2.1.0
description: Core execution primitives for agent loops.
author: DeepMind Advanced Agentic Coding
targets:
  - copilot
  - claude
  - cursor
```

| Field | Description |
|-------|-------------|
| `name` | Kebab-case package name. |
| `version` | Semver version string. |
| `description` | Short package description. |
| `author` | Attribution string. |
| `targets` | Array of supported agent environments. |

---

## 8. `apm.lock.yaml` Anatomy

The lockfile pins every resolved dependency to an exact commit and content hash so two clones of the repo install byte-identical primitives. **Generated by `apm install`; commit it.**

```yaml
lockfile_version: '1'
generated_at: '2026-04-21T21:45:34.516938+00:00'
apm_version: 0.10.0

dependencies:
  - repo_url: https://github.com/microsoft/apm-sample-package
    resolved_commit: a1b2c3d4e5f6...    # Exact SHA installed
    resolved_ref: v1.0.0               # Tag/branch the SHA came from
    version: 1.0.0
    depth: 1                           # 1 = direct, 2+ = transitive
    package_type: APM_PACKAGE
    content_hash: sha256:9f...         # Hash of the package file tree
    deployed_files:
      - .github/skills/review/SKILL.md
    deployed_file_hashes:
      .github/skills/review/SKILL.md: sha256:c4...

  # Single-primitive (virtual) import:
  - repo_url: https://github.com/github/awesome-copilot
    virtual_path: skills/review-and-refactor
    is_virtual: true
    resolved_commit: 7e8f9a...
    depth: 1

mcp_servers:
  - microsoft/azure-devops-mcp

# The package's own local content. Lets `apm audit` detect hand-edits.
local_deployed_files:
  - .github/instructions/python.instructions.md
local_deployed_file_hashes:
  .github/instructions/python.instructions.md: sha256:45...
```

| Field | Notes |
| :--- | :--- |
| `resolved_commit` | Full SHA — the thing that makes installs reproducible. |
| `depth` | `1` = direct dependency; `>1` = transitive. |
| `package_type` | `APM_PACKAGE`, `CLAUDE_SKILL`, or `HYBRID`. |
| `is_virtual` | `true` for single-primitive imports. |
| `content_hash` | SHA-256 of the entire package file tree. |
| `is_dev` | `true` for `devDependencies` entries. |

> `apm audit` rehashes everything in `deployed_file_hashes` and `local_deployed_file_hashes` to detect hand-edits to deployed files before they ship.

---

## 9. Governance without Killing Innovation

To avoid review bottlenecks, adopt a **tiered governance model**. Governance should control **promotion**, not experimentation.

### The Three-Lane Model

| Tier | Audience | Mechanism | Governance Level |
| :--- | :--- | :--- | :--- |
| **Lane 1: Experimental** | Individuals / Small Teams | Local install / Git branch | **Minimal**: Fast iteration in sandboxes. |
| **Lane 2: Team Approved** | Project Teams | Tagged Release / Lockfile | **Lightweight**: Peer review for utility and safety. |
| **Lane 3: Enterprise Approved** | Ministry / Organization | Approved Catalog / `apm-policy.yml` | **Formal**: Security, Privacy, and Data review. |

### Risk-Based Review Categories

| Risk Level | Example | Required Review |
| :--- | :--- | :--- |
| **Low** | Writing style prompts, README helpers. | Peer review only. |
| **Medium** | Code generation, architecture recommendations. | Peer review + test examples. |
| **High** | Skills with scripts, file modification, MCP access. | Security-aware review. |
| **Very High** | Skills touching production or protected data. | Formal Enterprise review. |

---

## 10. Primitives & Targets — Compatibility Matrix

> **Canonical reference**: https://microsoft.github.io/apm/concepts/primitives-and-targets/

A **primitive** is a unit of agent context APM can manage. A **target** is a harness APM compiles primitives for. This matrix is the full reach map — for any primitive × harness combination it tells you whether the harness receives it natively, after APM transforms it, or not at all.

### Primitive Catalogue

| Primitive | Source Path | Notes |
| :--- | :--- | :--- |
| **Instructions** | `.apm/instructions/*.instructions.md` | Coding standards scoped by file glob. Frontmatter: `description` (required), `applyTo` (optional glob). |
| **Prompts** | `.apm/prompts/*.prompt.md` | Executable, parameterized AI workflows. Also surfaced as **commands** for harnesses that read slash-commands. |
| **Agents** | `.apm/agents/*.agent.md` | Named AI personalities with tool boundaries. |
| **Skills** | `.apm/skills/<name>/SKILL.md` or root `SKILL.md` | Cross-tool meta-guides in the agent-skills format. Bundled resources live alongside the skill. |
| **Hooks** | `.apm/hooks/*.json` | Lifecycle event handlers (`PreToolUse`, `PostToolUse`, `Stop`) that invoke scripts. |
| **Commands** | _(same source as Prompts)_ | Sourced from `.apm/prompts/` — there is **no** separate `.apm/commands/` directory. The same `.prompt.md` becomes Copilot's prompt and Claude's `/command`. |
| **Plugins** | `plugin.json` at package root | A packaging format. APM normalizes plugins at install time into the same primitives above. |
| **MCP Servers** | `apm.yml` → `dependencies.mcp:` | APM writes the per-harness MCP config file at install time. |

### Target Catalogue

| Slug | Output Directory | Notes |
| :--- | :--- | :--- |
| `copilot` | `.github/` (project), `~/.copilot/` (user) | User-scope partial: prompts and instructions are project-scope only. |
| `claude` | `.claude/` | Full user-scope support. Hooks merge into `.claude/settings.json`. |
| `cursor` | `.cursor/` | Rules use `.mdc` extension. Instructions not deployable at user scope (Settings UI only). |
| `codex` | `.codex/` + `.agents/` for skills | Agents and hooks use TOML. |
| `gemini` | `.gemini/` | Commands are TOML. Hooks merge into `.gemini/settings.json`. No native agents or instructions — both arrive via compiled context files. |
| `opencode` | `.opencode/` (project), `~/.config/opencode/` (user) | No hooks support. |
| `windsurf` | `.windsurf/` (project), `~/.codeium/windsurf/` (user) | Agents delivered as auto-invokable skills under `.windsurf/skills/`. "Workflows" = commands. |

### The Compatibility Matrix

**Cell legend:** `native` = harness reads it directly as-is · `compiled` = APM transforms it into a format the harness understands · `unsupported` = not delivered · `gated` = delivered behind a trust prompt

| Primitive | Copilot | Claude | Cursor | Codex | Gemini | OpenCode | Windsurf |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **instructions** | native | native | native | compiled | compiled | compiled | native |
| **prompts** | native | compiled | compiled | unsupported | compiled | compiled | compiled |
| **agents** | native | native | compiled | compiled | unsupported | native | compiled |
| **skills** | native | native | native | native | native | native | native |
| **hooks** | native | native | native | native | native | unsupported | native |
| **commands** | unsupported | native | compiled | unsupported | compiled | compiled | compiled |
| **plugins** | compiled | compiled | compiled | compiled | compiled | compiled | compiled |
| **MCP servers** | native | native | native | native | native | native | native |

#### Reading the matrix — key examples

| Cell | Meaning |
| :--- | :--- |
| `instructions / claude = native` | APM writes `.claude/rules/<name>.md`; Claude Code reads it directly. |
| `prompts / claude = compiled` | APM transforms `.apm/prompts/<n>.prompt.md` into `.claude/commands/<n>.md`. The prompt becomes a `/command`. |
| `agents / gemini = unsupported` | Gemini CLI has no agents primitive. Content still reaches Gemini through the compiled `GEMINI.md` if referenced from instructions. |
| `commands / copilot = unsupported` | Copilot has no commands primitive; the same source `.prompt.md` reaches Copilot as a native prompt instead. |
| `plugins / *` | APM unpacks the plugin at install time into the primitives in the rows above; routing then follows those rows. |
| `MCP servers / *` | APM writes the harness's standard MCP config. Transitive MCP servers from deep dependencies require an explicit trust prompt (effectively gated). |

### Dev-Only Primitives

Mark a primitive as dev-only when it is useful to the package author but should not ship to consumers: release checklists, internal debugging agents, test-fixture skills, anything tied to your own infrastructure.

- Author such primitives **outside** `.apm/` (typically `dev/`)
- Reference them under `devDependencies` in `apm.yml`
- `apm pack` excludes them automatically
- `apm install --dev` deploys them locally

### 3. Installation & Deployment (`apm install`)

The installer materializes primitives into harness-specific directories.

#### Target Resolution Precedence
1.  **CLI Flag**: `--target <harness>` (e.g., `agent-skills`, `claude`, `all`)
2.  **Manifest**: `targets:` field in `apm.yml`
3.  **Auto-Detect**: Scans for `.claude/`, `.github/`, etc.

> [!IMPORTANT]
> If no target is detectable and no target is specified, `apm install` exits with **code 2** and a teaching message.

#### Converged vs. Legacy Skill Paths
*   **Converged (Default)**: Skills are deployed to `.agents/skills/<package-name>/`.
*   **Legacy**: Skills are deployed to per-client paths (e.g., `.cursor/skills/`) only if `--legacy-skill-paths` or `APM_LEGACY_SKILL_PATHS=1` is used.

#### Installer Primitives
- `--target agent-skills`: Deploys only the converged skills target.
- `--target all,agent-skills`: Deploys to all harnesses AND the converged skills path (`all` alone excludes `agent-skills`).
- `--dry-run`: Preview the installation plan.
- `--frozen`: Enforce lockfile parity (CI/CD mode).
- `--only apm|mcp`: Filter installation to specific primitive types.

> Unknown target slugs are rejected by the manifest parser — they never silently fall through to the default.

## 12. Duplicate Skill Discovery Risk

APM’s `agent-skills` target deploys skills to the converged cross-client location:

```text
.agents/skills/
```

Some runtimes or agent hosts may also read target-specific skill folders such as:

```text
.claude/skills/
.windsurf/skills/
```

If both the converged `.agents/skills/` path and a target-specific skill path are present and read by the same agent host, the same skill may appear more than once. This is a **runtime discovery overlap problem**, not an APM installation error.

### Target Selection Guidance

Do not blindly install to `all,agent-skills` for normal usage. It is a **broad routing smoke test**, not always the recommended runtime install mode. 

For normal usage, choose the smallest target set needed:

| Goal | Recommended target |
| :--- | :--- |
| **Cross-client skills only** | `agent-skills` |
| **Claude only** | `claude` (populates `.claude/`) |
| **Copilot/GitHub only** | `copilot` (populates `.github/`) |
| **Cursor only** | `cursor` (populates `.cursor/`) |
| **Gemini only** | `gemini` (populates `.gemini/`) |
| **Broad routing test** | `all,agent-skills` |

> [!TIP]
> Use `all,agent-skills` only when validating a package's routing matrix. For daily use, pick the specific target for your active harness to avoid duplicate visibility.

---

## 11. Strategic Recommendation

For enterprise teams, the factual case for APM is strongest when focused on **Supply Chain Governance**:

1. **Reproducibility**: `apm.yml` + `apm.lock.yaml` ensure every agent environment is byte-identical across machines.
2. **Auditability**: `apm audit` provides a clear report of exactly what instructions, skills, and MCP servers were active for a specific version, detecting any hand-edits to deployed files.
3. **Policy Gates**: `apm-policy.yml` allow-lists trusted dependencies and restricts high-risk MCP servers.
4. **Sandbox Freedom**: Maintain "Lane 1" for unhindered innovation. Do not force experimental prompts through formal enterprise review until they are ready for "promotion."

### 14. Operational Lifecycle

The APM workflow moves through four distinct phases. Successful automation requires understanding the handoff between source authoring and runtime materialization.

| Phase | Tool/Skill | Primary Action |
| :--- | :--- | :--- |
| **Authoring** | `scaffold-apm` / `migrate-to-apm` | Create the `.apm/` source tree and `apm.yml` manifest. |
| **Quality** | `validate-apm-package` | Run deterministic audits for schema, naming, and policy. |
| **Deployment** | `install-apm-package` | Run `apm install` to materialize primitives into target runtime dirs. |
| **Synthesis** | `compile-apm-package` | Run `apm compile` to generate merged context docs (Codex/Gemini). |

> [!CAUTION]
> **Source-of-Truth Discipline**: Primitives in runtime directories (e.g., `.agents/`, `.github/`, `.claude/`) are **ephemeral artifacts**. They are overwritten on every `apm install`. Always author your logic in the `.apm/` source directory.

---

### Bottom Line
**Govern the supply chain, not every idea.** Use manifests, lockfiles, and policy gates for shared packages, but keep the sandbox fast. Repackage your useful assets into portable, repo-owned formats and let APM handle the governed distribution across all your agent environments.
