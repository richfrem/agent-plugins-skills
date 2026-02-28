# Safety Learnings: Red Team Review Synthesis

## Source
Compiled from Red Team Review (Grok, GPT-5.2, Gemini 3.1 Pro, Claude 4.6 Opus)
conducted during Phase 0.5 of the Obsidian Agent Integration Suite.

## Critical Risks Identified and How They Were Mitigated

### 1. Concurrent Write Corruption (CRITICAL → MITIGATED)
**Risk**: Obsidian lacks OS-level file locking. Agents writing via `pathlib` while
the Obsidian app is open risks race conditions — missing edits, truncated frontmatter,
or silent JSON corruption in `.canvas` files.

**Mitigations Implemented**:
- ✅ **Atomic Writes** (T026): Write to `.agent-tmp`, then `os.rename()` (POSIX atomic)
- ✅ **Advisory Locking** (T027): `.agent-lock` file at vault root governs agent-vs-agent
- ✅ **mtime Detection** (T028): Capture mtime before read, verify before write, abort on change

### 2. YAML Frontmatter Corruption (HIGH → MITIGATED)
**Risk**: Standard Python `PyYAML` reorders keys and normalizes scalars, breaking
Dataview plugin queries that rely on type stability.

**Mitigation Implemented**:
- ✅ **Lossless YAML** (T029): Enforced `ruamel.yaml` for all frontmatter operations

### 3. Parser Depth & Wikilink Ambiguity (HIGH → MITIGATED)
**Risk**: Naive regex breaks on aliases (`[[Note|Alias]]`), block references
(`[[#^block]]`), and embedded callouts.

**Mitigation Implemented**:
- ✅ **Shared Parser** (WP05): Centralized `obsidian-parser` module handles all edge cases
- ✅ **Embed/Link Distinction**: Negative lookbehind `(?<!\!)` separates `![[embeds]]` from `[[links]]`

### 4. Inconsistent State Export (CRITICAL → PENDING WP09)
**Risk**: If CRUD and Legacy Scrubbing run concurrently with the Soul Exporter,
broken links or partially refactored notes could poison the HF dataset.

**Planned Mitigations** (for WP09: Forge Soul Exporter):
- ⏳ Snapshot isolation via tree hash before export
- ⏳ Fail-fast mtime check — abort if any file changes during export

### 5. Human-Active Vault Detection (MEDIUM → ADVISORY)
**Risk**: Agent writes while a human is actively editing in Obsidian.

**Current Approach**: The `.agent-lock` protocol is advisory. Future enhancement
could add `pgrep`-based detection of the Obsidian process as a "warm vault" warning signal.

## Design Principles Extracted

1. **Write defensively** — Always assume another process could be editing the same file
2. **Fail loudly** — Abort and alert rather than silently overwrite
3. **Preserve formatting** — Never use libraries that reorder or normalize YAML/JSON
4. **Separate concerns** — Parser ≠ I/O ≠ Init. Each skill has exactly one job
5. **Project-agnostic** — Skills know nothing about Sanctuary; only about Obsidian syntax
