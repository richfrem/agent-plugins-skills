I need you to perform a major architectural refactor and feature expansion, turning an existing Obsidian plugin into a dual-representation "Karpathy-style" LLM Wiki and RLM engine.

Here is what you have available to you:
1. `temp/bundles/obsidian-llm-wiki-bundle/obsidian-plugin-bundle.md` (the existing `obsidian-integration` plugin)
2. `temp/bundles/rlm-factory-plugin/rlm-factory-bundle.md` (the `rlm-factory` plugin that we will be integrating with)
3. `temp/obsidian-rlm-llm-wiki/plan.md` (The exact, step-by-step architectural design and execution plan)

To execute this, you must follow the `Execution Order for Sonnet Session` section precisely in `plan.md`. 
Please read all three of these files deeply before writing any code.

CRITICAL DIRECTIVES:
- Delegate all boilerplate (SKILL.md, YAML commands, templates, dependencies.md) to a single batch call via `copilot-cli-agent` using `gpt-5-mini` as defined in the plan. Do not waste your own tokens writing standard boilerplate if it can be offloaded.
- Implement the "Guided Discovery" agent for identifying raw sources during `#wiki-init`.
- The distillation logic MUST deprecate `rlm-distill-ollama`. Use strict cheap-model fallback paths (Copilot Pro -> Claude Haiku -> Gemini Flash) as described in the plan. 
- Do NOT move the user's raw files. Only index them via `raw-sources.json`.
- Output structure inside the `wiki-root` is strictly opinionated (`/wiki`, `/rlm`, `/meta`).

Begin by performing the `copilot-cli-agent` heartbeat, confirm the result, and let me know when you are ready to begin Step 3 (Rename).
