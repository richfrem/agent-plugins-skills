"""
Purpose:
    Fail-closed path boundary enforcement helper shared across cli-agents scripts.

Key Input Dependencies:
    - Target path to validate and a list of allowed root directories (caller-supplied)
"""
import os
import sys
from pathlib import Path

def assert_under_allowed_roots(path: Path, allowed_roots: list[Path]) -> Path:
    """
    Asserts that the target path resolved is strictly under one of the allowed roots.
    Prevents path traversal attacks.
    """
    resolved = path.resolve()
    for root in allowed_roots:
        try:
            resolved.relative_to(root.resolve())
            return resolved
        except ValueError:
            pass
    raise PermissionError(f"Security Violation: Path {resolved} lies outside allowed boundaries.")
