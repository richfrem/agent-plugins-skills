# Recursive Learning Model (RLM): The Holographic Cache Pattern

**Status:** Production Verified (Project Sanctuary)  
**Architecture Type:** Cognitive Memory Architecture  
**Primary Use Case:** Large-Scale Codebase & Documentation Understanding for AI Agents

## 1. The Problem: The "Needle in the Haystack"

Standard RAG (Retrieval-Augmented Generation) uses Vector Databases to find specific text chunks based on semantic similarity. While powerful, this approach suffers from **Context Blindness**:

*   **The Chunking Problem:** A chunk of text (e.g., "function process_data()") loses its meaning when separated from its file's purpose (e.g., "This file handles critical PII sanitization").
*   **The Latency Problem:** Querying a Vector DB for "What is the architecture of this project?" requires retrieving and synthesizing hundreds of disconnected chunks, which is slow and error-prone.
*   **The "Unknown Unknowns":** An agent cannot query for what it doesn't know exists.

## 2. The Solution: Recursive Learning Model (RLM)

The RLM is a **precognitive, holographic cache**. Instead of slicing the repository into incoherent chunks, it maintains a **"One-Sentence Source of Truth"** for every single file in the project.

**The Ecosystem View:**
This pattern is the memory core of the [Infinite Context Ecosystem](../../../docs/diagrams/workflows/archive/infinite-context-ecosystem.mmd).
![Ecosystem](../../../docs/diagrams/workflows/archive/infinite-context-ecosystem.png)

### Core Concepts

1.  **The Atom (Summary):** Every file is distilled into a dense, high-entropy summary (The "Essence").
2.  **The Ledger (JSON):** A flat, highly portable JSON file acts as the "Map of the Territory."
3.  **Incremental Persistence:** The ledger updates transactionally after every file is processed, ensuring resilience.
4.  **Hash-Based Validity:** Files are only re-processed if their MD5 hash changes.

## 3. Technical Implementation Blueprint

This pattern can be implemented in any language (Python/TS/Go). Below is the reference implementation logic used in Project Sanctuary.

### 3.1 The Schema (`ledger.json`)

Structure your cache as a flat Key-Value store to allow O(1) lookups.

```json
{
  "docs/architecture/system_design.md": {
    "hash": "a1b2c3d4e5f6...",
    "mtime": 1704092833.0,
    "summarized_at": "2024-01-01T12:00:00Z",
    "summary": "This document defines the 3-tier architecture (Frontend, API, Worker) and the data flow protocol for the entire system."
  },
  "src/utils/sanitizer.py": {
    "hash": "f6e5d4c3b2a1...",
    "mtime": 1704092900.0,
    "summarized_at": "2024-01-01T12:05:00Z",
    "summary": "A utility module responsible for stripping PII from user inputs before database insertion; critical for GDPR compliance."
  }
}
```

### 3.2 The Distillation Loop (Python Pseudo-code)

```python
def rlm_distill(target_dir):
    ledger = load_json("ledger.json")
    
    for file in walk(target_dir):
        current_hash = md5(file.content)
        
        # 1. Skip if unchanged (Cache Hit)
        if file.path in ledger and ledger[file.path]["hash"] == current_hash:
            continue
            
        # 2. Distill (The LLM Call)
        # Use a small, local model (see Section 4) for speed/privacy
        summary = llm_generate(
            model="qwen2.5-7b-instruct",
            prompt=f"Summarize the architectural purpose of this file in 2 sentences:\n\n{file.content}"
        )
        
        # 3. Incremental Persistence (CRITICAL)
        ledger[file.path] = {
            "hash": current_hash,
            "summary": summary
        }
        save_json(ledger, "ledger.json") # Write immediately!
```

## 4. Model Selection (Open Source Recommendations)

You do not need a massive model (GPT-4) for this. Summarization is a high-compression task suitable for 7B-class models.

| Model Family | Variant | Why Use It? |
| :--- | :--- | :--- |
| **IBM Granite** | `granite-3.2-8b` | **Project Standard.** High-performance coding model optimized for enterprise legacy systems. |
| **Qwen** | `Qwen2.5-7B-Instruct` | **Best All-Rounder.** Excellent at code understanding and concise technical writing. |
| **Llama 3** | `Llama-3-8B-Instruct` | **High Fidelity.** Very strong reasoning, good for complex prose documentation. |
| **Llama 3.2** | `Llama-3.2-3B` | **Ultra Fast.** Perfect for massive repos running on consumer laptops (M1/M2/M3). |
| **Mistral** | `Mistral-7B-v0.3` | **Reliable.** A classic workhorse with a large context window (32k). |

**Serving:** use [Ollama](https://ollama.com/) locally (`ollama serve`).

## 5. Augmenting the Vector DB (The "Super-RAG")

The RLM Ledger isn't just for humans/agents to look at—it is the **perfect meta-data source** for your Vector DB (Chroma/Pinecone/Weaviate).

**The "Context Injection" Strategy:**

When you chunk a file for your Vector DB, prepending the RLM Summary to *every single chunk* dramatically improves retrieval quality.

**Without RLM (Standard Chunk):**
> "def validate(x): return x > 0 else raise Error"
*(Vector DB doesn't know what this validates)*

**With RLM Injection:**
> **[Context: critical_financial_validator.py - ensuring no negative balances in user wallets]**
> "def validate(x): return x > 0 else raise Error"
*(Vector DB now perfectly matches queries about "financial validation")*

## 6. Benefits for Agent Systems

1.  **Fast Boot:** Agent reads the `ledger.json` (300KB) instead of scanning 5,000 files (500MB).
2.  **Code Navigation:** Agent uses the ledger to decide *which* files to open (`read_file`), reducing token costs by 95%.
3.  **Self-Healing:** If the ledger is missing, the agent can regenerate it locally.

## 7. Migration Guide

To adopt this pattern in your repo:
1.  **Install:** `ollama` and `python`.
2.  **Pull Model:** `ollama pull qwen2.5:7b`.
3.  **Script:** Implement the "Distillation Loop" above.
4.  **Policy:** Add `ledger.json` to your `.gitignore` (or commit it if you want shared team memory).
5.  **Doc:** Update your `README.md` to explain that `ledger.json` is the map.