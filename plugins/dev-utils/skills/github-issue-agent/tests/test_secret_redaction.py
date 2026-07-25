"""
Unit tests for secret redaction scanner in github-issue-agent.

Copyright (c) 2026. All rights reserved.
"""

import sys
from pathlib import Path

# Add script directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import pytest
from redaction_gate import scan_for_secrets


def test_scan_for_secrets_clean_text() -> None:
    """Test that text with no secrets passes scanning."""
    text = "This is a clean issue body with no sensitive data."
    is_clean, findings = scan_for_secrets(text)
    assert is_clean is True
    assert len(findings) == 0


def test_scan_for_secrets_github_pat() -> None:
    """Test detection of GitHub Personal Access Token."""
    text = "Here is my token: ghp_1234567890abcdefghijklmnopqrstuvwxyz"
    is_clean, findings = scan_for_secrets(text)
    assert is_clean is False
    assert any("GitHub Personal Access Token" in f for f in findings)


def test_scan_for_secrets_github_fine_grained_pat() -> None:
    """Test detection of GitHub fine-grained token."""
    text = "Token: github_pat_11ABCDEFG01234567890abcdefghijklmnopqrstuvwxyz_abcdefghijklmnopqrstuvwxyz1234567890"
    is_clean, findings = scan_for_secrets(text)
    assert is_clean is False
    assert any("GitHub Fine-Grained Token" in f for f in findings)


def test_scan_for_secrets_private_key() -> None:
    """Test detection of RSA/PEM private key block."""
    text = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----"
    is_clean, findings = scan_for_secrets(text)
    assert is_clean is False
    assert any("Private Key" in f for f in findings)


def test_scan_for_secrets_api_key() -> None:
    """Test detection of OpenAI / generic sk- API keys."""
    text = "OpenAI key: sk-abcdefghijklmnopqrstuvwxyz0123456789"
    is_clean, findings = scan_for_secrets(text)
    assert is_clean is False
    assert any("API Key" in f for f in findings)
