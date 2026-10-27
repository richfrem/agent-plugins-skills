# Authoring and audit failure handling

- Missing template/contract: report the exact bundled path and fail before generation.
  Repair the missing file inside the skill; do not emit placeholders.
- Existing output: preserve it and request a bounded update; do not overwrite on retry.
- Unexpected symlink or duplicate: replace symlinks with self-contained real files inside `.apm/skills/<name>/` and remove plugin-root duplicates.
  Real-file removal remains an exact-path permission gate.
- Invalid target/empty inventory: fail with input status; do not silently scan another root.
- Scan failure: retain partial results and exact failure evidence; coverage is incomplete.
- Semantic ambiguity: preserve the instruction and flag it for human/domain review.
- AI dispatch failure: record failed, exit code and authorized route; do not silently
  switch runtime/model or count an empty response as a completed review.
