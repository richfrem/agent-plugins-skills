# ADR-001: SQLite Path Strategy — Hardened Fixed Path & Fail-Closed

**Status:** Accepted  
**Date:** 2026-05-30

## Decision

**DB path:** `${CLAUDE_PROJECT_DIR}/context/exploration/active_session.sqlite`

- Fixed per project context. Added to `.gitignore`.
- `init_db` raises `RuntimeError` immediately if WAL mode cannot be enabled — no fallback.

## Alternatives Rejected

| Approach | Reason |
|---|---|
| Dynamic path per session | Directory permissions hard to secure; path injection risk |
| Fixed path + `/tmp` fallback | Silent split-brain drift; injection vectors on fallback |

## Consequences

- Project root must be on a local filesystem (no network mounts).
- All write failures are loud (`RuntimeError`), never silent.
