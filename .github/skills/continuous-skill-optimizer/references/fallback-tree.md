# Fallback Tree: continuous-skill-optimizer

## Primary Path
1. Run baseline eval.
2. Run iterative loop with selected engines/models.
3. Keep/discard/crash decisions recorded in ledger.

## Fallback A: Improvement backend auth failure
1. Verify backend auth (`copilot login` or equivalent).
2. Check token precedence conflicts (`GITHUB_TOKEN`, `GH_TOKEN`, `COPILOT_GITHUB_TOKEN`).
3. Re-run with env cleanup for command scope.

## Fallback B: Eval under-trigger across all positive prompts
1. Verify eval set quality (queries must clearly represent target intent).
2. Increase runs-per-query and reduce threshold ambiguity.
3. Add more intent-explicit positive prompts and near-miss negatives.

## Fallback C: No improvement after N iterations
1. Stop and preserve current best.
2. Export report and ledger.
3. Escalate to manual prompt redesign.
