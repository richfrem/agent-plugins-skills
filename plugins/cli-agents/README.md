# cli-agents

Multi-LLM Task Router Suite. `run_agent.py` dispatches bounded tasks to six backends: Claude CLI, GitHub Copilot, Gemini CLI, Antigravity (Agy), Codex/OpenAI-compatible, and a direct-HTTP local Gemma 4 12B bridge. Also maintains the API Compatibility Proxy — a global routing proxy that lets interactive CLI tools treat a local llama-server as a drop-in Anthropic/OpenAI endpoint (Mode A model replacement).

## Skills

| Skill | Purpose |
|---|---|
| `cli-agent` | One dispatcher for all backends (`--cli claude\|codex\|copilot\|agy\|gemini\|llama`), plus local llama-server setup, model catalog maintenance and project capability setup. |
| `agt-security` | Microsoft Agent Governance Toolkit (AGT) sandbox validation and HMAC key rotation. |
| `maf-adapter` | Microsoft Agent Framework (MAF) manifest validation and local skill simulation. |

`cli-agent` replaces the former `agy-cli-agent`, `claude-cli-agent`, `codex-cli-agent`, `copilot-cli-agent`, `local-llm-bridge`, `local-llm-setup`, `update-cli-models` and `project-setup` skills. Each skill is self-contained: its scripts and references live inside the skill directory as git-tracked files, with no symlinks or copy-manifest entries.

## Architecture: Two Modes

```
Mode A — Interactive model replacement (routing_proxy.py)
  Claude Code / Copilot / Agy / Codex → ANTHROPIC_BASE_URL=:4000
  → routing_proxy → llama-server :8089 (Gemma 4 12B)

Mode B — Task delegation (run_agent.py — the task router)
  Primary agent → run_agent.py cli=<backend>
  ├── cli=llama   → http://localhost:8089/v1/chat/completions  (direct, 2–5s)
  ├── cli=copilot → GitHub Copilot CLI subprocess
  ├── cli=gemini  → Gemini CLI subprocess
  ├── cli=claude  → Claude CLI subprocess
  ├── cli=agy     → Antigravity CLI subprocess
  └── cli=codex   → Codex/OpenAI-compatible CLI subprocess
```

## Plugin Structure

```
cli-agents/
├── .claude-plugin/
│   └── plugin.json               # Claude Code plugin manifest
├── plugin.yaml                   # Plugin manifest (skills list, platforms)
├── README.md                     # This file
├── requirements.in / .txt        # Python dependencies
├── agents/                       # Host sub-agents; also the persona files passed to run_agent.py
│   ├── architect-review.md       # C4/SOLID structural review, coupling, layer violations
│   ├── compliance-reviewer.md    # Project conventions, coding standards, drift detection
│   ├── critical-auditor.md       # Failure-seeking audit of enforced runtime contracts
│   ├── debate-synthesizer.md     # Multi-perspective dialectical synthesis, conflict resolution
│   ├── output-validator.md       # Output guardrail — hallucination, schema, policy checks
│   ├── performance-analyst.md    # Bottleneck analysis — Big-O, I/O amplification, scale
│   ├── pr-reviewer.md            # Diff review — correctness, risk, ship/hold decision
│   ├── red-team-reviewer.md      # Adversarial exploit scenarios, attack surface analysis
│   ├── refactor-expert.md        # Code quality — SOLID/DRY smell taxonomy
│   ├── security-auditor.md       # OWASP vulnerability audit, severity classification
│   ├── self-critic.md            # Reflection loop — task-fit, completeness, assumption check
│   ├── tdd-contract-reviewer.md  # Plan testability and Red-Green contract review
│   └── test-writer.md            # Unit test generation — happy/boundary/edge/failure paths
├── tests/                        # Plugin-level authoring alignment tests
├── references/                   # Plugin-level governance and evolution records
│   ├── plugin-acceptance-criteria.md # Plugin-wide acceptance criteria
│   ├── evolution-log.md          # Plugin evolution history
│   ├── program.md                # Skill improvement lab specification
│   └── self-evolution-profile.md # Self-evolution profile
└── skills/
    ├── cli-agent/                # Consolidated Multi-LLM Router, Local Server & Model Catalog
    │   ├── SKILL.md              # Central dispatcher (Claude, Codex, Copilot, Agy, Llama)
    │   ├── references/           # Backend dispatch guides, fallback tree, model catalogs, setup guides
    │   ├── scripts/              # run_agent.py, run_server.py, routing_proxy.py, sync_cheapest_models.py, unit tests
    │   ├── tests/                # Project-setup contract tests
    │   └── evals/                # Trigger eval suites
    ├── agt-security/             # Microsoft Agent Governance Toolkit (AGT) sandboxing & HMAC controls
    └── maf-adapter/              # Microsoft Agent Framework (MAF) adapter & test harness
```

## Features

