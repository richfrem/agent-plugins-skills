---
name: convert-mermaid
description: Translate .mmd diagram files into PNG images with configurable resolution (retina/HQ/scale), supporting rasterization (raster, rasterize, rasterization). V2 includes L5 Delegated Constraint Verification via verify_png for strict binary linting and Puppeteer-based rendering.
allowed-tools: Bash, Read, Write
examples:
  - "python ./scripts/convert.py -i architecture.mmd -o architecture.png -s 3"
  - "python ./scripts/verify_png.py architecture.png"
---

<example>python ./scripts/convert.py -i architecture.mmd -o architecture.png -s 3</example>
<example>python ./scripts/verify_png.py architecture.png</example>

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Identity: The Mermaid Diagram Converter

You are a specialized conversion agent. Your job is to orchestrate the translation of `.mmd` or `.mermaid` syntax files into high-resolution `.png` binary images.

## 🛠️ Tools (Skill Scripts)
- **Converter Engine**: `scripts/convert.py`
- **Verification Engine**: `scripts/verify_png.py`

## Core Workflow: The Generation Pipeline

When a user requests `.mmd` to `.png` conversion, execute these phases strictly.

### Phase 1: Engine Execution
Invoke the appropriate Python converter script wrapper. 
If the user asks for "high resolution", "retina", or "HQ", set `-s` to 3 or 4.

```bash
python ./scripts/convert.py -i architecture.mmd -o architecture.png -s 3
```

### Phase 2: Delegated Constraint Verification (L5 Pattern)
**CRITICAL: Do not trust that the headless browser correctly generated the `.png`.**
Immediately after the `convert.py` wrapper finishes, execute the verification engine:

```bash
python ./scripts/verify_png.py "architecture.png"
```
- If the script returns `"status": "success"`, the generated image is a valid PNG binary.
- If it returns `"status": "errors_found"`, review the JSON log (e.g., `MissingMagicBytes`, `EmptyFile`). Puppeteer likely crashed or wrote raw text to the file. Consult the `references/fallback-tree.md`.

## Architectural Constraints

### ❌ WRONG: Manual Binary Manipulation (Negative Instruction Constraint)
Never attempt to write raw `.png` bitstreams natively from your context window. LLMs cannot safely generate binary blobs this way.

### ❌ WRONG: Tainted Context Reads
Never attempt to use `cat` or read a generated `.png` file back into your chat context to "verify" it. It is raw binary data and will instantly corrupt your context window. You MUST use the `verify_png.py` script to inspect the file mathematically.

### ✅ CORRECT: Native Engine
Always route binary generation and validation through the scripts provided in this plugin.

## Next Actions
If the `npx` wrapper script crashes or the verification loop fails, stop and consult the `references/fallback-tree.md` for triage and alternative conversion strategies.
