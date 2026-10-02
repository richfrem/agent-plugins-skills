---
name: vibe-behavioral-test-capture
description: Builds an executable safety net of characterization tests by integrating browser flow recording, API payload snapshotting, DOM state captures, network traces, and mock fixture generation.
---

# Behavioral Test Capture (vibe-behavioral-test-capture)

Constructs an executable, deterministic behavioral safety net (characterization tests) around running prototypes.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Zero absolute paths: Scrub `/Users/`, `/home/`, real tokens, and machine IPs from fixtures.
- Preserve legacy behavior verbatim; never "fix" bugs inside characterization test assertions.
- Deterministic execution: Tests must load fixtures locally with zero live external network calls.

## Quick start
1. Identify interactive endpoints and state transitions from `DISCOVERY_REPORT.md`.
2. Dispatch telemetry recording to capture raw requests and UI states into static JSON fixtures.
3. Synthesize and execute characterization test suite under `tests/characterization/`.

## Workflow
1. **Flow Discovery**: Map out interactive endpoints, form submissions, and state mutations from the prototype.
2. **Telemetry Dispatch**: Trigger `runtime-observer` to record runtime traffic into `tests/characterization/fixtures/<slice-name>/`.
3. **Test Synthesis**: Generate characterization test specifications loading recorded local fixtures.
4. **Validation**: Execute test suite against original prototype, asserting exact legacy behavior.

## Verification
- Run characterization tests: confirm suite passes deterministically offline.
- Verify fixtures contain no unredacted environment variables, tokens, or absolute paths.
- Ensure test assertions match verbatim prototype responses.

## References
- [acceptance-criteria.md](references/acceptance-criteria.md)
