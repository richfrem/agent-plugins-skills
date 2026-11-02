# Autonomous Agent Platforms & Commercial VM Taxonomy

This reference documents external commercial autonomous agent platforms (Grok Bot, Claude Duet, OpenAI Dots/Operator, Gemini Agent) and defines their integration boundaries relative to local developer CLI agents (`claude`, `codex`, `copilot`, `agy`, `cursor-agent`).

---

## 1. High-Level Taxonomy & System Roles

| System | Primary Runtime Environment | Core Differentiators | Best Delegation Target | Integration Interface |
| :--- | :--- | :--- | :--- | :--- |
| **xAI: Grok Bot** | Cloud VM + iOS Frameworks | Autonomous PSTN telephony, native Apple Pay/Link checkout, disposable `@mail.grokbot.com` inbox | Real-world consumer tasks, automated merchant purchases, phone calls, mobile reminders/home control | Asynchronous Git handoff or webhook (No stdio REPL) |
| **Anthropic: Claude Duet** | Enterprise Cloud Connectors | Proactive outreach (initiates messages), human-in-the-loop business triage | Morning briefing, communications channel risk audit, accounting/CRM follow-up | Upstream task planner & brief generator |
| **OpenAI: Dots (Operator)** | Sandboxed Desktop / Web VM | OS-level GUI computer use (pixel vision, mouse/keyboard, raw browser interaction) | Legacy web scraping, multi-step web forms lacking public APIs, headless browser pipelines | Headless GUI workhorse / automation runner |
| **Google: Gemini Agent** | Chrome Engine + Google Workspace | Native enterprise coworker identity, real-time screen/video sight (Project Astra), Deep Research | Cross-tab web navigation, multi-source technical research dossiers, Docs/Sheets automation | Enterprise knowledge layer & research synthesizer |

---

## 2. Platform Deep-Dives & Boundaries

### A. Grok Bot (xAI)
* **Execution Boundary**: Isolated cloud VM paired with device-level iOS framework hooks.
* **Identity & Auth**: Dedicated email (`@mail.grokbot.com`) for independent service signups. Integrated with 1Password and Stripe Link for virtual card payments.
* **Why `run_agent.py` Cannot Pipe It**: Grok Bot does not expose a local POSIX command line or standard stdio REPL. Piped subagent execution will fail.
* **Integration Contract**: **Asynchronous Git & Webhook Handoff**. Developer agents create a dedicated feature branch with a structured markdown task brief. Grok Bot is triggered via webhook or AgentMail, executes the task in the cloud, and commits back to the branch or PR.

### B. Claude Duet (Anthropic)
* **Execution Boundary**: Multi-SaaS enterprise connector framework operating under strict safety boundaries.
* **Identity & Auth**: Authenticated enterprise workspace identity (Google Workspace, Microsoft 365, Slack, Salesforce, QuickBooks).
* **Core Strengths**: Proactively scans communication channels, flags operational risks, and stages sensitive actions behind one-click human approvals.
* **Integration Contract**: **Upstream Task Planner**. Generates four-pillar task specifications and issues work orders to developer CLI loops (`claude -p`, `codex exec`).

### C. Dots / Operator (OpenAI)
* **Execution Boundary**: Sandboxed VM running full desktop and browser viewports.
* **Identity & Auth**: ChatGPT Plus / Enterprise identity, headless session profiles, OpenAI checkout rails.
* **Core Strengths**: Direct vision-action computer use. Interprets pixel streams to click buttons, scroll, and operate desktop software or complex web applications lacking REST APIs.
* **Integration Contract**: **Headless GUI Workhorse**. Used when CLI tools (`curl`, `gh`, `fetch`) cannot traverse multi-factor web forms or dynamic JavaScript canvases.

### D. Gemini Agent & Project Astra (Google)
* **Execution Boundary**: Native Chrome browser runtime + deep Google Workspace integration.
* **Identity & Auth**: Dedicated corporate identity with internal Drive partitions and Slack/Chat presence.
* **Core Strengths**: Multimodal video/audio screen inspection (Astra) and 10-minute Deep Research autonomous web sweeps synthesizing dozens of technical sources into structured Docs.
* **Integration Contract**: **Enterprise Knowledge Synthesizer**. Prepares background research briefs and contextual dossiers for CLI coding agents (`agy`, Claude Code).

---

## 3. Subscription Models & Subscription Pooling

* **Cursor Premium ($30/mo)**: Specifically includes **Grok Bot** access alongside Cursor IDE, cloud agents & automations, code hosting/reviews, and the headless `cursor-agent` CLI with 4x usage pool compared to Plus. This represents a consolidated cost-efficient option over standalone subscriptions.
* **Personal Subscription Stack**:
  - Claude Pro ($20/mo): Claude Code CLI and architectural review.
  - ChatGPT Plus ($20/mo): Operator / Dots GUI computer-use and OpenAI models.
  - Gemini Pro (AGY / Google One): 2M context deep research and multimodal vision.
* **Enterprise Copilot Constraint**: GitHub Copilot is restricted exclusively to work repositories; never used for personal/sovereign research.

---

## 4. Regional Availability & Geo-Fencing Constraints

* **Claude Duet (Anthropic)**: Currently restricted to US-based enterprise beta workspaces. Invocations outside US regions fail or require US enterprise tenancy.
* **Dots / Operator (OpenAI)**: Rolling preview restricted primarily to US ChatGPT Plus/Pro accounts. Users outside the US may encounter waitlist or geo-blocking walls.
* **Grok Bot (xAI)**: Accessible globally through Cursor Premium ($30/mo) or X Premium+ subscriptions, though phone calling relies on supported carrier routing.
* **Gemini Agent / Project Astra (Google)**: Broadest global availability across Google AI Studio and Google One AI Premium tiers.

---

## 5. Architectural Rule: Asynchronous Handoff Invariant
Never attempt to pipe remote VM agents via standard stdio subshell wrappers. Always use asynchronous handoff briefs, git worktrees, or webhooks.
