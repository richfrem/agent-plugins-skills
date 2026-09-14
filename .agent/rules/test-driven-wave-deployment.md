---
description: >
  The wave-by-wave test -> deploy -> retest discipline this plugin automates
  is this repository's own TDD rule applied to infrastructure provisioning,
  not a separate convention invented for SharePoint deployment.
globs:
  - "plugins/sharepoint-migration-planning/**/*"
---

# Rule: Test-Driven Wave Deployment

**This rule specializes `.agent/rules/test-driven-development.md` — read that rule first.** It is
not a competing convention; it is TDD's Red-Green-Refactor cycle applied to infrastructure
deployment instead of application code.

## The parallel, stated explicitly

| TDD (code) | Wave deployment (infrastructure) |
|---|---|
| Write a failing test first | Run the wave's validation script before deploying — it should fail (the objects don't exist yet) |
| Write the minimum code to pass | Deploy the wave's objects |
| Re-run the test, confirm green | Re-run the same validation script, confirm it now passes |
| Never trust a change without its test passing | Never treat a wave as done because the deploy script ran without error — the validation script passing is the actual gate |

## Why this matters for generated wave scripts

`generate-sharepoint-wave-scripts` produces a deploy script **and** must produce (or reference) a
matching validation step for every wave — a generated wave script with no way to independently
verify it worked is not a complete deliverable, the same way implementation code with no test is
not complete under this repository's TDD rule.

## Why one wave at a time, not "deploy everything"

A single script that runs every wave in sequence without a human confirming each stage's
validation first reintroduces exactly the risk TDD's discipline exists to prevent: a failure in an
early stage can be masked or compounded by later stages running anyway. The generated wave guide
must present waves as discrete, individually-gated steps — never as one script a human runs
unattended end-to-end.
