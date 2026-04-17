---
concept: agent-plugin-analyzer
source: plugin-code
source_file: agent-plugin-analyzer/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.232331+00:00
cluster: analyze
content_hash: 9acf6c973198abbc
---

# Agent Plugin Analyzer

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Agent Plugin Analyzer

A meta-plugin that gives agents the ability to systematically analyze plugin and skill collections, extract design patterns, detect security risks, score maturity, and generate actionable improvement recommendations — powering a virtuous cycle of continuous learning.

## Purpose

When you encounter a plugin or collection of plugins built by others, this plugin helps you:
1. **Inventory** every file and classify its role (deterministic script)
2. **Analyze** structure, content quality, interaction design, and security posture
3. **Extract** reusable design patterns into a governed, living catalog
4. **Score** maturity (L1-L5) and quality across 6 weighted dimensions
5. **Synthesize** actionable improvement recommendations for your own meta-skills

The learnings feed back into improving `agent-scaffolders` and `agent-skill-open-specifications`, making every future plugin you build better.

## File Tree

```
agent-plugin-analyzer/
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── agents/
│   └── l5-red-team-auditor.md   # Sub-agent: conducts L5 architecture analysis
├── research/
│   ├── round-1-redteam-review-prompt.md
│   ├── round-1-synthesis.md
│   ├── round-2-redteam-review-prompt.md
│   ├── round-2-synthesis.md
│   ├── round-3-redteam-review-prompt.md
│   └── round-3-redteam-review-claude-opus.md
├── scripts/
│   ├── assert_audit.py          # Programmatic regression assertions
│   └── inventory_plugin.py      # Deterministic inventory + security scan
├── skills/
│   ├── analyze-plugin/
│   │   ├── SKILL.md             # 6-phase analysis engine
│   │   ├── analyze-plugin-flow.mmd
│   │   └── references/
│   │       ├── acceptance-criteria.md
│   │       ├── analysis-framework.md
│   │       ├── analysis-questions-by-type.md
│   │       ├── maturity-model.md
│   │       ├── output-templates.md
│   │       ├── pattern-catalog.md
│   │       └── security-checks.md
│   ├── audit-plugin/
│   │   ├── SKILL.md             # Standard compliance audit (manifest, structure, security)
│   │   ├── CONNECTORS.md        # Declares plugin-validator cross-plugin dependency
│   │   └── references/
│   ├── audit-plugin-l5/
│   │   ├── SKILL.md             # Triggers the l5-red-team-auditor sub-agent
│   │   └── references/
│   │       └── acceptance-criteria.md
│   ├── mine-plugins/
│   │   └── SKILL.md             # Full pipeline: inventory -> analyze -> extract -> synthesize
│   ├── mine-skill/
│   │   └── SKILL.md             # Targeted single-skill analysis
│   ├── self-audit/
│   │   └── SKILL.md             # Regression smoke test (analyzer vs itself + fixtures)
│   └── synthesize-learnings/
│       ├── SKILL.md
│       └── references/
│           ├── acceptance-criteria.md
│           ├── fallback-tree.md
│           ├── improvement-mapping.md
│           ├── input-contract.md    # Required sections from analyze-plugin output
│           └── open-recommendations.md  # Persistent recommendation tracker
└── tests/
    ├── gold-standard-plugin/    # Known-good fixture (should pass)
    ├── flawed-plugin/           # Known-bad fixture (should fail)
    └── goodhart-plugin/         # Structurally compliant but substantively hollow
```

## Usage

### Analyze a Single Plugin
```
Analyze the sales plugin at claude-knowledgework-plugins/sales
```

### Mine an Entire Collection
```
/mine-plugins claude-knowledgework-plugins/
```

### Analyze a Single Skill
```
/mine-skill ../../skills/my-skill
```

### L5 Red Team Audit (via Sub-Agent)
```
claude -p l5-red-team-auditor "Please deeply assess the plugin located at: plugins/[INSERT_PLUGIN_NAME_HERE]"
# Alternatively, via skill execution:
claude -s audit-plugin-l5
```

### Self-Audit (Regression Test)
```
/self-audit
```

### Synthesize Learnings
```
Take the analysis results and generate improvement recommendations for our scaffolders
```

## The Virtuous Cycle

```
┌─────────────────────────────────────────────────────┐
│                                           

*(content truncated)*

## See Also

- [[agent-plugin-analyzer---architecture]]
- [[red-team-review-agent-plugin-analyzer-meta-plugin]]
- [[round-2-red-team-review-refactored-agent-plugin-analyzer]]
- [[round-3-red-team-review-agent-plugin-analyzer-v3]]
- [[agent-plugin-analyzer-l5-red-team-auditor]]
- [[agent-plugin-analyzer-l5-red-team-auditor]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-plugin-analyzer/README.md`
- **Indexed:** 2026-04-17T06:42:09.232331+00:00
