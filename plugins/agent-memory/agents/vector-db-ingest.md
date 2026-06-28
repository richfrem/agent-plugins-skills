---
name: vector-db-ingest
description: >
  Ingests repository files into the ChromaDB vector store by chunking and embedding them.
  Supports full rebuild (--full) or incremental update (--since N hours). Trigger when the
  user says "ingest files into the vector store", "rebuild the vector index", "update the
  vector DB with new files", or "re-index the repository".

  <example>
  user: "Ingest the documentation into the vector store"
  assistant: "I'll use the vector-db-ingest agent to chunk and embed the documentation."
  </example>

  <example>
  user: "The vector index needs to be updated with files changed today"
  assistant: "I'll run the vector-db-ingest agent with --since 24 to pick up recent changes."
  </example>
context: fork
model: inherit
tools: ["Bash", "Read", "Write"]
---

Please run the `vector-db-ingest` skill immediately. $ARGUMENTS
