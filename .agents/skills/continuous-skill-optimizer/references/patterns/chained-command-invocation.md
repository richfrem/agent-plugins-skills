# Chained Command Invocation via Offer-Next-Steps Blocks

**Use Case:** Any plugin with multiple commands that logically connect (e.g., triage -> escalate, or research -> document).

## The Core Mechanic

Commands should not be dead ends. Instead of presenting the output and stopping, every command should act as a node in a workflow graph, explicitly surfacing the next logical commands to the user.

### Implementation Standard

Add an `## Offer Next Steps` block to the end of every command template:

```markdown
## Offer Next Steps

After presenting your output, offer contextually relevant follow-on actions. Each offer must name the specific command or action.

- "Should I escalate this? I can package it with `/escalate`."
- "Want me to draft a full response to the customer?"
- "Should I save these findings to your knowledge base for future reference?"
```

This ensures the user discovers the full capabilities of the plugin without needing to memorize the `README.md`.
