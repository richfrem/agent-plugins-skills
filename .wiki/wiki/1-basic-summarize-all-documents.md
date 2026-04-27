---
concept: 1-basic-summarize-all-documents
source: plugin-code
source_file: agent-loops/scripts/swarm_run.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.272620+00:00
cluster: file
content_hash: 242126ba39ec24e4
---

# 1. Basic: Summarize all Documents

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-loops/scripts/swarm_run.py -->
#!/usr/bin/env python
"""
swarm_run.py 2.0
================

Purpose:
    Generic parallel Claude CLI executor. Dispatches N workers over a set of
    input files, each worker running Claude with a prompt defined in a Job File,
    then optionally pipes the output through a post-command (e.g. cache injector).

WHAT IS A JOB FILE?
    A Job File is a single Markdown file (.md) that bundles ALL configuration
    and the prompt together. It has two parts:

    1. YAML Frontmatter (between --- delimiters) — Configuration:
       - model:      Claude model to use (haiku, sonnet, opus). Default: haiku
       - workers:    Number of parallel workers. Default: 5
       - timeout:    Seconds per worker before timeout. Default: 120
       - max_retries: Retry attempts on rate-limit errors. Default: 3
       - ext:        File extensions to include when using --dir. Default: [".md"]
       - post_cmd:   Shell command template run after each successful LLM call.
                     Placeholders: {file}, {output} (quoted), {output_raw},
                     {basename}, and any custom {vars}.
       - check_cmd:  Shell command to test if a file is already processed.
                     If exit code 0, the file is skipped. Placeholder: {file}.
       - vars:       Key-value pairs available as {key} in post_cmd/check_cmd.
       - dir:        Default directory to crawl (overridden by --dir CLI arg).
       - bundle:     Path to a context-bundler manifest JSON/YAML.

    2. Markdown Body (after the second ---) — The Prompt:
       This is the exact text sent to Claude as the system prompt. The file
       content being processed is piped to Claude's stdin.

    Example Job File (plugins/my-plugin/resources/jobs/my_job.job.md):
    ```
    ---
    model: haiku
    workers: 5
    timeout: 90
    ext: [".md"]
    post_cmd: >-
      python/scripts/inject_summary.py
      --profile {profile} --file {file} --summary {output}
    vars:
      profile: project
    ---
    Summarize this document as a single dense paragraph for the cache.
    Start with "Document Review". Include key decisions, outcomes, and
    technical artifacts. Keep it under 200 words.
    ```

MODEL CHOICE:
    The --model flag (or `model:` in the job file) accepts any model alias
    supported by the `claude` CLI:
      - haiku   — Fastest, cheapest. Best for bulk summarization, docs, tests.
      - sonnet  — Balanced. Good for code review, analysis.
      - opus    — Most capable. Use for complex reasoning, architecture.
    Rule of thumb: use the cheapest model that produces acceptable quality.

FEATURES:
    - Checkpoint/Resume:  State saved to .swarm_state_<job>.json every 5 files.
                          Use --resume to skip already-completed files.
    - Retry with Backoff: Rate-limit errors trigger exponential backoff (2^n sec).
    - Verification Skip:  check_cmd in the job file short-circuits already-done work.
    - Dry Run:            --dry-run lists files that would be processed, no LLM calls.

FILE DISCOVERY (checked in this order):
    1. --files file1.md file2.md    Explicit file list
    2. --bundle manifest.json       Context-bundler manifest (JSON/YAML with "files" key)
    3. --files-from checklist.md    Markdown checklist (extracts `- [ ] \`path\``)
    4. --dir some/directory         Recursive crawl filtered by ext

USAGE EXAMPLES:
    # 1. Basic: Summarize all Documents
    python/scripts/swarm_run.py \
        --job ../../resources/jobs/my_job.job.md \
        --dir docs/

    # 2. Resume after interruption (rate limit, Ctrl+C, crash)
    python/scripts/swarm_run.py \\
        --job ../../resources/jobs/my_job.job.md \
        --dir docs/ --resume

    # 3. Dry run to verify which files would be processed
    python/scripts/swarm_run.py \
        --job ../../resources/jobs/my_job.job.md \
        --dir docs/ --dry-run

    # 4. Override model and worker count at runtime
    python/scripts/swarm_run.py \\
        --job my_job.md --dir docs/ --model sonne

*(content truncated)*

<!-- Source: plugin-code/rlm-factory/scripts/swarm_run.py -->
#!/usr/bin/env python
"""
swarm_run.py 2.0
================

Purpose:
    Generic parallel Claude CLI executor. Dispatches N workers over a set of
    input files, each worker running Claude with a prompt defined in a Job File,
    then optionally pipes the output through a post-command (e.g. cache injector).

WHAT IS A JOB FILE?
    A Job File is a single Markdown file (.md) that bundles ALL configuration
    and the prompt together. It has two parts:

    1. YAML Frontmatter (between --- delimiters) — Configuration:
       - model:      Claude model to use (haiku, sonnet, opus). Default: haiku
       - workers:    Number of parallel workers. Default: 5
       - timeout:    Seconds per worker before timeout. Default: 120
       - max_retries: Retry attempts on rate-limit errors. Default: 3
       - ext:        File extensions to include w

*(combined content truncated)*

## See Also

- [[1-check-env]]
- [[1-check-root-structure]]
- [[1-configuration-setup-dynamic-from-profile]]
- [[1-copilot-gpt-5-mini]]
- [[1-handle-absolute-paths-from-repo-root]]
- [[1-heartbeat-free-model-always-first]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-loops/scripts/swarm_run.py`
- **Indexed:** 2026-04-27T05:21:04.272620+00:00
