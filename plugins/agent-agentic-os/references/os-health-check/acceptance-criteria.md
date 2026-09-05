# Acceptance Criteria: os-health-check

## ✅ Scenarios that must trigger
- "Run a health check on the OS."
- "Check os metrics."
- "Run a system monitor check on the OS."
- "Is the event bus healthy? any stuck agents?"

## ❌ Scenarios that must NOT trigger
- "Clear stale locks from context/.locks" (use `os-clean-locks`)
- "Summarize what the agentic OS ecosystem does" (use `os-guide`)
