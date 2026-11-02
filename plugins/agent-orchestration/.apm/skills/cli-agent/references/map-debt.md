# Map Debt — CLI Agents

| Logged | Cycle ID | Artifact | Friction | Why Not Fixed | Recommended Fix | Severity | Repeat | Status |
|--------|----------|----------|----------|---------------|-----------------|----------|--------|--------|
| 2026-09-10 | WP-576-20260910 | cli-agents consolidation/profile routing | Profile freshness and installed-helper parity were initially under-specified during implementation. | Resolved in this work package with managed helper symlinks, fail-soft routing, snapshot-unverified stale classification, reinstall, audits, and regression tests. | Keep profile snapshots and installed-runtime parity in future setup-health checks. | Tier 2 | 1 | RESOLVED |
| 2026-11-02 | WP-743-20261102 | cli-agent Cursor CLI dispatch | Cursor Agent CLI installed on host machine without active account caused routing probes to either crash or misreport standby CLI as missing or active. | Resolved by auditing `agent status` in `check_routing_readiness.py`, classifying unauthenticated CLI as STANDBY without counting toward active subscription compute pools, and documenting dispatch patterns in `cursor-cli-dispatch.md`. | Keep CLI authentication probes non-destructive and fail-closed across all third-party agents. | Tier 3 | 1 | RESOLVED |

# DEBT-20261102-CURSOR-CLI-DISPATCH

- Status: RESOLVED
- The Cursor Agent CLI (`agent` / `cursor-agent`) was installed on Apple Silicon macOS without an active subscription/account. `check_routing_readiness.py` now non-destructively probes `agent status` to classify unauthenticated state as `STANDBY (Not logged in)`, avoiding false compute pool inflation while preparing architectural dispatch reference for Grok/Composer loops.

# DEBT-20260910-AGY-EFFORT-FLAG

- Status: RESOLVED
- The agy review wrapper previously omitted the required `--effort` flag for explicit medium/high reasoning. `run_agent.py` now accepts `--effort low|medium|high` for agy and forwards it without changing other backends.
