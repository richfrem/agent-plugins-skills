# Search Extension Implementation Plan
**Tool:** Oracle Forms Visualizer
**Feature:** Super-RAG 3-Layer Search
**Status:** ✅ Phase 1 Complete | 🚧 Phase 2 In Progress

---

## Overview

Implement a production-grade search capability with:
- **Layer 1 (RLM):** Instant key-value lookup from cached summaries
- **Layer 2 (Vector):** Semantic concept search via ChromaDB
- **Layer 3 (Deep):** Exact code search via hardened ripgrep

**Architecture:** Node.js orchestrator + Python FastAPI sidecar

---

## Phase 1: Security Hardening (P0) — Week 1

### 1.1 Hardened Ripgrep Wrapper
- [x] Create `server/utils/safeSearch.js`
- [x] Implement input validation regex: `^[\w.\-/ ]{1,128}$`
- [x] Use argument array (never shell strings)
- [x] Add `--fixed-strings` and `--` separator
- [x] Add timeout (30s) and resource caps
- [ ] Unit tests for injection attempts

**Files:**
- `tools/oracle-forms-visualizer/server/utils/safeSearch.js` ✅
- `tools/oracle-forms-visualizer/server.js` ✅

### 1.2 Python Sidecar Foundation
- [x] Create `tools/oracle-forms-visualizer/sidecar/` directory
- [x] Create `sidecar/main.py` (FastAPI app)
- [x] Create `sidecar/requirements.txt`
- [x] Implement `/healthz` endpoint
- [ ] Implement `/embed` endpoint (query embedding)
- [x] Implement `/semantic_search` endpoint
- [x] Implement `/deep_search` endpoint (hardened scanner)
- [x] Add SIGTERM handler for graceful shutdown

**Files:**
- `tools/oracle-forms-visualizer/sidecar/main.py` ✅
- `tools/oracle-forms-visualizer/sidecar/README.md` ✅
- `tools/oracle-forms-visualizer/sidecar/requirements.txt` ✅

### 1.3 Sidecar Lifecycle Manager
- [x] Create `server/utils/SidecarManager.js`
- [x] Implement spawn with `detached: false`
- [x] Add health check loop (30s interval)
- [x] Add restart logic (max 3 attempts)
- [x] Add request queueing during startup (~2s window)
- [x] Add graceful shutdown on SIGTERM

**Files:**
- `tools/oracle-forms-visualizer/server/utils/SidecarManager.js` ✅
- `tools/oracle-forms-visualizer/server.js` ✅

---

## Phase 2: Core Search Logic (P1) — Week 2

### 2.1 Adaptive RRF Ranker
- [x] Create `server/utils/ranker.js`
- [x] Implement layer-specific k values (k_rlm=10, k_deep=20, k_vector=60)
- [x] Add confidence multipliers for exact matches
- [x] Implement result deduplication
- [ ] Unit tests for ranking scenarios

**Files:**
- `tools/oracle-forms-visualizer/server/utils/ranker.js` ✅

### 2.2 Search API Refactor
- [x] Refactor `GET /api/search` to use SidecarManager
- [x] Implement parallel layer execution (Promise.all)
- [x] Integrate adaptive RRF for result fusion
- [x] Add error handling per layer (graceful degradation)
- [ ] Add response timing metrics

**Files:**
- `tools/oracle-forms-visualizer/server.js` ✅

### 2.3 LLM Context Formatter
- [ ] Create `server/utils/contextFormatter.js`
- [ ] Implement hybrid Markdown format
- [ ] Add token budget enforcement (top-N=10, snippet=320 chars)
- [ ] Add citation extraction
- [ ] Add call graph builder (mermaid)

**Files:**
- `tools/oracle-forms-visualizer/server/utils/contextFormatter.js` (new)

---

## Phase 3: Frontend Search UI (P1) — Week 2

