---
concept: 1-initialize-a-custom-manifest-in-a-temp-folder
source: plugin-code
source_file: context-bundler/scripts/manifest_manager.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.310420+00:00
cluster: path
content_hash: 6ea365ffb37e7a5b
---

# 1. Initialize a custom manifest in a temp folder

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/context-bundler/scripts/manifest_manager.py -->
#!/usr/bin/env python
"""
manifest_manager.py (CLI)
=====================================

Purpose:
    Handles initialization and modification of the context-manager manifest. Acts as the primary CLI for the Context Bundler.

Layer: Curate / Bundler

Usage Examples:
    # 1. Initialize a custom manifest in a temp folder
    python ./scripts/manifest_manager.py --manifest temp/my_manifest.json init --type generic --bundle-title "My Project"

    # 2. Add files to that custom manifest
    python ./scripts/manifest_manager.py --manifest temp/my_manifest.json add --path "docs/example.md" --note "Reference doc"

    # 3. Bundle using that custom manifest
    python ./scripts/manifest_manager.py --manifest temp/my_manifest.json bundle --output temp/my_bundle.md

    # NOTE: Global flags like --manifest and --base MUST come BEFORE the subcommand (init, add, bundle, etc.)

Supported Object Types:
    - Generic

CLI Arguments:
    Global Flags (Must come BEFORE subcommand):
        --manifest          : Custom path to manifest JSON file (optional)
        --base [type]       : Target a Base Manifest Template (e.g. form, lib)

    Subcommands:
        init                : Bootstrap a new manifest
            --bundle-title  : Human-readable title for the bundle
            --type [type]   : Artifact type template to use
        add                 : Add file to manifest
            --path [path]   : Path to the target file
            --note [text]   : Contextual note about the file
        remove              : Remove file by path
            --path [path]   : Exact path to remove
        update              : Modify an existing entry
            --path [path]   : Target file path
            --note [text]   : New note
            --new-path [p]  : New path for relocation
        search [pattern]    : Find files in the manifest
        list                : Show all files in manifest
        bundle              : Compile manifest into Markdown
            --output [path] : Custom path for the resulting .md file

Input Files:
    - ../../base-manifests/*.json (Templates)
    - ../../base-manifests-index.json (Template Registry)
    - [Manifest JSON] (Input for bundling/listing)

Output:
    - temp/context-bundles/[title].md (Default Bundle Location)
    - [Custom Manifest JSON] (On init/add/update)

Key Functions:
    - add_file(): Adds a file entry to the manifest if it doesn't already exist.
    - bundle(): Executes the bundling process using the current manifest.
    - get_base_manifest_path(): Resolves base manifest path using index or fallback.
    - init_manifest(): Bootstraps a new manifest file from a base template.
    - list_manifest(): Lists all files currently in the manifest.
    - load_manifest(): Loads the manifest JSON file.
    - remove_file(): Removes a file entry from the manifest.
    - save_manifest(): Saves the manifest dictionary to a JSON file.
    - search_files(): Searches for files in the manifest matching a pattern.
    - update_file(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# =====================================================
# Plugin-aware path resolution
# =====================================================
current_dir = Path(__file__).parent.resolve()
plugin_root = current_dir.parent.resolve()  # skill root

# Detect project root: walk up from plugin looking for .git or .agent
def _find_project_root() -> str:
    """Find project root by traversing up from plugin location."""
    candidate = plugin_root
    for _ in range(10):  # Max 10 levels up
        if (candidate / ".git").exists() or (candidate / ".agent").exists():
            return str(candidate)
        parent = candidate.parent
        if parent == candidate:
            break
        candidate = parent
    return os.getcwd()

project_root = Path(_find_project_root())

# Impor

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/context-bundler/scripts/manifest_manager.py -->
#!/usr/bin/env python3
"""
manifest_manager.py (CLI)
=====================================

Purpose:
    Handles initialization and modification of the context-manager manifest. Acts as the primary CLI for the Context Bundler.

Layer: Curate / Bundler

Usage Examples:
    # 1. Initialize a custom manifest in a temp folder
    python ./scripts/manifest_manager.py --manifest temp/my_manifest.json init --type generic --bundle-title "My Project"

    # 2. Add files to that custom manifest
    python ./scripts/manifest_manager.py --manifest temp/my_manifest.json add --path "docs/example.md" --note "Reference doc"

    # 3. Bundle using that custom manifest
    python ./scripts/manifest_manager.py --manifest temp/my_manifest.json bundle --output temp/my_bundle.md

    # NOTE: Global flags li

*(combined content truncated)*

## See Also

- [[initialize-empty-hooks-schema-in-a-nested-hooks-dir]]
- [[1-initialize-client]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[install-plugin-in-a-different-repo-eg-context-bundler-specifically]]
- [[1-basic-summarize-all-documents]]
- [[1-check-env]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `context-bundler/scripts/manifest_manager.py`
- **Indexed:** 2026-04-27T05:21:04.310420+00:00
