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
