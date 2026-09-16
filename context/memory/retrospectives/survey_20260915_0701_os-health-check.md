# Post-Run Self-Assessment Survey — os-health-check

**Run timestamp:** 2026-09-15T14:01:12Z

## Count-Based Signals
- Anomalies detected: 2 (1 stale-check false positive, 1 lingering .bak file)
- False positives: 1 ("MISSING CLAUDE.md interview-spec rule" — the check greps the literal string `interview-spec`, but this repo correctly renamed that skill to `work-intake` in an earlier session per DEBT-20260913-RENAME-INTERVIEW-SPEC-TO-WORK-INTAKE; CLAUDE.md correctly references `work-intake`)
- Ambiguous/hard-to-interpret metrics: 0

## Qualitative Friction
1. **Hardest metric to interpret:** The Phase 3.5 substrate check's CLAUDE.md grep is a literal string match against `interview-spec`, which is now stale relative to this repo's own history — it doesn't know the skill was renamed, so it always reports MISSING even though the successor rule is present and correct.
2. **Anomaly the current metrics don't capture well:** None this run beyond the above.
3. **Most surprising/concerning pattern in events.jsonl:** None — 99 clean `post_run_hook` session_summary metric events (all zero friction/errors) plus this run's own intent/result pair. No unmatched intents from other agents, no hook errors.
4. **One additional metric that would help:** A configurable/derived check (e.g. reading the current skill name from a manifest or map-debt rename record) instead of a hardcoded literal string, so post-rename repos don't get a permanent false positive.

## Improvement Recommendation
Update Phase 3.5's CLAUDE.md substrate check to also accept the current work-intake skill name (or derive the expected name dynamically) before the next run, so this doesn't have to be manually explained away every time.
