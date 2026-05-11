# Fallback Tree: convert-plugin-to-apm

| Event | Action |
|-------|--------|
| Source plugin not found | Stop. Verify path. |
| Missing plugin.json | Use folder name for metadata. Warn user about missing context. |
| Full mode requested but no output path | Stop. Ask for an output destination. |
| Output path exists | Refuse to overwrite. Suggest new output folder. |
| Migration partially fails | Roll back changes if possible. Report partial success. |
| Dual-manifest conflict | Explain the risk. Suggest removing legacy `plugin.json` or documenting hybrid intent. |
| Validation fails | Point to specific failures in the report. |
