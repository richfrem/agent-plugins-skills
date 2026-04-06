---
name: visual-companion
description: >
  Browser-based visual companion for the Discovery Planning Session. Use when
  the SME needs to see mockups, layout options, or process flow diagrams to answer
  a question. MUST be offered once for consent before use — not invoked automatically.
  Trigger via the discovery-planning skill when visual content would help more than text.
allowed-tools: Bash, Read, Write
---

# Visual Companion

A browser-based companion for showing layout options, process diagrams, and mockups
during a Discovery Planning Session. Available as a tool — not a mode. Accepting the
companion means it is available for questions that benefit from visual treatment; it
does NOT mean every question goes through the browser.

## When to Offer

When you anticipate that upcoming questions will involve visual content (layout options,
process flows, interface arrangements), offer the Visual Companion once for consent:

> "Some of what we are exploring might be easier to understand if I can show it to you
> in a web browser — layout options, process diagrams, side-by-side comparisons. Would
> you like me to use that when it helps? (Requires opening a local URL)"

**This offer MUST be its own message.** Do not combine it with a question or summary.
Wait for the SME's response before continuing. If they decline, proceed with text only.

## Per-Question Routing Decision

Even after the SME accepts, decide FOR EACH QUESTION whether to use the browser or text.
The test: **would the SME understand this better by seeing it than reading it?**

| Use the browser for | Use plain text for |
|---|---|
| Layout mockups and options | Requirement clarification questions |
| Process flow diagrams | Option lists and trade-offs |
| Side-by-side visual comparisons | Scope and priority decisions |
| Interface arrangement choices | Conceptual questions |

A question about a visual topic is NOT automatically a visual question. "What kind of
flow does your team follow?" is a conceptual question — use plain text. "Which of these
two flow diagrams matches how your team works?" is a visual question — use the browser.

## How the Browser Companion Works

The server watches a directory for HTML files and serves the newest one to the browser.
You write content to the screen directory; the SME sees it in their browser and can click
to select options.

### Starting a Session

```bash
# Start the visual server
scripts/start-server.sh --project-dir /path/to/project

# Returns JSON with port, URL, screen_dir, state_dir
# Save screen_dir and state_dir — you will use them every step
```

Tell the SME to open the returned URL. Save the `screen_dir` and `state_dir` paths.

### Writing a Screen

Write an HTML content fragment (not a full HTML document) to a new file in `screen_dir`.
The server wraps it in the page template automatically.

```html
<h2>Which layout works better for your team?</h2>
<p class="subtitle">Consider which one matches how you think about the process</p>

<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>Step-by-Step Flow</h3>
      <p>Linear process — each step must complete before the next begins</p>
    </div>
  </div>
  <div class="option" data-choice="b" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content">
      <h3>Parallel Tracks</h3>
      <p>Multiple things happen at once — teams work independently</p>
    </div>
  </div>
</div>
```

**Never reuse filenames.** Each screen gets a fresh file with a semantic name
(`process-flow.html`, `layout-options.html`, `team-structure.html`).

### Reading the SME's Response

After the SME responds in the terminal, read `$STATE_DIR/events` if it exists.
This contains their browser interactions (clicks, selections) as JSON lines.
Merge with their terminal text to get the full picture.

### Returning to Text

When the next question does not need the browser, push a waiting screen:

```html
<div style="display:flex;align-items:center;justify-content:center;min-height:60vh">
  <p class="subtitle">Continuing our conversation in the terminal...</p>
</div>
```

This prevents the SME from looking at a resolved choice while the conversation has moved on.

### Ending the Session

```bash
scripts/stop-server.sh $SESSION_DIR
```

## Design Principles

- **Show real content when it matters** — for a real business process, use representative labels and flows, not generic placeholders
- **Scale detail to the question** — rough sketches for layout questions, clearer diagrams for process confirmation
- **2–4 options maximum** per screen — more than that overwhelms
- **Iterate before advancing** — if the SME's feedback changes the current screen, write a new version before moving on
- **Explain the question on each page** — the SME should not need to remember what you asked

## File Naming

- Use semantic names: `process-flow.html`, `layout-options.html`, `team-roles.html`
- Never reuse filenames — each screen must be a new file
- For revisions: append version suffix like `layout-v2.html`, `layout-v3.html`
