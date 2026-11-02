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

## 3. Subscription & Context Constraints

* **Employer / Work vs. Personal Boundaries**:
  * Tools tied to enterprise seats (such as GitHub Copilot) must remain strictly within enterprise/work project boundaries.
  * Personal and sovereign open-source engineering should leverage independent subscriptions (Claude Pro, ChatGPT Plus, Gemini Pro) or local offline models (`llama-server`).
* **Cost-Benefit Gating**:
  * Never invoke expensive frontier reasoning models (e.g. GPT-6 Astra, Claude Opus) for tasks solvable by standard subscription pools or specialized agent platforms.
