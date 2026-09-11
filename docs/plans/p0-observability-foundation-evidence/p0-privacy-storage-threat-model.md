# P00 Privacy and Storage Threat Model

Owner: Agentic OS control-plane maintainer
Reviewer: independent reviewer selected by the user
Status: PENDING_REVIEW — binding draft; not approved for runtime use

P0 is local-first. Other local users, backup software, sibling worktrees, and
processes with account/shared-checkout access may read local files. SQLite is not
tamper-resistant audit storage; DB/WAL/SHM, artifacts, and backups may be altered
by a local writer. The system reports this limitation rather than claiming
cryptographic audit integrity.

Prompts, output, stderr, secrets, source contents, raw environment values, and
unallowlisted paths are excluded before persistence. Repository paths and IDs are
redacted/hashed unless required for correlation; hashes remain sensitive metadata.

Where supported, DB, WAL/SHM, artifacts, temporaries, and backups use `0600`
files and `0700` directories. A permission failure or shared-worktree exposure
is a storage/measurement failure requiring user direction. Backups are local and
explicitly authorized; they are never uploaded automatically and must capture a
SQLite-consistent state (checkpoint/backup API or documented equivalent), not a
live DB copy that ignores WAL/SHM. Restore is separately authorized and cannot
overwrite an active DB without exact target and recovery plan.

Thirty days is a diagnostic retention target, not an automatic deletion schedule.
Capacity sampling, observed growth, collection overhead, and safety threshold can
require review sooner. Unknown capacity/samples stays unknown. There is no P0
auto-delete. A later preview inventories telemetry, sidecars, producer temps,
review bundles, interrupted output, and generated planning artifacts with owner,
status, last use, age, protected state, and estimated reclaim. Durable plans,
specs, audit/baseline evidence, learning, active/shared artifacts, symlinks, and
uncertain ownership are protected. Deletion needs a fresh preview, exact targets,
current protection checks, and explicit approval.

Tests must cover permissions, redaction, WAL/SHM, backup/restore, pressure,
no-auto-delete, and protected cleanup exclusions. Independent review is required
before this artifact can be marked PASS.
