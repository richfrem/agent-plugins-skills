---
name: maf-adapter
plugin: cli-agents
description: >-
  Provides validation, setup guidance, and a local test harness simulator to run 
  skills within the Microsoft Agent Framework (MAF).
allowed-tools: Bash, Read, Write
---

# Microsoft Agent Framework (MAF) Adapter

This skill contains the integration specifications and simulation utilities to test and run `.md` agent skills inside Microsoft's MAF engine (v1.6/v1.7.0).

---

## 1. Local Simulation Harness

To test a skill in a simulated MAF execution host locally:
```bash
python3 plugins/cli-agents/scripts/test_harness.py \
  --skill plugins/exploration-cycle-plugin/skills/exploration-workflow/ \
  --input temp/sample_input.txt \
  --instruction "Analyze the repository"
```

---

## 2. Manifest Validation for MAF

Before loading a plugin manifest or skill into MAF, validate it against the target runtime criteria:
```bash
python3 plugins/cli-agents/scripts/test_harness.py --validate --plugin plugins/exploration-cycle-plugin
```

This verifies:
1. Manifest `plugin.json` matches standard keys and is free of banned fields.
2. All commands defined have their matching target files on the correct path.
3. Frontmatter fences (`---`) are valid and contain the required name/description.
