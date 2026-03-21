# Agent Plugin Analyzer

A meta-plugin that gives agents the ability to systematically analyze plugin and skill collections, extract design patterns, detect security risks, score maturity, and generate actionable improvement recommendations — powering a virtuous cycle of continuous learning.

## Installation

### Option 1: From a Marketplace (Recommended)
```bash
/plugin marketplace add <marketplace-url>
/plugin install agent-plugin-analyzer
```
For skills-only portability across all agents (Claude, Gemini, Copilot, etc.):
```bash
npx skills add <marketplace-url>/plugins/agent-plugin-analyzer
```

### Option 2: From GitHub Directly
```bash
# Skills only
npx skills add richfrem/agent-plugins-skills --path plugins/agent-plugin-analyzer

# Full plugin (Claude Code native)
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install agent-plugin-analyzer
```

### Option 3: Local Development Checkout
```bash
npx skills add ./plugins/agent-plugin-analyzer
```

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
│                                                     │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    │
│   │ Analyze  │───▶│ Extract  │───▶│Synthesize│    │
│   │ Plugins  │    │ Patterns │    │ Learnings│    │
│   └──────────┘    └──────────┘    └──────────┘    │
│        ▲                               │           │
│        │                               ▼           │
│   ┌──────────┐                   ┌──────────┐     │
│   │  Build   │◀──────────────────│ Improve  │     │
│   │  Better  │                   │Scaffolds │     │
│   │ Plugins  │                   │ & Specs  │     │
│   └──────────┘                   └──────────┘     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Skills

| Skill | Description |
|-------|-------------|
| `analyze-plugin` | 7-phase analysis: Compliance Pre-Check + Inventory + Structure + Content + Patterns + Security + Scoring |
| `audit-plugin` | Standard compliance audit: manifest, structure, naming, components, security (uses plugin-validator agent) |
| `audit-plugin-l5` | Adversarial red team audit -- dispatches `l5-red-team-auditor` against 39-point architecture matrix |
| `synthesize-learnings` | Converts raw analysis into actionable recommendations for 4 targets |
| `mine-plugins` (user-invocable) | Full pipeline: inventory -> analyze -> extract -> synthesize -> recommend |
| `mine-skill` (user-invocable) | Targeted analysis of a single skill directory |
| `self-audit` (user-invocable) | Regression test: runs analyzer against itself + test fixtures |

## Commands

| Command | Description |
|---------|-------------|
| `/mine-plugins` | Full pipeline: inventory → analyze → extract → synthesize → recommend |
| `/mine-skill` | Targeted analysis of a single skill directory |
| `/self-audit` | Regression test: runs analyzer against itself + test fixtures |

## Scripts

| Script | Description |
|--------|-------------|
| `inventory_plugin.py` | Deterministic file inventory with classification, line counts, compliance checks, and `--security` scan |

## Key References

| Reference | Purpose |
|-----------|---------|
| `pattern-catalog.md` | 28 governed patterns with lifecycle, confidence, provenance |
| `security-checks.md` | Structural anti-patterns + security checks + LLM-native attack vectors |
| `maturity-model.md` | L1-L5 maturity levels + 6-dimension weighted scoring rubric |
| `analysis-questions-by-type.md` | 90+ self-prompt questions per file type + holistic design considerations |
| `analysis-framework.md` | Deep rubrics for each analysis phase |

## Red Team History

| Round | Reviewers | Key Improvements |
|-------|-----------|-----------------|
| Round 1 | Gemini 3.1 Pro, Grok 4.2, GPT 5.3, Claude 4.6 Opus | Pattern governance, security layer, maturity model, self-audit |
| Round 2 | GPT 5.3, Gemini 3.1 Pro, Grok 4.2, Claude Sonnet + Opus | Extract to references, test fixtures, score weights, LLM attack vectors |
| Round 3 | Claude Opus 4.6 | Fixture accuracy, eval schema alignment, Goodhart gap, input contract, pattern ossification |

## Plugin Components

### Skills
- `analyze-plugin`
- `audit-plugin`
- `audit-plugin-l5`
- `synthesize-learnings`

### Scripts
- `scripts/inventory_plugin.py`

