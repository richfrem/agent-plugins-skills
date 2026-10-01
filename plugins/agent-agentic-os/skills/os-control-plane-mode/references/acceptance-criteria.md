# Acceptance Criteria - os-control-plane-mode

The skill is working when all of these hold. Each is covered by `tests/test_control_plane_mode*.py`,
`tests/test_control_plane_hooks.py` and `tests/test_init_respects_control_plane_mode.py`.

## Behaviour

1. `status` reports the declared mode, every manifest member (declared vs installed), each guard
   (script present, executable, wired, stale), and exits `0` only when the repo matches the mode.
2. Nothing changes without `--yes`. `--dry-run` prints the plan and changes nothing.
3. `disable` ends with the mode `disabled`, both guards unwired (scripts kept), every member
   `should_install: false` and absent from disk, and `status` consistent.
4. `enable` ends with the mode `enabled`, members installed, guards installed and wired, and
   `status` consistent.
5. A repeated toggle in the same mode is a no-op; a toggle in the same mode on a drifted repo
   reconciles it.
6. `disable` then `enable` returns the ownership file byte-for-byte (formatting preserved).

## Safety

7. `context/control_plane.db` is never modified, moved or deleted.
8. Only the manifest members and the two control-plane guards are touched. `os-init`,
   `os-health-check`, the Claude Code plugin hooks, the evolution guard and custom hook content
   survive both directions.
9. Gates are never on while the machinery is missing: `enable` declares the mode last and does not
   declare it when the sync fails; `disable` declares the mode first.
10. A dispatcher hook in a shape the tool does not recognise is reported and left untouched.
11. A manifest member missing from the ownership file aborts before any change.
12. Ownership file, mode file and hooks are backed up before a change, and each toggle is logged.

## Integration

13. The guards exit 0 with a visible note when the mode is `disabled`, still gate when it is
    `enabled` or absent, and never treat an unrecognised value as `disabled`.
14. `init_agentic_os.py` does not install or wire the control-plane guards when the mode is
    `disabled`, still installs the evolution guard, and behaves exactly as before otherwise.
15. A component that mentions the control plane but is not classified in the manifest fails the
    test suite.
