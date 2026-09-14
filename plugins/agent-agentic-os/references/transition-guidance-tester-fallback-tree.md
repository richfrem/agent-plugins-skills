# Fallback Tree: transition-guidance-tester

1. If the requested transition is unknown, stop and report the valid transition names.
2. If deterministic simulation fails, inspect the raw reply and identify whether the
   guidance template or coordinator logic is at fault.
3. If the behavioral simulation fails, fix the specific guidance or question-handling
   defect and retry the same edge.
4. After three failed attempts, stop and escalate with all attempt evidence.
5. Never replace a failed behavioral test with a structural-only pass.
