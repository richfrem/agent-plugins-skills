# Copilot Prompt — README Update (main project README.md)

**Model:** claude-sonnet-4.6
**File to rewrite:** `README.md` (project root)
**Triggered by:** Post-simplification gap audit — README is stale against actual plugin inventory

---

## Context

The main README.md is out of date. A full audit of the actual plugin tree was run and compared
against the README contents. The README needs a full rewrite that:

1. Leads with what the project IS and how to install it (not the most exotic feature)
2. Has the accurate inventory (123 skills, 23 plugins — not 119)
3. Removes deleted components (triple-loop-architect, triple-loop-orchestrator, os-skill-improvement)
4. Adds missing skills and agents
5. Rewrites the Architecture section to describe the current system (not the deleted triple-loop)
6. Groups plugins by purpose (not alphabetically) — most valuable ones first

Read the current README first:
```bash
cat README.md
```

All file paths are relative to the repo root:
`/Users/richardfremmerlid/Projects/agent-plugins-skills`

---

## Authoritative Inventory (use this — do NOT re-scan the filesystem)

This is the exact current state from a verified Python scan. Use these facts for counts and lists.

```json
{
  "adr-manager": {
    "version": "2.0.0",
    "skills": ["adr-management"],
    "agents": [],
    "commands": ["adr-management"]
  },
  "agent-agentic-os": {
    "version": "1.6.0",
    "skills": [
      "optimize-agent-instructions", "os-architect", "os-clean-locks",
      "os-environment-probe", "os-eval-backport", "os-eval-lab-setup",
      "os-eval-runner", "os-evolution-planner", "os-evolution-verifier",
      "os-experiment-log", "os-guide", "os-improvement-loop",
      "os-improvement-report", "os-init", "os-memory-manager", "todo-check"
    ],
    "agents": ["agentic-os-setup", "improvement-intake-agent", "os-architect-agent", "os-architect-tester-agent", "os-health-check"],
    "commands": ["os-init", "os-loop", "os-memory"]
  },
  "agent-loops": {
    "version": "2.1.0",
    "skills": ["agent-swarm", "dual-loop", "learning-loop", "orchestrator", "red-team-review", "triple-loop-learning"],
    "agents": ["orchestrator"],
    "commands": []
  },
  "agent-scaffolders": {
    "version": "2.0.0",
    "skills": [
      "analyze-plugin", "audit-plugin", "audit-plugin-l5",
      "create-agentic-workflow", "create-azure-agent", "create-command",
      "create-docker-skill", "create-github-action", "create-hook",
      "create-mcp-integration", "create-plugin", "create-skill",
      "create-stateful-skill", "create-sub-agent",
      "ecosystem-authoritative-sources", "ecosystem-standards",
      "eval-autoresearch-fit", "fix-plugin-paths", "l5-red-team-auditor",
      "manage-marketplace", "mine-plugins", "mine-skill",
      "path-reference-auditor", "self-audit", "synthesize-learnings"
    ],
    "agents": [],
    "commands": ["audit-plugin", "create-plugin", "create-skill", "create-sub-agent", "mine-plugins", "self-audit"]
  },
  "claude-cli": {
    "version": "2.0.0",
    "skills": ["claude-cli-agent", "claude-project-setup", "optimize-context"],
    "agents": ["architect-review", "refactor-expert", "security-auditor"],
    "commands": []
  },
  "coding-conventions": {
    "version": "2.0.0",
    "skills": ["coding-conventions-agent"],
    "agents": ["coding-conventions-agent"],
    "commands": []
  },
  "context-bundler": {
    "version": "2.1.0",
    "skills": ["context-bundler", "red-team-bundler"],
    "agents": [],
    "commands": ["bundle", "redteam"]
  },
  "copilot-cli": {
    "version": "2.0.0",
    "skills": ["copilot-cli-agent"],
    "agents": ["architect-review", "refactor-expert", "security-auditor"],
    "commands": []
  },
  "dependency-management": {
    "version": "2.0.0",
    "skills": ["dependency-management"],
    "agents": [],
    "commands": ["dependency-management"]
  },
  "exploration-cycle-plugin": {
    "version": "0.1.0",
    "skills": [
      "business-requirements-capture", "business-workflow-doc",
      "discovery-planning", "exploration-handoff", "exploration-optimizer",
      "exploration-session-brief", "exploration-workflow", "prototype-builder",
      "subagent-driven-prototyping", "user-story-capture", "visual-companion"
    ],
    "agents": [
      "business-rule-audit-agent", "discovery-planning-agent",
      "exploration-cycle-orchestrator-agent", "handoff-preparer-agent",
      "intake-agent", "planning-doc-agent", "problem-framing-agent",
      "prototype-builder-agent", "prototype-companion-agent",
      "requirements-doc-agent", "requirements-scribe-agent"
    ],
    "commands": []
  },
  "gemini-cli": {
    "version": "2.0.0",
    "skills": ["antigravity-project-setup", "gemini-cli-agent"],
    "agents": ["architect-review", "refactor-expert", "security-auditor"],
    "commands": []
  },
  "huggingface-utils": {
    "version": "2.0.0",
    "skills": ["hf-init", "hf-upload"],
    "agents": [],
    "commands": ["hf-init", "hf-upload"]
  },
  "link-checker": {
    "version": "2.0.0",
    "skills": ["link-checker-agent", "symlink-manager"],
    "agents": ["link-checker-agent"],
    "commands": []
  },
  "memory-management": {
    "version": "2.0.0",
    "skills": ["memory-management"],
    "agents": [],
    "commands": ["memory-management"]
  },
  "mermaid-to-png": {
    "version": "2.0.0",
    "skills": ["convert-mermaid"],
    "agents": [],
    "commands": ["convert-mermaid"]
  },
  "obsidian-wiki-engine": {
    "version": "3.1.0",
    "skills": [
      "obsidian-bases-manager", "obsidian-canvas-architect",
      "obsidian-graph-traversal", "obsidian-init", "obsidian-markdown-mastery",
      "obsidian-query-agent", "obsidian-rlm-distiller", "obsidian-vault-crud",
      "obsidian-wiki-builder", "obsidian-wiki-linter"
    ],
    "agents": ["super-rag-setup-agent", "wiki-build-agent", "wiki-distill-agent", "wiki-init-agent", "wiki-lint-agent", "wiki-query-agent"],
    "commands": ["obsidian-init", "wiki-audit", "wiki-build", "wiki-distill", "wiki-init", "wiki-lint", "wiki-query", "wiki-rebuild"]
  },
  "plugin-manager": {
    "version": "2.0.0",
    "skills": ["plugin-installer", "plugin-remover", "plugin-syncer"],
    "agents": [],
    "commands": ["cleanup", "install", "remove", "sync"]
  },
  "rlm-factory": {
    "version": "2.0.0",
    "skills": ["rlm-audit", "rlm-cleanup-agent", "rlm-curator", "rlm-distill-agent", "rlm-init", "rlm-search"],
    "agents": ["rlm-cleanup-agent", "rlm-curator", "rlm-distill-agent", "rlm-factory-init-agent", "rlm-init", "rlm-search"],
    "commands": ["audit", "cleanup", "distill", "query", "rlm-init", "rlm-search"]
  },
  "rsvp-speed-reader": {
    "version": "1.0.0",
    "skills": ["rsvp-comprehension-agent", "rsvp-reading"],
    "agents": ["rsvp-comprehension-agent"],
    "commands": ["rsvp-reading"]
  },
  "spec-kitty-plugin": {
    "version": "2.0.0",
    "skills": [
      "spec-kitty-accept", "spec-kitty-analyze", "spec-kitty-checklist",
      "spec-kitty-clarify", "spec-kitty-constitution", "spec-kitty-dashboard",
      "spec-kitty-implement", "spec-kitty-merge", "spec-kitty-plan",
      "spec-kitty-research", "spec-kitty-review", "spec-kitty-specify",
      "spec-kitty-status", "spec-kitty-sync-plugin", "spec-kitty-tasks",
      "spec-kitty-tasks-finalize", "spec-kitty-tasks-outline",
      "spec-kitty-tasks-packages", "spec-kitty-workflow"
    ],
    "agents": ["spec-kitty-agent", "spec-kitty-setup"],
    "commands": []
  },
  "task-manager": {
    "version": "2.0.0",
    "skills": ["task-agent"],
    "agents": [],
    "commands": []
  },
  "vector-db": {
    "version": "2.0.0",
    "skills": ["vector-db-audit", "vector-db-cleanup", "vector-db-ingest", "vector-db-init", "vector-db-launch", "vector-db-search"],
    "agents": ["vector-db-cleanup", "vector-db-ingest", "vector-db-init-agent"],
    "commands": ["cleanup", "ingest", "query", "vector-db-init", "vector-db-launch", "vector-db-search"]
  },
  "voice-writer": {
    "version": "0.1.0",
    "skills": ["humanize"],
    "agents": [],
    "commands": []
  }
}
```

