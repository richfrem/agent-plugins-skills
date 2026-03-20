# markdown-to-msword-converter (V2)

Plugin wrapper that exposes Markdown-to-MS Word conversion as a single nested skill using plugin-local scripts. Upgraded to V2 with L5 Delegated Constraint Verification.

## Installation
### Option 1: Skills Only (End Users)
```bash
npx skills add ./plugins/markdown-to-msword-converter
```
This installs the skills from this plugin.

### Option 2: Full Deployment (Skills + Commands + Agents)
For complete access to all components, use the bridge-plugin skill:
```bash
# Use the bridge-plugin skill to deploy all components
# python ./plugins/plugin-manager/scripts/bridge_installer.py --plugin plugins/markdown-to-msword-converter
```

## Nested Skill

- `skills/markdown-to-msword-converter`

## Scripts

- Bulk wrapper: `./scripts/run_bulk_md_to_docx.py`
- Per-file converter: `./scripts/md_to_docx.py`
- Verification engine: `./scripts/verify_docx.py`
- Folder scope config: `./scripts/folders_to_convert.json`

The per-file converter resolves internal markdown links to `.docx` targets directly so generated Word docs keep clickable references.

## Dependencies

- Intent file: `plugins/markdown-to-msword-converter/requirements.in`
- Lockfile: `plugins/markdown-to-msword-converter/requirements.txt`

Compile lockfile:

```powershell
python -m piptools compile "../../requirements.in" --output-file "../../requirements.txt"
```

Install from lockfile:

```powershell
python -m pip install -r "../../requirements.txt"
```

## Typical usage

```powershell
python ./scripts/run_bulk_md_to_docx.py --dry-run
python ./scripts/run_bulk_md_to_docx.py --overwrite
```
