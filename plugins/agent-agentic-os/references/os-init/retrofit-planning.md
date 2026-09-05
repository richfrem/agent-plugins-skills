# Component Planning & Retrofit Matrix

Reference for component initialization and retrofit behaviors during `os-init` execution.

| Component | Fresh Init | Retrofit Mode | Purpose |
|---|---|---|---|
| `architecture.md` | Create Initial Layout | Context Review & Enrich | High-level system architecture & agentic layout |
| `CLAUDE.md` | Intelligent Seed | Context Blend & Reconcile | Authoritative project kernel |
| `GEMINI.md` | Create Mirror | Context Blend & Tool Mapping | Gemini CLI mirror with tool mappings |
| `.github/copilot-instructions.md` | Create Mirror | Context Blend & Header | Copilot CLI instructions header |
| `AGENTS.md` | Create Mirror | Context Blend | Cross-platform agent instructions |
| `wiki/` | Create | Create Index | Layer 2 Confirmed Knowledge Base |
| `references/map-debt.md` | Create | Create Ledger | Tier 3 Map Debt Tracking |
| `plugins/*/references/evolution-log.md` | Scaffold Stubs | Scaffold Missing Stubs | Per-plugin Layer 2 Evolution Log for local plugins |
| `context/control_plane.db` | Initialize (WAL) | Verify Schema | SQLite task DAG & receipt control plane |
| `.git/hooks/pre-commit-evolution-guard` | Install | Install / Enable | Deterministic pre-commit evolution & map-debt gate |
| `.github/workflows/verify-evolution-integrity.yml` | Install | Install / Enable | Deterministic GitHub Actions CI evolution & map-debt gate |
| `.agent/learning/traces/` | Create | Create Ledger | Layer 3 Evolution Trace Manifests |
| `audit-skill --fix` | N/A | Run on custom skills | Auto-upgrades legacy skills to boolean evals schema |
| `/os-health-check` | Run Gate | Run Gate | Post-init/retrofit deterministic verification of all substrates |


