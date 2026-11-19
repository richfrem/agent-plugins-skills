# Cowork Test Playbook

How to test what a Cowork skill can do without being fooled by stale files, missing
attachments or a model's confident summary. Built from the 2026-11-18 experiments.

## Contents

- [Before each test](#before-each-test)
- [Making a run provable](#making-a-run-provable)
- [Building and shipping a binary](#building-and-shipping-a-binary)
- [Prompt shapes that worked](#prompt-shapes-that-worked)
- [Reading a result](#reading-a-result)

## Before each test

1. **New name per build.** Re-uploading under the same name left Cowork on the old files. Use
   a new skill name and ZIP name, or delete the old skill first.
2. **Wait for the sync.** Users reported 2 to 3 minutes before a changed skill was usable.
   Start a new task afterwards.
3. **Finish uploads first.** Send the message only when the attachment shows as uploaded. One
   run saw an empty input folder.
4. **Ask for the skill name and file list first.** A reply that names the wrong skill or old
   files shows a stale load before anything else is wasted.

## Making a run provable

- Bake a **build id** into the binary and ship the expected id in a small text file in the skill's assets folder.
  Check it with `grep -c <id> <file>` without executing. Cowork declined `--version`.
- Ship **expected outputs** and their SHA-256 values; deterministic programs reproduce them
  exactly. Have the agent state `match` or `differ` for each.
- Derive values (colors, hashes) from the input and print a per-run id, so the agent cannot
  guess them.
- Require the agent to paste output verbatim, say which tools failed, and say where files
  were saved.

## Building and shipping a binary

```bash
rustup target add x86_64-unknown-linux-musl
RUSTFLAGS="-C linker=rust-lld -C link-self-contained=yes" \
  cargo build --release --target x86_64-unknown-linux-musl
```

Use `opt-level = "z"`, `lto`, `strip` and `panic = "abort"` to stay near 0.5 MB. Test under
WSL. Inside Cowork run it as `cp <copy> /tmp/prog && chmod +x /tmp/prog && /tmp/prog <dir>`.

For a browser page, build the shared logic as WebAssembly instead:

```bash
rustup target add wasm32-unknown-unknown
cargo build --release --lib --target wasm32-unknown-unknown   # crate-type includes "cdylib"
```

Export plain `extern "C"` functions, embed the `.wasm` as base64 in one HTML file, and load it
with `WebAssembly.instantiate`. That works from a file with no server. Test the module in
Node before shipping.

## Prompt shapes that worked

- State that the program was built from the user's own source and that running it is
  approved. Without it Cowork may refuse.
- Name the folders: attachments land in `/mnt/workspace/input`; run from `/tmp`.
- Ask it to try each available file tool when a file is missing and report every failure,
  instead of accepting "I cannot".
- Ask it to save generated files to the task output folder and show them.

## Reading a result

| Reply says | Meaning |
|---|---|
| Names an older skill or build id | Stale skill; rename and retry |
| "Folder not found" for the skill path | Skill files are not in the sandbox; use the viewer or an attachment |
| "Permission denied", exit 126 | Ran in the workspace; run from `/tmp` |
| Input folder empty | Attachment not uploaded in time |
| Prints your build id and matching hashes | Genuine run of the current files |

Do not ask a test program to dump the environment. The sandbox environment held service
credentials in a test (see [the security notes](cowork-sandbox-findings.md#security)).
