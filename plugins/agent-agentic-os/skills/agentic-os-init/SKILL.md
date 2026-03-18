---
name: agentic-os-init
description: >
  Trigger with "set up agentic OS", "initialize agent harness", "init my project for AI agents",
  "where do I put CLAUDE.md", "what goes in context folder", "create my agent environment",
  "scaffold my project for Claude Code", "how do I install skills", "set up persistent memory",
  or "get Claude to remember things between sessions". Guides users through a contextual 
  interview to understand their use case, then scaffolds the right Agentic OS structure. 
  Use this skill even when the user just asks WHERE to put files.
disable-model-invocation: false
allowed-tools: Bash, Read, Write
---

# Agentic OS Init

Bootstrap the Agentic OS / Agent Harness structure into any project. The setup is
not one-size-fits-all -- a solo developer using Claude for marketing strategy needs a
very different environment than a team using agents to document a legacy system.
The interview phase exists to get that right the first time.

There is no official Anthropic "agentic OS" reference implementation. This pattern
synthesizes Anthropic's documented features (CLAUDE.md hierarchy, /loop, sub-agents,
hooks) with community conventions for persistent memory and context management.
Official Anthropic docs:
- CLAUDE.md and memory: https://docs.anthropic.com/en/docs/claude-code/memory
- /loop scheduled tasks: https://docs.anthropic.com/en/docs/claude-code/loop
- Hooks (automation): https://docs.anthropic.com/en/docs/claude-code/hooks
- Sub-agents: https://docs.anthropic.com/en/docs/claude-code/sub-agents
- Claude Code overview: https://docs.anthropic.com/en/docs/claude-code/overview

## Execution Flow

Execute these phases in order. Do not skip phases.

---

## Phase 1: Discovery Interview

Do not assume defaults. Ask the user enough to make smart decisions. Pull answers
from the conversation if they are already there -- do not repeat questions already answered.

Ask only what is unclear. Group questions to minimize back-and-forth. Adapt your
language to the user's technical confidence level (a plumber opened a terminal for
the first time is different from a senior engineer).

### Core Questions (always ask these if not already answered)

1. **What is this project?** What kind of work are you doing here?
   - Is this a software project, a research/writing project, a business workflow?
   
2. **Who is using it?** Just you, or a team?
   - Solo: keep it simple. Team: shared CLAUDE.md matters more.

3. **What is your main use case for the agent?** Pick the closest:
   - Writing / content / marketing / strategy  
   - Software development (coding, debugging, reviewing)
   - Research / analysis / documentation
   - Business process automation (workflows, legacy system analysis, etc.)
   - Something else (describe it)

4. **What sub-tasks or specialized areas do you need the agent to handle?**
   Examples: "analyze screenshots of legacy screens", "draft blog posts", "review PRs",
   "document business rules", "manage project status".

5. **Do you need scheduled/autonomous work?** (e.g., nightly summaries, daily standups,
   background analysis while you sleep) -- this determines whether to set up /loop and heartbeat.md.

6. **How much context do you expect to persist?** (light = just a few facts, heavy = full
   project history, business rules, entity glossary, etc.)

### Use-Case-Specific Follow-Ups

After getting the core answers, ask targeted follow-ups based on the use case:

**If: legacy system documentation / analysis**
- How many screens/modules are you documenting?
- What outputs do you need: business rules, workflow diagrams, requirements docs?
- Are multiple people contributing or is this solo?
- Recommendation: set up sub-agents for screen analysis, business rules capture, and
  workflow documentation. Add an `entities/` folder for business terms glossary.

**If: marketing / strategy / communications**
- What content types? (blogs, social, strategy docs, competitor analysis?)
- Do you have brand voice guidelines to give the agent?
- Recommendation: set up `context/soul.md` with brand voice, a `content/` folder for
  work-in-progress, and session logs for capturing working decisions.

**If: software development**
- What stack? (the agent needs to know your build/test commands)
- Do you use GitHub PRs, CI/CD? Should the agent know about them?
- Recommendation: lean CLAUDE.md with build commands, optional hook for pre-commit.

**If: research / analysis**
- What is the source material? (papers, URLs, files, screenshots?)
- What is the deliverable? (report, synthesis, presentation?)
- Recommendation: set up a `research/` folder, `context/memory.md` for findings.

