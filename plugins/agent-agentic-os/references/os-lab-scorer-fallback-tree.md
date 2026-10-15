# Fallback Tree for os-lab-scorer

## From os-eval-runner (renamed to os-lab-scorer)

1. Run headless Python eval scripts -> 2. If eval script missing or fails to import, report FAIL with the import error rather than a false PASS.

## From os-skill-improvement (merged into os-lab-scorer)

1. RED-GREEN-REFACTOR cycle gated by os-lab-scorer's evaluate.py -> 2. If the scorer is unavailable, fall back to manual before/after routing comparison.
