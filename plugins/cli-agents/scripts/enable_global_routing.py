#!/usr/bin/env python3
"""
enable_global_routing.py (CLI)
=====================================

Purpose:
    Enables global routing of LLM CLI traffic through the proxy (port 4000).
    Installs the daemon, starts it, and adds proxy environment variables to
    the shell profile.

    macOS:   Creates and loads a launchd plist. Appends exports to ~/.zshrc.
    Windows: Installs an NSSM service. Sets User env var via PowerShell.
    Linux:   Creates and enables a systemd user service. Appends exports to ~/.bashrc.

Layer: Infrastructure / Configuration

Usage Examples:
    python3 enable_global_routing.py

Supported Object Types:
    None

CLI Arguments:
    None

Input Files:
    routing_proxy.py (copied to canonical location)

Output:
    Daemon/service install, shell profile entries, action-required instructions

Key Functions:
    main(): Execute setup and loading sequence for global daemon

Script Dependencies:
    os, re, shutil, subprocess, sys

Consumed by:
    local-llm-bridge skill workflows
"""

import os
import re
import shutil
import subprocess
import sys

_IS_WIN: bool = sys.platform == "win32"
_IS_MAC: bool = sys.platform == "darwin"

PLIST_LABEL = "com.local-llm-proxy"
PROXY_ENV_VAR = "ANTHROPIC_BASE_URL"
PROXY_MODEL_VAR = "ANTHROPIC_CUSTOM_MODEL_OPTION"
PROXY_VALUE = "http://localhost:4000"
PROXY_MODEL_VALUE = "gemma-4-12b"


def _find_proxy_source() -> str:
    """Locate routing_proxy.py in one of the standard candidate locations, or exit."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, "routing_proxy.py"),                          # same scripts/ dir (installed)
        os.path.join(script_dir, "../../../local-llm-bench/routing_proxy.py"), # dev repo sibling layout
        os.path.join(os.getcwd(), "routing_proxy.py"),                         # cwd fallback
    ]
    for c in candidates:
        if os.path.isfile(c):
            return os.path.abspath(c)
    print("ERROR: Could not find routing_proxy.py in any standard location.")
    sys.exit(1)


def _sync_proxy(proxy_dir: str, proxy_script: str, src: str) -> None:
    """Copy routing_proxy.py to the canonical proxy directory, creating dirs as needed."""
    os.makedirs(proxy_dir, exist_ok=True)
    os.makedirs(os.path.join(proxy_dir, "logs"), exist_ok=True)
    shutil.copy2(src, proxy_script)
    print(f"✓ Synced routing_proxy.py → {proxy_script}")


def _write_macos_plist(plist_path: str, python_path: str, proxy_script: str, log_dir: str) -> None:
    """Write the launchd plist XML file for the proxy daemon."""
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{PLIST_LABEL}</string>

    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>-u</string>
        <string>{proxy_script}</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>{os.path.join(log_dir, "proxy.log")}</string>

    <key>StandardErrorPath</key>
    <string>{os.path.join(log_dir, "proxy.error.log")}</string>
</dict>
</plist>
"""
    with open(plist_path, "w") as f:
        f.write(plist_content)
    print(f"✓ Created launchd plist at {plist_path}")


def _load_macos_daemon(plist_path: str) -> None:
    """Unload any existing daemon instance, then load the plist to (re)start it."""
    try:
        res = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
        if PLIST_LABEL in res.stdout:
            subprocess.run(["launchctl", "unload", plist_path], capture_output=True, check=False)
    except Exception:
        pass

    try:
        subprocess.run(["launchctl", "load", plist_path], check=True)
        print("✓ Started global proxy daemon (port 4000)")
    except Exception as e:
        print(f"WARNING: launchctl load failed: {e}")


