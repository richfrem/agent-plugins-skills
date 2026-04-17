---
concept: flawed-test-plugin
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/self-audit/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.216154+00:00
cluster: warning
content_hash: a4957f44d203bf69
---

# Flawed Test Plugin

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Flawed Test Plugin

A deliberately broken plugin used for self-audit regression testing. The analyzer MUST detect the following issues.

## Expected Scanner Findings (deterministic — `inventory_plugin.py`)

These MUST appear in the `security_flags` or `issues` arrays when the scanner runs.

| Finding | Severity | File |
|---------|----------|------|
| Unauthorized network call (`import requests`) | Critical | `scripts/bad_script.py` |
| Unauthorized network call (`requests.post`) | Critical | `scripts/bad_script.py` |
| Access to raw environment variables (`os.environ`) | Warning | `scripts/bad_script.py` |
| Unauthorized network call (`curl`) | Critical | `scripts/danger.sh` |
| Bash script violation | Error | `scripts/danger.sh` |

**Expected counts**: security_flags >= 4, issues >= 1

## Expected LLM Findings (Phase 5 — agent analysis)

These are structural anti-patterns the scanner doesn't check. The LLM must flag them during Phase 5.

| Finding | Severity |
|---------|----------|
| Hardcoded credential (obfuscated via string construction) | Critical | `scripts/bad_script.py` |
| Missing acceptance criteria for `flawed-skill` | Warning |
| Missing `references/` directory for `flawed-skill` | Warning |
| Missing README file tree (`├──` / `└──` chars) | Warning |
| No `./plugin.json` manifest | Warning |

> **Note**: The credential in `bad_script.py` uses string concatenation to evade regex scanners.
> The deterministic scanner will NOT detect it. Only the LLM phase catches this pattern.

## Regression Assertion

The self-audit command should verify:
```
assert len(security_flags) >= 4  # scanner catches network calls + env access (not obfuscated cred)
assert len(issues) >= 1          # bash script structural violation
assert len(warnings) >= 2        # missing acceptance criteria + references
```


## See Also

- [[test-scenario-bank-agentic-os-plugin]]
- [[gold-standard-test-plugin]]
- [[goodhart-plugin-test-fixture]]
- [[test-scenario-bank-agentic-os-plugin]]
- [[test-scenario-bank-agentic-os-plugin]]
- [[adr-manager-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/self-audit/README.md`
- **Indexed:** 2026-04-17T06:42:10.216154+00:00
