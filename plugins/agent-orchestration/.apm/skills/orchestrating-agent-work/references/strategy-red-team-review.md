# Strategy: red-team-review (adversarial review loop)

Orchestrated adversarial review loop pairing iterative plan/code generation with independent critique personas (Architecture Skeptic, Security Auditor, TDD Contract Reviewer) until an "Approved" verdict is earned.

## Critical Constraints
1. **Fan-Out Trio Invariant**: Multi-persona reviews must dispatch to all 3 Graph Planning roles: Architecture Skeptic (`architect-review`), Security / Edge-Case Auditor (`security-auditor`), and TDD Contract Reviewer (`tdd-contract-reviewer`).
2. **Directory Isolation**: Save review packets and critique outputs to isolated directories (e.g. `.history/review-iteration-1/`) so baseline artifacts are never destructively overwritten.
3. **Convergence Limit**: If 2-3 rounds pass without approval, stop looping and escalate outstanding disagreements to human/orchestrator tie-breaker.
4. **Non-Interactive Input Redirection**: Always append `< /dev/null` to headless CLI commands to prevent `SIGTTIN` hangs.

## Quick start

```bash
# Bundle context with the bundling-context skill (dev-utils)
python3 plugins/dev-utils/skills/bundling-context/scripts/bundle.py --manifest manifest.json --bundle temp/review/bundle.md
```

## Workflow

1. **Research & Packet Generation**: Draft `red-team-prompt.md`, prepare `manifest.json`, and run `bundling-context` in Multi-Persona Fan-Out Mode to generate persona packets.
2. **Select Backend**: Interactively confirm CLI backend (`agy`, `claude`, `copilot`, `codex`) and model tier with user.
3. **Parallel Dispatch**: Dispatch review bundles in parallel to designated persona reviewers.
4. **Synthesize Feedback**: Capture verdicts. If "More Research Needed", iterate with targeted questions. If consensus is reached, advance.
5. **Handoff**: On approval, terminate review loop and pass approved artifacts back to parent orchestrator.

## Verification

```bash
# Execute project unit tests to verify no regressions were introduced
pytest tests/ -k "not test_health_check_signing_status"
```
