# os-health-check — Detailed Reference

Extracted from SKILL.md per Layer-1 procedural-core line budget (issue #551).

## Phase 3.5 — os-init Substrate Completeness Check (full commands)

Verify the scaffolding artifacts `os-init --retrofit` is responsible for creating. This
check exists because of DEBT-20260905-12/-13/-14 (see `references/map-debt.md`): the retrofit code
path historically diverged from the fresh-setup path and silently skipped substrates —
run this check on every health check, not just once after install, since a stale/pre-fix
`init_agentic_os.py` copy can reintroduce the gap.

```bash
test -f context/control_plane.db && echo "OK control_plane.db" || echo "MISSING control_plane.db"
test -f .claude/hooks/hooks.json && echo "OK hooks.json (Stop turn hook)" || echo "MISSING hooks.json"
test -f .git/hooks/pre-commit-evolution-guard && echo "OK pre-commit-evolution-guard" || echo "MISSING pre-commit-evolution-guard"
test -f .github/workflows/verify-evolution-integrity.yml && echo "OK verify-evolution-integrity.yml (CI Gate)" || echo "MISSING verify-evolution-integrity.yml"

# Verify instruction files contain Phase 0 intake rule
grep -q "interview-spec" CLAUDE.md && echo "OK CLAUDE.md (interview-spec rule)" || echo "MISSING CLAUDE.md interview-spec rule"

# Audit for lingering backup files (.bak) requiring agent review
BAK_FILES=$(find . -maxdepth 2 -name "*.bak" 2>/dev/null)
if [ -n "$BAK_FILES" ]; then
    echo "ATTENTION: Lingering backup files detected (.bak):"
    echo "$BAK_FILES"
    echo "ACTION: Consuming agent must review diffs against active files, reconcile any custom rules, and then remove the .bak files."
else
    echo "OK: No unreviewed .bak backup files"
fi

# If local plugins exist, verify each has references/evolution-log.md
if [ -d "plugins" ]; then
    for p in plugins/*/; do
        [ -d "$p" ] || continue
        test -f "${p}references/evolution-log.md" && echo "OK ${p}references/evolution-log.md" || echo "MISSING ${p}references/evolution-log.md"
    done
fi
```

**If any report MISSING**: this is a Tier 1 finding, not merely informational.
Recommend re-running the retrofit immediately in the health check summary:

```bash
python3 .agents/skills/os-init/scripts/init_agentic_os.py --target . --retrofit
```

All substrates are idempotent to create (skip-if-exists), so re-running retrofit is always safe even
when only one substrate is missing — do not hand-create the individual file as a workaround, as
that bypasses schema/WAL-mode setup for `control_plane.db`, the guard-wiring logic for the
git hook, and the standard evolution header templates.

## Consumer Guidance on Plugin Drift & Gaps

If Phase 3.5 or runtime audits detect modified or drifted local skills/scripts:
1. **Upstream Defect/Gap**: If the local modification fixes an engine, harness, or shared skill bug, follow the **Upstream Contribution Protocol**: test the change, port it to a branch in `richfrem/agent-plugins-skills`, submit a PR, or log an issue with reproduction details.
2. **Local Domain Customization**: If the change is specific to the consuming project, ensure it is housed in `.agent/rules/local-*` or a project-specific plugin under `plugins/<local-name>/` rather than directly diverging shared upstream skills. This ensures `os-init --retrofit` can safely update core substrates without clobbering project-specific logic.

## Phase 5 — Self-Assessment Survey (full detail)

Complete the Post-Run Self-Assessment Survey (`references/memory/post_run_survey.md`) after
every run — reflect on what was found so the OS can improve its own diagnostics.

**Count-Based Signals**: How many anomalies were detected? How many false positives? How many
times was a metric ambiguous or hard to interpret?

**Qualitative Friction**:
1. Which metric was hardest to interpret — why?
2. Was any anomaly detected that the current metrics don't capture well?
3. What pattern in `events.jsonl` was most surprising or concerning?
4. What one additional metric would make the next health check more useful?

**Improvement Recommendation**: What one change to this skill or the metrics definition
should be tested before the next run?

Save to: `${CLAUDE_PROJECT_DIR}/context/memory/retrospectives/survey_[YYYYMMDD]_[HHMM]_os-health-check.md`

```bash
python3 scripts/kernel.py emit_event --agent os-health-check \
  --type learning --action survey_completed \
  --summary "retrospectives/survey_[DATE]_[TIME]_os-health-check.md"
```
