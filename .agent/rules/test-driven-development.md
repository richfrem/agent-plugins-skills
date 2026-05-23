---
description: >
  Enforce Test-Driven Development for all new code in this project.
  No implementation code is written before a failing test exists.
  The superpowers TDD skill MUST be invoked before writing any feature,
  bugfix, or script. Tests live in the canonical tier locations defined
  in the test suite vision spec.
globs:
  - "investment_screener/backend/py_services/*.py"
  - "investment_screener/backend/src/**/*.ts"
  - "investment_screener/frontend/src/**/*.tsx"
  - "plugins/**/scripts/*.py"
  - "plugins/**/node/**/*.js"
---

# Rule: Test-Driven Development — Tests Before Code

## Why This Rule Exists

A silent import bug (`validate_weights` missing from `py_services/`) was introduced
when `helpers.ts` was refactored to call `portfolio_action.py` via `bridge.ts`.
A one-line unit test for `getPythonActions()` would have caught it in under a minute.
Instead it was discovered during an unrelated session, after the code had already
been committed.

**Tests written after code only verify what you remember to check.
Tests written before code verify what you actually require.**

---

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.
```

This applies to:
- New Python services in `py_services/`
- New Express routes and middleware
- New TradingView CDP automation functions in `node/core/trading.js`
- New plugin scripts in `plugins/*/scripts/`
- Bug fixes to any of the above

It does NOT apply to:
- Throwaway exploration/prototyping (throw the prototype away before implementing)
- Configuration files and JSON data files
- Generated boilerplate (migration files, etc.)
- SKILL.md files and agent prompts (untestable by nature)

---

## Mandatory Pre-Implementation Step

**Before writing any implementation code**, invoke the superpowers TDD skill:

```
Skill: superpowers:test-driven-development
```

This is not optional. The skill enforces the Red-Green-Refactor cycle and blocks
the rationalization patterns ("too simple to test", "I'll test after", etc.) that
always lead to untested, broken code.

If you find yourself writing implementation before invoking this skill, stop.
The code you wrote is invalid. Delete it and start over.

---

## Test Tier Locations

When writing tests, place them in the correct tier:

| What you're building | Test location | Test file naming |
|---|---|---|
| Python service in `py_services/` | `investment_screener/backend/tests/py_services/` | `test_<script_name>.py` |
| Express route in `src/routes/` | `investment_screener/backend/tests/api/` | `test_<route_name>_routes.py` |
| TradingView CDP function in `trading.js` | `plugins/tradingview/tests/` | `tv_test_harness.py` (Section 0–5) |
| Plugin script in `plugins/*/scripts/` | `plugins/<plugin>/tests/` | `test_<script_name>.py` |
| React component | `investment_screener/frontend/tests/` | `<ComponentName>.spec.ts` |

**Reference:** `docs/superpowers/specs/2026-05-17-test-suite-vision-design.md`

---

## What a Passing Test Looks Like Here

### Python service (pure function)
```python
# WRITE THIS FIRST — watch it fail
def test_derive_action_exit_with_ai_override():
    result = derive_action("NVDA", current_pct=5.0, target_pct=0.0, ai_upside=15.0)
    assert result == "REVIEW"  # AI conflict overrides EXIT

