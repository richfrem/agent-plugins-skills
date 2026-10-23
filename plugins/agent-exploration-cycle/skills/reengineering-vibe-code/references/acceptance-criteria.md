# Acceptance Criteria: reengineering-vibe-code

The original per-skill criteria are kept next to this file: [reengineer](vibe-reengineer-acceptance-criteria.md), [browser audit](vibe-browser-audit-acceptance-criteria.md), [behavioral tests](vibe-behavioral-test-capture-acceptance-criteria.md), [domain extraction](vibe-domain-extractor-acceptance-criteria.md), [slice migrator](vibe-slice-migrator-acceptance-criteria.md), [spec packager](vibe-spec-packager-acceptance-criteria.md), [architecture package](vibe-togaf-architect-acceptance-criteria.md). The consolidated criteria are below.

## 1. Routing
- [ ] Triggers on "harden our local prototype", "rescue this vibe-coded app", "audit the UI", "capture characterization tests", "extract the domain", "migrate a slice".
- [ ] Does not trigger when there is no existing code; that is `running-exploration-cycle`.

## 2. Truth and safety
- [ ] The truth order is honored: `specs/REQS.md` over `tests/characterization/` over `/domain` over derived specs over prototype code; a conflict is logged `HUMAN_REQUIRED`, never silently resolved.
- [ ] Auth, billing, cryptography and compliance logging are never rewritten autonomously; a slice touching them stops until a valid, hash-bound `human-approval.json` exists.
- [ ] Destructive work runs in an isolated workspace (`os-control-worktree` skill); without one the skill halts.

## 3. Safety net
- [ ] Characterization tests assert legacy behavior verbatim, including quirks, and run offline against local fixtures.
- [ ] Fixtures contain no absolute paths, hostnames or secrets; the portability report `temp/fixture-portability-report.json` shows `fixtures_portable: true`.

## 4. Domain and slices
- [ ] `/domain` has no framework, UI, persistence, vendor SDK or raw I/O imports; `domain-purity-auditor` reports `purity_certified: true` at 100 percent.
- [ ] `semantic-drift-auditor` reports `drift_certified: true` against `specs/domain-lexicon.json`.
- [ ] Only `certification-verifier` writes `slice_certified: true`; the migrator never self-certifies. After two rejections for the same issue the user is asked to decide.

## 5. Contract and handoff
- [ ] The requirements contract is `specs/REQS.md` (with `specs/domain-lexicon.json`); the five architecture-package documents are produced only when the user wants the full package.
- [ ] The five architecture questions are asked one at a time and the expert signs off the specs before Phase 5.
- [ ] The final handoff goes through `handing-off-to-engineering` to `exploration/handoffs/handoff-package.md`; no third-party tool folders are created.
- [ ] Final verification shows 100 percent characterization parity.
