# Implementation Task Ledger Contract

The implementation plan at `docs/plans/<task-id>-implementation-plan.md` must include:

```markdown
## Implementation Task Ledger
```json
[
  {
    "id": "task-1",
    "status": "COMPLETE",
    "artifacts": ["plugins/example/file.py"],
    "evidence": "pytest -q plugins/example/tests"
  }
]
```
```

The `VERIFY_EXIT -> RETROSPECTIVE` transition fails closed unless:

- the ledger exists and is valid JSON;
- it contains at least one task;
- every task is marked `COMPLETE`;
- every task has non-empty completion evidence; and
- every listed artifact exists beneath the repository or registered worktree root.

This is a completeness gate, not a claim that artifact existence alone proves semantic
correctness. Tests, reviews, and the exit-verification receipts remain required separately.
