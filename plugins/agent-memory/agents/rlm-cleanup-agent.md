---
name: rlm-cleanup-agent
description: >
  Cleans the RLM summary cache by removing entries for files that no longer exist on disk.
  Trigger when the user says "clean the RLM cache", "remove stale summaries", "the RLM cache
  has entries for deleted files", or "prune outdated RLM entries".

  <example>
  user: "The RLM cache has summaries for files I deleted"
  assistant: "I'll run the rlm-cleanup-agent to scan and remove stale entries."
  </example>

  <example>
  user: "Clean up stale RLM entries"
  assistant: "I'll launch the rlm-cleanup-agent to remove cache entries for files no longer on disk."
  </example>
context: fork
model: inherit
tools: ["Bash", "Read", "Write"]
---

Please run the `rlm-cleanup-agent` skill immediately.
