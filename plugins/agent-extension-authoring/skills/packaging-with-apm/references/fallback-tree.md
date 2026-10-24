# Fallback Tree: packaging-with-apm

Merged verbatim from the five retired APM skills; one section per mode.

## Mode: create-apm-package

| Event | Action |
|-------|--------|
| Missing package name | Stop. Ask user for a name. |
| Invalid name (not kebab-case) | Explain naming rule. Suggest valid alternative. |
| Target directory exists | Warn user. Refuse to overwrite. Offer a different path. |
| Path inside existing plugin | Recommend `/convert-plugin-to-apm` overlay instead. |
| Script fails | Capture error. Suggest manual repair or retry. |
| Validation fails | Point to specific failures in the report. Suggest fixes. |

## Mode: convert-plugin-to-apm

| Event | Action |
|-------|--------|
| Source plugin not found | Stop. Verify path. |
| Missing plugin.json | Use folder name for metadata. Warn user about missing context. |
| Full mode requested but no output path | Stop. Ask for an output destination. |
| Output path exists | Refuse to overwrite. Suggest new output folder. |
| Migration partially fails | Roll back changes if possible. Report partial success. |
| Dual-manifest conflict | Explain the risk. Suggest removing legacy `plugin.json` or documenting hybrid intent. |
| Validation fails | Point to specific failures in the report. |

## Mode: compile-apm-package

- **Primary**: `apm compile`
- **Secondary**: `apm compile --target <detected_harness>`
- **Manual**: Manually merge context fragments from `.apm/context/` if CLI fails
- **Emergency**: Check `.apm/prompts/` for malformed param placeholders

## Mode: install-apm-package

- **Primary**: `apm install` (auto-target)
- **Secondary**: `apm install --target <detected_harness>`
- **Manual**: Direct primitive authoring in `.apm/` and retry install
- **Emergency**: Run `apm audit` to check for corrupted materialization