1. **Multi-LLM Task Router**: `run_agent.py` routes one bounded task to one selected backend. Named-flag interface (`--cli`, `--model`, `--tier`, `--effort`, `--max-tokens`, `--isolated`, `--require-input`, `--profile`) + legacy positional compat. 54 tests covering command builders, the isolated-flag security contract and the llama HTTP payload.
2. **Local Gemma Direct Bridge**: `cli=llama` POSTs a lean prompt directly to `http://localhost:8089/v1/chat/completions`. No proxy, no 29K system prompt overhead. **Measured: ~2s wall clock** vs 30–60s through Mode A.
3. **13 Expert Agent Personas** (`agents/`): architect-review, compliance-reviewer, critical-auditor, debate-synthesizer, output-validator, performance-analyst, pr-reviewer, red-team-reviewer, refactor-expert, security-auditor, self-critic, tdd-contract-reviewer, test-writer. Each has a structured analytical framework, severity taxonomy, and output format.
4. **Adversarial Pattern Family**: red-team-reviewer (attack surface), debate-synthesizer (dialectical synthesis), output-validator (guardrail), self-critic (reflection loop) — implements the adversarial collaboration and guardrail pattern families.
5. **API Compatibility Proxy**: `routing_proxy.py` (port 4000) routes `claude-*` → Anthropic API, `gemma-*` → llama-server. Mode A only (interactive sessions). Not used for task delegation.
6. **KV Cache Orchestrator**: `kv_cache_orchestrator.py` eliminates cold prefill for repeated calls with the same system prompt. SHA-256 keyed, 4 GiB budget. 31 TDD tests. Proxy integration wired. Eviction scoring inspired by [antirez/ds4](https://github.com/antirez/ds4).
7. **Secure by Default**: Sub-agents default to isolated execution. `--isolated` flag suppresses `--yolo` and `--dangerously-skip-permissions` per backend.
8. **Local LLM Setup**: `skills/cli-agent/references/local-llm-setup-deep-reference.md` — cross-platform setup guide for Day 1 bootstrap and Day 2+ reconfiguration.
9. **Model Catalogs**: `skills/cli-agent/references/*-models.json` and `cheapest_models.json` are the canonical catalogs, also read by the agent-agentic-os control plane. Refresh them per `references/model-catalog-maintenance.md`; preview with `python3 scripts/sync_cheapest_models.py --repository <repo> --dry-run`.
10. **Project Capability Setup**: `skills/cli-agent/references/project-setup.md` builds the reusable `context/agent-capability-profile.json` provider profile.
11. **Unified Fallback Tree**: `skills/cli-agent/references/fallback-tree.md` — one backend per task; halt, log to `map-debt.md` and surface on failure.

## Testing & Benchmarking

### Unit tests (no server required)

```bash
# Whole plugin, from the repository root
python3 -m pytest plugins/cli-agents

# Individual suites, from the skill's scripts/ directory
cd plugins/cli-agents/skills/cli-agent/scripts
python3 -m pytest test_run_agent.py -v               # 54 tests — command builders + isolated security contract
python3 -m pytest test_kv_cache.py -v                # 31 tests — KV cache orchestrator
python3 -m pytest test_routing_proxy.py -v           # 8 tests  — cache collision guard
python3 -m pytest test_model_catalog_contract.py -v  # 14 tests — catalog schema and tiers
python3 -m pytest test_capability_profile.py -v      # 14 tests — capability profile validation, staleness, secrets
python3 -m pytest test_run_agent_runtime.py -v       # 6 tests  — real-subprocess dispatch, effort, executable selection
```

### Start llama-server (required for live tests)

```bash
# In a dedicated terminal
python3 plugins/cli-agents/skills/cli-agent/scripts/run_server.py
curl http://localhost:8089/health    # must return {"status":"ok"}
```

### Mode B — task delegation speed test (the fast path)

```bash
time python3 plugins/cli-agents/skills/cli-agent/scripts/run_agent.py \
  /dev/null /dev/null /tmp/test_b.md \
  "List three capital cities. Be terse." \
  --cli llama
cat /tmp/test_b.md
```

**Measured result: ~2s wall clock, 7+ tok/s.** Example output:

```
Paris, Tokyo, Ottawa.
[run_agent] llama complete → /tmp/test_b.md
python3 ... --cli llama  0.06s user 0.03s system 4% cpu 1.977 total
```

### Mode A — interactive proxy comparison (the slow path)

```bash
# Proxy must be running: launchctl list | grep richfrem
time claude --model gemma-4-12b -p "List three capital cities. Be terse."
```

**Typical result: 40–60s cold** (29K token system prompt prefill at ~30 tok/s), then ~5–10s generation.

**Why Mode B is ~20–30x faster:** Mode A injects Claude Code's full 29K-token system prompt on every request. Mode B sends only the task — typically 50–500 tokens. Same hardware, same GGUF. Context size is the bottleneck.

### KV cache smoke test (proxy + orchestrator)

```bash
python3 plugins/cli-agents/skills/cli-agent/scripts/smoke_test_kv_cache.py
tail -20 ~/.claude/proxy/logs/proxy.log
# First call: [kv-cache] MISS → save
# Second call: [kv-cache] HIT → restore (skips prefill)
```
