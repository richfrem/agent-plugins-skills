# Cowork Sandbox Findings

What a skill can and cannot rely on once Cowork runs it. Observed on 2026-11-18 in Copilot
Cowork with small test skills (a dependency check, PDF and Word converters, and four tiny
Rust programs). These are observations, not Microsoft guarantees; re-test before relying
on them. The short capability table is in [capabilities and limits](cowork-capabilities-and-limits.md); how to
re-test is in [the test playbook](cowork-test-playbook.md).

## Contents

- [Summary](#summary)
- [Where files live](#where-files-live)
- [Running programs](#running-programs)
- [Tools present](#tools-present)
- [Stale skills](#stale-skills)
- [Verifying a run](#verifying-a-run)
- [Security](#security)
- [Design guidance](#design-guidance)
- [Open questions](#open-questions)

## Summary

| Question | Finding |
|---|---|
| Does Cowork read a skill's files? | Yes. The agent's file viewer reads `SKILL.md`, scripts and assets. |
| Does the command sandbox see them? | Not in the sessions tested last. `/mnt/user-config` was empty and `find / -name <script>` found nothing. |
| Did packaged scripts ever run? | Yes, earlier the same day a skill's Python scripts ran and wrote output files. The cause of the difference is unknown. |
| Can an attached file be run? | Yes, but only from `/tmp` after `chmod +x`. |
| Is anything interactive? | No. Cowork sees command output and files after a command ends. |

Treat "the skill folder is on disk in the sandbox" as unreliable, and design a fallback.

## Where files live

- **Skill files**: readable by the agent's file viewer only (ZIP upload and the OneDrive
  `Cowork\skills` folder behaved the same). Searching the command environment for a bundled
  script or binary found nothing. `/mnt/user-config` was still empty (dated 2026-11-13) in
  those sessions, including for skills placed in the OneDrive `Cowork\skills` folder.
- **Attachments** to a chat arrive in `/mnt/workspace/input`. Send the message only after
  the upload finishes; one run saw an empty `input` folder.
- **Working folder**: `/mnt/workspace/working`, temporary, writable.
- **Outputs**: the agent can save a file from the sandbox to the task output folder, which
  syncs to OneDrive (`Cowork\Tasks\<task>\output`).
- **Skill to session**: the agent said its viewer cannot copy a program file into the
  sandbox. Asking it to try other tools itself was set up but the result was not collected.

## Running programs

- `chmod +x` in `/mnt/workspace/...` reports success and does nothing, so running there
  fails with "Permission denied" (exit 126).
- Copy to `/tmp`, `chmod +x`, run from `/tmp` with `env -i` so the program does not inherit
  the session's credentials (`cp <copy> /tmp/prog && chmod +x /tmp/prog && env -i /tmp/prog <dir>`). A static `x86_64-unknown-linux-musl` Rust
  binary (about 0.4 to 0.5 MB, built with `opt-level=z`, `lto`, `strip`) ran with exit 0
  and wrote files into the working folder.
- Build on Windows with `rustup target add x86_64-unknown-linux-musl` and
  `RUSTFLAGS="-C linker=rust-lld -C link-self-contained=yes"`. Test under WSL.
- Cowork declined a separate `--version` run of an unknown binary ("the environment blocks
  that step") but ran it when the prompt said it is the user's own program and approved.
  Put that approval in the prompt or skill, and prefer checks that do not execute the file.
- The kernel was Linux 6.1 (Microsoft) on x86_64. Plan for one architecture.

## Tools present

Python 3.12, pandoc 3.9, LibreOffice 25.8, pdfplumber, pypdf, pdftotext, tesseract
(English), openpyxl. Not present: PyMuPDF (`fitz`). No network, so `pip install` fails.
A skill zip allows `SKILL.md` plus at most 20 other files, so a 20 MB wheel cannot be
bundled.

## Stale skills

- Re-uploading a ZIP under the same skill name left Cowork running the **old** skill files
  (old expected build id, old message). A skill with a new name loaded the new files.
- Give each test build a new skill name and ZIP name. (Deleting the old skill first may also
  work but is untested.) Check the name and file list Cowork reports on its first reply.
- Related: [install routes](skill-install-routes.md) records that edits to an existing
  folder may not refresh.

## Verifying a run

Patterns that made a run provable:

- Ship the expected outputs and their SHA-256 values in `assets/`; deterministic programs
  reproduced them exactly.
- Bake a build id into the binary and check it with `grep -c <id> <file>` before running.
- Have the program derive values (colors, hashes) from its input and stamp a per-run id, so
  the agent cannot guess them.
- Ask the agent to paste program output verbatim and to say where outputs were saved.

## Security

- A program run in the sandbox inherits the live session environment. A test program that
  dumped it printed 85 variables, about 15 of them service credentials (access tokens,
  certificate keys, passwords, storage links, a monitoring connection string). Any language
  can do this. Cowork refused to paste the full list into chat, but the program had run.
- Cowork's careful behaviour was to inspect the file first and offer `env -i` with sample
  values. A skill that tells the agent "the user approves running it" weakens that check, so
  use the wording only for binaries the user built, and verify the build id first.
- The sandbox had no network in these tests, which limits exfiltration, but output still
  returns to the agent and the chat. Treat a bundled binary like any other code the user
  installs: ship the source, keep it small, and never pass it environment variables.
- Checking `strings` output is weak: static Rust or musl binaries contain `environ`,
  `socket` and `connect` text from the runtime even when the program never uses them. Read
  the source instead.

## Design guidance

- Do not depend on bundled scripts or binaries reaching the sandbox. Prefer tools Cowork
  already has.
- If a script is essential, tell the agent to run it from the skill folder if present,
  otherwise to read it with the viewer and write it to `/tmp` (untested).
- Only for binaries the user built from their own source: say in the skill that the user
  approves running them, and check the build id with `grep` before running.
- Do not build interactive programs; use a deterministic mode with arguments (for example
  a move list) and shipped expected output.
- Asked to make a bundled game playable, Cowork wrote a separate JavaScript HTML copy that
  imitates the Rust program's look; no Rust ran in it. A browser cannot start a Linux
  binary. Only a WebAssembly build of the Rust logic, built off Cowork, lets a page call the
  real code. The tested route is `cargo build --target wasm32-unknown-unknown` with plain
  `extern "C"` exports (see the [test playbook](cowork-test-playbook.md)); `wasm-pack` is only
  needed to pass strings or structs.

## Open questions

- Why scripts ran in some sessions and the skill folder was absent in others.
- Whether the agent can add a skill file to `/mnt/workspace/input` by any tool.
- Whether a binary placed in OneDrive is readable from the sandbox.
- Whether deleting a skill and re-uploading it under the same name refreshes it.
