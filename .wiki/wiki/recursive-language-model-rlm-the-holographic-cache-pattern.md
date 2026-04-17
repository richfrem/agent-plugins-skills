---
concept: recursive-language-model-rlm-the-holographic-cache-pattern
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/rlm-search/references/BLUEPRINT.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.211673+00:00
cluster: vector
content_hash: 0f494d3556a2be4c
---

# recursive language model (RLM): The Holographic Cache Pattern

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# recursive language model (RLM): The Holographic Cache Pattern

**Status:** Production Verified (Project Ecosystem)  
**Architecture Type:** Cognitive Memory Architecture  
**Primary Use Case:** Large-Scale Codebase & Documentation Understanding for AI Agents

## 1. The Problem: The "Needle in the Haystack"

Standard RAG (Retrieval-Augmented Generation) uses Vector Databases to find specific text chunks based on semantic similarity. While powerful, this approach suffers from **Context Blindness**:

*   **The Chunking Problem:** A chunk of text (e.g., "function process_data()") loses its meaning when separated from its file's purpose (e.g., "This file handles critical PII sanitization").
*   **The Latency Problem:** Querying a Vector DB for "What is the architecture of this project?" requires retrieving and synthesizing hundreds of disconnected chunks, which is slow and error-prone.
*   **The "Unknown Unknowns":** An agent cannot query for what it doesn't know exists.

## 2. The Solution: recursive language model (RLM)

The RLM is a **precognitive, holographic cache**. Instead of slicing the repository into incoherent chunks, it maintains a **"One-Sentence Source of Truth"** for every single file in the project.

**The Ecosystem View:**
This pattern is the memory core of the Infinite Context Ecosystem.

### Core Concepts

1.  **The Atom (Summary):** Every file is distilled into a dense, high-entropy summary (The "Essence").
2.  **The Ledger (JSON):** A flat, highly portable JSON file acts as the "Map of the Territory."
3.  **Incremental Persistence:** The ledger updates transactionally after every file is processed, ensuring resilience.
4.  **Hash-Based Validity:** Files are only re-processed if their MD5 hash changes.

## 3. Technical Implementation Blueprint

This pattern can be implemented in any language (Python/TS/Go). Below is the reference implementation logic used in Project Ecosystem.

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
| **Qwen** | `Qwen2.5-7B-Instruct` | **Best All-Rounder.** Excellent at code understanding and concise technical writi

*(content truncated)*

## See Also

- [[recursive-logic-discovery-the-infinite-context-ecosystem]]
- [[query-rlm-cache]]
- [[rlm-init-cache-bootstrap]]
- [[architecture-rlm-late-binding-recursive-discovery]]
- [[recursive-logic-discovery-the-infinite-context-ecosystem]]
- [[recursive-logic-discovery-the-infinite-context-ecosystem]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/rlm-search/references/BLUEPRINT.md`
- **Indexed:** 2026-04-17T06:42:10.211673+00:00
