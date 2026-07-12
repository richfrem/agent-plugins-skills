#!/usr/bin/env python3
"""
run_server.py (CLI)
=====================================

Purpose:
    Starts the local llama-server with GPU acceleration and optimized parameters.
    Supports macOS Metal, Windows CUDA/Vulkan, and Linux CUDA/ROCm.
    Auto-detects binary path (pre-built or compiled), model file, and thread count.

Layer: Infrastructure / Execution

Usage Examples:
    python3 run_server.py

Supported Object Types:
    None

CLI Arguments:
    None

Input Files:
    Gemma 4 model file (.gguf)

Output:
    Foreground execution of llama-server process

Key Functions:
    find_paths(): Locate llama-server binary and model across pre-built and compiled layouts
    stop_existing_server(): Kill any existing process on port 8089 (cross-platform)
    get_thread_count(): Auto-detect optimal thread count for this platform

Script Dependencies:
    os, subprocess, sys, time

Consumed by:
    local-llm-bridge skill workflows
"""

import os
import subprocess
import sys
import time

# Evaluated once at module load — avoids Pyright false-positive static narrowing
# of sys.platform inside functions that need to run on all platforms.
_IS_WIN: bool = sys.platform == "win32"
_IS_MAC: bool = sys.platform == "darwin"


