---
concept: gstack-comparative-architecture-analysis-prompt
source: research-docs
source_file: gstack/analysis-prompt.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.452948+00:00
cluster: richfrem
content_hash: 1fad5c1309186242
---

# gstack: Comparative Architecture Analysis Prompt

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# gstack: Comparative Architecture Analysis Prompt

**Model target:** Claude Sonnet (claude-cli)
**Source repo:** https://github.com/garrytan/gstack
**Local copy:** `temp/gstack/`
**Output directory:** `plugin-research/gstack/`

---

## Important Context Before You Begin

gstack is architecturally the closest external reference to the richfrem plugin
ecosystem of any repo reviewed so far. Both share:

- `.agents/` as a central store for agent components
- `CLAUDE.md` conventions driving agent behavior  
- Skills as the primary knowledge primitive
- A workflow-first mindset organizing work into named operational modes

However, gstack appears to be built for a specific software team's engineering
workflow, while richfrem plugins are designed as a distributable, cross-agent
ecosystem. This distinction will shape your analysis.

Key structural signals to interpret:
- A root-level `SKILL.md` (24KB) -- unusual positioning; understand what it IS
- `SKILL.md.tmpl` -- there is a template system here
- `ETHOS.md` -- this codebase has a stated philosophy; read it first
- `conductor.json` -- an orchestration manifest; understand what it configures
- 39 subdirectories that appear to be named workflow modes (ship/, review/, guard/, canary/, etc.)
- `CHANGELOG.md` at 131KB -- extremely high signal; skim for architectural changes

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

### System C: gstack (garrytan)
```
temp/gstack/ which is a clone of https://github.com/garrytan/gstack
```

Read these files in this priority order:

**Group 1 -- Philosophy and conventions (read first):**
- `ETHOS.md` -- the stated philosophy; this shapes everything else
- `README.md`
- `CLAUDE.md` (17KB -- how agents are expected to work here)
- `AGENTS.md`
- `DESIGN.md` and `ARCHITECTURE.md`

**Group 2 -- The core skill system:**
- `SKILL.md` (24KB root-level -- understand what this actually IS and why it is at the root)
- `SKILL.md.tmpl` (the template system behind it)
- `.agents/` directory contents (what is stored here vs richfrem's `.agents/`)

**Group 3 -- Workflow mode directories (sample 5-6, not all 39):**
Read the full contents of these as representative examples:
- `ship/` -- core delivery workflow
- `review/` -- code review workflow
- `investigate/` -- debugging / research workflow
- `canary/` -- safe deployment pattern
- `guard/` -- quality gate
- `retro/` -- retrospective

For each: understand what files are inside and what the workflow actually does.

**Group 4 -- Orchestration and tooling:**
- `conductor.json`
- `autoplan/` directory
- `benchmark/` directory
- `TODOS.md` (31KB -- shows what is planned/in-progress; high signal for intent)
- `CHANGELOG.md` (131KB -- skim by section headers; look for major architectural
  decisions and evolution of the workflow system)

**Group 5 -- Browser and environment integration:**
- `BROWSER.md` (23KB -- this is a significant capability; what is it?)
- `browse/` and `connect-chrome/` directories
- `scripts/` directory overview

---

## Step 2: Produce the Analysis Report

Save all outputs to `plugin-research/gstack/`. One file per output.

---

### Output 1: `gstack-anatomy.md`

Before comparing anything, explain what gstack actually IS. Answer:

1. **What problem does gstack solve?** Who uses it and in what context?
2. **What is the root-level `SKILL.md`?** Is it one mega-skill? A meta-skill
   template? The "project SKILL.md" for the whole agent OS? Explain its role.
3. **What are the 39 workflow subdirectori

*(content truncated)*

## See Also

- [[hermes-agent-comparative-architecture-analysis-prompt]]
- [[paperclip-comparative-architecture-analysis-prompt]]
- [[superpowers-vs-mine-comparative-analysis-prompt]]
- [[post-integration-analysis-prompt-the-ecosystem-bake-off-ab-test]]
- [[triple-loop-learning-system---architecture-overview]]
- [[agentic-os-architecture]]

## Raw Source

- **Source:** `research-docs`
- **File:** `gstack/analysis-prompt.md`
- **Indexed:** 2026-04-17T06:42:10.452948+00:00
