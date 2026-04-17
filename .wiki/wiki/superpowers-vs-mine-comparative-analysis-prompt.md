---
concept: superpowers-vs-mine-comparative-analysis-prompt
source: research-docs
source_file: superpowers/analysis-prompt.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.459795+00:00
cluster: plugin
content_hash: 50017b2337549364
---

# Superpowers vs Mine: Comparative Analysis Prompt

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Superpowers vs Mine: Comparative Analysis Prompt

**Model target:** Claude Sonnet (claude-cli)
**Output directory:** `plugin-research/superpowers/`

---

## Context

You are a senior agentic workflow architect with deep knowledge of:
- Agent Skills Open Standard (agentskills.io)
- Anthropic Claude Code plugins, skills, hooks, sub-agents, slash commands
- Multi-agent patterns: orchestrator, dual-loop, parallel swarm, learning loop
- Agentic OS patterns: persistent memory, event bus, kernel, session lifecycle
- Exploration cycle and discovery-to-spec-driven development workflows

You will perform a comprehensive comparative analysis across three plugin systems
and produce a structured research report with actionable recommendations.

---

## Step 1: Read and Internalize All Three Systems

Read the following directories in full. For each plugin, read every SKILL.md,
agent definition, command file, hook configuration, and README. Do not skim.

### Plugin A: agent-agentic-os
```
plugins/agent-agentic-os/
```
Key files to prioritize:
- `README.md` and `SUMMARY.md` (if present)
- All files in `skills/` (each subdirectory)
- All files in `agents/`
- All files in `commands/`
- All files in `hooks/`
- `references/` directory

### Plugin B: exploration-cycle-plugin
```
plugins/exploration-cycle-plugin/
```
Key files to prioritize:
- `README.md`
- All files in `skills/`
- All files in `agents/`
- All files in `commands/`
- All files in `hooks/`
- `references/` and `templates/` directories

### Plugin C: superpowers (external reference)
```
temp/superpowers/ which is a clone of https://github.com/obra/superpowers
```
Key files to prioritize:
- `README.md`
- `RELEASE-NOTES.md` (high signal -- shows evolution)
- All files in `skills/` (14 skill directories)
- All files in `agents/`
- All files in `commands/`
- `hooks/hooks.json` and `hooks/session-start`
- `docs/` directory

---

## Step 2: Produce the Analysis Report

After reading all three, produce the following outputs. Save each as a
separate file in `plugin-research/superpowers/`.

### Output 1: `capabilities-matrix.md`

A structured comparison table covering every major capability area.
Rows = capability dimensions. Columns = Plugin A / Plugin B / Plugin C.
Mark each cell: Full / Partial / Missing / Not Applicable.

Capability dimensions to cover (add more if you find them):
- Session memory and persistence
- Learning loops and retrospectives
- Multi-agent orchestration (parallel / sequential)
- Exploration and discovery workflows
- Spec-driven development lifecycle
- Code review workflows
- Git worktree management
- Sub-agent dispatching
- Hook lifecycle (session start/stop, tool use)
- Slash command coverage
- Plan-execute-verify cycles
- Test-driven development support
- Debugging support
- Cross-agent portability (npx skills / multi-IDE)
- Documentation and onboarding quality

---

### Output 2: `strengths-and-gaps.md`

**Section 1: What agent-agentic-os does well**
Be specific. Name the skills, agents, or patterns that are genuinely strong.
Reference actual file names and approaches.

**Section 2: What exploration-cycle-plugin does well**
Same specificity. What does this plugin solve that is hard to solve elsewhere?

**Section 3: What superpowers does exceptionally well**
What architectural or design decisions make it stand out? What patterns does
it implement that the other two are missing entirely?

**Section 4: Critical weaknesses in agent-agentic-os and exploration-cycle-plugin**
Be direct. What is missing, underpowered, or architecturally fragile compared
to superpowers? Do not soften this -- it is the most valuable part of the report.

**Section 5: Critical weaknesses in superpowers**
What does superpowers lack that the richfrem plugins do better? Where does
the richfrem approach have genuine advantages?

---

### Output 3: `supercharge-recommendations.md`

Strategic recommendations for what to do next. Frame this as a decision brief:

**Decision A: Pivot to superpowers**

*(content truncated)*

## See Also

- [[gstack-comparative-architecture-analysis-prompt]]
- [[hermes-agent-comparative-architecture-analysis-prompt]]
- [[paperclip-comparative-architecture-analysis-prompt]]
- [[rlm-gap-analysis-version-10-vs-original-vision]]
- [[rlm-gap-analysis-version-10-vs-original-vision]]
- [[rlm-gap-analysis-version-10-vs-original-vision]]

## Raw Source

- **Source:** `research-docs`
- **File:** `superpowers/analysis-prompt.md`
- **Indexed:** 2026-04-17T06:42:10.459795+00:00
