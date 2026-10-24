# Acceptance Criteria: running-control-plane

Merged verbatim from the retired skills; one section per mode. Headings inside a section are one level deeper than in the original.

## Contents

- [Mode: intake](#mode-intake)
- [Mode: mode](#mode-mode)
- [Mode: health](#mode-health)
- [Mode: simulator](#mode-simulator)

## Mode: intake

1. Socratic defaulting protocol with 1-3 questions.
2. Session-aware native intake deferral.
3. 4-Pillar spec compilation.

## Mode: mode

The mode workflow is done when all of these hold. They are enforced by `tests/test_control_plane_mode.py` and `tests/test_control_plane_mode_guards.py`, which run the script from a copy deployed like an APM install (`.claude/skills/running-control-plane/scripts`).

1. `status` reports the declared mode (a missing file means `enabled`), each guard's state (script present and executable, wired, stale) and exits 0 only when consistent.
2. `--dry-run` prints the plan and changes nothing; without `--yes` the script refuses (exit 2) and changes nothing.
3. `disable` declares `disabled` first, then unwires both guards; the guard scripts stay for a fast re-enable.
4. `enable` installs and wires both guards first, then declares `enabled`, so a gate is only on while its machinery exists.
5. Repeating a toggle in the same mode when consistent is a no-op; if the repo has drifted it reconciles.
6. `context/control_plane.db` and its task history are byte-for-byte unchanged by any toggle.
7. Custom dispatcher content and the independent evolution guard survive any toggle; a hand-edited dispatcher is left untouched and reported.
8. The installed skill folder is never modified by a toggle.
9. The mode file and dispatcher hooks are backed up under `context/control-plane-backup/<timestamp>/` before any change, and each change is logged with the actor in `context/control-plane-mode.log`.
10. A corrupt mode file is a reported problem, not silently treated as enabled.
11. The toggle works when targeted from a git worktree (it resolves to the main checkout).
12. The guards copied into `.git/hooks` are stamped with the real paths of the installed skill's `agent_control.py` and `verify_gate_evidence.py`, name no path that exists only in the source repository, and are reported stale when the stamp no longer matches.
13. Both guards pass with a visible note when the mode is `disabled`, still gate when it is `enabled` or missing, and never turn a gate off for an unrecognised value.

## Mode: health

### ✅ Scenarios that must trigger
- "Run a health check on the OS."
- "Check os metrics."
- "Run a system monitor check on the OS."
- "Is the event bus healthy? any stuck agents?"

### ❌ Scenarios that must NOT trigger
- "Clear stale locks from context/.locks" (handled by the kernel: `acquire_lock` clears stale locks)
- "Summarize what the agentic OS ecosystem does" (belongs to the Agentic OS skill map and two-paths reference docs, not this skill)

### Identity registration

- With the control plane enabled, the health check reports the human, simulation and isolation identities
  separately; an unregistered human identity is Tier 1 and is never fixed by the agent, an unregistered
  simulation identity is Tier 1 and agent-fixable via the `init` mode, and isolation not ready is a Tier 2 recommendation.
- With the control plane disabled, the three identities are reported as informational with no finding.
- The command it names exists in the repository's layout (never a path that only exists in the plugin source repo).

## Mode: simulator

### Positive scenarios

- Runs a deterministic simulation for one requested transition.
- Grades approval, guidance summary, required questions, target state, and commit authorization.
- Reports evidence for each criterion and stops after three failed attempts.
- Does not weaken grading criteria to hide a failed transition.

### Negative scenarios

- Rejects an unknown transition instead of silently testing a different edge.
- Does not run the full regression suite unless `--all` is explicitly requested.
- Escalates after the third failed attempt rather than retrying indefinitely.
