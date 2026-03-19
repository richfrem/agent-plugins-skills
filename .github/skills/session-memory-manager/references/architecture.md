# Session Memory Architecture & Tiers

The Session Memory Manager acts as the Garbage Collector and Long-Term Storage controller for the Agentic OS.

## Memory Tiers
1. **L1 (Cache)**: The current active context window. Highly transient.
2. **L2 (Daily Logs)**: Stored in `context/memory/YYYY-MM-DD.md`. Populated asynchronously by `hooks/update_memory.py` when file-write events occur. Semi-transient.
3. **L3 (Permanent Record)**: Stored in `context/memory.md`. Curated facts. Permanent.

## Conflict Resolution & Dementia Guard
The most critical architectural rule of the `session-memory-manager`: **No blind appends to L3.** 
If an agent promotes a fact from a daily log that contradicts an existing fact in `memory.md`, the agent will experience "dementia" (conflicting rules). The architecture dictates an obligatory `Read` step to scan L3 before appending, pausing for user intervention if a conflict is detected.