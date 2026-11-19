# Cowork Capabilities and Limits

What a skill can ask Cowork to do, and what it cannot rely on. Each row carries an evidence
label so the table is not mistaken for a guarantee.

- **Observed**: seen in a Cowork reply or a local test on 2026-11-18.
- **Reported**: stated by a Cowork user from their own use, not re-tested here.
- **Not tested**: designed, but no Cowork result collected.

Details and the reasoning behind each row are in
[the sandbox findings](cowork-sandbox-findings.md).

## Contents

- [What runs](#what-runs)
- [What does not](#what-does-not)
- [Skill and file limits](#skill-and-file-limits)
- [How to read this table](#how-to-read-this-table)

## What runs

| Capability | Status | Notes |
|---|---|---|
| Python 3.12 scripts | Observed | Only with libraries already installed: pdfplumber, pypdf, pypdfium2, openpyxl. Scripts ran from a skill in earlier sessions. |
| pandoc 3.9, LibreOffice 25.8 (`soffice`), pdftotext, tesseract (English) | Observed | Called from a script or shell command. |
| JavaScript and TypeScript (`.js`) | Reported | Limited libraries; no package installs. |
| A static Linux x86_64 binary (for example Rust built for `x86_64-unknown-linux-musl`) | Observed | Only from `/tmp` after `chmod +x`, and the file has to be attached to the chat. |
| Writing files back | Observed | Output to the working folder, then saved to the task output folder, which syncs to OneDrive. |
| Reading a skill's own files with the file viewer | Observed | Works for `SKILL.md`, scripts, assets and binaries. |
| Generating images from a program (PNG written by a binary) | Observed | The agent showed and saved the image. |

## What does not

| Limit | Status | What to do instead |
|---|---|---|
| Compiling Rust (or other compiled code) | Reported | Build off Cowork, test under WSL, ship the result. |
| Installing packages (`pip install`, `npm install`) | Observed | There is no network. Use what is present or ship it inside the skill. |
| PyMuPDF (`fitz`) | Observed | Use pdfplumber and pypdf. |
| Executable flag in the workspace | Observed | `chmod +x` there reports success but does nothing. Run from `/tmp`. |
| Skill files on disk in the command sandbox | Observed | Often absent. Read them with the viewer and write copies into `/tmp`, or ask for an attachment. |
| Agent copying a skill binary into the session itself | Not tested | The agent said it could not. The latest test skills ask it to try every tool and report. |
| Interactive programs | Observed | Cowork sees command output and files after a command ends. Use a deterministic mode with arguments. |
| A web page running a Linux binary | Observed | Compile the shared logic to WebAssembly and embed the `.wasm`. |
| Running an unknown binary without approval | Observed | Cowork declines; it ran the program once told it is the user's own. |
| Same-name re-upload refreshing a skill | Observed | The old files kept running. Use a new name per build. |

## Skill and file limits

- Upload error seen: a skill may have `SKILL.md` plus at most 20 other files.
- Packager limits in this repo: 20 companion files per skill, 5 MB per file, 10 MB total.
  Microsoft Learn documents larger limits for a plain skill upload (see
  [install routes](skill-install-routes.md)); use the stricter ones for portability.
- Frontmatter must be valid YAML. An unquoted `run: Python` in a description made Cowork show
  the skill with no description.
- Plan for one architecture: Linux x86_64.

## How to read this table

Treat Observed rows as true for the sessions tested, not for every session. Run the small
test skills described in [the test playbook](cowork-test-playbook.md) before building a
skill that depends on a row, and record any change here.
