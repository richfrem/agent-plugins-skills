# Troubleshooting

## Exit code reference
| Code | Meaning | Fix |
|:---|:---|:---|
| `0` | KEEP — change accepted | Commit the change |
| `1` | DISCARD — change rejected, auto-reverted | Try a different change |
| `2` | Script error (path, missing file, arg parse) | Check error output; often a template path issue — see below |
| `3` | Locked loop deadlock — environment was tampered after baseline | Delete `<experiment-dir>/evals/.lock.hashes` and re-run `evaluate.py --baseline` |

## Exit 3: tampered environment reset
If you update `evals.json` after a partial baseline run, `evaluate.py` detects the SHA256 mismatch and exits 3. Fix:
```bash
rm <experiment-dir>/evals/.lock.hashes
python3 ./scripts/evaluate.py --skill <experiment-dir> --baseline --desc "re-baseline after evals update"
git add <experiment-dir>/evals/ && git commit -m "baseline: re-baseline after evals update"
```

## Exit 2: standalone template path fail
If `init_autoresearch.py` crashes with a `FileNotFoundError` pointing to a `./` nested path, the script is resolving templates against the full plugin repo layout instead of the installed standalone location. The fix is already applied in the master source (`TEMPLATES_DIR = PLUGIN_ROOT / "assets" / "templates" / "autoresearch"`). If you see it in a locally-patched copy, verify the script's `TEMPLATES_DIR` line uses `HERE.parent` resolution.

## Keywords frontmatter footgun
The `eval_runner.py` scorer treats an explicit `keywords:` field in skill frontmatter as authoritative — it stops scanning the `description` field. If `keywords:` is present but not exhaustive, critical routing words are missed and scores collapse (observed: 1.0000 → 0.5333, F1 1.0 → 0.29 in a single iteration). **Do not add a `keywords:` field unless the list is complete.** Remove it and rely on the description for routing if in doubt.

## 4-character word floor
The scorer only counts words ≥ 4 characters (`\w{4,}`). Words like "fix", "run", "doc" are invisible to the router. Ensure skill descriptions use longer trigger words: "broken", "audit", "paths", "links", "repair", "validation", "commit", "execute", "documentation".

## F1 guard — do not disable
Never disable the `f1 >= baseline_f1` check in `evaluate.py`. It is the only protection against keyword stuffing — where padding the description raises recall at the expense of precision. A high routing accuracy score with low F1 is a red flag, not a victory.

## Structural heuristic penalties
The heuristic engine applies soft penalties for missing structure (e.g. -0.30 for no `<example>` blocks). Do not ignore these even when routing accuracy is high. They are self-correcting signals for documentation quality, not noise.

## .lock.hashes and path portability
`.lock.hashes` currently uses absolute paths. If the skill folder is moved between environments or machines, the baseline hashes will mismatch and trigger exit 3. Re-establish the baseline with `--baseline` after any move.

## Re-baseline required after upgrading evaluate.py or eval_runner.py
Both scripts are SHA256-locked. If you pull an upstream update to either script, existing `.lock.hashes` files will mismatch and trigger exit 3. Fix:
```bash
python3 ./scripts/evaluate.py \
    --skill <experiment-dir> --baseline --desc "re-baseline after script upgrade"
git add <experiment-dir>/evals/ && git commit -m "baseline: re-baseline after evaluate.py upgrade"
```

## Milestone summaries for long runs (25+ iterations)

For runs exceeding 25 iterations, generate a milestone summary to preserve distant history context:

```bash
# Write a milestone if iteration count is a multiple of 25 (auto-check)
python3 ./scripts/generate_milestone.py \
    --experiment-dir <path/to/experiment-dir>

# Force-write a milestone at any iteration count
python3 ./scripts/generate_milestone.py \
    --experiment-dir <path/to/experiment-dir> --force

# Custom interval (e.g. every 10 iterations)
python3 ./scripts/generate_milestone.py \
    --experiment-dir <path/to/experiment-dir> --every 10
```

Output: `evals/traces/milestone_NNN.md` — score trajectory, top KEEPs, worst DISCARDs,
recurring false-positive inputs, dominant problem type, and recommended focus.

The proposer should read milestone summaries for distant history and raw traces for recent
iterations. This prevents the loop from losing context on early experiments as trace count grows.

## Reading traces to diagnose DISCARD iterations
```bash
# Find all false positives across recent traces
grep -h "false positive" evals/traces/iter_*.json | sort | uniq -c | sort -rn

# Show full routing detail for a specific DISCARD
cat evals/traces/iter_002_DISCARD_score0.71.json | python3 -m json.tool

# Show the mutation diff for a DISCARD
python3 -c "import json; d=json.load(open('evals/traces/iter_002_DISCARD_score0.71.json')); print(d['mutation_diff'])"
```
