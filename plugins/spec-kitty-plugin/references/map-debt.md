# Map Debt — Spec Kitty Plugin

| Logged | Cycle ID | Artifact | Friction | Why Not Fixed | Recommended Fix | Severity | Repeat | Status |
|--------|----------|----------|----------|---------------|-----------------|----------|--------|--------|
| 2026-06-28 | AUDIT-v3 | spec-kitty-plugin/assets/templates/* | Relative template references to .kittify/ directories | Template files include relative path segments that resolve outside the plugin directory, parsed as violations | Whitelist .kittify path segments in the plugin boundary checker | Warning | NO | OPEN |
