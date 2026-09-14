---
description: >
  Derive expected values, contracts, and magic strings from a live single source of
  truth (a registry, a config file, a production constant) rather than hardcoding
  literal copies of them into tests and scripts. Prevents the exact fragility this
  rule was written to name: adding one new required question broke 46 tests because
  each had its own hardcoded, literal answer sequence with no shared source.
globs: ["plugins/**/*.py", "plugins/**/*.yaml", "plugins/**/*.yml"]
---

# Rule: Config-Driven / Data-Driven Over Hardcoding

## Why This Rule Exists

On 2026-09-14, adding one new mandatory question (`guidance_compliance_confirmation`)
to every non-force-close transition broke 46 pre-existing tests. Every one of them
had independently hardcoded its own literal expected answer sequence
(`iter(["1", "y"])`, `lambda p: "1"`) instead of deriving the expected question count
and content from `TransitionRegistry` (which already parses the same
`transition_templates.yaml` the production code reads). One semantically small change
became 46 separate, mechanical, error-prone edits — the definition of brittle
hardcoding.

## The Rule

1. **If a value is already declared somewhere authoritative — a YAML registry, a
   production constant, a schema version — read it from there. Never retype it as a
   second, independent literal.** Two independently-maintained copies of the same
   fact will drift; only one of them can be wrong when they do, and finding out which
   costs real debugging time.
2. **Magic strings that mean something specific to the system (an accepted answer
   value, a sentinel, a status code) belong in one named constant the rest of the
   codebase imports** — not retyped as a literal at every call site. See
   `coordinator.py`'s `GUIDANCE_COMPLIANCE_CONFIRM_ANSWER` for the pattern: a single
   `"YES"` definition that every caller (production code, tests, future callers)
   references instead of retyping.
3. **Test fixtures that drive a data-shaped contract (a question sequence, a required
   field list, an edge's `human_questions`) should build their expected input from the
   same registry/loader the production code uses**, not a parallel hardcoded list.
   See `plugins/agent-agentic-os/tests/interview_helpers.py`'s
   `sequential_answers_for_edge()` — it asks `TransitionRegistry.load_default()`
   what an edge actually requires and derives the answer sequence from that, so a
   future universal question addition (or removal) only requires updating the
   registry-reading helper, not every individual test.
4. **A test asserting equality against a version number, a count, or a schema value
   that's already independently derivable from a live query should assert the query
   result matches the imported constant — never ALSO hardcode a second, literal
   expected value for that same constant.** A pattern like
   `assert query_result == CURRENT_SCHEMA_VERSION` is correct and durable;
   `assert CURRENT_SCHEMA_VERSION == 13` immediately below it is redundant, tests
   nothing the first line doesn't already cover, and breaks on every legitimate
   version bump for zero safety benefit. Delete assertions like the second one; don't
   just update the number.
5. **When you must write a magic value into a config/rules file that mirrors
   something computed elsewhere, put a comment naming the authoritative source it
   must stay consistent with**, so a future reader (human or agent) knows where to go
   to verify/update it, rather than discovering the relationship by breakage.

## Where Constants Live: One Shared `control_plane/constants.py`

**Revised 2026-09-14.** An earlier version of this rule recommended colocating each
constant group with the production module that "owned" the concept (state names in
`state_machine.py`, decision types in `adapters.py`, etc.). Review found that split
ownership still left every consumer guessing which file to import from, and produced
real duplication anyway (e.g. `adapters.py` independently re-defining
`GUIDANCE_COMPLIANCE_CONFIRM_ANSWER` and `STATE_*` instead of importing them). This is
standard practice, not a judgment call: **every domain constant used by more than one
file — production or test — lives in exactly one shared module,
`plugins/agent-agentic-os/scripts/control_plane/constants.py`.**

**Before writing any state, decision type, actor, status, task type, or other
domain-meaningful string literal: check `constants.py` first.** If the constant you
need isn't there yet, add it there (grouped with a `# --- <table/concept> ---` header
comment matching the existing sections), then import it — never define it locally,
even "just for this one file," and never assert against both the literal and the
imported constant in the same test (assert only against the constant).

Modules that build a *derived structure* from these raw names still own that
derivation, not the names themselves:
- `control_plane/state_machine.py` imports `STATE_*` from `constants.py` and builds
  `CANONICAL_STATES`/`ALLOWED_TRANSITIONS` (the adjacency DAG) from them — the DAG
  shape is domain logic; the state names it's built from are not.
