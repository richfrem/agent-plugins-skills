# [0001] Create skill for extracting text from Word documents

## Objective
Create a new skill (e.g., `msword-to-markdown-extractor`) that parses binary Microsoft Word documents (`.docx`) and converts them into pristine, flat Markdown or plain text. This is a prerequisite step before the RLM Factory can semantically distill the document's contents.

## Acceptance Criteria
- [ ] A new plugin/skill is scaffolded for Word extraction.
- [ ] The skill successfully converts a `.docx` file into a `.md` or `.txt` file.
- [ ] The output text is clean enough for `rlm-distill` or `distill-agent` to read and understand without parsing errors.
- [ ] The skill is documented and registered in the tool inventory.

## Notes
- **Why this is needed:** The RLM Distillation skills (`rlm-distill` and the `distill-agent` pipeline) rely entirely on the agent being able to read plain-text documents (`view_file`). Binary formats break the text-based distillation workflow.
- **Workflow:** This extraction skill represents Step 1. Step 2 is passing the generated markdown file to the RLM Curator Agent for distillation into the `rlm_summary_cache.json`.
- Consider leveraging existing python libraries like `python-docx` for the underlying script.
