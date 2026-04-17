---
concept: paperclip-comparative-architecture-analysis-prompt
source: research-docs
source_file: paperclip/analysis-prompt.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.459106+00:00
cluster: richfrem
content_hash: 9f35276fad7c91cf
---

# Paperclip: Comparative Architecture Analysis Prompt

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Paperclip: Comparative Architecture Analysis Prompt

**Model target:** Claude Sonnet (claude-cli)
**Source repo:** https://github.com/paperclipai/paperclip
**Local copy:** `temp/paperclip/`
**Output directory:** `plugin-research/paperclip/`

---

## Important Context Before You Begin

Paperclip is the most architecturally comparable external system to richfrem's
goals of any repo reviewed in this research series. Key signals:

- Uses `.agents/` AND `.claude/` directories -- exact same central store pattern
  as richfrem
- Has `skills/paperclip-create-agent` and `skills/paperclip-create-plugin` --
  direct counterparts to richfrem's `create-sub-agent` and `create-plugin`
  scaffolders
- Has `skills/para-memory-files` -- a dedicated memory system skill (PARA method)
- Is a deployable platform (TypeScript monorepo with Docker, server, UI, CLI)
- Has a TypeScript Plugin SDK in `packages/plugins/sdk`

The core tension to analyze: richfrem builds a **distributable plugin ecosystem**
(ship skills as files via npx). Paperclip appears to be a **platform** (deployable
service + plugin marketplace). Both are solving similar problems at different layers.

Do not pre-judge. Read first, compare second.

---

## Step 1: Read and Internalize All Systems

### Plugin A: agent-agentic-os (richfrem)
```
plugins/agent-agentic-os/
```
Priority files:
- `README.md` and `SUMMARY.md`
- All `skills/` subdirectories (each SKILL.md)
- All `agents/` files
- All `commands/` files
- `hooks/hooks.json`
- `references/` directory

### Plugin B: exploration-cycle-plugin (richfrem)
```
plugins/exploration-cycle-plugin/
```
Priority files:
- `README.md`
- All `skills/` subdirectories
- All `agents/` files
- All `commands/` files
- `references/` and `templates/` directories

### Also relevant from richfrem (for scaffolder comparison):
```
plugins/agent-scaffolders/skills/create-plugin/SKILL.md
plugins/agent-scaffolders/skills/create-skill/SKILL.md
```
Read these specifically for the scaffolder comparison in Output 3.

### System C: Paperclip (paperclipai)
```
temp/paperclip/ which is a clone of https://github.com/paperclipai/paperclip
```

Read these files in priority order:

**Group 1 -- What is this product? (read first):**
- `README.md` (13KB -- understand the product vision and target user)
- `AGENTS.md` (3.8KB -- agent working conventions)
- `releases/` directory listing and any release notes found (high signal for evolution)

**Group 2 -- The skills (highest priority for richfrem comparison):**
- `skills/paperclip/SKILL.md` (23KB -- the primary skill; what does it do?)
- `skills/paperclip/references/` -- read all files in this directory
- `skills/paperclip-create-agent/SKILL.md` -- compare directly against richfrem's `create-sub-agent`
- `skills/paperclip-create-agent/references/` -- all files
- `skills/paperclip-create-plugin/SKILL.md` -- compare directly against richfrem's `create-plugin`
- `skills/paperclip-create-plugin/references/` -- all files
- `skills/para-memory-files/SKILL.md` -- compare against richfrem's `memory-management` plugin
- `skills/para-memory-files/references/` -- all files

**Group 3 -- Platform infrastructure:**
- `packages/plugins/sdk/` -- directory listing and any index or README
- `packages/plugins/create-paperclip-plugin/` -- how they scaffold plugins programmatically
- `packages/adapters/` -- directory listing (what adapters exist?)
- `.agents/skills/` and `.claude/skills/` -- what is installed here vs the source skills/?

**Group 4 -- Product context:**
- `evals/` -- how they evaluate skills or agents
- `cli/` -- directory listing and README if present
- `doc/` or `docs/` -- any architecture or design documentation

---

## Step 2: Produce the Analysis Report

Save all outputs to `plugin-research/paperclip/`. One file per output.

---

### Output 1: `paperclip-anatomy.md`

Answer these questions before any comparison:

1. **What is paperclip as a product?** Who is the target user? What problem does
   it solve? Is it a platfor

*(content truncated)*

## See Also

- [[gstack-comparative-architecture-analysis-prompt]]
- [[hermes-agent-comparative-architecture-analysis-prompt]]
- [[superpowers-vs-mine-comparative-analysis-prompt]]
- [[post-integration-analysis-prompt-the-ecosystem-bake-off-ab-test]]
- [[triple-loop-learning-system---architecture-overview]]
- [[agentic-os-architecture]]

## Raw Source

- **Source:** `research-docs`
- **File:** `paperclip/analysis-prompt.md`
- **Indexed:** 2026-04-17T06:42:10.459106+00:00
