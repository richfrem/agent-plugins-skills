"""Repository-level pytest collection rules.

The plugin smoke tests are standalone executable programs.  Their shared
filename is intentional for direct invocation, but pytest would import both
as the same top-level ``smoke_test`` module during recursive collection.
"""

collect_ignore = [
    "plugins/agent-agentic-os/scripts/smoke_test.py",
    "plugins/exploration-cycle-plugin/scripts/smoke_test.py",
]
