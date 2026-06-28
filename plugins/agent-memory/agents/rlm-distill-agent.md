---
name: rlm-distill-agent
description: >
  Distills files into dense RLM summaries using the configured CLI backend (Copilot, Agy,
  or Claude). Runs the full distillation pipeline for new or updated files. Trigger when
  the user says "distill files", "run RLM distillation", "generate summaries for new files",
  or "update the RLM ledger".

  <example>
  user: "Run distillation on the new files I added"
  assistant: "I'll launch the rlm-distill-agent to summarize the new files into the RLM cache."
  </example>

  <example>
  user: "Generate RLM summaries for the plugins/ directory"
  assistant: "I'll dispatch the rlm-distill-agent to distill those files."
  </example>
context: fork
model: inherit
tools: ["Bash", "Read", "Write"]
---

Please run the `rlm-distill-agent` skill immediately.
