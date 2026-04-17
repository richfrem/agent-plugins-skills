---
concept: continuous-skill-optimizer-protocol-reference
source: plugin-code
source_file: agent-scaffolders/references/skill-optimizer-architecture.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.343183+00:00
cluster: plugin-code
content_hash: dab05f1e09985ee1
---

# continuous-skill-optimizer Protocol Reference

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# continuous-skill-optimizer Protocol Reference

This skill operationalizes the autoresearch pattern for skill optimization:

- Single target artifact focus (`./SKILL.md` description by default).
- Fixed iteration budget.
- Keep/discard gate after each eval pass.
- Crash/timeout discipline with rollback to last known good.
- Persistent experiment ledger for auditability.

Execution engine:
- Evaluates trigger behavior via `../../../scripts/benchmarking/run_eval.py`.
- Proposes improvements via `improve_description.py` using either Claude or Copilot backend.
- Orchestrates loop via `run_loop.py`.


## See Also

- [[optimizer-engine-patterns-reference-design]]
- [[optimizer-engine-patterns-reference-design]]
- [[skill-continuous-improvement-red-green-refactor]]
- [[skill-optimizer]]
- [[optimizer-engine-patterns-reference-design]]
- [[optimizer-engine-patterns-reference-design]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/references/skill-optimizer-architecture.md`
- **Indexed:** 2026-04-17T06:42:09.343183+00:00
