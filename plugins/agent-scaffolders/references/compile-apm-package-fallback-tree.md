# Fallback Tree: compile-apm-package

- **Primary**: `apm compile`
- **Secondary**: `apm compile --target <detected_harness>`
- **Manual**: Manually merge context fragments from `.apm/context/` if CLI fails
- **Emergency**: Check `.apm/prompts/` for malformed param placeholders
