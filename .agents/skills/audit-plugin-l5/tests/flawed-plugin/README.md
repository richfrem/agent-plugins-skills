# Flawed Test Plugin

A deliberately broken plugin used for self-audit regression testing. The analyzer MUST detect the following issues.

## Expected Scanner Findings (deterministic — `inventory_plugin.py`)

These MUST appear in the `security_flags` or `issues` arrays when the scanner runs.

| Finding | Severity | File |
|---------|----------|------|
| Hardcoded credential (`sk-` pattern) | Critical | `scripts/bad_script.py` |
| Unauthorized network call (`import requests`) | Critical | `scripts/bad_script.py` |
| Unauthorized network call (`requests.post`) | Critical | `scripts/bad_script.py` |
| Access to raw environment variables (`os.environ`) | Warning | `scripts/bad_script.py` |
| Unauthorized network call (`curl`) | Critical | `scripts/danger.sh` |
| Bash script violation | Error | `scripts/danger.sh` |

**Expected counts**: security_flags ≥ 5, issues ≥ 1

## Expected LLM Findings (Phase 5 — agent analysis)

These are structural anti-patterns the scanner doesn't check. The LLM must flag them during Phase 5.

| Finding | Severity |
|---------|----------|
| Missing acceptance criteria for `flawed-skill` | Warning |
| Missing `references/` directory for `flawed-skill` | Warning |
| Missing README file tree (`├──` / `└──` chars) | Warning |
| No `.claude-plugin/plugin.json` manifest | Warning |

## Regression Assertion

The self-audit command should verify:
```
assert len(security_flags) >= 5  # scanner catches network + credential + env
assert len(issues) >= 1          # bash script structural violation
assert len(warnings) >= 2        # missing acceptance criteria + references
```
