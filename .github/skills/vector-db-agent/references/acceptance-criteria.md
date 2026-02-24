# Acceptance Criteria: Vector DB Agent

These test metrics guarantee the `vector-db-agent` correctly interfaces with the Python-based ingestion and retrieval scripts.

### Scenario: Local Ingestion & Vector Storage
**Given** the user triggers the Vector DB Agent to ingest a file
**When** the agent runs the ingestion wrapper script
**Then** the script should pass the target arguments to the decoupled `operations.py` library
**And** the document should be successfully split and embedded into ChromaDB.

### Scenario: Local Semantic Search
**Given** an indexed repository
**When** the user asks the agent to query a technical topic
**Then** the agent should run the query wrapper script
**And** the output should yield exact semantic matches retrieved from the Chroma database.