**Skill count by plugin (use to verify your totals):**
adr-manager:1, agent-agentic-os:16, agent-loops:6, agent-scaffolders:25,
claude-cli:3, coding-conventions:1, context-bundler:2, copilot-cli:1,
dependency-management:1, exploration-cycle-plugin:11, gemini-cli:2,
huggingface-utils:2, link-checker:2, memory-management:1, mermaid-to-png:1,
obsidian-wiki-engine:10, plugin-manager:3, rlm-factory:6, rsvp-speed-reader:2,
spec-kitty-plugin:19, task-manager:1, vector-db:6, voice-writer:1
**Total: 123 skills across 23 plugins**

---

## What the current README gets wrong (must fix)

1. **Count**: Says "119 skills" → correct to **123 skills**
2. **Deleted components still listed**:
   - `triple-loop-architect` agent (deleted in v1.6.0)
   - `triple-loop-orchestrator` agent (deleted in v1.6.0)
   - `os-skill-improvement` skill (deleted in v1.6.0)
   - `os-nightly-evolver` agent (never existed in current code)
   - `references/sample-prompts/triple-loop-architect-prompt.md` (deleted)
   - `rlm-distill-ollama` skill (no longer in source)
   - `ollama-launch` skill (no longer in source)
3. **Architecture section "Triple-Loop Autonomous Skill Improvement"** — describes the deleted L0/L1/L2 agent chain. Must be rewritten to describe the CURRENT system.
4. **Missing skills**: os-environment-probe, os-evolution-verifier, os-experiment-log (agentic-os); optimize-context (claude-cli); symlink-manager (link-checker); rlm-audit (rlm-factory); vector-db-audit (vector-db)
5. **Missing agent lists**: claude-cli, copilot-cli, gemini-cli each have architect-review, refactor-expert, security-auditor sub-agents — not documented anywhere
6. **agent-loops triple-loop-learning** skill not listed in the agent-loops section
7. **Flywheel description** mentions `os-skill-improvement` and `os-nightly-evolver` — update

