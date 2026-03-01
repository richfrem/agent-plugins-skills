---
name: env-helper
description: |
  Resolves shared ecosystem environment constants (HuggingFace credentials,
  dataset repo IDs, project root path) for any plugin without depending on
  internal shared libraries.
trigger: on_demand
---

# env-helper Skill

## Purpose
Provides a single, zero-dependency Python helper (`env_helper.py`) that any plugin can call to safely resolve ecosystem constants.

## Usage

```bash
# Resolve a single key
python3 plugins/env-helper/scripts/env_helper.py --key HF_TOKEN

# Dump all known constants as JSON
python3 plugins/env-helper/scripts/env_helper.py --all

# Get the full HuggingFace upload config block
python3 plugins/env-helper/scripts/env_helper.py --hf-config
```

## Importing in Python
```python
import sys
sys.path.insert(0, "plugins/env-helper/scripts")
from env_helper import resolve, resolve_hf_config

token = resolve("HF_TOKEN")
hf_config = resolve_hf_config()
```

## Resolution Order
1. `os.environ` (process environment)
2. `.env` file at project root (walked up from script location)
3. Built-in defaults (e.g. `HF_DATASET_REPO=SanctuaryDB`)

## Known Constants
| Key | Description | Default |
|:---|:---|:---|
| `HF_TOKEN` | HuggingFace API token | *(required)* |
| `HF_USERNAME` | HuggingFace username | *(required)* |
| `HF_DATASET_REPO` | Dataset repo name | `SanctuaryDB` |
| `HF_LINEAGE_FOLDER` | Remote lineage folder name | `lineage` |
| `HF_SOUL_TRACES_FILE` | Remote JSONL traces path | `data/soul_traces.jsonl` |
