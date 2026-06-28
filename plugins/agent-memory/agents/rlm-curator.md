---
name: rlm-curator
description: >
  Curates and maintains the RLM summary cache — updates stale summaries, validates cache
  integrity, and promotes high-quality entries. Trigger when the user says "curate the RLM
  cache", "update stale summaries", "validate RLM integrity", or "the summaries are outdated".

  <example>
  user: "Some of my RLM summaries are outdated after recent code changes"
  assistant: "I'll launch the rlm-curator to update stale entries and validate cache integrity."
  </example>

  <example>
  user: "Validate and maintain the RLM cache"
  assistant: "I'll use the rlm-curator agent to check and refresh the summary cache."
  </example>
context: fork
model: inherit
tools: ["Bash", "Read", "Write"]
---

Please run the `rlm-curator` skill immediately.
