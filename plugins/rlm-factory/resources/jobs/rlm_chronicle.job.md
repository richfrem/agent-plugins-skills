---
# ── Swarm Job: RLM Chronicle Distillation ──────────────────────────────────
# Distills every Chronicle entry in 00_CHRONICLE/ENTRIES into the project RLM cache.
# Uses Claude Haiku (fast/cheap) dispatched in parallel.
#
# Run (from project root):
#   python3 plugins/agent-loops/skills/agent-swarm/scripts/swarm_run.py \
#       --job plugins/rlm-factory/resources/jobs/rlm_chronicle.job.md \
#       --dir 00_CHRONICLE/ENTRIES
#
# Or against a context-bundler manifest:
#   python3 ... --job <this file> --bundle path/to/manifest.json

model: haiku
workers: 10
timeout: 90
ext: [".md"]

post_cmd: >-
  python3 plugins/rlm-factory/skills/rlm-curator/scripts/inject_summary.py
  --profile {profile} --file {file} --summary {output}

vars:
  profile: project
---
Summarize the provided Project Sanctuary Chronicle entry as a single dense plain-text paragraph for the RLM cache. An AI agent will read only this summary—not the original file—so every word must count.

Rules:
1. Start with: Chronicle Entry [N] ([date]):  — extract N from the heading number and date from the Date field.
2. Name every protocol canonized or created (include number and short name).
3. Name every paradox raised and its resolution.
4. Name contributors (Grok, Council, Scribe, Steward, Phoenix, Auditor, etc.) only when architecturally significant.
5. If the entry is a Mnemonic Fracture or test stub with no real content, output: "Chronicle Entry [N]: Mnemonic Fracture / placeholder — no doctrine recorded."
6. Be dense. No filler phrases. No repetition of the filename.
7. Output ONLY the paragraph. Nothing else.
8. PREREQUISITE: Do NOT use tools. Do NOT search the filesystem. Rely ONLY on the piped stdin text.
