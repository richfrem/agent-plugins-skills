# rsvp-speed-reader

A plugin and skill for AI-assisted **Rapid Serial Visual Presentation (RSVP)** speed reading.

## Installation
### Option 1: Skills Only (End Users)
```bash
npx skills add ./plugins/rsvp-speed-reader
```
This installs the skills from this plugin.

### Option 2: Full Deployment (Skills + Commands + Agents)
For complete access to all components, use the bridge-plugin skill:
```bash
# Use the bridge-plugin skill to deploy all components
# python ./plugins/plugin-manager/scripts/bridge_installer.py --plugin plugins/rsvp-speed-reader
```

## What is RSVP Speed Reading?

RSVP is a speed reading method popularized by tools like [Spritz](https://spritzinc.com/). Instead of scanning across a page, words are **flashed one at a time in the same fixed position**. One letter in each word is highlighted (typically in red) as a visual anchor called the **Optimal Recognition Point (ORP)** — the character your eye naturally gravitates to for fastest recognition.

This approach dramatically reduces eye movement, which is one of the main bottlenecks in traditional reading. At calibrated speeds (200-600+ WPM), readers can increase throughput while maintaining solid comprehension.

## What this Plugin Does

This plugin converts any document into a structured **RSVP token stream** — a JSON array where each entry contains the word, its ORP index, display delay, and flags for sentence/paragraph boundaries. The token stream can then be consumed by a UI component or agent to drive a reading session.

**Supported input formats:** `.txt`, `.md`, `.pdf`, `.docx`

## Skills

| Skill | Description |
|---|---|
| `rsvp-reading` | Parses a document and generates an RSVP token stream with ORP alignment and WPM-based delays |

## Agents

| Agent | Description |
|---|---|
| `rsvp-comprehension-agent` | Session manager for interactive RSVP reading with pause/resume/speed control |

## Dependencies

Declare dependencies in `requirements.in`, then compile:

```bash
cd plugins/rsvp-speed-reader
pip-compile requirements.in
pip install -r requirements.txt
```

**Core deps:** `pdfminer.six` (PDF parsing), `python-docx` (DOCX parsing). Plain `.txt`/`.md` use stdlib only.

## Directory Structure

```text
rsvp-speed-reader/
├── .claude-plugin/plugin.json
├── README.md
├── requirements.in
├── agents/
│   └── rsvp-comprehension-agent.md
├── hooks/
├── skills/
│   └── rsvp-reading/
│       ├── SKILL.md
│       ├── scripts/
│       │   ├── parse_document.py    <- file ingestion (.txt .md .pdf .docx)
│       │   └── orp_engine.py        <- ORP calc + token stream generation
│       ├── references/
│       │   ├── token-stream-schema.md
│       │   ├── acceptance-criteria.md
│       │   └── fallback-tree.md
│       └── examples/
└── rsvp-speed-reader-architecture.mmd
```

## Plugin Components

### Skills
- `rsvp-reading`

