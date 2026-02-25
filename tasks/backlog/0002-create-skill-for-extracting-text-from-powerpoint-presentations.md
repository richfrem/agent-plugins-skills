# [0002] Create skill for extracting text from PowerPoint presentations

## Objective
Create a new skill (e.g., `mspowerpoint-to-markdown-extractor`) that parses binary Microsoft PowerPoint presentations (`.pptx`) and extracts all slide text and speaker notes into a flat Markdown or plain text format. This is a prerequisite step before the RLM Factory can semantically distill the presentation's contents.

## Acceptance Criteria
- [ ] A new plugin/skill is scaffolded for PowerPoint extraction.
- [ ] The skill successfully extracts text from all slides within a `.pptx` file and outputs a `.md` or `.txt` file.
- [ ] Speaker notes are included in the extraction.
- [ ] The output text is clean enough for `rlm-distill` or `distill-agent` to read and understand without parsing errors.
- [ ] The skill is documented and registered in the tool inventory.

## Notes
- **Why this is needed:** The RLM Distillation skills (`rlm-distill` and the `distill-agent` pipeline) rely entirely on the agent being able to read plain-text documents (`view_file`). Binary formats break the text-based distillation workflow.
- **Workflow:** This extraction skill represents Step 1. Step 2 is passing the generated markdown file to the RLM Curator Agent for distillation into the `rlm_summary_cache.json`.
- Consider leveraging existing python libraries like `python-pptx` for the underlying script.
