---
name: rlm-init
description: >
  Initializes the RLM cache for an existing project — creates rlm_profiles.json, scans
  configured directories, and runs the first distillation pass. Trigger when the user says
  "initialize RLM", "set up RLM for this project", "create the RLM profile", or "first-time
  RLM setup". For a guided wizard experience use the rlm-factory-init-agent instead.

  <example>
  user: "Set up the RLM cache for this project"
  assistant: "I'll use the rlm-init agent to create the profile and run the first distillation pass."
  </example>
context: fork
model: inherit
tools: ["Bash", "Read", "Write"]
---

Please run the `rlm-init` skill immediately.
