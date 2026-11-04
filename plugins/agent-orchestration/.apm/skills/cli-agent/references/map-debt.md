# Map Debt — CLI Agents

| Logged | Cycle ID | Artifact | Friction | Why Not Fixed | Recommended Fix | Severity | Repeat | Status |
|--------|----------|----------|----------|---------------|-----------------|----------|--------|--------|
| 2026-09-10 | WP-576-20260910 | cli-agents consolidation/profile routing | Profile freshness and installed-helper parity were initially under-specified during implementation. | Resolved in this work package with managed helper symlinks, fail-soft routing, snapshot-unverified stale classification, reinstall, audits, and regression tests. | Keep profile snapshots and installed-runtime parity in future setup-health checks. | Tier 2 | 1 | RESOLVED |
| 2026-11-02 | WP-743-20261102 | cli-agent Cursor CLI dispatch | Cursor Agent CLI installed on host machine without active account caused routing probes to either crash or misreport standby CLI as missing or active. | Resolved by auditing `agent status` in `check_routing_readiness.py`, classifying unauthenticated CLI as STANDBY without counting toward active subscription compute pools, and documenting dispatch patterns in `cursor-cli-dispatch.md`. | Keep CLI authentication probes non-destructive and fail-closed across all third-party agents. | Tier 3 | 1 | RESOLVED |
| 2026-11-02 | WP-744-20261102 | cli-agent Native Fallback Chain & Copilot Guard | In single-backend dispatch, provider rate-limit (429/capacity) exhaustion caused unrecoverable failures without daemon-less pooling; Copilot risked accidental routing to personal tasks. | Resolved by implementing `--fallback-chain` in `run_agent.py` with automatic 429/capacity failover, adding strict `--allow-copilot` governance gating, and adding `--validate-chain` readiness testing in `check_routing_readiness.py`. | Keep multi-subscription fallback foreground-native and strictly enforce boundary guards. | Tier 2 | 1 | RESOLVED |
| 2026-11-04 | WP-CATALOG-20261104 | cli-agent model catalogs (claude/codex/agy) and select_model | Catalogs (verified 2026-09-09) lacked the models in use (claude-sonnet-5-5, claude-haiku-5-5, claude-opus-5-5, gpt-6-luna and the GPT-6.1 family, gemini-4-argon); codex-models.json lacked gpt-6-luna although cheapest_models.json already named it; select_model raised TypeError on a null-priced model in a tier (pre-existing for agy low tier); tier equality tests pinned a stale picker snapshot. | Refreshed from official pricing pages plus the live agy/codex pickers, cross-checked against a real Claude Code session cost ($29.55 vs $29.49 computed); select_model now sorts unknown prices last (2 tests added); snapshot tests updated with dated evidence. | Re-run this refresh whenever a picker changes; add a catalog-staleness check (updated date vs today) to the readiness probe. | Tier 2 | 1 | RESOLVED |
| 2026-11-04 | WP-CATALOG-20261104 | sync_cheapest_models.py | Script expects plugins/agent-orchestration/skills/cli-agent/references but the repo layout is plugins/agent-orchestration/.apm/skills/cli-agent/references, so it errors; cheapest picks were updated by hand in the canonical cli-agent copy only, other plugin copies of cheapest_models.* were not synchronised. | Out of scope for the catalog refresh. | Fix the script path (support .apm layout) and re-sync the other copies of cheapest_models.json/md. | Tier 3 | 1 | OPEN |
| 2026-11-04 | WP-CATALOG-20261104 | test_run_agent_runtime.py::test_failure_does_not_echo_source_prompt | Fails on main before this change: a failed dispatch prints the argv including the isolated source text. | Pre-existing; unrelated to catalogs. | Redact the prompt argument in the error path of run_agent.py. | Tier 2 | 1 | OPEN |


# DEBT-20261104-MODEL-CATALOG-REFRESH

- Status: RESOLVED (catalog refresh and select_model fix); sync script path and run_agent prompt-echo remain OPEN above.
- Sources: platform.claude.com pricing page (Sonnet 5.5 $2/$10, Opus 5.5 $4/$20, Haiku 5.5 $0.10/$0.50 up to 100K prompt tokens), developers.openai.com pricing page (GPT-6 family), aistudio.google.com pricing page (Gemini 4 Argon, 3.6/3.8 Flash), `agy models`, and the Codex CLI model cache.
- Cross-check: a real Claude Code session on claude-sonnet-5-5 (4.0k input, 592.9k output, 175.5M cache read, 1.5M cache write at the 1h rate) reported $29.55; the refreshed catalog prices it at $29.49. A stand-in with the older claude-sonnet-5 rates overestimated by 52%, so telemetry must use exact model ids.
- Cheapest picks changed: claude haiku-4-5 to haiku-5-5; codex already gpt-6-luna (now present in codex-models.json); agy unchanged (gemini-3.8-flash).
- Not asserted: context/output limits for the 5.5 Claude models, hosted agy Claude prices, Gemini 3.7 Flash price (not on the page).

# DEBT-20261102-NATIVE-FALLBACK-CHAIN

- Status: RESOLVED
- Implemented native zero-daemon multi-subscription fallback in `run_agent.py` (`--fallback-chain agy,codex`). Failover triggers exclusively on recognized rate-limit or capacity exhaustion errors (`429`, `ResourceExhausted`, `at capacity`, `resets in`), safely unlinking partial outputs and avoiding wasted quota on non-quota task errors.
- Enforced hard governance boundary requiring explicit `--allow-copilot` flag before `copilot` can be included in dispatch or fallback chains.
- Built `--validate-chain` pre-flight testing mechanism into `check_routing_readiness.py`.

# DEBT-20261102-CURSOR-CLI-DISPATCH

- Status: RESOLVED
- The Cursor Agent CLI (`agent` / `cursor-agent`) was installed on Apple Silicon macOS without an active subscription/account. `check_routing_readiness.py` now non-destructively probes `agent status` to classify unauthenticated state as `STANDBY (Not logged in)`, avoiding false compute pool inflation while preparing architectural dispatch reference for Grok/Composer loops.

# DEBT-20260910-AGY-EFFORT-FLAG

- Status: RESOLVED
- The agy review wrapper previously omitted the required `--effort` flag for explicit medium/high reasoning. `run_agent.py` now accepts `--effort low|medium|high` for agy and forwards it without changing other backends.
