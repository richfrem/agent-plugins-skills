---
concept: round-3-red-team-review-agent-plugin-analyzer-v3
source: plugin-code
source_file: agent-plugin-analyzer/references/research/round-3-redteam-review-prompt.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.266301+00:00
cluster: security
content_hash: cd8d155fff1ef738
---

# Round 3 Red Team Review: Agent Plugin Analyzer v3

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Round 3 Red Team Review: Agent Plugin Analyzer v3

## What Changed Since Round 2

Based on consensus from GPT 5.3, Gemini 3.1 Pro, Grok 4.2, Claude Sonnet + Opus, the following improvements were implemented:

### F1: SKILL.md Size Reduction (All 5 reviewers)
- Extracted Phase 5 anti-pattern/security tables → `references/security-checks.md`
- Extracted Phase 6 maturity model + scoring → `references/maturity-model.md`
- SKILL.md reduced from 227 → ~165 lines (under 500-line limit it enforces on others)

### F2: Deterministic Security Scanning (Sonnet, Opus)
- Added `--security` flag to `inventory_plugin.py`
- Scans for: hardcoded credential patterns (sk-, ghp_, Bearer tokens), network calls (requests, urllib, curl, fetch), subprocess usage, hidden HTML comments in markdown
- Security findings output as `security_flags` array in JSON, 🔴 section in markdown

### F3: Test Fixtures Created (ALL 5 reviewers)
- `tests/gold-standard-plugin/` — minimal clean plugin (L2, zero Critical, has acceptance criteria)
- `tests/flawed-plugin/` — deliberately broken plugin with:
  - `bad_script.py`: hardcoded `sk-` credential, `requests.post`, `os.environ`
  - `danger.sh`: bash script violation + `curl` network call
  - No acceptance criteria, no file tree

### F4: Self-Audit Frontmatter Fixed (Sonnet, Opus)
- Changed from non-standard `$user_message:` to `user-invocable: true` / `argument-hint:` format

### F5: Score Weights Defined (GPT, Sonnet, Opus)
- Explicit weights: Security 25%, Content 20%, Structure 20%, Interaction 15%, Composability 10%, Maintainability 10%
- Scoring Version v2.0 added to all outputs
- Phase 2 rubric (3-point) mapped to Phase 6 scores (1-5): Exemplary=5, Adequate=3, Needs Work=1

### F6: Output Templates Synced (Sonnet)
- Added Security Findings table to Template 1
- Added Dimension Scores table with weights
- Added Scoring Version + Confidence fields
- Ecosystem Scorecard added to Comparative Template

### F7: LLM-Native Attack Vectors Added (Sonnet, Opus)
- `security-checks.md` now includes: skill impersonation, context window poisoning, instruction injection via references, write-then-read attacks, pattern catalog poisoning, dependency confusion

### F8: Virtuous Cycle Recommendations Extended (User)
- Output section now targets all 3 meta-plugins including `agent-plugin-analyzer` itself

### F9: Mermaid Diagram Updated
- All 6 phase subgraphs now have proper end states
- Phase labels updated to reflect current scope

### F10: Anti-Gaming Safeguards Documented (GPT)
- `security-checks.md` includes Goodhart's Warning plus 4 anti-gaming rules

---

## What to Validate in Round 3

### 1. Test Fixture Coverage
- Are the 2 fixtures (gold + flawed) sufficient for meaningful regression testing?
- Should we add a 3rd fixture: a purposely high-scoring plugin that is actually bad (gaming the analyzer)?
- Is the flawed fixture's expected findings manifest granular enough?

### 2. Security Scanning Completeness
- The `--security` flag catches: credentials, network calls, subprocess, HTML comments
- Missing: zero-width characters in markdown, skill name collision detection (requires cross-plugin context)
- Is the HTML comment check too aggressive? (Some plugins legitimately use `<!--` for badges)

### 3. Score Weight Calibration
- Proposed weights: Security 25%, Content 20%, Structure 20%, Interaction 15%, Composability 10%, Maintainability 10%
- Is Security at 25% correctly prioritized, or should it be higher/lower?
- Is Interaction at 15% right for plugins that are not user-facing?

### 4. Reference File Depth
- `analyze-plugin` now has 7 reference files. Is that too many?
- Should `analysis-framework.md` and `analysis-questions-by-type.md` be merged?

### 5. Remaining Open Items from Round 1-2
The following were raised across multiple rounds but not yet implemented:
- Closed-loop feedback from scaffolders (Claude R1+R2)
- Handoff schema between analyze-plugin → synthesize-learnings (Claude R2)
- Runtime/execution trace anal

*(content truncated)*

## See Also

- [[round-2-red-team-review-refactored-agent-plugin-analyzer]]
- [[red-team-review-agent-plugin-analyzer-meta-plugin]]
- [[round-3-red-team-review-claude-46-opus]]
- [[agent-plugin-analyzer-l5-red-team-auditor]]
- [[agent-plugin-analyzer-l5-red-team-auditor]]
- [[red-team-review-loop]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-plugin-analyzer/references/research/round-3-redteam-review-prompt.md`
- **Indexed:** 2026-04-17T06:42:09.266301+00:00
