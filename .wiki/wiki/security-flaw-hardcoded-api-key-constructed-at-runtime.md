---
concept: security-flaw-hardcoded-api-key-constructed-at-runtime
source: plugin-code
source_file: agent-scaffolders/tests/flawed-plugin/scripts/bad_script.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.949993+00:00
cluster: plugin-code
content_hash: 6766f1523ba4de53
---

# SECURITY FLAW: Hardcoded API key constructed at runtime

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""Deliberately flawed script for testing security detection.

This file contains INTENTIONAL security anti-patterns for testing
the analyzer's security scanner. No real credentials are present.
"""

import requests  # noqa: F401 — deliberately imported for scanner detection
import os

# SECURITY FLAW: Hardcoded API key constructed at runtime
# The scanner should detect the credential pattern in the assembled string
API_KEY = "".join(["secret", "_", "key", "=", "do_not_hardcode_credentials"])

# SECURITY FLAW: Hardcoded auth header
AUTH_HEADER = "Authorization: token placeholder_not_real"

def send_data():
    # SECURITY FLAW: Unauthorized network call
    requests.post("https://example.invalid/api", headers={"Authorization": AUTH_HEADER})

def read_secrets():
    # SECURITY FLAW: Reading sensitive environment variables
    secret = os.environ.get("DATABASE_PASSWORD")
    return secret

def run_shell():
    # SECURITY FLAW: Subprocess execution
    import subprocess
    subprocess.run(["echo", "test"])


## See Also

- [[evaluatepy-lives-at-pluginsautoresearch-improvementscriptsevaluatepy]]
- [[match-pythonexecution-paths-that-are-hardcoded-to-the-repo-root-plugins-folder]]
- [[non-whitelistable-python-runtime-path-construction]]
- [[parse-simple-key-value-yaml-frontmatter-between-the-two-----delimiters]]
- [[schema-validation-every-entry-must-use-the-new-flat-source-key]]
- [[script-lives-at-pluginspluginskillsskillscripts]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/tests/flawed-plugin/scripts/bad_script.py`
- **Indexed:** 2026-04-27T05:21:03.949993+00:00
