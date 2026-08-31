---
name: evo-smoketest
description: Converts temperatures between Celsius, Fahrenheit, and Kelvin (K = C + 273.15) for the evolution end-to-end smoke test harness.
version: 0.2.0
---

# evo-smoketest

A disposable fixture skill used only by the evolution end-to-end acceptance suite.

## Purpose

Provide deterministic temperature-unit conversions so the router has a concrete capability to score
against `evals/evals.json`.

## When to use

Use this skill when the user asks to convert a temperature between Celsius, Fahrenheit, or Kelvin.

## Procedure

1. Identify the source unit, target unit, and numeric value in the request.
2. Apply the conversion:
   - Celsius to Fahrenheit: `F = C * 9/5 + 32`
   - Fahrenheit to Celsius: `C = (F - 32) * 5/9`
   - Kelvin to Celsius: `C = K - 273.15`
3. Return the converted value rounded to one decimal place.
