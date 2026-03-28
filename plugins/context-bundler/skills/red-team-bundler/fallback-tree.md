# Procedural Fallback Tree: Red Team Bundler

## 1. User Fails to Specify a Topic
If the user says "Prep a red team review" without specifying what code to look at:
- **Action**: STOP. Ask the user what specific module, feature, or folder they want reviewed so you can draft an accurate prompt and name the temp directory appropriately.

## 2. Temp Directory Already Exists
If `temp/red-team-review-[topic]` already exists from a previous run:
- **Action**: Do not halt. Either safely overwrite the existing `prompt.md`, `file-manifest.json`, and output `.md` file, or append a timestamp to the new directory name to prevent collisions.

## 3. Missing Core Context Files
If the user asks to review a specific feature, but you cannot find the core logic files:
- **Action**: Draft the prompt and manifest using whatever related documentation you *can* find, but explicitly warn the user that the core implementation files appear missing and ask if they want to manually add paths to the manifest before bundling.