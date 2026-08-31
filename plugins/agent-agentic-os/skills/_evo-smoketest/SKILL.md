---
name: _evo-smoketest
description: Converts temperatures between Celsius and Fahrenheit for the evolution end-to-end smoke test harness.
version: 0.1.0
---

# _evo-smoketest

A disposable fixture skill used only by the evolution end-to-end acceptance suite. It exists to give
a real self-evolution cycle a controlled, reproducible routing gap to triage, fix (E2E-PASS), or fail
three times (E2E-ROLLBACK). Do not deploy or depend on this skill in production.

## Purpose

Provide deterministic temperature-unit conversions so the router has a concrete capability to score
against `evals/evals.json`.

## When to use

Use this skill when the user asks to convert a temperature between Celsius and Fahrenheit.

## Deliberate baseline gap (do not remove without updating evals)

The description above intentionally names only Celsius and Fahrenheit. `evals/evals.json` contains one
`should_trigger: true` case about a Kelvin conversion. Because the description omits Kelvin, the
routing evaluator will MISS that case at baseline, producing a measurable sub-100% score.

- E2E-PASS: the evolution cycle closes the gap by broadening the `description` and `When to use`
  section to include Kelvin (K = C + 273.15), which flips the failing eval case to green
  (`evaluate.py --decision-only` exit 0).
- E2E-ROLLBACK: an intentionally wrong "fix" that does NOT add Kelvin fails the verifier three
  times, forcing the controller into ROLLBACK.

## Procedure

1. Identify the source unit, target unit, and numeric value in the request.
2. Apply the conversion:
   - Celsius to Fahrenheit: `F = C * 9/5 + 32`
   - Fahrenheit to Celsius: `C = (F - 32) * 5/9`
3. Return the converted value rounded to one decimal place.
