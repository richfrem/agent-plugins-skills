---
trigger: always_on
description: Enforces test-driven methodologies for both code development and orchestration workflows.
---

# Rule: Test-Driven Work (TDW) — Tests & Contracts Before Execution

## Why This Rule Exists

A silent logic, path resolution, or orchestration contract bug is easily introduced during development or refactoring. Verification contracts written before execution force clarity of intent, define clear success boundaries, and catch bugs before any work is committed.

**Verification contracts written after the work only verify what you remember to check.  
Verification contracts written before the work verify what you actually require.**

---

## The Iron Law

```
NO CODE DEVELOPMENT OR ORCHESTRATION EXECUTION WITHOUT A FAILING TEST OR SUCCESS CONTRACT FIRST.
```

This applies to:
- **Code Development (TDD)**: New service modules, functions, API routes, automation scripts, and bug fixes to any of these.
- **Orchestration & Workflows (TDW/TDO)**: New prompt templates, agent tool execution paths, coordinator scripts, workflow engines, and task runners.

It does NOT apply to:
- Throwaway exploration or prototyping (which must be discarded before the actual implementation begins)
- Static, non-executable configuration files and JSON/YAML data files
- Automatically generated code (migration files, boilerplate, etc.)
- Declarative task checklists or static documents (unless executable)

---

## Mandatory Pre-Execution Step

**Before writing any implementation code or executing any new orchestration flow**, establish the verification contract:

1. **For Code**: Write a failing unit or integration test first.
2. **For Orchestration**: Write a mock evaluation scenario, an assertions list, or an expected output schema validator first.
3. **Skill Tooling**: If the workspace contains a custom test-driven development skill or test runner (such as `superpowers:test-driven-development`), invoke it:
   ```
   Skill: superpowers:test-driven-development (if available)
   ```

This enforces the Red-Green-Refactor cycle and blocks the rationalization patterns ("too simple to test", "I'll do it after") that lead to broken systems. If you start the work before writing the contract, it is invalid. Delete it and start over.

---

## Test Tier Locations

Place tests in the correct tier directory designated for the project. Always locate the project's existing test structure (e.g. `tests/`, `test/`, `spec/`) first and follow its naming patterns. Typical default locations:

| What you're building | Test location | Test file naming |
|---|---|---|
| Pure business logic / services | `/tests/unit/` or `/test/` | `test_<module_name>.py` / `<ModuleName>.spec.ts` |
| API routes / Controllers | `/tests/integration/` or `/tests/api/` | `test_<route_name>_routes.py` / `<RouteName>.spec.ts` |
| UI components | `/tests/ui/` or `/tests/frontend/` | `<ComponentName>.spec.ts` |
| Script automation / CLI tools | `/tests/cli/` or `/tests/` | `test_<script_name>.py` |

---

## What a Passing Test Looks Like

### 1. Pure Function (Deterministic Unit Test)
```python
# WRITE THIS FIRST — watch it fail
def test_calculate_total_with_override():
    result = calculate_total(base_amount=100.0, tax_rate=0.05, discount=10.0)
    assert result == 95.0  # discount applied before tax

# THEN write the implementation in calculations.py
```

### 2. CLI Argument Validation (Integration Test)
```python
# WRITE THIS FIRST
def test_tool_requires_target_argument():
    result = subprocess.run(
        ["python3", "cli_tool.py", "--action", "sync"],
        capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "--target is required" in result.stderr
```

### 3. API Route Test (Backend Server)
```javascript
// WRITE THIS FIRST
describe('POST /api/payment/preflight', () => {
  it('should block transaction when balance is insufficient', async () => {
    const res = await request(app)
      .post('/api/payment/preflight')
      .send({ accountId: '123', amount: 1000.0 });
    expect(res.status).toBe(422);
    expect(res.body.state).toBe('INSUFFICIENT_FUNDS');
  });
});
```

---

## What Counts as a Valid Failing Test

A test only satisfies the TDD requirement if — **before** any implementation is written:
1. The test executes without syntax/runtime compilation errors.
2. The test **fails** for the expected reason (e.g., assertion error, missing function).
3. The failure **proves** the feature or bugfix does not yet exist.

**Invalid examples — these do NOT satisfy TDD:**
```python
assert True  # Trivial — proves nothing
```
```python
with pytest.raises(Exception): ...  # Too broad — does not verify the specific failure cause
```
```python
mock_fn.return_value = expected_value
assert mock_fn() == expected_value  # Tests the mock, not the actual code path
```
```python
@pytest.mark.skip  # Skipped test — does not prove a failure
pass
```

