# Chart Reading Guide

Reference for interpreting `os-improvement-report` output charts and text summaries.

---

## Progress Chart Layout

The chart mirrors the autoresearch `progress.png` format:

| Element | Meaning |
|---------|---------|
| X-axis | Cycle number (chronological) |
| Y-axis | Eval score for the target skill (higher = better) |
| Gray dots | DISCARD cycles -- attempts that did not improve the skill |
| Green dots | KEEP cycles -- improvements that were accepted |
| Green step line | Running best -- the frontier of improvement over time |
| Annotations | What change was made on each KEEP cycle |

---

## Interpreting Signals

**Flat or declining step line**
The loop is not improving the skill. Check the test scenarios seed
(`references/testing/test-scenarios-seed.md`) -- the current hypotheses may be exhausted.
Review the survey-to-action trace (Section 2 of the ledger) for unresolved friction items.

**Frequent DISCARD clusters**
Hypothesis quality needs work. Review the test design in closed scenario files
(`context/memory/tests/`) to see what approach keeps failing and why.

**Steep step-line rises**
The survey-to-action trace is working well -- friction items from surveys are being
turned into effective improvements. This is the target state.

**No data / empty chart**
The improvement ledger exists but has no Section 1 rows. At least one complete
`os-improvement-loop` cycle must run before the chart has meaningful data.

---

## Text Summary Fields

The `summary_YYYYMMDD_HHMM.md` file produced alongside the chart contains:

| Field | What it shows |
|-------|--------------|
| Baseline score | First eval score from `results.tsv` for this skill |
| Best score | Highest KEEP score recorded |
| Score delta | Best minus baseline -- the net improvement |
| Top KEEP cycles | The cycles with the largest positive score delta |
| Survey effectiveness | Ratio of survey friction items to KEEP cycles they produced |
| North Star trend | Completion rate per session (from Section 3 of ledger) |

---

## Cross-Plugin Reporting

Both `agent-agentic-os` and `exploration-cycle-plugin` use the same ledger format.
To generate reports for both, run `generate_report.py` once per plugin, passing each
plugin's project dir and plugin dir. Each run produces its own chart and summary.
The text summaries can be concatenated for a combined view.

---

## Ledger Format Reference

See `improvement-ledger-spec.md` for the three-section ledger format
that `generate_report.py` reads:

- **Section 1**: Eval score progression (one row per cycle)
- **Section 2**: Survey-to-action trace (friction item -> what changed)
- **Section 3**: North Star metric (completion rate per session)
