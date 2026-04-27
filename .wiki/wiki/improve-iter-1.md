---
concept: improve-iter-1
source: plugin-code
source_file: agent-scaffolders/skills/create-skill/evals/experiments/2026-03-13_194300/logs/improve_iter_1.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.171062+00:00
cluster: skill
content_hash: e36df56b55bd406b
---

# Improve Iter 1

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/skills/create-skill/evals/experiments/2026-03-13_194300/logs/improve_iter_1.json -->
{
  "iteration": 1,
  "prompt": "You are optimizing a skill description for a CLI coding agent skill called \"create-skill\". A \"skill\" is sort of like a prompt, but with progressive disclosure -- there's a title and description that the assistant sees when deciding whether to use the skill, and then if it does use the skill, it reads the .md file which has lots more details and potentially links to other resources in the skill folder like helper files and scripts and additional documentation or examples.\n\nThe description appears in Claude's \"available_skills\" list. When a user sends a query, Claude decides whether to invoke the skill based solely on the title and on this description. Your goal is to write a description that triggers for relevant queries, and doesn't trigger for irrelevant ones.\n\nHere's the current description:\n<current_description>\n\"Interactive initialization script that acts as a Skill Designer and Architect. Generates a compliant Agent Skill containing strict YAML frontmatter, optimal interaction designs, and L4 patterns based on diagnostic questioning.\"\n</current_description>\n\nCurrent scores (Train: 2/4):\n<scores_summary>\nFAILED TO TRIGGER (should have triggered but didn't):\n  - \"Please scaffold a new skill called log-sanitizing with proper SKILL.md frontmatter.\" (triggered 0/2 times)\n  - \"Generate an Agent Skill with acceptance criteria, eval prompts, and fallback tree.\" (triggered 0/2 times)\n\nPREVIOUS ATTEMPTS (do NOT repeat these \u2014 try something structurally different):\n\n<attempt train=2/4>\nDescription: \"Interactive initialization script that acts as a Skill Designer and Architect. Generates a compliant Agent Skill containing strict YAML frontmatter, optimal interaction designs, and L4 patterns based on diagnostic questioning.\"\nTrain results:\n  [FAIL] \"Please scaffold a new skill called log-sanitizing with proper SKILL.md frontmatt\" (triggered 0/2)\n  [PASS] \"Add a new MCP server integration for postgres tools.\" (triggered 0/2)\n  [FAIL] \"Generate an Agent Skill with acceptance criteria, eval prompts, and fallback tre\" (triggered 0/2)\n  [PASS] \"Convert this plugin into a GitHub Actions workflow.\" (triggered 0/2)\n</attempt>\n\n</scores_summary>\n\nSkill content (for context on what the skill does):\n<skill_content>\n---\nname: create-skill\ndescription: Interactive initialization script that acts as a Skill Designer and Architect. Generates a compliant Agent Skill containing strict YAML frontmatter, optimal interaction designs, and L4 patterns based on diagnostic questioning.\ndisable-model-invocation: false\nallowed-tools: Bash, Read, Write\n---\n# Agent Skill Designer & Architect\n\nYou are not merely a file generator; you are an **Agent Skill Architect**. Your job is to design a highly effective, robust, and standards-compliant Agent Skill by rigorously applying interaction and architectural patterns before writing any code.\n\n> [!NOTE]\n> This skill incorporates interviewing and research patterns inspired by Anthropic's [skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/).\n\n## Core Educational Principles (Enforce These on the User)\nBefore generating any code, you must ensure the designed skill adheres to:\n1. **Concise is Key**: Keep `SKILL.md` under 500 lines. Abstract deep knowledge out.\n2. **Progressive Disclosure**: Split knowledge into physical levels (`Metadata` \u2192 `SKILL.md` \u2192 `references/`).\n3. **Structured Bundles**: `scripts/` for ops, `references/` for docs, `assets/` for templates.\n\n## Execution Steps\n\n### Phase 1: Capture Intent & Discovery Interview\n#### Step 1A: Capture Intent\nFirst, understand the user's intent. Review the conversation history to extract existing context\u2014tools used, sequences of steps, corrections, and observed input/output formats.\nAsk for clarification on:\n- **Skill Name**: (kebab-case, gerund form preferred)\n- **Trigger Description**: (third-person trigger l

*(content truncated)*

<!-- Source: plugin-code/copilot-cli/skills/copilot-cli-agent/evals/experiments/2026-03-13_183345/logs/improve_iter_1.json -->
{
  "iteration": 1,
  "prompt": "You are optimizing a skill description for a CLI coding agent skill called \"copilot-cli-agent\". A \"skill\" is sort of like a prompt, but with progressive disclosure -- there's a title and description that the assistant sees when deciding whether to use the skill, and then if it does use the skill, it reads the .md file which has lots more details and potentially links to other resources in the skill folder like helper files and scripts and additional documentation or examples.\n\nThe description appears in Claude's \"available_skills\" list. When a user sends a query, Claude decides whether to invoke the skill based solely on the title and on this description. Your goal is to

*(combined content truncated)*

## See Also

- [[improve-iter-2]]
- [[improve-iter-3]]
- [[improve-iter-4]]
- [[improve-iter-5]]
- [[improve-iter-6]]
- [[improve-iter-7]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/skills/create-skill/evals/experiments/2026-03-13_194300/logs/improve_iter_1.json`
- **Indexed:** 2026-04-27T05:21:04.171062+00:00
