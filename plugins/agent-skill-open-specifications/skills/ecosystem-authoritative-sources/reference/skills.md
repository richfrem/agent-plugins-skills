# Skills Research

This document captures our accumulated knowledge and definitive specifications for **Skills**.

**Source:** [Extend Claude with skills](https://code.claude.com/docs/en/skills)

## Definition
Skills are modular capabilities that package procedural knowledge, context, and workflows into reusable, filesystem-based resources. While built primarily for Claude and Claude Code, they adhere to the open [Agent Skills](https://agentskills.io/) standard originally developed by Anthropic. Because it is an open standard, skills are highly portable and supported by a wide ecosystem of AI developer tools (e.g., Cursor, Gemini CLI, Goose, VS Code, Letta, Roo Code, etc.). They replace and expand upon older legacy feature sets like `/commands`.

## Creation & Structure
- Skills are individual directories named `<skill-name>`, housing at least one `SKILL.md` file.
- The `SKILL.md` file contains YAML frontmatter configuring the skill and Markdown content acting as the prompt instructions.
- Supporting files (e.g., templates, scripts, reference docs) can be stored in the skill directory and referenced inside `SKILL.md`. Claude will read them only if needed or explicitly invoked.

## Resolution Precedence
Skills are resolved automatically. Any nested `.claude/skills/` directory relative to the current working file is also discovered (useful in monorepos).
1. **Enterprise** (`managed settings`)
2. **Personal** (`~/.claude/skills/<skill-name>/SKILL.md`)
3. **Project** (`.claude/skills/<skill-name>/SKILL.md`)
4. **Plugin** (`<plugin_root>/skills/<skill-name>/SKILL.md` - namespaces prevent conflicts here)

## Configuration (YAML Frontmatter)
The frontmatter configures invocation rules, argument hints, tool allowances, and execution environments.

### Open Standard Properties (`agentskills.io`)
- `name` **(Required)**: Display name. Max 64 characters. Must contain only lowercase letters, numbers, and hyphens. Cannot start/end with a hyphen, nor contain consecutive hyphens (`--`). Must match the parent directory name.
- `description` **(Required)**: Helps the agent decide autonomously when it should trigger the skill based on the conversation context. Max 1024 characters.
- `license` *(Optional)*: License name or reference to a bundled license file (`Apache-2.0`).
- `compatibility` *(Optional)*: Indicates specific environment requirements like system packages or network access. Max 500 characters.
- `metadata` *(Optional)*: Arbitrary key-value map for tool-specific meta (e.g., `author: org`, `version: "1.0"`).
- `allowed-tools` *(Optional/Experimental)*: Space-delimited list of tools the agent can use without asking for explicit permission (e.g., `Bash(git:*) Read`).

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

## Packaging & Distribution (ZIP)
When creating a skill for distribution (e.g. sharing across an enterprise):
- The skill folder must match the Skill's name.
- Package it as a ZIP file where the **folder itself** is the root (not the loose files).
  - **Correct:** `my-skill.zip -> my-skill/SKILL.md`
  - **Incorrect:** `my-skill.zip -> SKILL.md`
- **Dependencies:** `dependencies` can be added to the frontmatter (e.g. `python>=3.8, pandas>=1.5.0`) to define software packages required. Claude Code can install from standard endpoints like PyPI or npm. (Note: API Skills require pre-installed containers).

## Best Practices & Authoring Guidelines
- **Focus & Conciseness:** Assume Claude is highly intelligent. Do not waste tokens explaining basic concepts. Create separate, composable skills for different workflows instead of a single monolithic skill.
- **Naming Conventions:** Use the **gerund form** (verb + -ing) for skill names (e.g., `processing-pdfs`, `analyzing-spreadsheets`). Always lowercase and hyphenated.
- **Descriptions:** Must be written in the **third person** (e.g., "Processes Excel files", not "I process"). Must clearly state both *what* it does and *when* Claude should trigger it autonomously. Max 1024 characters.
- **Progressive Disclosure:** Claude reads only the frontmatter `description` fields first to decide if a skill is relevant, before reading the `SKILL.md` body. Be precise.

### Refined Progressive Disclosure Patterns
To keep `SKILL.md` under the recommended 500 max lines without overloading Context:
1. **High-level guide with references:** SKILL.md provides quick-starts, then links to `REFERENCE.md` or `EXAMPLES.md` for deep dives.
2. **Domain-specific organization:** Group references by type so Claude only reads what's relevant (e.g., `reference/finance.md`, `reference/sales.md`).
3. **One-Level Deep References:** **CRITICAL:** Do not nest references (e.g., SKILL.md -> A.md -> B.md). Claude may only partially read deeply nested chains. All reference files should be linked directly from `SKILL.md`.
4. **Table of Contents:** Any reference file longer than 100 lines must have a TOC at the top so Claude can navigate partial reads effectively.

### Anti-Patterns to Avoid
- **Windows Paths:** Always use Unix-style forward slashes (`/`), even on Windows.
- **Bash/PowerShell Scripts:** Avoid `.sh` or `.ps1` files for complex logic. **Python (`.py`) is the required standard** for skill scripts to guarantee true cross-platform execution (Windows, Mac, Linux) regardless of the host environment.
- **Punting Errors:** Utility scripts should handle exceptions and edge cases themselves (e.g., creating a missing file with default content) rather than failing and forcing Claude to figure it out. Provide explicit error messages in `stdout/stderr` back to Claude.
- **Voodoo Constants:** Document *why* magical numbers or timeouts are set to what they are in your scripts so Claude understands the parameters.
- **Unqualified MCP Tools:** When referencing an MCP tool, always explicitly provide the namespace: `ServerName:tool_name` (e.g., `GitHub:create_issue`).

## Example Repositories
Official open-source repositories containing exemplary and foundational Agent Skills configurations:
- [Anthropic Skills Repository](https://github.com/anthropics/skills/tree/main/skills)
- [Microsoft Skills Repository](https://github.com/microsoft/skills)

## Architecture & Progressive Disclosure
The filesystem-based architecture of Skills naturally forces a 3-level "Progressive Disclosure" strategy that preserves context window space:
1. **Level 1 (Metadata) - Discovery:** Loaded at startup. The YAML frontmatter (`name`, `description`). Only ~100 tokens. Claude uses this to determine *if* the skill is useful.
2. **Level 2 (Instructions) - Activation:** Loaded when triggered. The `SKILL.md` body. Usually < 5k tokens. Loaded via a background bash command (`read pdf-skill/SKILL.md`).
3. **Level 3+ (Resources & Code) - Execution:** Loaded as-needed. Arbitrary scripts or reference files (`REFERENCE.md`) referenced by Level 2. Executing scripts uses tokens only for the *output*, not the script content itself.This makes skills self-documenting, extensible, and highly portable.

*See visual representation of this lifecycle in [skill-execution-flow.mmd](./skill-execution-flow.mmd)*

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
3. **MCP Server Calls:** Ensure referenced tools (`ServerName:tool_name`) are expected and authorized.
4. **Network Access / Exfiltration:** Review scripts/prompts for unauthorized `curl`, `requests.get`, or other network calls. Ensure there are no patterns reading sensitive data and encoding/transmitting it externally.
5. **Hardcoded Credentials:** Reject any skill storing API keys or passwords directly in `.md` or scripts. Use environment variables.
6. **Tool Invocations:** Audit which bash/file tools are explicitly allowed or directed to run.

### Lifecycle Management
1. **Start Specific:** Build narrow skills (`querying-pipeline-data`) before consolidating into broad role-based bundles (`sales-operations`). 
2. **Evaluate First:** Require 3-5 evaluation queries ensuring the skill triggers accurately without overlapping with other skills, handles edge cases, and reliably executes before passing it to production.
3. **Recall Limits:** Don't load hundreds of skills simultaneously. API requests max out at 8 skills per request explicitly. Evaluate recall accuracy when bundling too many skills into a single system prompt.
4. **Source Control:** Maintain skill directories via Git and use CI/CD deployment hooks to sync up to the API/Marketplace.
5. **Versioning:** Pin skills to specific tested versions, and provide quick rollback paths for failed workflows.

## Integrating Skills into Custom Agents (`agentskills.io`)
If building a custom agent or product, skills can be integrated in two ways:
1. **Filesystem-based Agents:** The model operates fully within a sandboxed Unix environment, activating skills by issuing native `cat /path/to/SKILL.md` shell commands, identical to Claude Code.
2. **Tool-based Agents:** The model lacks native filesystem tools, and instead relies on custom-built MCP tools to read the `SKILL.md` file and execute its references.

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

### Ecosystem Tooling
Anthropic maintains an official reference library at [agentskills.io/skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) that provides Python validation tools (e.g., `skills-ref validate ./my-skill` and `skills-ref to-prompt <path>`) for custom agent deployment.

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
