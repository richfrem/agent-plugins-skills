---
concept: round-3-red-team-review-claude-46-opus
source: plugin-code
source_file: agent-plugin-analyzer/references/research/round-3-redteam-review-claude-opus.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.265827+00:00
cluster: patterns
content_hash: 051039e8f5279ec7
---

# Round 3 Red Team Review — Claude 4.6 Opus

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Round 3 Red Team Review — Claude 4.6 Opus

**Reviewer**: Claude 4.6 Opus
**Bundle Version**: Agent Plugin Analyzer v3
**Date**: 2026-03-03
**Method**: Live folder review (not bundle) — read all 30 files, executed `inventory_plugin.py --security` against both test fixtures

---

## Round 2 Fixes — Assessment

- **F1 SKILL.md size**: Resolved. Down to 164 lines. Security checks and maturity model cleanly extracted to dedicated reference files. The analyzer now practices what it preaches.
- **F2 Security scanning**: Resolved. The `--security` flag works correctly — I ran it against both fixtures. Detected all 3 CRITICAL findings in the flawed plugin (requests import, requests.post, curl) plus the WARNING for os.environ. Gold-standard plugin returned zero security flags. Clean implementation.
- **F3 Test fixtures**: Partial. The fixtures exist and function, but have significant gaps (detailed below).
- **F4 Frontmatter**: Resolved. Self-audit now uses standard `user-invocable: true` / `argument-hint:` format.
- **F5 Score weights**: Resolved. Explicit weights defined in `maturity-model.md` with calibration guidance (5=zero findings, 3=warnings only, 1=critical). The L4/L3 non-strict note is a good addition — a sharp L2 plugin is not worse than a bloated L5.
- **F6 Output templates**: Resolved. Both templates now include Security Findings table, Dimension Scores with weights, Scoring Version v2.0, and Confidence field. Comparative template has the Ecosystem Scorecard. Good cross-references between output-templates.md, maturity-model.md, and security-checks.md.
- **F7 LLM attack vectors**: Resolved. Six LLM-native vectors documented: skill impersonation, context window poisoning, instruction injection via references, write-then-read attacks, pattern catalog poisoning, dependency confusion. These cover the attack surface well.

---

## New Issues Introduced

### 1. Security scanner misses the hardcoded credential in `bad_script.py`

This is the most important finding of this review. The flawed plugin's `bad_script.py` contains `API_KEY = "sk-test-1234567890abcdef"` and a `Bearer` token usage. I ran the scanner — it detected `import requests` and `requests.post` and `os.environ`, but **did not flag the hardcoded `sk-test-...` credential**.

Looking at the code, the regex `r"sk-[a-zA-Z0-9]{20,}"` requires 20+ alphanumeric characters after `sk-`, but the test credential `sk-test-1234567890abcdef` has only 22 characters total (including "sk-"), so the match portion after `sk-` is `test-1234567890abcdef` which is 22 chars and contains a hyphen. The regex `[a-zA-Z0-9]{20,}` doesn't allow hyphens, so it won't match. The `Bearer` pattern also fails because it requires 15+ chars of `[\-\._~]` class but the token structure doesn't match how it appears in the f-string.

This means the test fixture's expected findings manifest claims "Hardcoded credential in `bad_script.py`" at Critical severity, but the deterministic scanner doesn't actually catch it. The self-audit would pass because it relies on the LLM's Phase 5 to catch what the script misses — but the whole point of F2 was to provide deterministic ground truth.

**Fix**: Either adjust the regex to be more inclusive (e.g., `r"sk-[a-zA-Z0-9\-_]{16,}"`) or adjust the test credential to match the current pattern (e.g., `sk-abcdefghijklmnopqrstuvwxyz1234`). Also add a `Bearer` token test case that the pattern actually matches.

### 2. Flawed fixture README expected findings don't match scanner output

The `tests/flawed-plugin/README.md` expected findings manifest lists 4 items:

| Expected | Scanner detects? |
|----------|-----------------|
| Hardcoded credential in bad_script.py (Critical) | **No** — regex mismatch (see above) |
| Bash script danger.sh (Error) | **Yes** — structural issue detected |
| Missing acceptance criteria (Warning) | **Yes** — in warnings array |
| Missing README file tree (Warning) | **No** — not checked by scanner |

The "Missing README file tree" is a structural an

*(content truncated)*

## See Also

- [[round-3-red-team-review-agent-plugin-analyzer-v3]]
- [[round-2-red-team-review-refactored-agent-plugin-analyzer]]
- [[red-team-review-loop]]
- [[acceptance-criteria-red-team-review]]
- [[procedural-fallback-tree-red-team-review]]
- [[red-team-review-agent-plugin-analyzer-meta-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-plugin-analyzer/references/research/round-3-redteam-review-claude-opus.md`
- **Indexed:** 2026-04-17T06:42:09.265827+00:00
