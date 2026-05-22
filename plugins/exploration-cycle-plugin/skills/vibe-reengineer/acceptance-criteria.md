# Acceptance Criteria: vibe-reengineer

## Correct Behaviors

- **Correct:** Vibe-reengineer drives the full 7-step surgical refactoring workflow in the designated order.
- **Correct:** Vibe-reengineer establishes `specs/REQS.md` as the single canonical contract before code extraction.
- **Correct:** Vibe-reengineer coordinates behavioral capture, domain extraction, visual audit, and progressive migrations.
- **Correct:** Vibe-reengineer validates 100% test completion with zero regressions at the end of the pipeline.

## Incorrect Behaviors

- **Incorrect:** Vibe-reengineer skips characterization testing or domain extraction and does a standard direct migration of legacy files.
- **Incorrect:** Vibe-reengineer lets files in Domain or Application import database/framework packages.
- **Incorrect:** Vibe-reengineer makes monolithic changes that break multiple parts of the application at once instead of slice-by-slice migrates.
