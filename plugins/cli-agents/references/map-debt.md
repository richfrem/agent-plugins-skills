# Map Debt — CLI Agents

| Logged | Cycle ID | Artifact | Friction | Why Not Fixed | Recommended Fix | Severity | Repeat | Status |
|--------|----------|----------|----------|---------------|-----------------|----------|--------|--------|
| 2026-09-10 | WP-576-20260910 | cli-agents consolidation/profile routing | Profile freshness and installed-helper parity were initially under-specified during implementation. | Resolved in this work package with managed helper symlinks, fail-soft routing, snapshot-unverified stale classification, reinstall, audits, and regression tests. | Keep profile snapshots and installed-runtime parity in future setup-health checks. | Tier 2 | 1 | RESOLVED |
# DEBT-20260910-AGY-EFFORT-FLAG

- Status: RESOLVED
- The agy review wrapper previously omitted the required `--effort` flag for explicit medium/high reasoning. `run_agent.py` now accepts `--effort low|medium|high` for agy and forwards it without changing other backends.
