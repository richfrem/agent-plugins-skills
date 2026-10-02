---
name: os-improvement-report
plugin: agent-agentic-os
description: >
  Trigger with "show me the improvement chart", "how are we improving", "progress report",
  "graph the eval scores", "show cycle of improvement", "what's the trend", "are we getting
  better". Produces a visual/text summary of how the agentic loop is improving across cycles.
  Do NOT use this to run the learning loop or evaluate a specific skill change.
allowed-tools: Bash, Read, Write
---

# Loop Progress Report (os-improvement-report)

Generates visual charts and structured text summaries tracking agentic loop improvement cycles across plugins.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Reporting Scope Only**: Dedicated to generating visual and text progress summaries. Do NOT use to execute the learning loop or evaluate skill modifications.
- **Primary Source of Truth**: Read numeric results primarily from `context/experiment-log/index.md`; treat `context/memory/improvement-ledger.md` strictly as a legacy fallback.
- **Data Availability Gate**: If no numeric entries or completed cycles exist, report "No cycles completed yet" rather than rendering empty charts.
- **Output Placement**: Write charts and summaries exclusively to `context/memory/reports/` using timestamped filenames.

## Quick start

```bash
# Generate progress report and trend chart for the workspace
python3 plugins/agent-agentic-os/scripts/generate_report.py \
  --project-dir . \
  --plugin-dir plugins/agent-agentic-os

# Generate report for a single skill
python3 plugins/agent-agentic-os/scripts/generate_report.py \
  --project-dir . \
  --plugin-dir plugins/agent-agentic-os \
  --skill <skill-name>
```

## Workflow

1. **Phase 1: Log & Ledger Ingestion**: Query `context/experiment-log/index.md` for numeric evaluation entries; check legacy ledger if no numeric rows exist.
2. **Phase 2: Metric Aggregation**: Parse progression scores, baseline-vs-best deltas, and step-line progression points across cycles.
3. **Phase 3: Chart & Report Generation**: Execute `generate_report.py` to render the PNG chart and write markdown summary under `context/memory/reports/`.
4. **Phase 4: Presentation**: Output the image artifact path, display summary highlights inline, and offer drill-downs into per-skill trends.

## Verification

```bash
# Verify generator CLI options
python3 plugins/agent-agentic-os/scripts/generate_report.py --help

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/agent-agentic-os/skills/os-improvement-report --mode source
```

## References
- [detailed-reference.md](references/detailed-reference.md) - Ledger specifications, parsing rules, and cross-plugin commands.
- [chart-reading-guide.md](references/chart-reading-guide.md) - How to interpret KEEP/DISCARD dots and running-best step lines.
- [improvement-ledger-spec.md](references/memory/improvement-ledger-spec.md) - Improvement ledger format, writing protocol, and initialization.
- [acceptance-criteria.md](references/acceptance-criteria.md) - Acceptance criteria and output validation standards.
- [fallback-tree.md](references/fallback-tree.md) - Fallback handling for missing logs or execution errors.
