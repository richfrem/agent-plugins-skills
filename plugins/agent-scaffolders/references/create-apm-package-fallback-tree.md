# Fallback Tree: create-apm-package

| Event | Action |
|-------|--------|
| Missing package name | Stop. Ask user for a name. |
| Invalid name (not kebab-case) | Explain naming rule. Suggest valid alternative. |
| Target directory exists | Warn user. Refuse to overwrite. Offer a different path. |
| Path inside existing plugin | Recommend `/convert-plugin-to-apm` overlay instead. |
| Script fails | Capture error. Suggest manual repair or retry. |
| Validation fails | Point to specific failures in the report. Suggest fixes. |
