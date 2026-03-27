# dependency-analysis

Maps relationships between Forms, generates dependency graphs, and retrieves direct/indirect dependency chains. Includes discovery mechanisms and dependency severity routing.

## Workflows

| Command | Purpose |
|---|---|
| `/dependency-analysis_retrieve-dependency-graph` | Generate or retrieve the full dependency network graph |
| `/dependency-analysis_investigate-direct-dependencies` | Extract immediate callers (Level 1) for rapid impact assessment |
| `/dependency-analysis_investigate-lineage` | Trace Form reachability from the application menu |

## Scripts

| Script | Purpose |
|---|---|
| `GenerateFormDependencyGraph.py` | Generate a dependency graph for a single Form |
| `BatchGenerateGraphs.py` | Batch-generate dependency graphs for all Forms |
| `generate_dependency_map.py` | Build the full dependency map JSON |
| `dependencies.py` | Core dependency resolution library |
| `run_all_form_dependencies.py` | Run dependency analysis across the entire Forms corpus |

## Severity Classification

| Level | Condition | Action |
|---|---|---|
| ORPHANED | 0 callers, 0 outbound calls | Safe to delete — execute implicitly |
| STANDARD | ≤ 5 callers, same module | Standard impact analysis — execute and report |
| CRITICAL | > 5 callers or cross-module | Stop — request explicit user consent |
| CIRCULAR | Mutual call path detected | Stop — flag as architectural risk |
