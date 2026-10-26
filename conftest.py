"""Repository-level pytest collection rules.

The plugin smoke tests are standalone executable programs.  Their shared
filename is intentional for direct invocation, but pytest would import both
as the same top-level ``smoke_test`` module during recursive collection.
"""

collect_ignore = [
    "plugins/agent-agentic-os/.apm/skills/running-control-plane/scripts/smoke_test.py",
    "plugins/agent-exploration-cycle/.apm/skills/running-exploration-cycle/scripts/smoke_test.py",
    "plugins/agent-orchestration/.apm/skills/orchestrating-agent-work/tests/test_swarm_run_models.py",
]
