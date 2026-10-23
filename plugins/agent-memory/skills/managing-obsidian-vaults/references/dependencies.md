# Wiki and vault dependencies

The Obsidian skill works independently of RLM/vector sibling implementations.
Choose optional layers in the main-session guided setup; use APM for selected
skills rather than the retired obsidian-wiki-engine package or agent wrappers.

## Python

Use this skill's locked requirements.txt for PyYAML and lossless ruamel.yaml
frontmatter/Base operations. Install only within authorized scope. Parser, Canvas
and graph operations use standard-library components where their scripts permit.
Do not install arbitrary unpinned package lists.

## Desktop viewing

Obsidian Desktop is useful for browsing/rendering vault notes, Bases and Canvas.
It is not required merely to run the Python wiki build/query tools. For installation,
use the platform's package manager or the [Obsidian download page](https://obsidian.md/download).

## Model-backed operations

Wiki concept distillation and semantic lint require an available cloud CLI.
The distill_wiki.py implementation detects copilot, then claude, then gemini, with
its configured low-cost model registry; explicit engine selection must be available.
Do not silently use deprecated local/Ollama runners. Model selection and any actual
run remain subject to the requested scope; a dry run makes no model call.

## Optional integration

Use managing-rlm-cache for per-file summary ledgers and managing-vector-db for
semantic retrieval. These are optional skill modes in the same conversation.
Resolve the vector query executable explicitly through AGENT_MEMORY_VECTOR_QUERY.
Keep all consumer configuration under its selected project root, not the skill
installation. Wiki concept summaries remain a separate three-layer format.