- `control_plane/adapters.py` imports the SQL-CHECK-constrained value groups
  (`DECISION_TYPES`, `COST_TIERS`, `TASK_TYPES`, `WORKTREE_STATES`,
  `CRITIC_VERDICTS`, `DELEGATION_STATUSES`, `RETROSPECTIVE_*`, `FOLLOW_UP_*`, etc.)
  and renders them into `SCHEMA_SQL`'s `CHECK (... IN (...))` clauses via
  `constants.sql_in_list()`.

**Exception — `SCHEMA_MIGRATIONS` in `adapters.py` is an immutable historical
record.** It captures DDL literally as it was executed against real databases over
time and must NEVER be rewritten to reference `constants.py`, even where a value
overlaps with a shared constant. Only the fresh-create `SCHEMA_SQL` and all Python
logic after `SCHEMA_MIGRATIONS` derive from the shared constants.

## SQL Parameterization: `?` at Runtime, f-strings Only at DDL/Trigger Load Time

A literal string interpolated into a *runtime* query (inside a method, executed with
caller-supplied or looped values) must be passed as a bound `?` parameter, never
spliced into the SQL text via an f-string — even when the interpolated value is a
trusted internal constant, not user input. This was found as a live, if low-risk, bug
during this rule's 2026-09-14 revision: three `adapters.py` methods embedded
`'{DECISION_TYPE_APPROVAL}'` inside a **plain** (non-f) triple-quoted string, so
SQLite was literally comparing against the 25-character text `{DECISION_TYPE_APPROVAL}`
instead of `APPROVAL` — parameterizing forces this class of mistake to fail loudly
(wrong bind-parameter count) instead of silently matching nothing.

- **Runtime query, e.g. inside a method body:** `conn.execute("... WHERE actor = ?", (ACTOR_HUMAN,))` — never `f"... WHERE actor = '{ACTOR_HUMAN}'"`.
- **Module-load-time DDL (`SCHEMA_SQL`) or a `CREATE TRIGGER` body:** an f-string
  interpolating constants (`f"... CHECK (state IN ({sql_in_list(CANONICAL_STATES)}))"`)
  is correct and is the ONLY place this rule permits it — SQLite triggers cannot
  accept bind parameters in their body at all, so there is no `?`-based alternative
  for trigger DDL; `SCHEMA_SQL` itself is likewise built once at import time, not
  per-call, so injection risk does not apply the way it does to a runtime query.

## Repo-Relative Path Resolution: No Fixed `.parent` Chains

Never resolve a repository-root-relative path via a fixed-depth chain like
`Path(__file__).resolve().parent.parent.parent.parent.parent` — it breaks silently
(resolves to the wrong directory, no error) the moment the file moves one level.
Resolve via `git rev-parse --show-toplevel` (see `adapters.py`'s
`_resolve_repo_root()`) or by anchoring on a known marker directory/file (see
`adapters.py`'s `_discover_shared_db_path()`, which walks up looking for `.agents/`
before falling back to `git rev-parse --git-common-dir`), with a fixed-depth walk only
as a last-resort fallback if git is unavailable — never as the primary strategy.

## Where This Applies

- Test fixtures that drive `TransitionCoordinator.coordinate_transition()` or any
  other registry-shaped contract.
- Any hardcoded literal that duplicates a fact already expressed in
  `transition_templates.yaml`, a schema version constant, `constants.py`, or another
  single authoritative production source.
- Any new state, decision type, actor, status, task type, gate name, or other
  domain-meaningful string used in more than one place — define once in
  `control_plane/constants.py`, import everywhere else.

## Non-Negotiables

- Never hardcode an answer sequence for a control-plane edge without first checking
  whether `TransitionRegistry`/`interview_helpers.py`'s data-driven helpers already
  express the same contract.
- Never add a second, literal-hardcoded assertion of a value that's already
  dynamically verified against its authoritative source in the same test.
- Never introduce a new "magic string" answer/sentinel value without first checking
  `control_plane/constants.py`, and adding it there if it's not already present.
- Never interpolate a Python constant directly into a runtime SQL query string; pass
  it as a `?` bind parameter. f-string interpolation is reserved for `SCHEMA_SQL` and
  trigger DDL bodies at module-load time only.
- Never resolve the repository root via a fixed `.parent.parent...` chain; use
  `_resolve_repo_root()` (git-based) or an equivalent marker-anchored resolver.
- Never rewrite `SCHEMA_MIGRATIONS` to reference `constants.py` — it is an immutable
  historical record and keeps its own literal strings forever.