### 3.1 SearchView Enhancements
- [ ] Add loading states with skeleton UI
- [ ] Implement result cards with provenance badges
- [ ] Add "Why matched" tooltips
- [ ] Add confidence tier indicators (High/Med/Low)
- [ ] Integrate with file preview drawer

**Files:**
- `tools/oracle-forms-visualizer/src/components/SearchView.tsx` (enhance)

### 3.2 Search Results Visualization
- [ ] Add tabbed results (Concepts | Code | Quick)
- [ ] Add syntax highlighting for code snippets
- [ ] Add layer indicator icons
- [ ] Add result count badges

**Files:**
- `tools/oracle-forms-visualizer/src/components/SearchResultCard.tsx` (new)

---

## Phase 4: Performance & Polish (P2) — Week 3

### 4.1 IPC Optimization (Optional)
- [ ] Evaluate Unix Domain Sockets (Uvicorn `--uds`)
- [ ] Benchmark HTTP vs UDS latency
- [ ] Implement if >20% improvement

### 4.2 Dependency Graph Visualization
- [ ] Add D3.js force graph component
- [ ] Extract call relationships from results
- [ ] Implement interactive node clicking

**Files:**
- `tools/oracle-forms-visualizer/src/components/DependencyGraph.tsx` (new)

### 4.3 Observability
- [ ] Add Prometheus-style metrics endpoint
- [ ] Track: search latency, error rate, cache hits
- [ ] Add structured logging (JSON)

---

## Verification Checklist

### Security Tests
- [ ] Injection payloads rejected (OWASP top 10)
- [ ] Path traversal blocked
- [ ] Regex DoS patterns blocked
- [ ] Timeout enforced on stuck queries

### Functional Tests
- [ ] RLM exact key lookup works
- [ ] Vector semantic search returns concepts
- [ ] Deep search finds exact code matches
- [ ] Unified ranking prioritizes exact matches
- [ ] File preview opens from search results

### Performance Tests
- [ ] Cold start < 3s (model loading)
- [ ] Hot query < 100ms
- [ ] 10 concurrent users supported
- [ ] No memory leaks over 1 hour

---

## File Structure (Target State)

```
tools/oracle-forms-visualizer/
├── server.js                      # Main orchestrator (refactored)
├── server/
│   └── utils/
│       ├── safeSearch.js          # Hardened ripgrep wrapper
│       ├── SidecarManager.js      # Lifecycle management
│       ├── ranker.js              # Adaptive RRF
│       └── contextFormatter.js    # LLM context builder
├── sidecar/
│   ├── main.py                    # FastAPI endpoints
│   ├── scanner.py                 # Hardened deep search
│   ├── embedder.py                # Vector embedding
│   └── requirements.txt           # Python deps
├── src/
│   ├── App.tsx                    # (existing, minor updates)
│   └── components/
│       ├── SearchView.tsx         # (enhance)
│       ├── SearchResultCard.tsx   # (new)
│       └── DependencyGraph.tsx    # (new, P2)
└── package.json                   # (add deps if needed)
```

---

## Dependencies to Add

### Python (sidecar/requirements.txt)
```
fastapi>=0.104.0
uvicorn>=0.24.0
chromadb>=0.4.0
sentence-transformers>=2.2.0
pydantic>=2.0.0
```

### Node.js (package.json)
```json
{
  "dependencies": {
    "node-fetch": "^3.3.0"  // For sidecar HTTP calls
  }
}
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Sidecar crash | Lifecycle manager with auto-restart |
| Slow model load | Request queueing + health endpoint |
| Injection attack | Input validation + fixed-strings mode |
| Memory leak | Resource caps + timeout enforcement |
| WSL I/O slow | Store data on native ext4 filesystem |

---

## Definition of Done

- [ ] All P0 security hardening complete
- [ ] All P1 core functionality working
- [ ] Security tests pass
- [ ] Functional tests pass
- [ ] Performance within targets
- [ ] Documentation updated
- [ ] Red Team Round 3 approval (implementation review)
