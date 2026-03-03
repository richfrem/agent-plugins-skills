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
├── commands/
│   ├── mine-plugins.md          # Full analysis pipeline
│   ├── mine-skill.md            # Single-skill analysis
│   └── self-audit.md            # Regression smoke test
├── research/
│   ├── round-1-redteam-review-prompt.md
│   ├── round-1-synthesis.md
│   ├── round-2-redteam-review-prompt.md
│   └── round-2-synthesis.md
├── scripts/
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
│   └── synthesize-learnings/
│       ├── SKILL.md
│       └── references/
│           ├── acceptance-criteria.md
│           └── improvement-mapping.md
└── tests/
    ├── gold-standard-plugin/    # Known-good fixture (should pass)
    └── flawed-plugin/           # Known-bad fixture (should fail)
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
/mine-skill plugins/my-plugin/skills/my-skill
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
| `analyze-plugin` | 6-phase analysis: Inventory → Structure → Content → Patterns → Security → Synthesis & Scoring |
| `synthesize-learnings` | Converts raw analysis into actionable recommendations for 4 targets |

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
