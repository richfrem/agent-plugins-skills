---
trigger: always_on
---

# Git Workflow Policy

### Non-Negotiables
1. **Never commit directly to `main`** — always use a feature branch.
2. **Never `git push` without explicit, fresh user approval** (Constitution: Human Gate).
3. **One feature branch at a time** — avoid concurrent branches.

### Branch Naming
- `feat/description` — New features
- `fix/description` — Bug fixes
- `docs/description` — Documentation updates
- `refactor/description` — Code refactoring
- `test/description` — Test additions/updates

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):
`<type>: <description>` — types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

### Conflict Resolution
```bash
git fetch origin
git merge origin/main
# Resolve, test, then:
git add . && git commit -m "merge: resolve conflicts with main"
```