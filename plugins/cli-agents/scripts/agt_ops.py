#!/usr/bin/env python3
"""
agt_ops.py
==========
Operational utility to verify local sandboxing rules and manage key rotation for
HMAC signing envelopes under Agentic Group Theory (AGT).
"""

import os
import sys
import secrets
import argparse
from pathlib import Path

def verify_sandbox():
    print("[*] Performing AGT Sandbox Compliance Verification...")
    
    # 1. Environment hygiene check
    banned_vars = ["PYTHONPATH", "PYTHONHOME", "LD_PRELOAD", "DYLD_LIBRARY_PATH"]
    violations = [v for v in banned_vars if v in os.environ]
    if violations:
        print(f"⚠️  Warning: Banned environment variables found in parent env: {violations}")
    else:
        print("✅ Environment hygiene check passed (no dirty variables detected).")
        
    # 2. Path boundaries verification test
    from path_security import assert_under_allowed_roots
    allowed = [Path("/tmp").resolve()]
    try:
        assert_under_allowed_roots(Path("/etc/passwd"), allowed)
        print("❌ Error: Path containment failed! Out-of-bounds path was allowed.")
    except PermissionError:
        print("✅ Path containment check passed (out-of-bounds access blocked).")

    print("[+] Sandbox validation check complete.")

def rotate_key():
    print("[*] Generating new HMAC Session Key...")
    secret_dir = Path(os.getcwd()) / "context" / "exploration" / ".secrets"
    secret_dir.mkdir(parents=True, exist_ok=True)
    
    key_file = secret_dir / "session_hmac.key"
    
    # Generate 32 bytes of secure random key
    key_data = secrets.token_bytes(32)
    
    # Write with strict 0600 permissions
    if key_file.exists():
        key_file.unlink()
        
    # Open with exclusive creation flags
    fd = os.open(key_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(key_data)
        
    print(f"✅ Key rotated successfully. Saved to: {key_file}")
    print(f"[*] Permissions verified: {oct(os.stat(key_file).st_mode & 0o777)}")

def main():
    parser = argparse.ArgumentParser(description="AGT Operational Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")
    
    subparsers.add_parser("verify-sandbox", help="Verify local sandbox isolation criteria")
    subparsers.add_parser("rotate-key", help="Rotate local HMAC session key")

    args = parser.parse_args()

    if args.command == "verify-sandbox":
        verify_sandbox()
    elif args.command == "rotate-key":
        rotate_key()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
