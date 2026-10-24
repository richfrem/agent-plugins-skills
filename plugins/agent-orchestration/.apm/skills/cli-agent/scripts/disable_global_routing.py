#!/usr/bin/env python3
"""
disable_global_routing.py (CLI)
=====================================

Purpose:
    Disables global routing proxy configuration. Stops the background daemon
    and removes proxy environment variables from the shell profile.

    macOS:   Unloads and removes the launchd plist. Comments out ~/.zshrc exports.
    Windows: Stops the NSSM service if registered. Removes User env var via registry.
    Linux:   Stops systemd user service if active. Comments out ~/.bashrc exports.

Layer: Infrastructure / Configuration

Usage Examples:
    python3 disable_global_routing.py

Supported Object Types:
    None

CLI Arguments:
    None

Input Files:
    None

Output:
    Daemon/service stop, shell profile cleanup, action-required instructions

Key Functions:
    main(): Execute teardown and configuration restoration for current platform

Script Dependencies:
    os, subprocess, sys

Consumed by:
    local-llm-bridge skill workflows
"""

import os
import subprocess
import sys

_IS_WIN: bool = sys.platform == "win32"
_IS_MAC: bool = sys.platform == "darwin"

PLIST_LABEL = "com.local-llm-proxy"
PROXY_ENV_VAR = "ANTHROPIC_BASE_URL"
PROXY_MODEL_VAR = "ANTHROPIC_CUSTOM_MODEL_OPTION"
PROXY_VALUE = "http://localhost:4000"


def _disable_macos() -> None:
    """Unload/remove the launchd proxy daemon and comment out ~/.zshrc proxy exports."""
    home = os.path.expanduser("~")
    plist_dir = os.path.join(home, "Library", "LaunchAgents")

    # Find the plist by label prefix — avoids hardcoding any username
    plist_path = None
    if os.path.isdir(plist_dir):
        for fname in os.listdir(plist_dir):
            if fname.endswith(".plist") and "llm-proxy" in fname:
                plist_path = os.path.join(plist_dir, fname)
                break

    if plist_path and os.path.isfile(plist_path):
        try:
            subprocess.run(["launchctl", "unload", plist_path], capture_output=True, check=False)
        except Exception:
            pass
        try:
            os.remove(plist_path)
            print(f"✓ Unloaded and removed launchd daemon ({os.path.basename(plist_path)})")
        except Exception as e:
            print(f"WARNING: Failed to remove plist: {e}")
    else:
        print("✓ No active launchd proxy daemon found")

    # Comment out exports in ~/.zshrc
    zshrc = os.path.join(home, ".zshrc")
    if os.path.isfile(zshrc):
        with open(zshrc, "r") as f:
            content = f.read()
        updated = content
        for export in (
            f"export {PROXY_ENV_VAR}={PROXY_VALUE}",
            f"export {PROXY_MODEL_VAR}=gemma-4-12b",
        ):
            if export in updated:
                updated = updated.replace(export, f"# {export}")
        if updated != content:
            with open(zshrc, "w") as f:
                f.write(updated)
            print("✓ Commented out proxy exports in ~/.zshrc")

    print("\n=== ACTION REQUIRED ===")
    print("To restore cloud endpoints in your current terminal:")
    print(f"  unset {PROXY_ENV_VAR}")
    print(f"  unset {PROXY_MODEL_VAR}")
    print("  source ~/.zshrc")


def _disable_windows() -> None:
    """Stop/remove the NSSM proxy service and remove proxy env vars from the User scope."""
    # Stop NSSM service if registered
    try:
        res = subprocess.run(["nssm", "status", "LlamaProxy"], capture_output=True, text=True)
        if "SERVICE_RUNNING" in res.stdout or res.returncode == 0:
            subprocess.run(["nssm", "stop", "LlamaProxy"], check=False)
            subprocess.run(["nssm", "remove", "LlamaProxy", "confirm"], check=False)
            print("✓ Stopped and removed LlamaProxy NSSM service")
        else:
            print("✓ LlamaProxy NSSM service was not running")
    except FileNotFoundError:
        print("✓ NSSM not found — no service to stop")

    # Remove User-level environment variable via PowerShell
    try:
        for var in (PROXY_ENV_VAR, PROXY_MODEL_VAR):
            subprocess.run(
                ["powershell", "-Command",
                 f'[System.Environment]::SetEnvironmentVariable("{var}", $null, "User")'],
                check=False, capture_output=True
            )
        print(f"✓ Removed {PROXY_ENV_VAR} and {PROXY_MODEL_VAR} from User environment")
    except Exception as e:
        print(f"WARNING: Could not remove env vars via PowerShell: {e}")
        print(f"  Remove manually: System Properties → Environment Variables → User variables")

    print("\n=== ACTION REQUIRED ===")
    print("Open a new terminal for the changes to take effect.")
    print(f"Or in current PowerShell session:")
    print(f'  Remove-Item Env:\\{PROXY_ENV_VAR} -ErrorAction SilentlyContinue')
    print(f'  Remove-Item Env:\\{PROXY_MODEL_VAR} -ErrorAction SilentlyContinue')


def _disable_linux() -> None:
    """Stop/disable the systemd user proxy service and comment out shell rc proxy exports."""
    home = os.path.expanduser("~")

    # Stop systemd user service if active
    try:
        res = subprocess.run(
            ["systemctl", "--user", "is-active", "llm-proxy"],
            capture_output=True, text=True
        )
        if res.returncode == 0:
            subprocess.run(["systemctl", "--user", "stop", "llm-proxy"], check=False)
            subprocess.run(["systemctl", "--user", "disable", "llm-proxy"], check=False)
            print("✓ Stopped and disabled llm-proxy systemd user service")
        else:
            print("✓ llm-proxy systemd service was not active")
    except FileNotFoundError:
        print("✓ systemd not available — no service to stop")

    # Comment out exports in ~/.bashrc and ~/.zshrc (if present)
    for rc_file in (os.path.join(home, ".bashrc"), os.path.join(home, ".zshrc")):
        if not os.path.isfile(rc_file):
            continue
        with open(rc_file, "r") as f:
            content = f.read()
        updated = content
        for export in (
            f"export {PROXY_ENV_VAR}={PROXY_VALUE}",
            f"export {PROXY_MODEL_VAR}=gemma-4-12b",
        ):
            if export in updated:
                updated = updated.replace(export, f"# {export}")
        if updated != content:
            with open(rc_file, "w") as f:
                f.write(updated)
            print(f"✓ Commented out proxy exports in {rc_file}")

    print("\n=== ACTION REQUIRED ===")
    print("To restore cloud endpoints in your current terminal:")
    print(f"  unset {PROXY_ENV_VAR}")
    print(f"  unset {PROXY_MODEL_VAR}")
    print("  source ~/.bashrc  (or source ~/.zshrc)")


def main() -> None:
    """Detect the current platform and run its proxy-teardown routine."""
    print("=== DISABLING GLOBAL ROUTING PROXY ===")
    if _IS_MAC:
        _disable_macos()
    elif _IS_WIN:
        _disable_windows()
    else:
        _disable_linux()
    print("\nAny new terminal windows will connect directly to Anthropic cloud endpoints.")


if __name__ == "__main__":
    main()
