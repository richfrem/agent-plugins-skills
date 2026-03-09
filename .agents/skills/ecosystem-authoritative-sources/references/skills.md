# Skills Research

This document captures our accumulated knowledge and definitive specifications for **Skills**.

**Source:** [Extend Claude with skills](https://code.claude.com/docs/en/skills)

## Definition
Skills are modular capabilities that package procedural knowledge, context, and workflows into reusable, filesystem-based resources. While built primarily for Claude and Claude Code, they adhere to the open [Agent Skills](https://agentskills.io/) standard originally developed by Anthropic. Because it is an open standard, skills are highly portable and supported by a wide ecosystem of AI developer tools (e.g., Cursor, Gemini CLI, Goose, VS Code, Letta, Roo Code, etc.). They replace and expand upon older legacy feature sets like `/commands`.

## Creation & Structure
- Skills are individual directories named `<skill-name>`, housing at least one `SKILL.md` file.
- The `SKILL.md` file contains YAML frontmatter configuring the skill and Markdown content acting as the prompt instructions.
- Supporting files must be strictly organized into the official standard directories (`scripts/`, `references/`, or `assets/`) and referenced inside `SKILL.md`. Claude will read them only if needed.

## Optional Directories
Agent skills support three standard optional directories to keep the root clean:
- **`scripts/`**: Contains executable code (Python, Bash, JS). Must be self-contained, handle edge cases gracefully, and include helpful error messages instead of failing silently. **Scripts must live inside the skill's own `scripts/` directory, never at the parent plugin level.** This ensures the skill is fully portable when installed via `npx skills add`, which copies skill folders individually.
- **`references/`**: Contains additional documentation loaded on-demand (e.g., `REFERENCE.md`, `FORMS.md`, `domain.md`). Keep these small and focused to save context window space.
- **`assets/`**: Contains static resources like templates, images (diagrams), and data files (lookup tables, schemas).

### Self-Containment Rule (Portability)
Each skill folder must be **fully self-contained**. All scripts, references, and assets that a skill depends on must exist inside the skill's own directory tree. Do not place shared scripts at the plugin level and reference them from skills -- this breaks `npx skills add` installation, which copies only the skill folder into the consumer's agent environment.

**Shared scripts across sibling skills:** When multiple skills within the same plugin share utility scripts, use **relative symlinks** from the secondary skill's `scripts/` directory pointing to the primary skill's copy. This avoids file duplication while maintaining portability -- `npx skills add` automatically dereferences symlinks into real files during installation, so each installed skill receives a standalone copy.

Example structure:
```
my-plugin/
  skills/
    primary-skill/scripts/shared_util.py       # Real file (single source of truth)
    secondary-skill/scripts/shared_util.py      # Symlink -> ../../primary-skill/scripts/shared_util.py
```

## Resolution Precedence
Skills are resolved automatically. Any nested `.claude/skills/` directory relative to the current working file is also discovered (useful in monorepos).
1. **Enterprise** (`managed settings`)
2. **Personal** (`~/.claude/skills/<skill-name>/SKILL.md`)
3. **Project** (`.claude/skills/<skill-name>/SKILL.md`)
4. **Plugin** (`<plugin_root>/skills/<skill-name>/SKILL.md` - namespaces prevent conflicts here)

## Configuration (YAML Frontmatter)
The frontmatter configures invocation rules, argument hints, tool allowances, and execution environments.

### Open Standard Properties (`agentskills.io`)
- `name` **(Required)**: Display name. 1-64 characters. Must contain only lowercase alphanumeric characters and hyphens (`a-z` and `-`). Cannot start/end with a hyphen, nor contain consecutive hyphens (`--`). **Must perfectly match the parent directory name.**
- `description` **(Required)**: Helps the agent decide autonomously when it should trigger the skill. 1-1024 characters.
- `license` *(Optional)*: License name or reference to a bundled license file (e.g., `Apache-2.0`). Recommendation: Keep it short.
- `compatibility` *(Optional)*: Indicates specific environment requirements like system packages or network access. Max 500 characters.
- `metadata` *(Optional)*: A map from string keys to string values for tool-specific meta. Make key names unique to avoid conflicts (e.g., `author: org`, `version: "1.0"`).
- `allowed-tools` *(Optional/Experimental)*: Space-delimited list of pre-approved tools the skill may use (e.g., `Bash(git:*) Read`). Support varies by implementation.

### Claude Code Specific Properties
- `argument-hint`: Visual hint for the autocomplete UI (e.g., `[issue-number]`).
- `disable-model-invocation`: Boolean. If `true`, Claude *cannot* automatically decide to run this skill; it must be manually invoked by the user `/name`.
- `user-invocable`: Boolean. If `false`, the user *cannot* manually invoke the skill (hidden from `/` menu), meaning it acts as background system context for Claude.
- `context`: If set to `fork`, the skill content executes identically to a *subagent* invocation with a clean state.
- `agent`: The subagent type to use if `context: fork` (e.g., `Explore`, `Plan`).
- `hooks`: Standard hook definitions scoped exclusively to this skill's lifecycle.

## Arguments & String Substitutions
The skill content (markdown) replaces strict interpolation variables before being run by Claude.
- `$ARGUMENTS`: All arguments passed. (Fallback: if missing, appended at the end as `ARGUMENTS: <value>`).
- `$ARGUMENTS[N]` or `$N`: Positional zero-indexed parameter.
- `${CLAUDE_SESSION_ID}`: Injects the active session ID.

### Dynamic Context / Shell Execution
You can use `!`command\`\` syntax to execute shell commands **before** Claude reads the instruction prompt.
**Example:** `PR diff: !`gh pr diff\`\``
This acts as a preprocessor, inserting the standard output directly into the markdown prior to AI inference.

## Integration with Subagents
If you use `context: fork`, the `SKILL.md` body becomes the System Prompt task for a new subagent, defined by the `agent` property. This protects the main thread's context limit or isolates specific workflows (like exhaustive testing or background code exploration).

## Installation via `npx skills`
The open standard provides a universal installer that automatically detects the active agent environment (Claude Code, GitHub Copilot, Gemini CLI, Cursor, etc.) and routes the skills to the correct configuration directories.

### Installing from Remote Repositories
You can install single skills or entire curated collections directly from GitHub and other git providers:
- **Specific Skill:** `npx skills add <github-user>/<repo>/plugins/<plugin-name>`
- **Full Collection:** `npx skills add <github-user>/<repo>`

**Notable Open Skill Collections:**
- **Anthropic Official:** `npx skills add anthropics/skills`
- **Microsoft Official:** `npx skills add microsoft/skills`
- **Agent Plugins (This Repo):** `npx skills add richfrem/agent-plugins-skills`

### Updating Skills
To update all skills installed via `npx` to their latest versions from their respective remote sources:
```bash
npx skills update
```

### Local Development & Reinstallation
When authoring or modifying skills locally, you can install them from your local filesystem instead of a remote repository:
```bash
# Install a specific local plugin
npx skills add ./plugins/my-plugin --force

# Install all local plugins
npx skills add ./plugins/ --force
```

**CRITICAL:** When iterating locally, `npx` may cache symlinks or encounter folder lock constraints when attempting to overwrite an existing installation. To ensure a clean local reinstallation, you must manually wipe the destination environment first:
```bash
# Example for Antigravity / universal agents
rm -rf .agents/
npx skills add ./plugins/my-plugin --force
```

## Packaging & Distribution (ZIP)
When creating a skill for distribution (e.g. sharing across an enterprise):
- The skill folder must match the Skill's name.
- Package it as a ZIP file where the **folder itself** is the root (not the loose files).
  - **Correct:** `my-skill.zip -> my-skill/SKILL.md`
  - **Incorrect:** `my-skill.zip -> SKILL.md`
- **Dependencies:** `dependencies` can be added to the frontmatter (e.g. `python>=3.8, pandas>=1.5.0`) to define software packages required. Claude Code can install from standard endpoints like PyPI or npm. (Note: API Skills require pre-installed containers).

## Best Practices & Authoring Guidelines
- **Concise is Key:** The context window is a public good. Assume Claude is highly intelligent and only add context Claude doesn't already know. Challenge each piece of information: "Does Claude really need this explanation?"
- **Degrees of Freedom (Fragility):** Match the level of specificity (High vs Low freedom) to the task's fragility. 
    - Text-based review = High freedom (general direction).
    - Pseudocode/Script templating = Medium freedom (preferred patterns).
    - Database migrations/Deployments = Low freedom (exact scripts, no deviations).
- **Test Across Models:** Skills act as additions to models. Ensure instructions are clear enough for smaller/faster models (Haiku) but efficient enough not to bog down powerful reasoning models (Opus).
- **Evaluating First:** Create evaluations *first* before writing extensive documentation. Measure baseline performance, write minimal instructions to pass the eval, and iterate. Do not solve imagined problems.
- **Naming Conventions:** Use the **gerund form** (verb + -ing) for skill names (e.g., `processing-pdfs`, `analyzing-spreadsheets`). Always lowercase and hyphenated. Avoid generic vague nouns (`helper`, `utils`).
- **Descriptions:** Must be written in the **third person** (e.g., "Processes Excel files", not "I process"). Must clearly state both *what* it does and *when* Claude should trigger it autonomously. Avoid vague descriptions like "Helps with documents." Max 1024 characters.
- **Progressive Disclosure:** Claude reads only the frontmatter `description` fields first to decide if a skill is relevant, before reading the `SKILL.md` body. Be precise.

### Refined Progressive Disclosure Patterns
To keep `SKILL.md` under the recommended 500 max lines without overloading Context:
1. **High-level guide with references:** SKILL.md provides quick-starts, then links to `REFERENCE.md` or `EXAMPLES.md` for deep dives.
2. **Domain-specific organization:** Group references by type so Claude only reads what's relevant (e.g., `reference/finance.md`, `reference/sales.md`).
3. **One-Level Deep References:** **CRITICAL:** Do not nest references (e.g., SKILL.md -> A.md -> B.md). Claude may only partially read deeply nested chains (often via `head -n 100`). All reference files should be linked directly from `SKILL.md`.
4. **Table of Contents:** Any reference file longer than 100 lines must have a TOC at the top so Claude can navigate partial reads effectively.
5. **Workflow Checklists:** For complex workflows, provide a copyable Markdown checklist in `SKILL.md` that Claude can paste into its response and check off as it progresses.
6. **Verifiable Intermediate Plans:** For destructive or massive operations, use a plan-validate-execute loop. Have Claude output an intermediate `plan.json`, run a validation script strictly against it, and *then* execute.

### Anti-Patterns to Avoid
- **Windows Paths:** Always use Unix-style forward slashes (`/`), even on Windows.
- **Bash/PowerShell Scripts:** Avoid `.sh` or `.ps1` files for complex logic. **Python (`.py`) is the required standard** for skill scripts to guarantee true cross-platform execution (Windows, Mac, Linux).
- **Punting Errors:** Utility scripts should handle exceptions and edge cases themselves (e.g., creating a missing file with default content) rather than failing and forcing Claude to figure it out. Provide explicit error messages in `stdout/stderr` back to Claude.
- **Voodoo Constants:** Document *why* magical numbers (e.g., `TIMEOUT=47`) or timeouts are set to what they are in your scripts so Claude understands the parameters.
- **Unqualified MCP Tools:** When referencing a tool, always explicitly provide the namespace: `ServerName:tool_name` (e.g., `GitHub:create_issue`) to avoid "tool not found" collisions.

## Example Repositories
Official open-source repositories containing exemplary and foundational Agent Skills configurations:
- [Anthropic Skills Repository](https://github.com/anthropics/skills/tree/main/skills)
- [Microsoft Skills Repository](https://github.com/microsoft/skills)

## Architecture & Progressive Disclosure
The filesystem-based architecture of Skills naturally forces a 3-level "Progressive Disclosure" strategy that preserves context window space:
1. **Level 1 (Metadata) - Discovery:** Loaded at startup. The YAML frontmatter (`name`, `description`). Only ~100 tokens. Claude uses this to determine *if* the skill is useful.
2. **Level 2 (Instructions) - Activation:** Loaded when triggered. The `SKILL.md` body. Usually < 5k tokens. Loaded via a background bash command (`read pdf-skill/SKILL.md`).
3. **Level 3+ (Resources & Code) - Execution:** Loaded as-needed. Arbitrary scripts or reference files (`REFERENCE.md`) referenced by Level 2. Executing scripts uses tokens only for the *output*, not the script content itself.This makes skills self-documenting, extensible, and highly portable.

*See visual representation of this lifecycle in [skill-execution-flow.mmd](./diagrams/skill-execution-flow.mmd)*

## Cross-Surface Constraints
Skills run in different environments depending on the host surface. Always plan the execution requirements correctly:
- **Claude.ai / API:** Sandboxed VM environments. No network access by default, and you cannot install packages at runtime. You must rely on pre-installed dependencies.
- **Claude Code:** Runs securely but fully natively on the user's host machine. Full network access and filesystem access. Avoid installing global packages during runtime to protect the user's OS integrity.

## Enterprise Governance & Security
When deploying skills at scale, establish strict evaluations and security reviews prior to deployment due to their high privileges.

### Security Review Checklist
Since skills provide instructions and execute code, review third-party or internal skills for:
1. **Script Execution:** Scripts run with full environment access based on the host surface. Sandboxed execution is advised.
2. **Instruction Manipulation:** Check for directives asking Claude to ignore safety rules or hide operations.
3. **Agent Tool Calls:** Ensure referenced tools (`ServerName:tool_name`) are expected and authorized.
4. **Network Access / Exfiltration:** Review scripts/prompts for unauthorized `curl`, `requests.get`, or other network calls. Ensure there are no patterns reading sensitive data and encoding/transmitting it externally. NOTE: Plugins dealing with DevOps orchestration or datasets may legitimately require these instructions; in these cases, ensure the plugin declares a `security_override.json` detailing exactly where and why network fetches occur.
5. **Hardcoded Credentials:** Reject any skill storing API keys or passwords directly in `.md` or scripts. Use environment variables.
6. **Tool Invocations:** Audit which bash/file tools are explicitly allowed or directed to run.

### Lifecycle Management
1. **Start Specific:** Build narrow skills (`querying-pipeline-data`) before consolidating into broad role-based bundles (`sales-operations`). 
2. **Evaluate First:** Require 3-5 evaluation queries ensuring the skill triggers accurately without overlapping with other skills, handles edge cases, and reliably executes before passing it to production.
3. **Recall Limits:** Don't load hundreds of skills simultaneously. API requests max out at 8 skills per request explicitly. Evaluate recall accuracy when bundling too many skills into a single system prompt.
4. **Source Control:** Maintain skill directories via Git and use CI/CD deployment hooks to sync up to the API/Marketplace.
5. **Versioning:** Pin skills to specific tested versions, and provide quick rollback paths for failed workflows.

### File References
When referencing other files inside your skill (e.g. scripts or docs), use **relative paths from the skill root**.
- Good: `See [the guide](references/REFERENCE.md)` or `Run scripts/extract.py`
- Bad: `../` or absolute paths.
- Bad: `plugins/my-plugin/scripts/shared.py` (plugin-level scripts break `npx skills add` portability -- use a relative symlink inside the skill's own `scripts/` directory pointing to the primary skill's copy).

### Official Validation
The open standard provides an official NPM-based CLI validator for skill structure. When authoring new skills, always manually run:
```bash
skills-ref validate ./my-skill
```
This ensures frontmatter is syntactically valid and length constraints are respected.

## Integrating Skills into Custom Agents (`agentskills.io`)
If building a custom agent or product, skills can be integrated in two ways:
1. **Filesystem-based Agents:** The model operates fully within a sandboxed Unix environment, activating skills by issuing native `cat /path/to/SKILL.md` shell commands, identical to Claude Code.
2. **Tool-based Agents:** The model lacks native filesystem tools, and instead relies on custom-built agent tools to read the `SKILL.md` file and execute its references.

### Metadata Injection (Level 1)
At startup, the custom agent parses the YAML frontmatter of every discovered skill and injects it into the system prompt as an XML block. For example:
```xml
<available_skills>
  <skill>
    <name>pdf-processing</name>
    <description>Extracts text and tables from PDF files, fills forms, merges documents.</description>
    <location>/path/to/skills/pdf-processing/SKILL.md</location>
  </skill>
</available_skills>
```
*Note: The `location` parameter is crucial for Filesystem-based agents so they know exactly what path to `cat` or `read`.*

## GitHub Ecosystem Integration
The GitHub ecosystem leverages the Agent Skills open standard across multiple distinct surfaces. Because GitHub fully embraces the open format, any compatible bridge implementation maps your standard plugin `skills/` directly into `.github/skills/` without requiring any translation or schema changes.

### 1. Copilot Native Support (IDE & Chat)
GitHub Copilot natively loads skills to improve its performance in specialized tasks during interactive conversational development (for Copilot coding agent, GitHub Copilot CLI, and VS Code Insiders).

- **Project Skills:** `.github/skills/<skill-folder>/` or `.claude/skills/<skill-folder>/`
- **Personal Skills:** `~/.copilot/skills/<skill-folder>/`

### 2. Copilot in CI/CD (GitHub Actions)
Agent Skills stored in the repository (`.github/skills`) can also be invoked autonomously during Continuous Integration and Deployment workflows. 

To use an Agent Skill within a GitHub Action:
1. Ensure the skill is exported to `.github/skills/<skill-id>/SKILL.md`.
2. Ensure the frontmatter defines the `name` (unique identifier), `description`, and any required `argument-hint` text.
3. Configure the GitHub Agentic Workflow or Actions pipeline to trigger the skill by its identifier. The AI Agent will read the `SKILL.md` file, adhere to its guidelines, and execute any referenced scripts contextually during the CI run.

*Note: This differs from **GitHub Models Prompts** (`.github/prompts/*.prompt.yml`), which are static templates exported via `github-model-export: true`, whereas `.github/skills` are fully dynamic agent behaviors.*

## Antigravity Implementation
For platforms like **Antigravity** (Google Deepmind's agent framework), the open standard for Agent Skills is natively supported with a few platform-specific nuances:

### Skill Locations & Scopes
- **Workspace Skills:** `<workspace-root>/.agent/skills/<skill-folder>/` (Great for project-specific workflows, testing tools).
- **Global Skills:** `~/.gemini/antigravity/skills/<skill-folder>/` (Personal utilities, general-purpose routines to use across all workspaces).

### Frontmatter Nuances
- **`name`:** In Antigravity, the `name` field is technically *Optional*. If omitted, the agent simply defaults to the folder name.
- **`description`:** Follows standard rules (Third person, heavily keyworded so the model knows when to autonomously trigger it).

### Best Practices (Antigravity Specific)
- **Scripts as Black Boxes:** If providing helper scripts (e.g., in `scripts/`), design them so the agent can simply run `python script.py --help` rather than needing to read and map the full source code. This saves massive context space.
- **Decision Trees:** For complex, ambiguous tasks, embed a clear decision-tree inside the `SKILL.md` to guide the agent on choosing the right sub-path or script based on the situational context.
