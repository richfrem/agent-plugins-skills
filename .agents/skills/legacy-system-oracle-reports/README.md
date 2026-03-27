# legacy-system-oracle-reports

Specialized workflows for codifying and investigating Oracle Reports (.rdf) components.

## Workflows

| Command | Purpose |
|---|---|
| `/legacy-system-oracle-reports_codify-report` | Full documentation for an Oracle Report (.rdf) |
| `/legacy-system-oracle-reports_investigate-report` | Analyze a Report's queries, parameters, triggers, and dependencies |

## Scripts

| Script | Purpose |
|---|---|
| `report_miner.py` | Extract queries, parameters, triggers, and dependencies from Report XML exports |
| `batch_process_reports.py` | Orchestrate ReportMiner to batch-process all report XML files and generate Report Overview docs |

## References

- `references/diagrams/workflows/report-discovery.mmd` — Report investigation workflow
- `references/acceptance-criteria.md` — Acceptance criteria
