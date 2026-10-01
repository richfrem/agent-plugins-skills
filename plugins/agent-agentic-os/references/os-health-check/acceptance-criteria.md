# Acceptance Criteria: os-health-check

## ✅ Scenarios that must trigger
- "Run a health check on the OS."
- "Check os metrics."
- "Run a system monitor check on the OS."
- "Is the event bus healthy? any stuck agents?"

## ❌ Scenarios that must NOT trigger
- "Clear stale locks from context/.locks" (use `os-clean-locks`)
- "Summarize what the agentic OS ecosystem does" (use `os-guide`)

## Identity registration

- With the control plane enabled, the health check reports the human, simulation and isolation identities
  separately; an unregistered human identity is Tier 1 and is never fixed by the agent, an unregistered
  simulation identity is Tier 1 and agent-fixable via os-init, and isolation not ready is a Tier 2 recommendation.
- With the control plane disabled, the three identities are reported as informational with no finding.
- The command it names exists in the repository's layout (never a path that only exists in the plugin source repo).