---

## Structure to use for the new README

Write the README in this order. Keep each section tight — this is a reference doc, not a tutorial.

### 1. Title + one-line pitch

```markdown
# Universal Agent Plugins & Skills Ecosystem

**123 skills · 23 plugins** — a self-improving, cross-platform library of reusable AI agent
capabilities for Claude Code, GitHub Copilot, Gemini CLI, and any compliant agent framework.
```

### 2. Platforms (brief, keep current content, just tighten)

One paragraph. Keep the `.agents/` folder standard note.

### 3. Installation (near top — important)

Keep the INSTALL.md pointer box. Add the one-liner for quick install:
```bash
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills
```

### 4. Core Philosophy (keep existing content, it's good)

Transitional Architectures + Skills as Applications. Keep as-is, maybe shorten slightly.

### 5. Architecture — rewrite this section entirely

Replace the stale "Triple-Loop Autonomous Skill Improvement" with the CURRENT architecture.
The current system has THREE key architectural pillars:

**Pillar 1: The Improvement OS (agent-agentic-os)**

```
os-architect           ← intent classifier + ecosystem router
    ↓
os-improvement-loop    ← learning engine: orchestrates multi-iteration improvement
    ↓
os-eval-runner         ← inner gate: KEEP/DISCARD per iteration (evaluate.py)
    ↓
os-eval-backport       ← human gate: review before lab winner → production
    ↓
os-experiment-log      ← scientific backbone: longitudinal tracking + synthesis
```

