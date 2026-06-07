# Spec: CLI Billing Reference and Dynamic Model Refactoring

## 1. Problem Statement
Many plugins and scripts across the `agent-plugins-skills` repository hardcode `gpt-5-mini` as a cheap/free default model option under GitHub Copilot CLI or standalone Gemini CLI. As of June 2026, Copilot CLI billing has shifted to paid AI Credits (per-token), and the standalone Gemini CLI is deprecated. We need a systematic way to:
- Stop hardcoding specific model targets like `gpt-5-mini` in every script.
- Dynamically point scripts/workflows to the authoritative `cheapest_models.json` mapping.
- Ensure all agents prioritize the free, self-hosted local Gemma model (`llama` CLI) for simple tasks when running on acceleration-capable hardware.

## 2. Proposed Approaches

### Approach A: Standalone JSON Loader Helper
Create a small, reusable utility function in the `dev-utils` or `cli-agents` plugins that loads `cheapest_models.json` and parses it to retrieve defaults.
* *Pros*: Completely clean, zero duplication.
* *Cons*: Requires other plugins to import from `cli-agents` which violates the loose-coupling architecture policy (ADR 001/004).

### Approach B: Co-located JSON Symlinks & Independent Parsing (Recommended)
Add file-level symlinks of `cheapest_models.json` to the references or scripts directory of every skill that needs it, and have each script independently load the co-located JSON dynamically.
* *Pros*: Follows `plugin-architecture-policy.md` and ADR 003 (zero duplication via symlinks, strict relative path execution).
* *Cons*: Requires managing symlinks in `symlinks.json`.

## 3. Detailed Design

### 3.1. Dynamic Model Resolution in `run_agent.py`
Modify `run_agent.py` to check for `cheapest_models.json` in the parent `references/` directory. If found, load it to populate `_DEFAULT_MODELS`. Fall back to hardcoded defaults otherwise.

```python
def _load_default_models() -> dict[str, str | None]:
    defaults = {
        "copilot": "gpt-5-mini",
        "gemini": "gemini-3-flash-preview",
        "claude": "haiku-4.5",
        "agy": "gemini-3.5-flash",
        "codex": "gpt-5-mini",
        "llama": "gemma-4-12b",
    }
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        ref_path = os.path.join(script_dir, "..", "references", "cheapest_models.json")
        if os.path.exists(ref_path):
            with open(ref_path, "r") as f:
                data = json.load(f)
                for cli, info in data.items():
                    if "model" in info:
                        defaults[cli] = info["model"]
    except Exception:
        pass
    return defaults
```

### 3.2. Auditing and Updating Documentation References
Scan all `.md` and `SKILL.md` files in `plugins/` and replace static "free" or "$0" claims with:
- `Paid (AI Credits)` or `Paid (Per-token)` for Copilot/Gemini.
- Point to local `llama` as the only true zero-cost alternative.

## 4. Verification Plan
1. Run `test_run_agent.py` to confirm that command-building defaults work properly.
2. Confirm the JSON is correctly resolved when run from within a skill subdirectory.
