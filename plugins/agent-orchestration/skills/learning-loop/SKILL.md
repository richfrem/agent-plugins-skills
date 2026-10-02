---
name: learning-loop
plugin: agent-orchestration
description: "(Industry standard: Loop Agent / Single Agent) Self-directed research and cognitive continuity loop across Orientation, Synthesis, Strategic Gate, and Completion."
allowed-tools: Bash, Read, Write
---

## Dependencies

Requires Python 3.8+ (standard library only).

---

# Learning Loop (`learning-loop`)

Cognitive continuity protocol ensuring knowledge survives across isolated agent sessions.

## Contents

- [Dependencies](#dependencies)
- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Anti-simulation rule**: Never describe what you "would do" or mark steps complete without executing them.
- **Mandatory closure**: Full closure sequence must be performed upon session completion.
- **Prerequisite context**: Always establish valid session context upon Wakeup before modifying code.

## Quick start

```bash
# Initialize learning loop session and load orientation context
python3 -c "import sys; print('Learning loop initialized across Orientation -> Synthesis -> Gate')"
```

## Workflow

```
Orientation -> Synthesis -> Strategic Gate -> Red Team Audit -> [Execution] -> Completion
```

1. **Phase I (Orientation)**: Read local primers, load session state, verify readiness.
2. **Phase II (Synthesis)**: Conduct research and record modular findings in memory/wiki.
3. **Phase III (Strategic Gate)**: Present findings to human; require explicit approval to proceed.
4. **Phase IV (Red Team Audit)**: Submit research packet to adversarial review before execution.
5. **Phase V (Execution & Completion)**: Single Loop (solo implementation) or Dual Loop (delegation); log retrospective.

## Verification

```bash
# Verify session completion and check retrospective entry
test -f references/phases.md && echo "Phase contracts valid"
git status --short
```

## References

- [phases.md](references/phases.md) — Exhaustive phase breakdown and exit criteria.
- [self-correction.md](references/self-correction.md) — Backtracking and correction protocol.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Verification gate criteria.
- [fallback-tree.md](references/fallback-tree.md) — Escalation paths for research stalls.
