#!/usr/bin/env python3
"""
check_routing_readiness.py - Multi-Subscription Routing & Gateway Readiness Probe
================================================================================

Purpose:
    Performs a non-destructive pre-flight readiness audit for multi-subscription
    routing and gateway health. Designed specifically for macOS Apple Silicon (M1/M2/M3)
    environments where local LLM compute is bypassed in favor of paid cloud subscriptions
    (Claude Pro, ChatGPT Plus, Gemini Pro).

Usage:
    python3 scripts/check_routing_readiness.py
    python3 scripts/check_routing_readiness.py --json
    python3 scripts/check_routing_readiness.py --port 4000
"""

import os
import sys
import json
import shutil
import subprocess
import urllib.request
import urllib.error
import argparse
from pathlib import Path


def probe_http_gateway(port: int = 4000, timeout: float = 1.0) -> dict:
    """Probe local gateway HTTP health endpoint."""
    url = f"http://localhost:{port}/health"
    models_url = f"http://localhost:{port}/v1/models"
    
    status = "DOWN"
    details = "No daemon listening"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Sanctuary-Probe/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                status = "ACTIVE"
                details = f"HTTP {resp.status} on port {port}"
    except (urllib.error.URLError, ConnectionRefusedError, TimeoutError, OSError):
        # Fall back to probing models endpoint
        try:
            req = urllib.request.Request(models_url, headers={"User-Agent": "Sanctuary-Probe/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    status = "ACTIVE"
                    details = f"HTTP {resp.status} on /v1/models (port {port})"
        except Exception:
            pass

    return {
        "port": port,
        "status": status,
        "details": details
    }


def check_env_redirects() -> dict:
    """Inspect environment variable redirections for Anthropic and OpenAI SDKs."""
    anthropic_base = os.environ.get("ANTHROPIC_BASE_URL", "")
    openai_base = os.environ.get("OPENAI_BASE_URL", "")
    
    is_routed = bool(anthropic_base or openai_base)
    
    return {
        "is_routed": is_routed,
        "ANTHROPIC_BASE_URL": anthropic_base or "Not set (direct cloud API)",
        "OPENAI_BASE_URL": openai_base or "Not set (direct cloud API)"
    }


def check_cli_binaries() -> dict:
    """Audit installed CLI tools and availability on PATH."""
    cursor_path = shutil.which("agent") or shutil.which("cursor-agent")
    cursor_status = "NOT INSTALLED"
    cursor_authenticated = False
    if cursor_path:
        try:
            proc = subprocess.run([cursor_path, "status"], capture_output=True, text=True, timeout=2.0)
            status_out = proc.stdout.strip()
            if "Not logged in" in status_out:
                cursor_status = "STANDBY (Not logged in)"
            elif status_out:
                cursor_status = f"AUTHENTICATED ({status_out.splitlines()[0]})"
                cursor_authenticated = True
            else:
                cursor_status = "INSTALLED (Status unknown)"
        except Exception as e:
            cursor_status = f"INSTALLED (Probe error: {e})"

    tools = {
        "claude": {"path": shutil.which("claude"), "subscription": "Claude Pro ($20/mo)", "installed": bool(shutil.which("claude"))},
        "codex": {"path": shutil.which("codex"), "subscription": "ChatGPT Plus ($20/mo)", "installed": bool(shutil.which("codex"))},
        "agy": {"path": shutil.which("agy"), "subscription": "Gemini Pro / Google One", "installed": bool(shutil.which("agy"))},
        "cursor": {
            "path": cursor_path,
            "subscription": "Cursor Free / Pro ($0-$30/mo)",
            "installed": bool(cursor_path),
            "status_detail": cursor_status,
            "authenticated": cursor_authenticated
        },
        "copilot": {"path": shutil.which("copilot"), "subscription": "GitHub Copilot (Work Strictly)", "installed": bool(shutil.which("copilot"))}
    }
    
    return tools


def evaluate_routing_readiness(port: int = 4000) -> dict:
    """Synthesize complete readiness assessment."""
    gateway = probe_http_gateway(port=port)
    env_vars = check_env_redirects()
    binaries = check_cli_binaries()
    
    # Assess available subscriptions
    active_cloud_subs = []
    if binaries["claude"]["installed"]:
        active_cloud_subs.append("Claude Pro (claude)")
    if binaries["agy"]["installed"]:
        active_cloud_subs.append("Gemini Pro (agy)")
    if binaries["codex"]["installed"]:
        active_cloud_subs.append("ChatGPT Plus (codex)")
    if binaries.get("cursor", {}).get("authenticated"):
        active_cloud_subs.append("Cursor Pro (agent)")
        
    # Boundary audit
    copilot_status = "INSTALLED (Strictly Work Only)" if binaries["copilot"]["installed"] else "NOT INSTALLED"
    
    # Determine primary routing posture
    if gateway["status"] == "ACTIVE":
        posture = "LOCAL_PROXY_ACTIVE"
        summary = f"Local proxy gateway active on port {port}. Traffic transparently intercepted."
    elif len(active_cloud_subs) >= 2:
        posture = "MULTI_CLI_READY"
        summary = f"Multi-CLI cloud pooling ready across {len(active_cloud_subs)} subscriptions ({', '.join(active_cloud_subs)}). Native CLI fallback enabled."
    else:
        posture = "DEGRADED"
        summary = "Insufficient CLI subscriptions discovered on PATH."
        
    return {
        "posture": posture,
        "summary": summary,
        "hardware_profile": "Apple Silicon (M1/M2/M3) Optimized - Local LLMs Bypassed",
        "gateway": gateway,
        "env_redirects": env_vars,
        "cli_binaries": binaries,
        "active_cloud_subscriptions": active_cloud_subs,
        "copilot_work_boundary": copilot_status
    }


def main():
    parser = argparse.ArgumentParser(description="Multi-Subscription Routing & Gateway Readiness Probe")
    parser.add_argument("--port", type=int, default=4000, help="Port to probe (default: 4000)")
    parser.add_argument("--json", action="store_true", help="Emit raw JSON output")
    args = parser.parse_args()
    
    result = evaluate_routing_readiness(port=args.port)
    
    if args.json:
        print(json.dumps(result, indent=2))
        return

    print("=================================================================")
    print("      MULTI-SUBSCRIPTION ROUTING & GATEWAY READINESS PROBE       ")
    print("=================================================================")
    print(f"Hardware Optimization : {result['hardware_profile']}")
    print(f"Overall Posture       : [{result['posture']}]")
    print(f"Readiness Summary     : {result['summary']}")
    print("-----------------------------------------------------------------")
    print("1. Gateway Daemon Status:")
    print(f"   Port {result['gateway']['port']}             : [{result['gateway']['status']}] ({result['gateway']['details']})")
    print(f"   ANTHROPIC_BASE_URL : {result['env_redirects']['ANTHROPIC_BASE_URL']}")
    print(f"   OPENAI_BASE_URL    : {result['env_redirects']['OPENAI_BASE_URL']}")
    print("-----------------------------------------------------------------")
    print("2. Cloud Subscriptions Available (Personal):")
    for name in ["claude", "agy", "codex"]:
        info = result["cli_binaries"][name]
        status = "INSTALLED" if info["installed"] else "MISSING"
        path = info["path"] or "N/A"
        print(f"   • {name:<8} [{status:<9}] - {info['subscription']} -> {path}")
    cursor_info = result["cli_binaries"].get("cursor", {})
    if cursor_info.get("installed"):
        if cursor_info.get("authenticated"):
            c_status = "INSTALLED"
            c_note = f"({cursor_info.get('status_detail', 'Authenticated')})"
        else:
            c_status = "STANDBY"
            c_note = "(Not logged in / Unconfigured)"
    else:
        c_status = "MISSING"
        c_note = ""
    c_path = cursor_info.get("path") or "N/A"
    print(f"   • {'agent':<8} [{c_status:<9}] - {cursor_info.get('subscription', 'Cursor')} -> {c_path} {c_note}")
    print("-----------------------------------------------------------------")
    print("3. Corporate Boundary Governance:")
    print(f"   • copilot  : {result['copilot_work_boundary']}")
    print("     (Must NEVER be routed to personal or sovereign research)")
    print("=================================================================")


if __name__ == "__main__":
    main()
