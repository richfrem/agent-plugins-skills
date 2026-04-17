---
concept: fallback-tree
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/rsvp-reading/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.215546+00:00
cluster: print
content_hash: d7c6edfebc250426
---

# Fallback Tree

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Fallback Tree

## FB-01: Unsupported File Format

**Trigger:** Input file has extension not in `.txt`, `.md`, `.pdf`, `.docx`

**Steps:**
1. Print: `Error: Unsupported file type '{ext}'.`
2. List supported extensions.
3. Ask user to convert the file (suggest `pandoc` for other formats).
4. Exit with code 1.

---

## FB-02: PDF Dependency Missing (pdfminer.six)

**Trigger:** `import pdfminer` raises `ImportError`

**Steps:**
1. Print: `Error: pdfminer.six not installed.`
2. Print: `Run: pip install pdfminer.six`
3. Exit with code 1.
4. Do NOT fall back to raw PDF byte parsing.

---

## FB-03: DOCX Dependency Missing (python-docx)

**Trigger:** `import docx` raises `ImportError`

**Steps:**
1. Print: `Error: python-docx not installed.`
2. Print: `Run: pip install python-docx`
3. Exit with code 1.

---

## FB-04: File Not Found

**Trigger:** `--input` path does not exist on disk

**Steps:**
1. Print: `Error: File not found: {path}`
2. Confirm the path with the user before re-running.
3. Exit with code 1.

---

## FB-05: Empty Document

**Trigger:** Parser returns 0 tokens

**Steps:**
1. Print: `Warning: No words found in '{file}'. Document may be empty or image-based.`
2. If PDF: suggest OCR (e.g., `pytesseract`) as a post-step.
3. Exit with code 0 (do not generate empty stream file).

---

## FB-06: WPM Out of Range

**Trigger:** `--wpm` value is < 100 or > 1000

**Steps:**
1. Print: `Error: WPM must be between 100 and 1000. Got: {wpm}`
2. Suggest: "Try 200 for slow, 300 for average, 600 for speed reading."
3. Exit with code 1.


## See Also

- [[procedural-fallback-tree-adr-management]]
- [[procedural-fallback-tree-agent-swarm]]
- [[procedural-fallback-tree-dual-loop]]
- [[procedural-fallback-tree-learning-loop]]
- [[procedural-fallback-tree-orchestrator-routing]]
- [[procedural-fallback-tree-red-team-review]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/rsvp-reading/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.215546+00:00