# THEN write the implementation in portfolio_action.py
```

### Python service (CLI arg validation — no TV required)
```python
# WRITE THIS FIRST
def test_place_order_cancel_requires_order_id():
    result = subprocess.run(
        ["python3", PLACE_ORDER_PY, "--cancel"],
        capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "--order-id is required" in result.stderr
```

### TradingView CDP function
```python
# WRITE THIS FIRST in tv_test_harness.py Section 5
def test_5_1_cancel_nonexistent_order():
    result = cancel_order(order_id="00000000-0000-0000-0000-000000000000")
    assert result["cancelled"] is False
    # THEN implement the error path in trading.js
```

### Express route (backend must be running)
```python
# WRITE THIS FIRST
def test_preflight_blocked_when_tv_offline():
    r = requests.post(f"{BASE}/api/trading/preflight", json={
        "ticker": "AAPL", "action": "buy", "shares": 1,
        "orderType": "market", "account": "tfsa"
    })
    assert r.status_code == 422
    assert r.json()["state"] == "PREFLIGHT_BLOCKED"
```

---

## What Counts as a Valid Failing Test

A test only satisfies the TDD requirement if — **before** any implementation is written:
1. The test executes without syntax error
2. The test **fails** for the expected reason
3. The failure **proves** the feature or bugfix does not yet exist

**Invalid examples — these do NOT satisfy TDD:**

```python
assert True  # trivial — proves nothing
```
```python
with pytest.raises(Exception): ...  # too broad — doesn't verify failure reason
```
```python
mock_fn.return_value = expected_value
assert mock_fn() == expected_value  # tests the mock, not the real path
```
```python
@pytest.mark.skip  # skipped test — not a failing test
pass
```

**For bug fixes:** The failing test must reproduce the original bug before the fix is applied. If the test passes before you change anything, it is not a valid TDD cycle.

---

## Test Categories — Different Standards Apply

### Category A — Pure deterministic tests
Fast, isolated, no I/O (e.g., `derive_action()`, valuation math, ticker normalization).
- Exhaustive branch coverage + edge cases
- Mocking acceptable
- No network, no broker

### Category B — Runtime integration tests
Real subprocess execution, real files, real CLI (e.g., `portfolio_action.py`, `place_order.py`, `extractJson()`, Express route transitions).
- **Subprocess-first** — do not mock the execution path
- Real stdout/stderr parsing with real fixture files
- See "Critical Runtime Paths" section below

### Category C — Live broker automation tests
TradingView/Questrade automation that places real orders.
- Explicit `--live --i-understand-live-broker-test` opt-in required
- Orphan cleanup ledger required before any order attempt
- Safe-price enforcement (≤ min($1.00, 1% of market price))
- CRITICAL severity gate — suite aborts if any CRITICAL fails first
- Never market orders in tests

---

## Critical Runtime Paths — No Mocking Allowed

These paths must be tested with **real subprocess execution and real file resolution** in Category B tests:

- `spawnPythonScript()` in `bridge.ts`
- `portfolio_action.py` (via subprocess, from `py_services/` path)
- `place_order.py` (via subprocess, each mode independently)
- `tv_cancel_order.py`, `tv_modify_order.py`, `tv_get_orders.py`
- `extractJson()` in `trading.ts` (with captured real stdout fixtures)
- `sys.path` bootstrap logic and `Path(__file__).resolve()` path resolution

**Do NOT mock these in the primary integration test:**
```python
# FORBIDDEN for Category B tests:
mock_subprocess_run.return_value = ...
mock_spawn_python_script.return_value = ...
mock_os_path_exists.return_value = True
```

**Reason:** The original `portfolio_action.py` production bug was caused by runtime path resolution through subprocess. Mocking these layers would have hidden the bug entirely.

---

## Anti-Patterns — Stop and Start Over

These patterns break TDD and will introduce bugs:

| Pattern | What it produces |
|---|---|
| Writing the function, then writing a test that calls it | Tests that only verify what you built, not what's required |
| Adding `sys.path` manipulation without a test that imports the module | Silent import failures in production (the exact bug this rule exists to prevent) |
| Refactoring a bridge/helper without a test that calls it end-to-end | Path bugs invisible until runtime |
| Testing only the happy path | Missed error handling, bad argument handling |
| Testing via the Express API when the Python function is the real unit | Slow tests that hide where the failure is |
| Testing internal implementation details instead of observable behavior | Brittle tests that fail on refactor but miss real regressions |

**Observable behavior is the contract.** Test exit codes, API response fields, JSON output shape, and state transitions — not internal flags, private fields, or cache internals.

Bad: `assert helper._cache["x"] == value`  
Good: `assert response.json()["state"] == "PREFLIGHT_PASSED"`

**Full anti-pattern reference:** `superpowers:test-driven-development` → `testing-anti-patterns.md`

---

## Mutation Safety Rule

Any change touching these areas **must** include a regression test that reproduces the pre-change behavior AND an assertion for the new expected behavior:

- Order execution path (preflight → execute → submit)
- Valuation calculations or DCF thresholds
- Portfolio action classification (ACCUMULATE/TRIM/EXIT bands)
- Broker automation (TradingView CDP)
- State machine transitions in `trading.ts`
- Stale-data gates (freshness checks, exit code 4)

No existing CRITICAL-path test coverage may be reduced by a mutation. If you need to refactor a test, the refactored version must cover at least the same cases.

---

## Prefer Replay Fixtures Over Synthetic Mocks

When capturing external behavior for tests, prefer **recorded real output** over fabricated mocks:

- Captured `place_order.py` stdout (all modes)
- Captured TradingView DOM snippets
- Captured API responses
- Captured projection JSON files
- Captured audit log entries

Store in `tests/fixtures/stdout_samples/` or appropriate fixture directory. Real captures preserve formatting quirks and edge cases that synthetic mocks routinely miss.

---

## Red Flags — Stop Immediately

These thoughts mean you are rationalizing. Stop and invoke the TDD skill.

- "This is just a quick script, tests would be overkill"
- "I'll add tests after I see if this approach works"
- "I manually ran it and it worked"
- "It's just a path change, nothing could break"
- "The test is too hard to write before I know the interface"

The last one especially: if you don't know the interface, write the test that describes
the interface you want. That IS the design.

---

## Minimum Test Coverage Per Code Type

| Code type | Minimum tests required before merge |
|---|---|
| Pure Python function (no I/O) | All branches + error inputs |
| Python CLI script | Valid args → expected exit code; missing required args → non-zero exit |
| Express route (GET) | 200 happy path; 404 for unknown resource |
| Express route (POST) | 400 for missing required fields; expected state on success |
| New CDP function in trading.js | Section in `tv_test_harness.py` (at minimum dry-run) |
| New plugin script | Smoke test: valid input → valid JSON output |

---

## Related Rules and References

- `.agent/rules/no-inline-python.md` — extraction policy for scripts (complement: if it's worth extracting, it's worth testing)
- `.agent/rules/coding-conventions.md` — file headers and docstrings that make tests easier to write
- `docs/superpowers/specs/2026-05-17-test-suite-vision-design.md` — full test suite vision (Tier 1–5)
- `docs/adrs/023-tradingview-test-harness.md` — TV harness design decisions
- `docs/adrs/010-testing-approach.md` — original testing ADR (pre broker-automation)
- `superpowers:test-driven-development` skill — invoke BEFORE writing any implementation
