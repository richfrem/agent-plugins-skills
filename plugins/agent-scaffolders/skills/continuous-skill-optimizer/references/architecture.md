# continuous-skill-optimizer Protocol Reference

This skill operationalizes the autoresearch pattern for skill optimization:

- Single target artifact focus (`SKILL.md` description by default).
- Fixed iteration budget.
- Keep/discard gate after each eval pass.
- Crash/timeout discipline with rollback to last known good.
- Persistent experiment ledger for auditability.

Execution engine:
- Evaluates trigger behavior via `plugins/agent-scaffolders/scripts/benchmarking/run_eval.py`.
- Proposes improvements via `improve_description.py` using either Claude or Copilot backend.
- Orchestrates loop via `run_loop.py`.
