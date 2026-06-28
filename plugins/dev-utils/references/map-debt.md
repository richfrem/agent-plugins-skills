# Map Debt — Dev Utils

| Logged | Cycle ID | Artifact | Friction | Why Not Fixed | Recommended Fix | Severity | Repeat | Status |
|--------|----------|----------|----------|---------------|-----------------|----------|--------|--------|
| 2026-06-28 | AUDIT-v3 | dev-utils/references/* | Doc refs to project root references/assets directories | Documentation diagrams and indexes point to top-level folder layout, which boundary checker flags as outside plugin | Update boundary checker to ignore documentation files (.md, .mmd) or ignore parent root paths | Warning | NO | OPEN |
