Runtime terminal wrapper backgrounding error

When running multiple `task_manager.py` commands in quick succession from the terminal tool, some environments will reject grouped commands with an error like:

"Foreground command uses '&' backgrounding. Use terminal(background=true) for long-lived processes..."

What causes it
- The agent terminal wrapper enforces foreground/backgrounding guards to prevent runaway background processes in the execution environment.
- Commands joined with `&`, `;`, or run inside a single shell script can triggger the guard.

Fix / Workaround
1. Execute each `python3 ./scripts/task_manager.py <command>` as its own terminal call.
2. If you must run many operations, loop from the agent and run them sequentially, capturing each result before the next call.
3. For longer-lived processes, use terminal(background=true) when available and then run health checks separately.

Why we write this reference
- The fix is environment-specific and reproducible; having a small reference file helps future agents detect and recover from the issue quickly.
