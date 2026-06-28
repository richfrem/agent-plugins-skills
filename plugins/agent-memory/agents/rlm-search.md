---
name: rlm-search
description: >
  Searches the RLM summary cache using keyword lookup (Phase 1 of the 3-phase search
  protocol). Fast O(1) lookup across dense file summaries — no embeddings required.
  Trigger when the user says "search the RLM cache", "find files using RLM", "keyword
  search the summaries", or "Phase 1 search". For semantic/vector search use vector-db-search.

  <example>
  user: "Find files related to authentication using the RLM cache"
  assistant: "I'll use the rlm-search agent for a fast keyword lookup across the summary ledger."
  </example>

  <example>
  user: "Search the RLM summaries for database schema references"
  assistant: "I'll launch the rlm-search agent to scan the summary cache."
  </example>
context: fork
model: inherit
tools: ["Bash", "Read", "Write"]
---

Please run the `rlm-search` skill immediately. $ARGUMENTS
