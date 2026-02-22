# RAG Architecture & Design Choices (Confirmed)

**Status:** Finalized for Migration
**Architecture:** Parent-Child Multi-Vector Retriever
**Embeddings:** `nomic-embed-text-v1.5`
**Database:** ChromaDB (Network Hosted / Podman)

This document outlines the finalized architectural integration for the `vector-db` plugin, synthesizing the requirements extracted from the legacy Project Sanctuary deployment environment.

---

## 1. Retrieval Strategy: Parent-Child / Multi-Vector Retriever
We are formally adopting the **Parent-Child** architecture to ensure the language model is fed deep contextual clarity rather than fragmented, isolated fragments of code.

* **Child Chunks (400 characters)**: Small, granular chunks optimized strictly for high-precision semantic search. Stored in `CHROMA_CHILD_COLLECTION` (e.g., `child_chunks_v5`).
* **Parent Documents (2000 characters or full file)**: Large contextual blocks stored in a `SimpleFileStore` on disk (`CHROMA_PARENT_STORE`, e.g., `parent_documents_v5`).
* **Workflow**: A query matches against the 400-char child string in Chroma. The system grabs the linked `parent_id` and feeds the full 2000-char parent document to the LLM. 

**Why we chose this:** Code is highly contextual. Returning a single isolated `if` statement without the surrounding class definition is often useless to an LLM.

---

## 2. Embedding Model: `nomic-embed-text-v1.5`
We are migrating to HuggingFace's `nomic-embed-text-v1.5` (running locally via CPU).

* **Why we chose this:** Nomic is a top-tier open-weight model specifically designed for long-context retrieval (up to 8192 tokens), far surpassing standard `all-MiniLM` implementations, while still running freely and privately without requiring external API keys.

---

## 3. Deployment Architecture Selection

The final decision is how ChromaDB actually runs. Chroma supports three distinct deployment models.

### Option A: In-Process (`chromadb.PersistentClient`)
The database runs entirely within the context of the script executing the query (e.g. `query.py`).
* **Pros:** Zero setup required. The user just runs the script. No ports to configure, no background services to manage.
* **Cons:** The database file is locked by the Python process. You cannot have two different agents (or an agent and an API server) querying or ingesting at the exact same time without SQLite lock errors.

### Option B: Podman / Docker Container (Project Sanctuary Legacy)
Chroma runs as an isolated containerized service, accessed via `chromadb.HttpClient`.
* **Pros:** Enterprise-grade isolation. Can be deployed consistently across fleets. Safely handles massive concurrent requests from dozens of different agents simultaneously.
* **Cons:** High friction for local users. Requires installing Podman/Docker Desktop, managing container lifecycles (`make up`), and debugging complex volume mount permissions (e.g. SELinux `:Z` flags). 

### Option C: Python Native Server (`chroma run`)
Chroma runs as a standalone HTTP server launched directly via pip, accessed via `chromadb.HttpClient`.
* **Pros:** Provides the concurrency benefits of Option B (multiple agents can connect simultaneously) without the heavy system requirements of installing Docker/Podman.
* **Cons:** Still requires the user to open a separate terminal and keep a background process running (`chroma run --host 127.0.0.1 --port 8110 --path .vector_data`).

### Recommendation: Option C (Python Native Server)
For a Coding Agent running locally on Mac/Windows, **Option C is the clear winner**.
* Running `chroma run --host 127.0.0.1 --port 8110 --path .vector_data` in a background terminal gives you full concurrency (multiple agents or scripts can read/write at the same time).
* It avoids the massive overhead, permission issues, and host-VM networking headaches associated with Podman/Docker (Option B).
* It avoids the SQLite database locking errors that plague Option A.

**How the Plugin Handles This:**
The `operations.py` library we wrote is **Environment-Agnostic**. This means the code itself doesn't care whether you chose Option B or Option C. If you set `CHROMA_HOST=127.0.0.1` and `CHROMA_PORT=8110` in your `.env`, the plugin will connect to whatever is listening on that port via HTTP.

---

## Final `.env` Configuration Schema

To utilize the explicitly recommended **Option C**, your environment should mirror this structure:

```env
# --- CHROMA CONNECTION ---
# Used to connect to the Python `chroma run` background server
CHROMA_HOST=127.0.0.1
CHROMA_PORT=8110

# Fallback path if no Host is provided
CHROMA_DATA_PATH=.vector_data
VECTOR_DB_PATH=~/.agent/learning/chroma_db

# --- COLLECTIONS ---
# Parent-Child mapping variables
CHROMA_CHILD_COLLECTION=child_chunks_v5
CHROMA_PARENT_STORE=parent_documents_v5
```
