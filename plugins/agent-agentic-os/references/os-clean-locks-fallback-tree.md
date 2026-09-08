# Fallback Tree for os-clean-locks

1. Remove stale lock dirs via kernel.py -> 2. If kernel.py unavailable, manually delete context/.locks/* after confirming no active agent PID holds them.
