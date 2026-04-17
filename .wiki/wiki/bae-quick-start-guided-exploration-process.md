---
concept: bae-quick-start-guided-exploration-process
source: plugin-code
source_file: exploration-cycle-plugin/BAE-start-guide.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.560665+00:00
cluster: session
content_hash: 7659b283085476bd
---

# BAE Quick Start — Guided Exploration Process

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# BAE Quick Start — Guided Exploration Process

Purpose
-------
A concise how-to for Business Area Experts (BAEs) to start a guided exploration session using the exploration-cycle-plugin. No technical background required.

---

How to start
------------
Just say it in plain language. The canonical phrase is:

> **"Let's explore [your idea]."**

Or any of these:
- "I have an idea I want to explore"
- "Start an exploration session"
- "Let's think through this before building anything"
- "Help me figure out what we should build"

The `exploration-workflow` skill takes it from there. It asks one question at a time, keeps you in control at every gate, and adapts to what you actually need — whether that's a working prototype, a set of requirements, a process map, or a "don't build this" conclusion.

---

What happens next
-----------------
The session runs in four phases. You only move forward when you say so.

**Phase 1 — Problem Framing**
Five guided questions that establish what problem you're solving, who's affected, and whether software is even the right answer. Produces a Discovery Plan you approve before anything else happens.

**Phase 2 — Visual Blueprinting** *(optional for some session types)*
You see layout or structure options in plain language before anything is built. You pick one. Nothing gets built until you confirm.

**Phase 3 — Build** *(skipped for docs/analysis sessions)*
The AI builds what was agreed in Phase 1 and Phase 2. Each component is checked against the plan before moving to the next. You get a walkthrough before anything is locked in.

**Phase 4 — Handoff**
The session wraps up with a risk check (four yes/no questions) and a packaged output ready for whoever needs it next — whether that's you deploying it directly, a security team reviewing it, or an engineering team building from the spec.

---

The four session types
----------------------
Tell the assistant which type fits, or it will ask:

| Type | Use when | Phases |
|------|----------|--------|
| **New app** | Building something from scratch | All 4 |
| **Feature for existing app** | Adding to something that already exists | Phase 1 required, rest flexible |
| **Analysis or documentation** | No code — requirements, process maps, policies, reports | Phases 1 & 4, Phase 2 optional |
| **Spike** | Exploring a question or technology | Phase 1 required, rest flexible |

---

Choosing how the AI handles the heavy lifting
----------------------------------------------
Early on, the assistant will ask how to handle complex tasks. Three options:

1. **I have GitHub Copilot Pro** — uses free `gpt-5-mini` for mechanical tasks, one premium request for complex ones (batched for value)
2. **No Copilot** — uses `haiku` for simple tasks, `sonnet` for complex ones
3. **I'll handle it myself** — everything happens in this session directly

If you're unsure, choose option 3. You can change later.

---

Gates and approvals
--------------------
The session will never move forward without your explicit sign-off. You'll see these checkpoints:

- **Discovery Plan approval** — Phase 1 cannot complete until you say "looks good". Nothing gets built before this.
- **Layout confirmation** — Phase 2 requires you to choose a direction before building starts.
- **Phase completion gates** — after each phase, the assistant presents a plain-language summary and waits for your confirmation before marking it complete.

If you say "this isn't going to work" at any point — the session closes cleanly, saves what was learned, and that's a valid outcome.

---

Risk check at handoff (Phase 4)
--------------------------------
Before packaging the final output, the assistant asks four yes/no questions:

1. Does this handle personal information or sensitive data?
2. Will it be used by people outside your team, or be public-facing?
3. Does it require access to production systems or high-privilege tools?
4. Does it involve financial transactions or regulatory compliance?

Based on your answers,

*(content truncated)*

## See Also

- [[quick-start-zero-context-guide]]
- [[quick-start-zero-context-guide]]
- [[agent-execution-prompt-exploration-cycle-plugin-upgrade]]
- [[opportunity-3-exploration-design]]
- [[the-exploration-cycle-plugin-democratizing-discovery]]
- [[exploration-cycle-plugin-design-recommendation]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/BAE-start-guide.md`
- **Indexed:** 2026-04-17T06:42:09.560665+00:00
