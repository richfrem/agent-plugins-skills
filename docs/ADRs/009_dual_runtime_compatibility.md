# ADR-009: Dual-Runtime Compatibility — Portable Plugins, Optional Orchestration

**Status:** Accepted  
**Date:** 2026-05-30

## Decision

All plugin components must remain consumable by **any LLM CLI runtime** (Claude Code,
Gemini CLI, Cursor, or any shell-based agent) without modification:

1. **Agent `.md` files** are the portable interface definition. They contain agent
   identity, instructions, and domain vocabulary. They are never rewritten into
   framework-specific formats.

2. **`state_engine.py` and `sandbox_runner.py`** are standalone Python scripts using
   stdlib only. They expose both:
   - A Python import interface (for `dispatch.py` and future MAF middleware)
   - A CLI interface via argparse (for any shell-based agent runtime)

3. **MAF integration is optional.** If adopted, MAF agents load `.md` files via
   `Agent(instructions=Path(...).read_text())` and call `state_engine`/`sandbox_runner`
   via Python import. MAF does not replace these files.

## Consequences

- No framework-specific imports (MAF, LangChain, CrewAI) in `state_engine.py` or
  `sandbox_runner.py`. These remain stdlib-only.
- The `if __name__ == "__main__":` CLI block in `state_engine.py` must be maintained
  as any shell-based agent runtime can call it via subprocess.
- `SKILL.md` files continue to contain orchestration instructions readable by any LLM.
  The database enforces the rules; the SKILL.md explains them to the model.

## MAF Adapter Surface (Future Reference)

| Local Primitive | MAF Extension Point | Adapter Pattern |
|---|---|---|
| Agent `.md` file | `Agent(instructions=...)` | `Path.read_text()` |
| `state_engine.commit_task_complete` | `TDDComplianceMiddleware` | `.Use()` middleware |
| `sandbox_runner.run_hygienic` | `WorktreeIsolationExecutor` | Custom executor |
| `dispatch.check_approval` | `GovernancePolicyMiddleware` | AGT integration |
| `state_engine.project_dashboard` | `AIContextProvider` | Pre-call context injection |
