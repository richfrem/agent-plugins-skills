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
- What would be gained?
- What would be lost from the existing investment?
- What is the migration path?
- Under what conditions does this make sense?

**Decision B: Keep doing what you are doing but supercharge it**
- Which specific superpowers patterns should be imported into agent-agentic-os?
- Which specific superpowers patterns should be imported into exploration-cycle-plugin?
- What is the priority order (quick wins vs long-term rewrites)?
- What new skills or agents should be built based on superpowers learnings?

**Decision C: Hybrid approach**
- Which parts of superpowers are worth adopting as-is (copy or reference)?
- Which parts of the richfrem approach are architecturally superior and worth
  keeping regardless of what superpowers does?

**Your recommendation:** End with a clear recommendation of which path you
would take and why. Apply your knowledge of agentic workflow architecture
to make this opinionated, not hedged.

---

### Output 4: `architecture-comparison.mmd`

A Mermaid diagram comparing the three systems architecturally. Show:
- Core components of each plugin
- Data flow and agent orchestration patterns
- Where they overlap and where they diverge
- Any clear dependency or integration opportunities

Use `graph TD` or `graph LR` format. Keep node labels short and readable.
Do not use em dashes or special characters in node labels.

---

### Output 5: `quick-wins.md`

A prioritized list of 5-10 concrete, implementable improvements to
agent-agentic-os and exploration-cycle-plugin based on superpowers patterns.

For each quick win:
- What to build or change (specific, not vague)
- Which superpowers skill/pattern it is inspired by
- Estimated effort: Small (under 2 hours) / Medium (half day) / Large (multi-day)
- Expected impact: which gap it closes

---

## Step 3: Self-Review Before Saving

Before saving any output file, verify:
1. Every claim is grounded in something you actually read in the source files
2. No file contains vague advice -- every recommendation names a specific
   file, pattern, or skill
3. The Mermaid diagram is syntactically valid (no special characters in labels)
4. `supercharge-recommendations.md` ends with a clear, opinionated recommendation

---

## Constraints

- Do NOT fabricate capabilities. If a plugin does something, it is because
  you read a file that proves it.
- Do NOT be balanced for the sake of politeness. This is a critical review.
  Honest gaps are more valuable than diplomatic summaries.
- Do use your deep knowledge of agentic architecture to contextualize findings
  beyond what is literally in the files.
- Save all outputs to `plugin-research/superpowers/` (one file per output above).
- Confirm each file saved with its path and line count.