def _update_macos_zshrc(home: str) -> None:
    """Add or uncomment the proxy environment exports in ~/.zshrc."""
    zshrc = os.path.join(home, ".zshrc")
    if not os.path.isfile(zshrc):
        return
    with open(zshrc, "r") as f:
        content = f.read()
    if re.search(r'#\s*export ANTHROPIC_BASE_URL=http://localhost:4000', content):
        content = re.sub(r'#\s*export ANTHROPIC_BASE_URL=http://localhost:4000',
                         f'export {PROXY_ENV_VAR}={PROXY_VALUE}', content)
    elif f'export {PROXY_ENV_VAR}' not in content:
        content += f'\nexport {PROXY_ENV_VAR}={PROXY_VALUE}\n'

    if re.search(r'#\s*export ANTHROPIC_CUSTOM_MODEL_OPTION=gemma-4-12b', content):
        content = re.sub(r'#\s*export ANTHROPIC_CUSTOM_MODEL_OPTION=gemma-4-12b',
                         f'export {PROXY_MODEL_VAR}={PROXY_MODEL_VALUE}', content)
    elif f'export {PROXY_MODEL_VAR}' not in content:
        content = content.replace(
            f'export {PROXY_ENV_VAR}={PROXY_VALUE}',
            f'export {PROXY_ENV_VAR}={PROXY_VALUE}\nexport {PROXY_MODEL_VAR}={PROXY_MODEL_VALUE}'
        )

    with open(zshrc, "w") as f:
        f.write(content)
    print("✓ Added/uncommented proxy exports in ~/.zshrc")


def _enable_macos(proxy_script: str, python_path: str, log_dir: str) -> None:
    """Install and load the launchd daemon, and update ~/.zshrc with proxy exports."""
    home = os.path.expanduser("~")
    plist_dir = os.path.join(home, "Library", "LaunchAgents")
    os.makedirs(plist_dir, exist_ok=True)
    plist_path = os.path.join(plist_dir, f"{PLIST_LABEL}.plist")

    _write_macos_plist(plist_path, python_path, proxy_script, log_dir)
    _load_macos_daemon(plist_path)
    _update_macos_zshrc(home)

    print("\n=== ACTION REQUIRED ===")
    print("To apply routing in this terminal:")
    print("  source ~/.zshrc")


def _enable_windows(proxy_script: str, python_path: str, log_dir: str) -> None:
    """Install/start the NSSM proxy service and set proxy env vars in the User scope."""
    try:
        nssm = shutil.which("nssm")
        if not nssm:
            print("ERROR: NSSM not found. Install from https://nssm.cc or via Chocolatey: choco install nssm")
            sys.exit(1)

        # Stop existing service if running
        subprocess.run(["nssm", "stop", "LlamaProxy"], capture_output=True, check=False)
        subprocess.run(["nssm", "remove", "LlamaProxy", "confirm"], capture_output=True, check=False)

        subprocess.run([
            "nssm", "install", "LlamaProxy", python_path,
            f"-u {proxy_script}"
        ], check=True)
        subprocess.run(["nssm", "set", "LlamaProxy", "AppStdout",
                        os.path.join(log_dir, "proxy.log")], check=False)
        subprocess.run(["nssm", "set", "LlamaProxy", "AppStderr",
                        os.path.join(log_dir, "proxy.error.log")], check=False)
        subprocess.run(["nssm", "start", "LlamaProxy"], check=True)
        print("✓ Installed and started LlamaProxy NSSM service (port 4000)")
    except Exception as e:
        print(f"WARNING: NSSM service setup failed: {e}")

    # Set User-level environment variables via PowerShell
    try:
        for var, val in ((PROXY_ENV_VAR, PROXY_VALUE), (PROXY_MODEL_VAR, PROXY_MODEL_VALUE)):
            subprocess.run(
                ["powershell", "-Command",
                 f'[System.Environment]::SetEnvironmentVariable("{var}", "{val}", "User")'],
                check=False, capture_output=True
            )
        print(f"✓ Set {PROXY_ENV_VAR} and {PROXY_MODEL_VAR} in User environment")
    except Exception as e:
        print(f"WARNING: Could not set env vars via PowerShell: {e}")

    print("\n=== ACTION REQUIRED ===")
    print("Open a new terminal for the env vars to take effect.")
    print("Or in current PowerShell session:")
    print(f'  $env:{PROXY_ENV_VAR} = "{PROXY_VALUE}"')
    print(f'  $env:{PROXY_MODEL_VAR} = "{PROXY_MODEL_VALUE}"')


