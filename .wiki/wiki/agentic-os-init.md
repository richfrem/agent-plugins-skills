---
concept: agentic-os-init
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-init/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.175871+00:00
cluster: claude
content_hash: 28c9c0fdb5a00101
---

# Agentic OS Init

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: os-init
description: >
  Trigger: "set up agentic OS", "initialize agent harness", "init my project for AI agents",
  "where do I put CLAUDE.md", "create my agent environment", "set up persistent memory".
  Guides users through an interview to understand their use case, then scaffolds the right
  Agentic OS structure. Use even when the user just asks WHERE to put files.

  

  

  
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

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

**If: marketing / strategy /

*(content truncated)*

## See Also

- [[agent-harness-learning-layer-formerly-agentic-os]]
- [[agentic-os-setup-orchestrator]]
- [[os-init-command]]
- [[agentic-os-architecture]]
- [[canonical-agentic-os-file-structure]]
- [[agentic-os---future-vision]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-init/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.175871+00:00
