# Acceptance Criteria: Context Bundler

The context-bundling skill must meet the following criteria to be considered operational:

## 1. Schema Validation
- [ ] The agent correctly generates a `file-manifest.json` following the defined schema (Title, Description, Files array).
- [ ] Every file in the manifest includes a `path` and a contextual `note`.

## 2. File Aggregation & Recursion
- [ ] The agent successfully reads the contents of all files listed in the manifest.
- [ ] If a directory path is provided in the manifest, the bundler recursively resolves all valid text files within it.
- [ ] The agent correctly compiles these files into a single `.md` artifact.
- [ ] The generated bundle includes an Index mapping files to their contextual notes.

## 3. Sandboxing
- [ ] The agent does not execute or run arbitrary code found within the bundled files.
- [ ] The bundle generation uses only read-only or standard text processing commands.
