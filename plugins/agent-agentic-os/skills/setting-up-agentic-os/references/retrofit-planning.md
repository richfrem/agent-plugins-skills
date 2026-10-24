# Component Planning & Retrofit Matrix

What `scripts/init_agentic_os.py` does for each component in a fresh setup and in `--retrofit` mode, during the `init` mode of the running-control-plane skill. `AGENTS.md` is the single canonical instruction file; `CLAUDE.md` is at most a pointer to it, and no other tool-specific instruction file is created.

| Component | Fresh init | Retrofit mode | Purpose |
|---|---|---|---|
| `AGENTS.md` | Create from the project template | Merge missing Agentic OS sections, preserve local content | Canonical project instructions, including the intake trigger for the running-control-plane skill |
| `CLAUDE.md` | Optional pointer to `AGENTS.md` | Keep a pointer; leave a non-pointer file untouched and report it | Compatibility stub only |
| `GEMINI.md`, `.github/copilot-instructions.md`, `CLAUDE.local.md` | Not created | Preserved if present; never rewritten | Legacy copies are left for the owner to reconcile |
| `architecture.md` | Create initial layout | Context review and enrich | High-level system architecture |
| `.agent/rules/` | Sync ecosystem rules when a rule source is found | Reconcile, preserving downstream custom sections | Workspace constraints linked from `AGENTS.md` |
| `wiki/` | Create | Create index | Layer 2 confirmed knowledge base |
| `map-debt.md` ledger (repository `references/` folder) | Create | Create ledger | Tier 3 map debt tracking |
| `evolution-log.md` per local plugin (its `references/` folder) | Scaffold stubs | Scaffold missing stubs | Layer 2 evolution log for local plugins |
| `context/` (soul, user, memory, events, locks) | Create | Fill what is missing | Layer 1 session state and the event bus (`kernel.py`) |
| `context/control_plane.db` | Initialize (WAL) | Verify schema | SQLite task DAG and receipt store |
| `.git/hooks/pre-commit-pipeline-guard`, `pre-push-review-guard` | Install and wire (unless the declared mode is `disabled`) | Same | Commit and push gates for the control plane |
| `.git/hooks/pre-commit-evolution-guard` | Install | Install or enable | Map-debt and evolution-log discipline gate |
| `.github/workflows/verify-evolution-integrity.yml` | Install | Install or enable | CI copy of the evolution gate |
| `.agent/learning/traces/` | Create | Create | Layer 3 evolution trace manifests |
| Custom skills | N/A | Audit with the `authoring-skills` skill's `audit_skill.py --fix` when it is installed | Upgrade legacy skills to the boolean evals schema |
| Health check | Run | Run | Post-init verification of all substrates (the `health` mode) |
