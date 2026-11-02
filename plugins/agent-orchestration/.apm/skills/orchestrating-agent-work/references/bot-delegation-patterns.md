# Bot Delegation Patterns: Synchronous CLI vs. Asynchronous Remote Bots

## 1. Context & Purpose

The `orchestrating-agent-work` skill coordinates tactical workers and execution topologies (Graph DAG, Dual-Loop, Swarm). Historically, execution assumed local, synchronous CLI processes (`claude`, `agy`, `codex`) running inside isolated git worktrees via shell redirection.

Modern multi-agent architectures also incorporate **commercial autonomous agent platforms ("bots")** that operate as independent cloud or sandboxed VMs. This reference defines the orchestration contracts, boundary rules, and handoff protocols when dispatching to or receiving tasks from these platforms.

---

## 2. Platform Taxonomy & Capability Matrix

| Platform | Primary Modality | Strengths & Capabilities | Availability & Subscription | Orchestration Pattern |
|---|---|---|---|---|
| **xAI: Grok Bot** | Autonomous Cloud VM + iOS Frameworks | Outbound PSTN phone calls, disposable agent email (`@mail.grokbot.com`), 1Password/Shop Pay checkouts | Bundled in Cursor Premium ($30/mo) & X Premium+ | **Asynchronous Git / PR Handoff**: Dispatch via committed brief or webhook; results ingest via branch merge. |
| **Anthropic: Claude Duet** | Enterprise SaaS Connector | Proactive channel audit, calendar/inbox risk briefing, human-in-the-loop payment confirmation | US-only enterprise/preview beta; multi-SaaS auth | **Upstream Task Planner**: Claude Duet identifies operational issues and stages work packets for CLI loops. |
| **OpenAI: Dots (Operator)** | Sandboxed Desktop / Web VM | Direct GUI pixel-stream vision-action (mouse clicks, keyboard input), multi-step web forms lacking APIs | US-only preview rollout (ChatGPT Plus / Pro / Enterprise) | **Headless Browser Workhorse**: Dispatch task packet with target URLs and verification criteria. |
| **Google: Gemini Agent (Astra)** | Chrome Browser Engine + Multimodal | Real-time screen sight, live video synthesis, Deep Research cross-tab web dossiers | Global rollout (Google AI Studio / Advanced / AGY) | **Deep Research Layer**: Dispatches multi-source exploration jobs and writes synthesis dossiers. |

---

## 3. Synchronous CLI vs. Asynchronous Bot Execution

```
               ┌────────────────────────────────────────────────────────┐
               │           orchestrating-agent-work                     │
               │         (Strategic Planner / Router)                   │
               └───────────────────┬────────────────────────────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
┌─────────────────────────────────┐         ┌─────────────────────────────────┐
│ Synchronous In-Process CLI      │         │ Asynchronous Remote Bot         │
│ (Dual-Loop / Swarm / Local DAG) │         │ (Grok Bot, Dots, Duet, Astra)   │
├─────────────────────────────────┤         ├─────────────────────────────────┤
│ • Local subprocess / worktree   │         │ • Isolated Cloud / Web VM       │
│ • Stdin redirection (< /dev/null│         │ • No direct stdio REPL pipe     │
│ • Direct file read/write        │         │ • PR, branch, or webhook handoff│
│ • Immediate test suite feedback │         │ • Asynchronous join barrier     │
└─────────────────────────────────┘         └─────────────────────────────────┘
```

---

## 4. Orchestration Boundaries & Invariants

1. **No Stdio Blocking for Remote Bots**: Never attempt to run remote VM bots (`grok`, `dots`) as synchronous terminal pipes or blocking subprocesses in `graph_runner.py` or `agent_orchestrator.py`.
2. **Asynchronous Barrier Steps**: In a Directed Acyclic Graph (`graph-manifest.json`), external bot dispatches must be structured as:
   - Node 1: `write_handoff_brief` (author atomic request packet in `handoffs/`).
   - Node 2: `await_external_artifact` (barrier waiting for branch commit, PR, or human confirmation).
   - Node 3: `verify_and_integrate` (run test suite and compiler checks on returned payload).
3. **Workspace Boundary Rule**:
   - **Enterprise / Work Projects**: GitHub Copilot CLI is permitted.
   - **Sovereign / Personal Research**: Restricted strictly to personal subscriptions (Claude Pro, ChatGPT Plus, Gemini Pro). Never route work-scoped tokens to sovereign research repositories.
4. **Anti-Asch Verification**: Remote bot outputs are untrusted until verified. Run linters, unit tests, and SHA-256 payload integrity audits before admitting changes to repository state.