Entry point: `/os-architect` — describe what you want in plain language.

The Karpathy autoresearch loop (mutate SKILL.md → evaluate.py → KEEP/DISCARD → repeat)
still applies and is still worth documenting. Keep that subsection.

**Pillar 2: Execution Patterns (agent-loops)**

5 composable primitives: learning-loop, dual-loop, agent-swarm, red-team-review,
triple-loop-learning. Used as the execution substrate by the improvement OS and standalone
by any agent workflow.

**Pillar 3: Super-RAG 3-tier retrieval**

O(1) RLM keyword → O(log N) vector semantic → wiki concept nodes.
Keep existing description, it's accurate.

Keep the existing eval progress chart and image link for convert-mermaid — it's a good concrete example.

Keep the Hub-and-Spoke ADR callout (it's architecturally correct).

Remove entirely:
- The L0/L1/L2 table (triple-loop agents deleted)
- The "@triple-loop-architect" invocation example
- The sample-prompts reference
- os-nightly-evolver mention
- "INNER flywheel (os-skill-improvement)" mention

### 6. Plugin Ecosystem section

Group plugins into logical categories. Use this grouping:

**Group 1: The Improvement OS**
- agent-agentic-os (lead with os-architect as entry point)

**Group 2: Engineering Workflows**
- spec-kitty-plugin (Spec→Plan→Tasks→Implement→Review→Merge)
- exploration-cycle-plugin (Discovery & Requirements)

**Group 3: Execution Patterns**
- agent-loops (5 execution primitives)

**Group 4: Code Quality & Safety**
- coding-conventions
- agent-scaffolders (scaffolding + audit + analysis)
- link-checker

**Group 5: CLI Sub-Agents**
- claude-cli (note: ships 3 sub-agents: architect-review, refactor-expert, security-auditor)
- copilot-cli (same 3)
- gemini-cli (same 3)

**Group 6: Knowledge & Memory**
- obsidian-wiki-engine (Super-RAG + wiki)
- rlm-factory (O(1) keyword search)
- vector-db (semantic search)
- memory-management

**Group 7: Infrastructure & Utilities**
- plugin-manager
- task-manager
- dependency-management
- context-bundler
- mermaid-to-png
- adr-manager
- huggingface-utils
- voice-writer
- rsvp-speed-reader

For each plugin listing:
- Use the accurate skill list from the inventory above
- For agent-agentic-os: list the 16 skills correctly (no os-skill-improvement)
- For agent-loops: include triple-loop-learning in the skill list
- For CLI sub-agents: mention the 3 sub-agents per plugin
- For exploration-cycle-plugin: list the 11 agents (this is a differentiator)

Add the Execution Disciplines (obra/superpowers) section after CLI sub-agents — keep it as-is.

### 7. Completed Experiments

Keep the Ecosystem Fitness Sweep v1 section — it has good data. Just verify the table
and links are still accurate (don't change them, they should be fine).

### 8. Repository Structure

Update the comment to say "23 plugins, 123 skills". Keep the rest.

Update the footer tagline:
```
*123 skills · 23 plugins · Improvement OS (os-architect) · Karpathy autoresearch loops · Super-RAG 3-tier retrieval*
```

---

## Tone guidance

- Lead with benefits and use cases, not component lists
- Install information is near the top (section 3)
- Architecture explains WHY the components exist, not just WHAT they are
- Plugin listings are complete but not padded — one line per skill where possible
- No marketing fluff, no future-tense promises

---

## Output Contract

Write the new README.md directly to `README.md` in the project root.

After writing, verify:
```bash
# Confirm no stale component names remain
grep -n "triple-loop-architect\|triple-loop-orchestrator\|os-skill-improvement\|os-nightly-evolver\|rlm-distill-ollama\|ollama-launch" README.md

# Confirm correct counts appear
grep -n "123\|23 plugins" README.md

# Line count (should be in the range 200-350 lines — tight, not padded)
wc -l README.md
```

Do NOT write a summary file — the only output is the updated README.md itself.
