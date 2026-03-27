# Architecture Overview: 3-Layer Search System

## System Design
A hybrid search architecture integrating deterministic lookup, semantic understanding, and exact pattern matching to provide comprehensive code analysis capabilities.

### Layer 1: Deterministic Memory (RLM)
*   **Mechanism:** Key-Value lookup against a pre-distilled JSON cache.
*   **Data Source:** `rlm_summary_cache.json` (Local file).
*   **Logic:** Query matches file keys to retrieve instant summaries.
*   **Strength:** O(1) Access for known entities.

### Layer 2: Semantic Search (Vector)
*   **Mechanism:** Embedding similarity search (Cosine Similarity).
*   **Engine:** ChromaDB (Local persistence).
*   **Model:** `all-MiniLM-L6-v2`.
*   **Logic:** Query is embedded and compared against a vector index of code chunks.
*   **Strength:** Conceptual understanding ("How does bail work?").

### Layer 3: Exact Code Search (Deep)
*   **Mechanism:** Recursive token/string matching (Grep-like).
*   **Engine:** Custom Python Script (`findPLSQLTermAttributeKeyword.py`).
*   **Strength:** Precision finding (Variable usage, specific PL/SQL calls).

---

## Red Team Engagement Protocol

We are soliciting a "Red Team" review from top-tier AI models. Please assume the following roles and answer the specific questions below to help us build an **industry-leading local search architecture**.

### 🎭 Protocol Roles

| Model | Persona | Focus Area |
| :--- | :--- | :--- |
| **Gemini 3 Web** | **The Systems Architect** | Holistic design, integration patterns, and future scalability. How does this evolve into a fully autonomous agent memory? |
| **GPT-5** | **The Security Fortress** | Attack surface analysis. We are spawning shells. Where are the injection points? rigorous input validation checks. |
| **Claude 4.5** | **The Cognitive Data Scientist** | Result ranking and user cognition. How do we blend Vector scores (0-1) with Keyword binary matches without cognitive overload? |
| **Grok 4** | **The Performance Hacker** | Raw speed, I/O optimization, and Linux/WSL internals. How do we make this fly? (Daemonizing Python? Memory mapping?) |

### ❓ Key Analysis Questions

1.  **Unified Ranking Algorithm:** How can we normalize and merge results from three disparate sources (Text Match, Vector Score, Fuzzy Key) into a single, meaningful "Relevance List"?
2.  **Process Overhead:** Is spawning a Python subprocess (`exec`/`spawn`) for every search query scalable? What is the recommended pattern for keeping the Embedding Model hot in memory using our current Node.js + Python stack?
3.  **Input Sanitization:** Given we are passing user input to a shell command (`python query.py "INPUT"`), what is the most robust implementation to prevent Command Injection, ensuring we cover all edge cases?
4.  **Context Window Injection:** The ultimate goal is to feed these results back into an LLM Context Window. How should we format the "Least Common Denominator" of these results to maximize LLM reasoning while minimizing token usage?
5.  **Amazing UI/UX:** What is the specific "Wow Factor" feature missing from this list that would make this tool indispensable for a human analyst?
