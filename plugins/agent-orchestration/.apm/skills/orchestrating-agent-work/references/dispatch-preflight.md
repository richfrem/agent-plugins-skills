# Dispatch preflight and completion discipline

Observed in a four-worker batch (Sanctuary MISSION-052). Each rule says where it is enforced; scripts are in `scripts/dispatch_guard.py`.

| Failure | Rule | Enforced by |
|---|---|---|
| Worker returned a partial slice and it was treated as done | Done = the assigned OUTCOME (for experiments: a verdict or a recorded "cannot decide"), not worker return. Redispatch defects. | acceptance-criteria.md; judgment |
| Independent review waited for all workers | Review each ready delivery while other independent work keeps running. | judgment (schedule it explicitly) |
| Cloud arm idled behind a congested local resource | Start independent arms at once; schedule the shared resource explicitly and record its effect on validity. | judgment |
| Duplicate execution detected only afterward | Claim the unit before launch; a failed claim means do not launch. | `dispatch_guard.py claim` |
| Worker lacked a required executable | Check in the worker's own environment (its PATH and sandbox), before dispatch. | `dispatch_guard.py exec-check --path <worker PATH>` run by the worker or its wrapper |
| Hundreds of calls ran with hooks, memory and CLAUDE.md loaded | Verify the call context from the CLI's init event before any large run; refuse a contaminated invocation; record what is unobservable. Do not pool contaminated and clean outputs. | `dispatch_guard.py context-check` on a stream-json probe |
| Progress counted log rows | Report unique planned/completed/malformed/duplicate/missing units. Malformed answers stay in the denominator. | `dispatch_guard.py reconcile` |
| Permission asked again inside a standing authorization | Quote the authorization and act within its scope; ask only for new scope or a real blocker. | judgment |
| Telemetry showed zero errors or corrections despite observed ones | Report a telemetry gap; never treat missing as zero. | judgment; Sanctuary `eval_gate.py invest` |

A held lock or shared resource is announced to the affected worker before it is held. Give each execution unit one owner.
