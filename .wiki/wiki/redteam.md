---
concept: redteam
source: plugin-code
source_file: context-bundler/commands/redteam.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.547266+00:00
cluster: phase
content_hash: 159c157436e13b3e
---

# Redteam

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: redteam
description: Prepare a targeted Red Team Review bundle for an external auditor.
argument-hint: "[threat-model or target-feature]"
allowed-tools: Bash, Read, Write
---

Follow the `red-team-bundler` skill workflow to prepare a security and architecture review package.

## Inputs

- `$ARGUMENTS` — optional threat model (e.g., "auth bypass") or target feature to seed the discovery phase.

## Steps

1. **Phase 1: Discovery** — Conduct a targeted interview to define the Threat Model / Security Focus and negotiate the output format (.md or .zip).
2. **Phase 2: Recap & Confirm** — Present a "Red Team Bundle Plan" including the target topic, threat model persona, and proposed files. Wait for user approval.
3. **Phase 3: Initialize & Draft** — Create a unique temp directory for the review and draft a custom `prompt.md` covering the rules of engagement and severity scoring.
4. **Phase 4: Build Manifest** — Create `file-manifest.json` with the `prompt.md` as the **very first item** to ensure context-first reading by the auditor.
5. **Phase 5: Execute & Handoff** — Invoke the core bundler scripts to generate the final review payload.
6. Inform the user the package is ready for handoff to an external LLM or human auditor.

## Output

A "Red Team Payload": either a single Markdown file (`.md`) combining instructions and code, or a ZIP archive (`.zip`) containing the prompt and source files.

## Edge Cases

- **Sensitive Data:** Explicitly filter out `.env`, keys, and configuration secrets during discovery.
- **LLM Context:** If the payload is for an LLM web UI, favor Markdown; if for an offline auditor, favor ZIP.
- **Prompt Priority:** Ensure the `prompt.md` instructions are always ordered first in the final bundle.

## See Also

- [[context-bundler-redteam]]
- [[context-bundler-redteam]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `context-bundler/commands/redteam.md`
- **Indexed:** 2026-04-17T06:42:09.547266+00:00
