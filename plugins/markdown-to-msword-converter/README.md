# markdown-to-msword-converter (V2)

Plugin wrapper that exposes Markdown-to-MS Word conversion as a single nested skill using plugin-local scripts. Upgraded to V2 with L5 Delegated Constraint Verification.

## Installation

### Option 1: From a Marketplace (Recommended)
```bash
/plugin marketplace add <marketplace-url>
/plugin install markdown-to-msword-converter
```
For skills-only portability across all agents (Claude, Gemini, Copilot, etc.):
```bash
npx skills add <marketplace-url>/plugins/markdown-to-msword-converter
```

### Option 2: From GitHub Directly
```bash
# Skills only
npx skills add richfrem/agent-plugins-skills --path plugins/markdown-to-msword-converter

# Full plugin (Claude Code native)
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install markdown-to-msword-converter
```

### Option 3: Local Development Checkout
```bash
npx skills add ./plugins/markdown-to-msword-converter
```

## Nested Skill

- `skills/markdown-to-msword-converter`

## Scripts

- Bulk wrapper: `./skills/markdown-to-msword-converter/scripts/run_bulk_md_to_docx.py`
- Per-file converter: `./skills/markdown-to-msword-converter/scripts/md_to_docx.py`
- Verification engine: `./skills/markdown-to-msword-converter/scripts/verify_docx.py`
- Folder scope config: `./skills/markdown-to-msword-converter/scripts/folders_to_convert.json`

The per-file converter resolves internal markdown links to `.docx` targets directly so generated Word docs keep clickable references.

## Dependencies

- Intent file: `plugins/markdown-to-msword-converter/requirements.in`
- Lockfile: `plugins/markdown-to-msword-converter/requirements.txt`

Compile lockfile:

```powershell
python -m piptools compile "requirements.in" --output-file "requirements.txt"
```

Install from lockfile:

```powershell
python -m pip install -r "requirements.txt"
```

## Typical usage

```powershell
python ./scripts/run_bulk_md_to_docx.py --dry-run
python ./scripts/run_bulk_md_to_docx.py --overwrite
```