def get_thread_count() -> int:
    """Return optimal thread count for this platform (physical cores, not hyperthreaded)."""
    if _IS_MAC:
        try:
            res = subprocess.run(
                ["sysctl", "-n", "hw.perflevel0.physicalcpu"],
                capture_output=True, text=True
            )
            count = int(res.stdout.strip())
            if count > 0:
                return count
        except Exception:
            pass
        return 4  # fallback: Apple M1 performance core count
    else:
        # Windows/Linux: physical core count (not hyperthreaded logical count)
        logical = os.cpu_count() or 8
        return max(1, logical // 2)


def find_paths():
    """Locate llama-server binary and Gemma 4 model. Handles pre-built and compiled layouts."""
    home = os.path.expanduser("~")
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Search roots — relative from script dir covers plugin repo layout,
    # explicit home path covers the common dev setup
    candidates = [
        os.path.join(script_dir, "../../../local-llm-bench"),
        os.getcwd(),
        os.path.join(home, "Projects", "local-llm-bench"),
        os.path.join(home, "projects", "local-llm-bench"),
    ]

    if _IS_WIN:
        binary_name = "llama-server.exe"
        # Ordered: pre-built flat extract first (recommended), then compiled layouts
        bin_subdirs = [
            os.path.join("llama-server"),             # pre-built: extracted flat dir
            "",                                        # pre-built: extracted to base
            os.path.join("llama.cpp", "build", "bin", "Release"),   # MSVC multi-config
            os.path.join("llama.cpp", "build", "bin"),               # Ninja single-config
        ]
    else:
        binary_name = "llama-server"
        bin_subdirs = [
            os.path.join("llama.cpp", "build", "bin"),
            "",
        ]

    for base in candidates:
        base = os.path.abspath(base)
        for subdir in bin_subdirs:
            binary = os.path.join(base, subdir, binary_name) if subdir else os.path.join(base, binary_name)
            model = os.path.join(base, "llama.cpp", "models", "gemma-4-12b-UD-Q4_K_XL.gguf")
            if os.path.isfile(binary) and os.path.isfile(model):
                return binary, model

    # Fallback: find binary + any gemma-4 .gguf
    for base in candidates:
        base = os.path.abspath(base)
        for subdir in bin_subdirs:
            binary = os.path.join(base, subdir, binary_name) if subdir else os.path.join(base, binary_name)
            if os.path.isfile(binary):
                models_dir = os.path.join(base, "llama.cpp", "models")
                if os.path.isdir(models_dir):
                    for f in os.listdir(models_dir):
                        if f.endswith(".gguf") and "gemma-4" in f.lower():
                            return binary, os.path.join(models_dir, f)

    return None, None


def stop_existing_server():
    """Kill any existing llama-server process on port 8089."""
    try:
        if _IS_WIN:
            res = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
            for line in res.stdout.splitlines():
                if ":8089" in line and "LISTENING" in line:
                    pid = line.strip().split()[-1]
                    if pid and pid.isdigit():
                        print(f"[llama-server] Stopping existing process on port 8089 (PID {pid})...")
                        subprocess.run(["taskkill", "/F", "/PID", pid], check=False)
                        time.sleep(1)
        else:
            res = subprocess.run(["lsof", "-t", "-i", ":8089"], capture_output=True, text=True)
            for pid in res.stdout.strip().split():
                if pid:
                    print(f"[llama-server] Stopping existing process on port 8089 (PID {pid})...")
                    subprocess.run(["kill", "-9", pid], check=False)
                    time.sleep(1)
    except Exception:
        pass


def _check_paths_or_exit() -> tuple:
    """Locate the llama-server binary and model, printing setup instructions and exiting if missing."""
    binary, model = find_paths()
    if not binary or not model:
        print("ERROR: llama-server binary or Gemma 4 model not found.")
        if _IS_WIN:
            print("  Download a pre-built binary from: https://github.com/ggml-org/llama.cpp/releases")
            print("  Extract to: local-llm-bench\\llama-server\\")
        else:
            print("  Run setup_and_build.sh to compile llama.cpp from source.")
        print("  Model must be at: local-llm-bench/llama.cpp/models/gemma-4-12b-UD-Q4_K_XL.gguf")
        sys.exit(1)
    return binary, model


def _build_llama_cmd(binary: str, model: str, threads: int, slot_save_path: str) -> list:
    """Assemble the llama-server command-line argument list."""
    return [
        binary,
        "-m", model,
        "-c", "32768",
        "-np", "1",
        "--port", "8089",
        "-ngl", "99",
        "--jinja",
        "--reasoning", "off",
        "-fa", "on",
        "-b", "2048",
        "-ub", "512",
        "-t", str(threads),
        "-ctk", "q8_0",
        "-ctv", "q8_0",
        "--cache-ram", "2048",
        "--slot-save-path", slot_save_path,
        "--timeout", "-1",
        "--chat-template-kwargs", '{"enable_thinking": false}',
    ]


def _launch(binary: str, cmd: list) -> None:
    """Execute llama-server: subprocess on Windows, execv (process replacement) elsewhere."""
    try:
        if _IS_WIN:
            # os.execv is unreliable on Windows — use subprocess instead
            subprocess.run(cmd, check=True)
        else:
            # execv replaces this process entirely — zero overhead
            os.execv(binary, cmd)
    except KeyboardInterrupt:
        print("\n[llama-server] Stopped.")
    except Exception as e:
        print(f"ERROR executing llama-server: {e}")
        sys.exit(1)


def main():
    """Locate llama-server and the model, stop any existing instance, then launch the server."""
    binary, model = _check_paths_or_exit()

    stop_existing_server()

    # Slot save/restore: enables KV cache persistence to disk via REST API
    # POST /slots/0/save and /slots/0/restore allow pre-baked system prompt states
    # to survive server restarts — critical for direct-API delegation workflows.
    home = os.path.expanduser("~")
    slot_save_path = os.path.join(home, ".claude", "proxy", "kv_cache")
    os.makedirs(slot_save_path, exist_ok=True)

    threads = get_thread_count()
    print(f"[llama-server] Starting Gemma 4 12B — binary: {binary}")
    print(f"[llama-server] Model: {model}")
    print(f"[llama-server] Threads: {threads} | Context: 32768 | GPU layers: 99")
    print(f"[llama-server] Slot cache dir: {slot_save_path}")

    cmd = _build_llama_cmd(binary, model, threads, slot_save_path)
    _launch(binary, cmd)


if __name__ == "__main__":
    main()