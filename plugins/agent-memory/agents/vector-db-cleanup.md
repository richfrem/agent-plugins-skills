---
name: vector-db-cleanup
description: >
  Removes stale chunks from the ChromaDB vector store for files that have been deleted or
  renamed on disk. Dry-run by default — shows what would be removed without deleting.
  Trigger when the user says "clean the vector database", "remove stale vector entries",
  "vector DB has orphaned chunks", or "sync the vector store with current files".

  <example>
  user: "The vector DB has chunks for files I deleted"
  assistant: "I'll run the vector-db-cleanup agent to preview and remove orphaned chunks."
  </example>

  <example>
  user: "Clean up stale vector entries"
  assistant: "I'll launch the vector-db-cleanup agent — it shows a dry-run preview before deleting."
  </example>
context: fork
model: inherit
tools: ["Bash", "Read", "Write"]
---

Please run the `vector-db-cleanup` skill immediately.