**For bug fixes:** The failing test must reproduce the original bug before the fix is applied. If the test passes before you change anything, it is not a valid TDD cycle.

---

## Critical Runtime Paths — No Mocking Allowed

Certain critical paths must be tested with **real subprocess execution, real file system resolution, and actual I/O** rather than synthetic mocks:

- Script execution wrappers and bridges (e.g., spawning helper scripts or subprocesses)
- File system path resolution logic and directory setup
- File readers and parsers handling external formats
- External API client boundaries

**Do NOT mock these in the primary integration test:**
```python
# FORBIDDEN for critical integration paths:
mock_subprocess_run.return_value = ...
mock_os_path_exists.return_value = True
mock_file_read.return_value = "fake file content"
```

**Reason:** Production bugs are frequently caused by runtime path resolution and formatting anomalies. Mocking these layers hides the bug entirely.

---

## Anti-Patterns — Stop and Start Over

| Pattern | What it produces |
|---|---|
| Writing the function first, then writing a test | Tests that only verify what you built, not what was required |
| Modifying paths or imports without verifying via an import test | Silent import and runtime load failures |
| Refactoring a bridge/helper without an end-to-end integration test | Invisible path or argument mismatch bugs |
| Testing only the happy path | Missed edge cases, poor error handling, and silent crashes |
| Testing via a heavy API when a unit test is more appropriate | Slow test suites that hide where the actual failure lies |
| Testing internal private methods instead of observable behavior | Brittle tests that break during refactoring without protecting against regression |

**Observable behavior is the contract.** Test exit codes, API response structures, JSON schemas, and state transitions—not internal flags, private variables, or cache internals.

---

## Mutation Safety Rule

Any change touching core business logic or security boundaries **must** include a regression test that reproduces the pre-change behavior AND an assertion for the new expected behavior. No existing critical-path test coverage may be reduced. If you refactor a test, the new version must cover at least the same cases.

---

## Prefer Replay Fixtures Over Synthetic Mocks

When capturing external behavior for tests, prefer **recorded real output** over fabricated mocks:
- Captured stdout/stderr logs from tools
- Raw API response payloads (saved as local JSON/YAML fixtures)
- Sample static files and databases

Real captures preserve formatting quirks, character encodings, and edge cases that synthetic mocks routinely miss.

---

## Red Flags — Stop Immediately

If you think any of the following, you are rationalizing. Stop and write the test first:
- *"This is just a quick script, tests would be overkill"*
- *"I'll add tests after I see if this approach works"*
- *"I manually ran it in my terminal and it worked"*
- *"It's just a path change, nothing could break"*
- *"The test is too hard to write before I know the interface"*

The last one especially: if you don't know the interface, write the test that describes **the interface you want**. That IS the design.

---

## Test-Driven Orchestration (TDO) & Prompt-Driven Work — Success Contracts First

For coordinator scripts, workflow engines, master orchestrators, agent prompts, and tool execution flows:
- **Define the Orchestration Contract First**: Before writing any coordination logic or sequencing scripts, write an integration test or schema assertion that verifies parameter propagation between sub-components, execution orders, and error bubbling.
- **Prompt & Output Schema Assertions**: When developing LLM prompts or templates, first define the exact output structure (e.g., JSON schema, markdown headings, or exact tone boundaries). Write validation checks (e.g., matching keys, non-empty outputs, schema compliance) before finalizing the prompt instruction.
- **Safety and Boundary Invariance**: Assert that critical safety boundaries (e.g., user confirmations, budget caps, authorization gates, and data privacy limits) cannot be bypassed by any code path, flag override, or exception handler in the orchestrator.
- **Runnable Integration Scenarios**: Every orchestrated workflow or skill must have a matching runnable evaluation scenario. Mock input fixtures must trigger the flow and verify that the output payload matches expectations in an offline or sandboxed environment.

---

## Related Rules and References

- `<project_root>/.agent/rules/no-inline-python.md` (or local script extraction policy) — extraction policy for scripts
- `<project_root>/.agent/rules/coding-conventions.md` (or local style guides) — coding conventions and documentation standards
- `<project_root>/docs/architecture/` (or project design docs) — system architecture details and design specifications
- `superpowers:test-driven-development` skill (if available) — invoke BEFORE writing any implementation