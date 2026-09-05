"""
Secret redaction scanner module for GitHub issues.

Purpose:
    Scans GitHub issue payload text for common secret patterns (tokens, keys,
    private key blocks) before an issue body is submitted, to prevent
    accidental credential leakage into a public issue tracker.

Key Input Dependencies:
    - Issue body / comment text passed in by the caller (github-issue-agent scripts)

Copyright (c) 2026. All rights reserved.
"""

import re
from typing import List, Tuple

SECRET_PATTERNS: List[Tuple[str, str]] = [
    (r"ghp_[A-Za-z0-9]{36}", "GitHub Personal Access Token"),
    (r"github_pat_[A-Za-z0-9_]{82}", "GitHub Fine-Grained Token"),
    (r"-----BEGIN [A-Z ]+ PRIVATE KEY-----", "Private Key"),
    (r"sk-[A-Za-z0-9]{32,}", "API Key"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    (r"bearer\s+[A-Za-z0-9\-\._~\+\/]+=*", "Bearer Token"),
]


def scan_for_secrets(text: str) -> Tuple[bool, List[str]]:
    """Scan text for potential secrets or credentials.

    Args:
        text: Input string to scan for secrets.

    Returns:
        Tuple of (is_clean, findings) where is_clean is True if no secrets were found,
        and findings contains descriptive strings of detected secrets.
    """
    findings: List[str] = []
    for pattern, label in SECRET_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            findings.append(f"Detected potential secret ({label}) matching pattern: {pattern}")
    return (len(findings) == 0, findings)
