# Canonical Agentic OS Architecture Protocol

The Agentic OS is not a binary—it is a directory structure and behavioral convention that turns an LLM into a persistent, self-managing entity. 

## 1. The Kernel (`CLAUDE.md`)
The root system instruction file. It defines the core identity of the repository, the non-negotiable standards, and delegates deeper knowledge down the directory tree.

## 2. RAM & Persistence (`context/`)
- `context/memory/`: Dated Markdown files storing daily events that are parsed by the `SessionStart` / `PostToolUse` hooks via `update_memory.py`.
- `context/memory.md`: The long-term, curated memory. Facts promoted from the daily logs land here.
- `context/status.md`: The "active register". Contains current tasks, blockers, and the state of the system loop. See `status-file-spec.md`.

## 3. Standard Library (`skills/`)
Reusable procedural modules defined in YAML+Markdown (`SKILL.md`). They define triggers and execution paths. Used to extend the capabilities of the agent without bloated context.

## 4. Processes / Background Tasks (`agents/`)
Standalone Sub-Agents optimized for narrow execution. Examples include the `agentic-os-setup` orchestration agent and the `os-learning-loop` auto-optimizing loop.