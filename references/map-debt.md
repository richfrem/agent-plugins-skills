# Map Debt Ledger

Persistent tracking of architectural friction, structural anomalies, and unclosed loops across sessions.

| ID | Title | Status | Severity | Repeat | First Seen | Description | Resolution Commit |
|---|---|---|---|---|---|---|---|
| DEBT-20260902-01 | Downstream Self-Evolution Policy drift & missing deterministic pre-commit evolution guard | RESOLVED | Tier 0 | 1 | 2026-09-02 | Downstream InvestmentToolkit developed stronger Turn-by-Turn Mandatory Protocol that drifted from upstream; agents routinely skipped map-debt writes under context pressure due to lack of mechanical hooks. | Backported Turn-by-Turn policy to .agent/rules/; added pre-commit-evolution-guard, turn_evolution_guard.py Stop hook, and CI verification workflow. |
| DEBT-20260902-02 | Blind overwrite in sync_rules clobbered downstream additions & schema modifications | RESOLVED | Tier 0 | 1 | 2026-09-02 | sync_rules() in init_agentic_os.py previously used blind force=True overwrite or identical-string short-circuits, clobbering downstream custom additions and duplicating contradictory schema lines. | Implemented fine-grained difflib SequenceMatcher in init_agentic_os.py to preserve downstream insertions and give upstream precedence on line replacements, backed by comprehensive pytest suite. |
