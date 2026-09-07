# Fallback Tree for os-health-check

1. Deterministic scan of events.jsonl/os-state.json/memory.md via kernel.py -> 2. If kernel.py unavailable, fall back to direct file existence + line-count checks.
