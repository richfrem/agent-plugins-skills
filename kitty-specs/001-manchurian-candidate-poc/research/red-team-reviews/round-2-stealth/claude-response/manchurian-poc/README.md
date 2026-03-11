# Manchurian Candidate POC
## AI Agent Prompt Injection via EXIF Metadata

**Security Research Only**  
Payload is harmless — writes a `.env` variable and forensic hash files only.

---

## Overview

Demonstrates that a seemingly benign L4 AI plugin can execute arbitrary
payloads delivered via crafted image EXIF metadata, exploiting the trust
boundary between an orchestrator's granted permissions and a vulnerable
sub-agent's behaviour.

## Project Structure

```
manchurian-poc/
├── README.md
├── run_poc.sh                          # Full demo runner
├── pipeline_simulator.py               # Agent pipeline (mock LLM calls)
├── artifacts/
│   ├── create_poisoned_image.py        # Generates poisoned JPEG
│   └── (sample_batch_001.jpg)          # Generated at runtime
├── forensics/                          # Created at runtime
│   ├── hash_timeline.json              # Pre/post .env hashes
│   ├── execution_proof.json            # Payload-written proof
│   └── run_summary.json                # Pipeline run summary
├── plugins/image-metadata-processor/
│   ├── plugin.json                     # Plugin manifest
│   ├── skills/image-resizer/SKILL.md   # Surface vector (benign)
│   └── agents/profile-optimizer/agent.md  # Vulnerable sub-agent
└── docs/
    └── FINDINGS_REPORT.md              # Full red team findings
```

## Quick Start

```bash
# Run full POC in one command
./run_poc.sh

# Or step by step:
python3 artifacts/create_poisoned_image.py
python3 pipeline_simulator.py artifacts/sample_batch_001.jpg
```

## Expected Output

1. `artifacts/sample_batch_001.jpg` — poisoned JPEG created
2. `.env` — modified by payload (MANCHURIAN_ACTIVATED=true)
3. `forensics/hash_timeline.json` — hash divergence proves execution
4. `forensics/execution_proof.json` — payload self-reports its own execution
5. `forensics/run_summary.json` — pipeline summary

## Requirements

- Python 3.8+
- No external dependencies (stdlib only)
