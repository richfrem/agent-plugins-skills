# Ways to Get a Skill into Cowork

## Contents

- [Summary](#summary)
- [1. Create in Cowork](#1-create-in-cowork)
- [2. Upload a file or ZIP](#2-upload-a-file-or-zip)
- [3. Sync from a GitHub repo](#3-sync-from-a-github-repo)
- [4. Drop a folder in OneDrive and ask for a sync](#4-drop-a-folder-in-onedrive-and-ask-for-a-sync)
- [Choosing a route](#choosing-a-route)
- [Open questions](#open-questions)

## Summary

Four routes were observed. Skills end up in the user's OneDrive folder
`Documents\Cowork\skills\<skill-name>\` (the "Cowork folder"); that folder is the durable
store. The `/` picker in Cowork is fed by something other than a live read of the folder
(see route 4).

| Route | Output | Limits | Status |
|-------|--------|--------|--------|
| 1. Create in Cowork | Folder in the Cowork folder | Cowork decides | Observed |
| 2a. Upload skill (Skills tab) | Folder in the Cowork folder | Microsoft Learn: `.md` up to 1 MB; `.zip` or `.skill` with `SKILL.md` at root, up to 100 files, 10 MB compressed, 50 MB uncompressed | Documented |
| 2b. Upload plugin (Plugins tab) | Installed plugin | Our packager enforces 20 companion files per skill, 5 MB per file, 10 MB total | Documented, tooling in this skill |
| 3. GitHub repo via GitHub MCP | Skills synced from a repo | Not tested here | Reported, unverified |
| 4. Drop a folder, then ask for a sync | Folder is recognised after the sync prompt | 158 files accepted | Observed 2026-11-12 |

## 1. Create in Cowork

In **Customize > Skills > Add > Create new**, or by asking Cowork to create a skill. Cowork
builds the skill in its writable `working/` folder, then promotes it to the Cowork folder
with its copy tool, which shows an approval card (target `skills/<name>`, overwrite and
recursive flags). The Cowork folder's own `AGENTS.md` says the folder is read-only to the
agent except through those tools. Approve only after checking the target name and that
overwrite will not replace a skill you want to keep.

## 2. Upload a file or ZIP

Two different uploads exist; do not mix them up.

- **Upload skill** (Skills tab, arrow next to Add): one `SKILL.md`, or a `.zip` or `.skill`
  archive with `SKILL.md` at its root. Frontmatter needs `name` and `description`. A
  duplicate name is kept and renumbered. Microsoft Learn says Cowork saves the skill to
  OneDrive.
- **Upload plugin** (Plugins tab): an M365 app package `.zip` with `manifest.json`, icons
  and `skills/`. Build it with this skill's scaffold and packager (see
  [the package lifecycle](cowork-package-lifecycle.md)). A Claude or Open Plugin package is
  converted automatically by Cowork.

## 3. Sync from a GitHub repo

Skills can reportedly be pulled from a GitHub repository through the GitHub MCP connector.
This route was seen in use but was not tested or documented here: record the exact prompt,
repo layout and result before relying on it, and keep tokens out of skill files.

## 4. Drop a folder in OneDrive and ask for a sync

Tested on 2026-11-12:

1. A skill folder with 158 files (about 0.96 MB, over the 100-file upload limit) was copied
   into `Documents\Cowork\skills\`.
2. It did not appear in the `/` picker by itself.
3. After asking Cowork "can you show my current skills sync them with my one drive", Cowork
   listed it ("Already there") and the `/authoring-skills` entry appeared in the picker with
   the correct description.

Findings:

- A plain folder with `SKILL.md` is enough; no manifest or registry file was needed.
- The upload limits did not block a direct drop.
- The folder alone is not enough: the sync prompt (or some other refresh) is the
  registration step.
- Cowork said it only checked that each skill folder exists, not that file contents match,
  so an edited skill that already exists may not be refreshed by this prompt.
- Skills that are built in to Cowork are not stored in OneDrive and are not synced.
- Deleting the folder was done afterwards; whether the picker entry disappears on its own
  or after another sync was not recorded.

## Choosing a route

- Quick personal skill: route 1.
- Single skill from a repo, within the upload limits: route 2a.
- Plugin to share or deploy, with connectors or several skills: route 2b with the
  tools in this skill; share only with explicit approval.
- Many skills that need to stay in step with a repository: route 3, after testing it.
- Skill too large for upload, or an iterative personal test: route 4, then run the sync
  prompt and check the picker in a new session.

## Open questions

- Is the sync prompt the actual trigger, or would a new session or later OneDrive sync
  also register the skill?
- Does a directly dropped skill appear in the Copilot web or other devices?
- Do edits to an existing skill folder get picked up?
- Is a size or file count limit enforced for a direct drop?
