# P00 Producer Artifact Contract

Owner: CLI Agents maintainer
Reviewer: independent reviewer selected by the user
Status: PENDING_REVIEW — binding draft; not approved for runtime use

The standalone producer may accept `--measurement-artifact <path>` plus explicit
`--task-id`, `--task-generation-id`, `--run-id`, `--invocation-id`, and
`--attempt-id`. Without the artifact option it preserves current output and exit
behavior and never imports Agentic OS.

The artifact is UTF-8, versioned JSON no larger than 1 MiB with only allowlisted
timing, exit, usage, requested/observed model, producer/install identity, and
correlation fields. It excludes prompts, output, stderr, secrets, source,
arbitrary environment values, and unrestricted paths. It uses the P00 canonical
SHA-256 digest. `producer_namespace`, producer version, and schema version are
required; an unobservable install fingerprint is explicitly unavailable.

Destination behavior is fail-closed. Validate a caller-authorized parent/root;
reject an existing final destination, final symlink, symlinked parent component,
non-regular entry, root escape, `EXDEV`, partial file, and uncertain atomicity.
Create a unique mode-`0600` temporary regular file in the final directory on the
same filesystem, write and fsync it, recheck the final name, atomically create/
rename only into an absent destination, then fsync the directory where supported.
No overwrite or copy fallback is allowed. Ingest ignores temporary/partial files;
their cleanup is separately authorized.

If the CLI succeeds but artifact creation fails, report
`CLI_SUCCESS_METADATA_FAILED` separately. Do not impersonate process failure or
claim complete usage. Consumer-invalid artifacts are `artifact_invalid` and never
automatically re-run the provider. Tests cover absent option, allowlist/digest,
oversize, collision, parent/final symlinks, interruption, permission, and EXDEV.
Independent review is required before this artifact can be marked PASS.
