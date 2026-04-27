---
concept: improve-iter-7
source: plugin-code
source_file: agent-scaffolders/skills/create-skill/evals/experiments/2026-03-13_194300/logs/improve_iter_7.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.176910+00:00
cluster: skill
content_hash: cc42a7340b422cde
---

# Improve Iter 7

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/skills/create-skill/evals/experiments/2026-03-13_194300/logs/improve_iter_7.json -->
{
  "iteration": 7,
  "prompt": "You are optimizing a skill description for a CLI coding agent skill called \"create-skill\". A \"skill\" is sort of like a prompt, but with progressive disclosure -- there's a title and description that the assistant sees when deciding whether to use the skill, and then if it does use the skill, it reads the .md file which has lots more details and potentially links to other resources in the skill folder like helper files and scripts and additional documentation or examples.\n\nThe description appears in Claude's \"available_skills\" list. When a user sends a query, Claude decides whether to invoke the skill based solely on the title and on this description. Your goal is to write a description that triggers for relevant queries, and doesn't trigger for irrelevant ones.\n\nHere's the current description:\n<current_description>\n\"Interactive initialization script that acts as a Skill Designer and Architect. Generates a compliant Agent Skill containing strict YAML frontmatter, optimal interaction designs, and L4 patterns based on diagnostic questioning.\"\n</current_description>\n\nCurrent scores (Train: 2/4):\n<scores_summary>\nFAILED TO TRIGGER (should have triggered but didn't):\n  - \"Generate an Agent Skill with acceptance criteria, eval prompts, and fallback tree.\" (triggered 0/2 times)\n  - \"Please scaffold a new skill called log-sanitizing with proper SKILL.md frontmatter.\" (triggered 0/2 times)\n\nPREVIOUS ATTEMPTS (do NOT repeat these \u2014 try something structurally different):\n\n<attempt train=2/4>\nDescription: \"Interactive initialization script that acts as a Skill Designer and Architect. Generates a compliant Agent Skill containing strict YAML frontmatter, optimal interaction designs, and L4 patterns based on diagnostic questioning.\"\nTrain results:\n  [FAIL] \"Please scaffold a new skill called log-sanitizing with proper SKILL.md frontmatt\" (triggered 0/2)\n  [PASS] \"Add a new MCP server integration for postgres tools.\" (triggered 0/2)\n  [FAIL] \"Generate an Agent Skill with acceptance criteria, eval prompts, and fallback tre\" (triggered 0/2)\n  [PASS] \"Convert this plugin into a GitHub Actions workflow.\" (triggered 0/2)\n</attempt>\n\n<attempt train=2/4>\nDescription: \"Use this skill to scaffold a complete, standards-compliant Agent Skill folder and SKILL.md. Interactively capture skill name, trigger/usage text, goal, edge cases and acceptance criteria, then generate strict YAML frontmatter, clear trigger description, eval prompts/test cases (evals/evals.json), procedural fallback tree, and references/iteration ledger for trigger optimization. Best for requests like \u201cscaffold a new skill X\u201d, \u201cgenerate SKILL.md with frontmatter and acceptance criteria\u201d, or \u201ccreate skill scaffolding with test prompts and fallback flows.\u201d Not for unrelated infra or non-skill automation tasks.\"\nTrain results:\n  [PASS] \"Add a new MCP server integration for postgres tools.\" (triggered 0/2)\n  [FAIL] \"Generate an Agent Skill with acceptance criteria, eval prompts, and fallback tre\" (triggered 0/2)\n  [FAIL] \"Please scaffold a new skill called log-sanitizing with proper SKILL.md frontmatt\" (triggered 0/2)\n  [PASS] \"Convert this plugin into a GitHub Actions workflow.\" (triggered 0/2)\n</attempt>\n\n<attempt train=2/4>\nDescription: \"Use this skill to interactively scaffold a standards-compliant Agent Skill folder and SKILL.md. It captures the skill name and strict YAML frontmatter, precise trigger text, goal, acceptance criteria, eval prompts/test cases (evals/evals.json), a procedural fallback tree, and linked references. Best for requests like \u201cscaffold a new skill X\u201d or \u201cgenerate SKILL.md with frontmatter, acceptance tests, and fallback flows.\u201d The tool asks diagnostic questions before writing and produces iteration-friendly artifacts for trigger optimization. Not intended for unrelated infra or generic automation tasks.\"\nT

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/create-skill/evals/experiments/2026-03-13_194300/logs/improve_iter_7.json -->
{
  "iteration": 7,
  "prompt": "You are optimizing a skill description for a CLI coding agent skill called \"create-skill\". A \"skill\" is sort of like a prompt, but with progressive disclosure -- there's a title and description that the assistant sees when deciding whether to use the skill, and then if it does use the skill, it reads the .md file which has lots more details and potentially links to other resources in the skill folder like helper files and scripts and additional documentation or examples.\n\nThe description appears in Claude's \"available_skills\" list. When a user sends a query, Claude decides whether to invoke the skill based solely on the title and on this description. Your goal i

*(combined content truncated)*

## See Also

- [[improve-iter-1]]
- [[improve-iter-2]]
- [[improve-iter-3]]
- [[improve-iter-4]]
- [[improve-iter-5]]
- [[improve-iter-6]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/skills/create-skill/evals/experiments/2026-03-13_194300/logs/improve_iter_7.json`
- **Indexed:** 2026-04-27T05:21:04.176910+00:00
