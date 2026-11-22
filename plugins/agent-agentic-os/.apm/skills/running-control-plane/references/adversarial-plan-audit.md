# Adversarial Plan & Code Audit in the Control Plane

At `PLAN_REVIEW` (before Gate 1 `PLAN_REVIEW -> APPROVED`) and `WORKTREE_REVIEW` (before Gate 3 `WORKTREE_REVIEW -> VERIFY_EXIT`), the control plane uses `orchestrating-agent-work/scripts/plan_audit.py` and signed human decisions (`control_plane/signed_decisions.py`).

## Required Order (B17 / Q1 / Q2)

1. **Human signs the review preset** (or skip) in `signed_decisions` (`plan_review_preset` / `code_review_preset`). The control plane stamps `decided_at` using its own UTC clock.
2. **Build the isolated packet** with `plan_audit.py packet` (artifacts + target paths only).
3. **Run independent read-only reviewers** (host subagents with `tools: Read, Grep, Glob`, CLI reviewers, or external bundle) and record every round with `plan_audit.py record`.
4. **Verify convergence** with `plan_audit.py check --verdict docs/plans/work-tasks/<id>/<plan|code>-audit/verdict.json --artifact ... --not-before <decided_at>`. Any round recorded before the human's signed preset is refused.
5. **Bind the verdict hash in the gate snapshot**: `snapshot.py` includes `verdict` in the Gate 1 / Gate 3 content snapshot, so the human's SSH signature covers the exact reports shown.
6. **Human signs Gate 1 or Gate 3**.
