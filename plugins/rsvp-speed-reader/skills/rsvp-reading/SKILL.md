---
name: rsvp-reading
plugin: rsvp-speed-reader
description: Converts a document (.txt, .md, .pdf, .docx) into an RSVP (Rapid Serial Visual Presentation) token stream using the Spritz ORP formula. Invoked when a user wants to speed-read a file, generate a token stream at a target WPM, or prepare a Spritz/RSVP reading session.
disable-model-invocation: false
user-invocable: true
allowed-tools: Bash, Read, Write
dependencies: ["pip:docx", "pip:pdfminer"]
keywords: |
  rsvp token stream
  spritz orp alignment
  rapid serial visual presentation
  flash-read wpm paragraphs
argument-hint: "[file-path] [wpm=300] [output-path=./rsvp_output.json]"
version: 1.1.0
tags: [rsvp, speed-reading, document-processing, token-stream, spritz]
---

<example>
<commentary>User wants to speed-read a markdown file at a specific WPM rate.</commentary>
user: "Speed read my notes.md at 300 WPM."
assistant: [triggers rsvp-reading, parses notes.md, generates RSVP token stream at 300 WPM, reports word count and estimated reading time]
</example>

<example>
<commentary>User wants to convert a PDF into an RSVP token stream using ORP alignment.</commentary>
user: "RSVP this article: research.pdf at 500 WPM with ORP alignment."
assistant: [triggers rsvp-reading, parses research.pdf, generates token stream with ORP index per word at 500 WPM]
</example>

<example>
<commentary>User references Rapid Serial Visual Presentation explicitly.</commentary>
user: "Apply Rapid Serial Visual Presentation to my lecture notes at 400 WPM."
assistant: [triggers rsvp-reading, parses lecture notes, generates RSVP stream using Spritz ORP formula]
</example>

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# RSVP Reading Skill

**Rapid Serial Visual Presentation (RSVP)** is a speed reading method popularized by tools like [Spritz](https://spritzinc.com/). Words are flashed one at a time in a fixed position, while one letter per word is highlighted (typically in red) as an eye anchor — the **Optimal Recognition Point (ORP)**. This eliminates horizontal eye movement, the primary bottleneck of traditional reading, enabling speeds of 200-600+ WPM with solid comprehension.

This skill converts any document into an RSVP token stream: each word paired with its ORP index and a calibrated display delay based on your target WPM.

> Full architecture: `references/architecture/architecture.md`
> Acceptance criteria: `references/acceptance-criteria.md`
> Fallback tree: `references/fallback-tree.md`
> Token stream schema: `references/token-stream-schema.md`

---

## Trigger Conditions

Invoke this skill when the user:
- Says "speed read [file]", "RSVP [file]", or "read [file] at [N] WPM"
- Uploads or references a document and asks to "read it fast"
- Requests a token stream or reading session from a document
- Mentions "Rapid Serial Visual Presentation", "Spritz", or "ORP alignment"
- Wants to "flash-read" content at a target WPM
- Asks to convert a document into an RSVP-compatible stream for a reading UI

---

## Discovery Phase

Before executing, collect:

1. **Input file path** - What file should be parsed? (`.txt`, `.md`, `.pdf`, `.docx`)
2. **WPM** - Reading speed in words-per-minute. Default: `300`. Range: `100-1000`.
3. **Output format** - Where to save the token stream JSON? Default: `./rsvp_output.json`
4. **Pause at sentence ends** - Insert extra delay at sentence boundaries? Default: `false`.
5. **ORP alignment** - Use Spritz ORP highlighting formula? Default: `true`.

If any required fields (file path, WPM) are missing, ask for them before proceeding. Reasonable defaults apply for optional fields.

---

## Execution

### Step 1: Parse the Document
```bash
python ./scripts/parse_document.py \
  --input <file_path> \
  --output /tmp/rsvp_words.json
```

### Step 2: Generate Token Stream
```bash
python ./scripts/orp_engine.py \
  --input /tmp/rsvp_words.json \
  --wpm <wpm> \
  --output <output_path>
```

> **ORP accuracy**: The ORP index follows the Spritz formula. Verified by `tests/test_orp_engine.py`.

### Step 3: Confirm Output
Report to the user:
- Total word count
- Estimated reading time at the chosen WPM
- Output file path
- Preview of first 5 tokens

---

## Output Format

Each token in the stream follows the schema in `references/token-stream-schema.md`:
```json
{"w": "Hello", "orp": 1, "delay_ms": 200, "is_sentence_end": false, "is_para_end": false}
```

---

## Confirmation Gate

Before generating for files > 50,000 words, display:
```
This document contains ~{word_count} words.
At {wpm} WPM this will take ~{minutes} minutes to read.
Generating token stream (~{token_count} tokens) to {output_path}.
Proceed? [yes/no]
```

---

## Next Actions

After successful generation, offer:
1. Open the reading session with the `rsvp-comprehension-agent`
2. Adjust WPM and regenerate
3. Parse a different document

---

## Limitations

- **PDF fidelity**: Scanned PDFs or image-heavy PDFs may produce degraded word extraction; recommend `.txt` or `.md` inputs when possible.
- **WPM range**: Very high WPM (>800) may reduce comprehension; the skill will warn but not block.
- **Large documents**: Files >50,000 words trigger a confirmation gate before processing.
- **Language**: ORP formula is optimized for English; other languages may have suboptimal ORP placement.