def _write_linux_service(service_path: str, python_path: str, proxy_script: str, log_dir: str) -> None:
    """Write the systemd user service unit file for the proxy daemon."""
    service_content = f"""[Unit]
Description=Local LLM routing proxy (port 4000)
After=network.target

[Service]
ExecStart={python_path} -u {proxy_script}
Restart=always
StandardOutput=append:{os.path.join(log_dir, "proxy.log")}
StandardError=append:{os.path.join(log_dir, "proxy.error.log")}

[Install]
WantedBy=default.target
"""
    with open(service_path, "w") as f:
        f.write(service_content)
    print(f"✓ Created systemd user service at {service_path}")


def _load_linux_daemon() -> None:
    """Reload systemd, enable, and start the llm-proxy user service."""
    try:
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
        subprocess.run(["systemctl", "--user", "enable", "llm-proxy"], check=False)
        subprocess.run(["systemctl", "--user", "start", "llm-proxy"], check=True)
        print("✓ Enabled and started llm-proxy systemd user service (port 4000)")
    except Exception as e:
        print(f"WARNING: systemd setup failed: {e}")


def _update_linux_rc_files(home: str) -> None:
    """Add proxy environment exports to ~/.bashrc and ~/.zshrc if not already present."""
    for rc_file in (os.path.join(home, ".bashrc"), os.path.join(home, ".zshrc")):
        if not os.path.isfile(rc_file):
            continue
        with open(rc_file, "r") as f:
            content = f.read()
        changed = False
        if f'export {PROXY_ENV_VAR}' not in content:
            content += f'\nexport {PROXY_ENV_VAR}={PROXY_VALUE}\n'
            changed = True
        if f'export {PROXY_MODEL_VAR}' not in content:
            content += f'export {PROXY_MODEL_VAR}={PROXY_MODEL_VALUE}\n'
            changed = True
        if changed:
            with open(rc_file, "w") as f:
                f.write(content)
            print(f"✓ Added proxy exports to {rc_file}")


def _enable_linux(proxy_script: str, python_path: str, log_dir: str) -> None:
    """Install/enable the systemd user proxy service and update shell rc files."""
    home = os.path.expanduser("~")
    systemd_dir = os.path.join(home, ".config", "systemd", "user")
    os.makedirs(systemd_dir, exist_ok=True)

    service_path = os.path.join(systemd_dir, "llm-proxy.service")
    _write_linux_service(service_path, python_path, proxy_script, log_dir)
    _load_linux_daemon()
    _update_linux_rc_files(home)

    print("\n=== ACTION REQUIRED ===")
    print("To apply routing in this terminal:")
    print(f"  export {PROXY_ENV_VAR}={PROXY_VALUE}")
    print(f"  export {PROXY_MODEL_VAR}={PROXY_MODEL_VALUE}")


def main() -> None:
    """Sync routing_proxy.py and install/start the platform-specific daemon and env vars."""
    print("=== ENABLING GLOBAL ROUTING PROXY ===")

    src_proxy = _find_proxy_source()
    python_path = sys.executable or shutil.which("python3")
    if not python_path:
        print("ERROR: python3 executable not found.")
        sys.exit(1)
    print(f"✓ python3: {python_path}")

    home = os.path.expanduser("~")
    proxy_dir = os.path.join(home, ".claude", "proxy")
    proxy_script = os.path.join(proxy_dir, "routing_proxy.py")
    log_dir = os.path.join(proxy_dir, "logs")

    _sync_proxy(proxy_dir, proxy_script, src_proxy)

    if _IS_MAC:
        _enable_macos(proxy_script, python_path, log_dir)
    elif _IS_WIN:
        _enable_windows(proxy_script, python_path, log_dir)
    else:
        _enable_linux(proxy_script, python_path, log_dir)


if __name__ == "__main__":
    main()