---

## Phase 2: Component Planning

Based on the discovery answers, propose a component plan before running the script.
Show the user a simple table of what will be created and what will be skipped.

Example output format:
```
Here is what I plan to set up for your [use case]:

| Component              | Include? | Why |
|------------------------|----------|-----|
| CLAUDE.md (project)    | YES      | Core kernel for your project conventions |
| context/soul.md        | YES      | Agent personality for your brand voice |
| context/user.md        | YES      | Your working style preferences |
| context/memory.md      | YES      | Persistent facts across sessions |
| context/memory/ logs   | YES      | Dated session logs |
| START_HERE.md          | YES      | Bootstrap prompt for new sessions |
| heartbeat.md + /loop   | NO       | You didn't mention scheduled tasks |
| .claude/agents/        | YES      | Sub-agents for [specific tasks] |
| ~/.claude/CLAUDE.md    | OPTIONAL | Global kernel if you want this across all projects |

Additional folders I recommend for your use case:
- entities/   -- glossary of business terms (legacy docs use case)
- research/   -- source material and findings (research use case)
```

Get confirmation or adjustments before proceeding to Phase 3.

---

## Phase 3: Execution

Run the setup script with flags derived from the plan:

```bash
# Fallback to current directory if not running inside the plugin manager
PLUGIN_DIR="${CLAUDE_PLUGIN_ROOT:-$(pwd)}"

python3 "${PLUGIN_DIR}/skills/agentic-os-init/scripts/init_agentic_os.py" \
  --target <path> \
  [--global] \
  [--dry-run] \
  [--force]
```

Flags:
- `--target PATH` : Project root (default: current directory)
- `--global` : Also scaffold `~/.claude/CLAUDE.md` for the global kernel  
- `--dry-run` : Preview what would be created without writing anything
- `--force` : Overwrite existing files (show this option only for existing projects)

For existing projects: always run `--dry-run` first and show the user the preview.

After the script runs, create any use-case-specific additional folders that the
interview surfaced (entities/, research/, content/, etc.) but the script does not
create automatically.

---

## Phase 4: Post-Init Guidance

After creating the structure, walk the user through what to fill in, in priority order.
Do not just dump a list -- explain WHY each file matters.

### Priority 1: CLAUDE.md (the kernel -- this is everything)
CLAUDE.md is the single file that Claude reads at the start of every session. It is
your project's kernel. Do not let the user leave it blank.

Prompt them with specific questions based on their use case:
- "What are the most important things Claude should always know about this project?"
- "What commands does Claude need to know to build, test, or run things?"
- "Are there conventions or rules Claude should always follow?"

### Priority 2: context/soul.md (identity and tone)
This only matters if the agent needs a persona. For a coding project it is less
critical. For marketing/communications it is essential. Ask: "Do you want Claude to
have a specific voice or personality in this project?"

### Priority 3: context/user.md (your working style)
Help the user fill this in with a few targeted questions:
- "Do you prefer concise responses or detailed explanations?"
- "Are there workflows or shortcuts Claude should know about how you work?"

### Priority 4: .gitignore recommendations
Remind the user:
```
# Add to .gitignore:
CLAUDE.local.md
context/memory/
context/events.jsonl
context/os-state.json
context/.locks/
.claude/
context/memory.md
context/status.md
```

Keep in git (shared with team):
```
CLAUDE.md
context/soul.md
context/user.md
context/kernel.py
context/agents.json
heartbeat.md
START_HERE.md
```

### Priority 5: Install skills (optional)
If the user wants additional skills for this environment:
```bash
# Install the agentic-os plugin skills
npx skills add richfrem/agent-plugins-skills/plugins/agent-agentic-os

# Or from local checkout
npx skills add ./plugins/agent-agentic-os --force
```

> [!TIP]
> **Avoid File Duplication**: When installing local/development plugins, ensure they are linked as **Symbolic Links** rather than deep copied (verify if `npx skills add` does this, or use `ln -s`). This guarantees that continuous improvements made during your session update the primary source file instantly.

---

## Reference Materials

For the agent running this skill:
- Full Agentic OS pattern explained -> `agentic-os-guide` skill
- Memory write/promote/archive decisions -> `session-memory-manager` skill
- Project setup reference -> `references/project-setup-guide.md`
