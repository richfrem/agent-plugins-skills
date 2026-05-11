# Fallback Tree: install-apm-package

- **Primary**: `apm install` (auto-target)
- **Secondary**: `apm install --target <detected_harness>`
- **Manual**: Direct primitive authoring in `.apm/` and retry install
- **Emergency**: Run `apm audit` to check for corrupted materialization
