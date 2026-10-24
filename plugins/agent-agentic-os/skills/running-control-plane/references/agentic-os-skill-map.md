# Agentic OS Skill Map

Read this before routing to, recommending, or handing off to an `agent-agentic-os` skill. The plugin
ships two skills; each is a router whose modes were separate skills before the consolidation.

Verify the skill is installed in your active runtime harness (via `apm list` or your client's installed skills directory) before relying on it.

## Contents

- [The two skills](#the-two-skills)
- [How they relate](#how-they-relate)
- [Where the old skills went](#where-the-old-skills-went)

## The two skills

| Skill | Job | Modes |
|---|---|---|
| `running-control-plane` | Run engineering tasks under signed human gates, set up and check the substrate, switch gating on or off | `intake`, `init`, `mode`, `health`, `signing-setup`, `simulator`, `worktree` |
| `improving-skills-in-lab` | Plan, run, score, log and backport experiments that improve skills and agents | `plan`, `setup`, `loop`, `score`, `log`, `backport`, `memory` |

## How they relate

`running-control-plane` stands alone: it is a general task pipeline and does not depend on the lab.
Its state is `context/control_plane.db`; its authority is the human's SSH signature at the three
gates (APPROVED, VERIFY_EXIT, DONE).

The links run one way, from the lab to the control plane:

- When the lab updates or creates a skill, it registers that work as a control-plane task
  (`agent_control.py`, task type `EVOLUTION`) and logs a prior-art scan, so lab changes pass the
  same gates.
- The evolution cycle (`evolution_state.py`) runs the lab's locked evaluator
  (`evaluate.py --decision-only`), so a repository that uses evolution cycles needs
  `improving-skills-in-lab` installed too.
- The lab calls the installed `context/kernel.py` for the event bus and locks; it does not carry a copy.

## Where the old skills went

| Old skill | Now |
|---|---|
| the `intake` mode, `-init`, `-mode`, `-health`, `-signing-setup`, `-simulator`, `-worktree` and the `init` interview | the same-named mode of `running-control-plane` (`references/<mode>/workflow.md`) |
| the `plan` mode of `improving-skills-in-lab`, `-setup`, `-loop`, `-scorer`, `-log`, `-backport`, `-memory` and the interview | `plan`, `setup`, `loop`, `score`, `log`, `backport`, `memory` modes of `improving-skills-in-lab` |

See also `two-improvement-paths` in the `improving-skills-in-lab` skill for the two ways to improve a skill.
