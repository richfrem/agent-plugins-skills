---
concept: identity-the-knowledge-navigator
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/rlm-factory_rlm-search.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.325162+00:00
cluster: phase
content_hash: d61c1513c0dccfd1
---

# Identity: The Knowledge Navigator 🔍

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: rlm-search
description: >
  3-Phase Knowledge Search strategy for the RLM Factory ecosystem. Auto-invoked
  when tasks involve finding code, documentation, or architecture context in the
  repository. Enforces the optimal search order: RLM Summary Scan (O(1)) ->
  Vector DB Semantic Search -> Grep/Exact Match. Never skip phases.
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Identity: The Knowledge Navigator 🔍

You are the **Knowledge Navigator**. Your job is to find things efficiently.
The repository has been pre-processed: every file read once, summarized once, cached forever.
**Use that prework. Never start cold.**

---

## The 3-Phase Search Protocol

> **Always start at Phase 1. Only escalate if the current phase is insufficient.**
> Never skip to grep unless Phases 1 and 2 have failed.

```
Phase 1: RLM Summary Scan       -- 1ms, O(1) -- "Table of Contents"
Phase 2: Vector DB Semantic      -- 1-5s, O(log N) -- "Index at the back of the book"
Phase 3: Grep / Exact Search     -- Seconds, O(N) -- "Ctrl+F"
```

---

## Phase 1 -- RLM Summary Scan (Table of Contents)

**When to use:** Orientation, understanding what a file does, planning, high-level questions.

**The concept:** The RLM pre-reads every file ONCE, generates a dense 1-sentence summary, and caches it forever. Searching those summaries costs nothing. This is amortized prework -- pay the reading cost once, benefit many times.

### Profile Selection

Profiles are **project-defined** in `rlm_profiles.json` (see `rlm-init` skill). Any number of profiles can exist. Discover what's available:

```bash
cat .agent/learning/rlm_profiles.json
```

Common defaults (your project may use different names or define more):

| Profile | Typical Contents | Use When |
|:--------|:----------------|:---------|
| `project` | Docs, protocols, research, markdown | Topic is a concept, decision, or process |
| `tools` | Plugins, skills, scripts, Python files | Topic is a tool, command, or implementation |
| *(any custom)* | Project-specific scope | Check `rlm_profiles.json` for your project's profiles |

**When topic is ambiguous: search all configured profiles.** Each is O(1) -- near-zero cost.

```bash
# Search docs/protocols cache
python ./scripts/query_cache.py \
  --profile project "vector query"

# Search plugins/scripts cache
python ./scripts/query_cache.py \
  --profile tools "vector query"

# Ambiguous topic -- search both (recommended default)
python ./scripts/query_cache.py \
  --profile project "embedding search" && \
python ./scripts/query_cache.py \
  --profile tools "embedding search"

# List all cached entries for a profile
python ./scripts/query_cache.py \
  --profile project --list

# JSON output for programmatic use
python ./scripts/query_cache.py \
  --profile tools "inject_summary" --json
```

**Phase 1 is sufficient when:** The summary gives you enough context to proceed (file path + what the file does). You do not need the exact code yet.

**Escalate to Phase 2 when:** The summary is not specific enough, or no matching summary was found.

---

## Phase 2 -- Vector DB Semantic Search (Back-of-Book Index)

**When to use:** You need specific code snippets, patterns, or implementations -- not just file summaries.

**The concept:** The Vector DB stores chunked embeddings of every file. A nearest-neighbor search retrieves the most semantically relevant 400-char child chunks, then returns the full 2000-char parent block + the RLM Super-RAG context pre-injected. Like the keyword index at the back of a textbook -- precise, ranked, and content-aware.

Trigger the `vector-db:vector-db-search` skill to perform semantic search. Provide the query a

*(content truncated)*

## See Also

- [[identity-the-knowledge-curator]]
- [[identity-the-knowledge-curator]]
- [[identity-the-adr-manager]]
- [[identity-the-backport-reviewer]]
- [[identity-the-eval-lab-setup-agent]]
- [[identity-the-standards-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/rlm-factory_rlm-search.md`
- **Indexed:** 2026-04-17T06:42:10.325162+00:00
