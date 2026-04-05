#!/usr/bin/env python3
"""
test_hook.py
=====================================

Purpose:
    Test runner for Claude Code hook scripts. Accepts a hook script path and
    a JSON input file, pipes the input to the hook via subprocess, and reports
    the exit code, duration, stdout/stderr output, and parsed JSON decision.
    Also supports generating sample input payloads via --create-sample.

Layer: Investigate

Usage:
    python3 test_hook.py [options] <hook-script> <test-input.json>
    python3 test_hook.py --create-sample PreToolUse
    python3 test_hook.py -v -t 30 validate_write.py write-input.json
"""
import sys
import os
import json
import argparse
import subprocess
import time

_SEPARATOR = "━" * 40

# Sample payloads keyed by Claude Code event type name
_SAMPLES: dict = {
    "PreToolUse": {
        "session_id": "test-session",
        "transcript_path": "/tmp/transcript.txt",
        "cwd": "/tmp/test-project",
        "permission_mode": "ask",
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": "/tmp/test.txt", "content": "Test content"},
    },
    "PostToolUse": {
        "session_id": "test-session",
        "transcript_path": "/tmp/transcript.txt",
        "cwd": "/tmp/test-project",
        "permission_mode": "ask",
        "hook_event_name": "PostToolUse",
        "tool_name": "Bash",
        "tool_result": "Command executed successfully",
    },
    "Stop": {
        "session_id": "test-session",
        "transcript_path": "/tmp/transcript.txt",
        "cwd": "/tmp/test-project",
        "permission_mode": "ask",
        "hook_event_name": "Stop",
        "reason": "Task appears complete",
    },
    "UserPromptSubmit": {
        "session_id": "test-session",
        "transcript_path": "/tmp/transcript.txt",
        "cwd": "/tmp/test-project",
        "permission_mode": "ask",
        "hook_event_name": "UserPromptSubmit",
        "user_prompt": "Test user prompt",
    },
    "SessionStart": {
        "session_id": "test-session",
        "transcript_path": "/tmp/transcript.txt",
        "cwd": "/tmp/test-project",
        "permission_mode": "ask",
        "hook_event_name": "SessionStart",
    },
}
_SAMPLES["SubagentStop"] = {**_SAMPLES["Stop"], "hook_event_name": "SubagentStop"}
_SAMPLES["SessionEnd"] = {**_SAMPLES["SessionStart"], "hook_event_name": "SessionEnd"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Print a sample JSON payload for the requested event type and exit
def _create_sample(event_type: str) -> None:
    """
    Print a JSON sample payload for the given event type.

    Args:
        event_type: One of the valid Claude Code hook event names.

    Raises:
        SystemExit: Code 1 if the event type is unknown; code 0 on success.
    """
    if event_type not in _SAMPLES:
        print(f"Unknown event type: {event_type}")
        print(f"Valid types: {', '.join(_SAMPLES)}")
        sys.exit(1)
    print(json.dumps(_SAMPLES[event_type], indent=2))
    sys.exit(0)


# Build the subprocess command list to run the hook script
def _build_cmd(hook_script: str) -> list:
    """
    Determine the execution command for a hook script.

    Python scripts are run via `python3`; others are tried directly, falling
    back to `bash` if not executable.

    Args:
        hook_script: Path to the hook script file.

    Returns:
        List of command components suitable for subprocess.run().
    """
    if hook_script.endswith(".py"):
        return ["python3", hook_script]
    if os.access(hook_script, os.X_OK):
        return [hook_script]
    print("⚠️  Warning: Hook script is not executable. Attempting to run with bash...")
    return ["bash", hook_script]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

# Entry point: parse args, run the hook, and report results
def main() -> None:
    """
    Run a hook script with a JSON test input file and report the outcome.

    Raises:
        SystemExit: Code 0 on hook pass (exit 0 or 2); code 1 on failure or bad args.
    """
    parser = argparse.ArgumentParser(
        description="Test a Claude Code hook script with sample input",
        add_help=True,
    )
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show detailed execution information")
    parser.add_argument("-t", "--timeout", type=int, default=60,
                        help="Timeout in seconds (default: 60)")
    parser.add_argument("--create-sample", metavar="EVENT_TYPE",
                        help="Print a sample JSON payload and exit")
    parser.add_argument("hook_script", nargs="?")
    parser.add_argument("test_input", nargs="?")
    opts = parser.parse_args()

    if opts.create_sample:
        _create_sample(opts.create_sample)

    if not opts.hook_script or not opts.test_input:
        parser.print_help()
        sys.exit(1)

    hook_script = opts.hook_script
    test_input = opts.test_input

    if not os.path.isfile(hook_script):
        print(f"❌ Error: Hook script not found: {hook_script}")
        sys.exit(1)

    if not os.path.isfile(test_input):
        print(f"❌ Error: Test input not found: {test_input}")
        sys.exit(1)

    try:
        with open(test_input) as fh:
            input_data = json.load(fh)
        input_text = json.dumps(input_data)
    except json.JSONDecodeError:
        print("❌ Error: Test input is not valid JSON")
        sys.exit(1)

    print(f"🧪 Testing hook: {hook_script}")
    print(f"📥 Input: {test_input}")
    print()

    if opts.verbose:
        print("Input JSON:")
        print(json.dumps(input_data, indent=2))
        print()

    env = os.environ.copy()
    env.setdefault("CLAUDE_PROJECT_DIR", "/tmp/test-project")
    env.setdefault("CLAUDE_PLUGIN_ROOT", os.getcwd())
    env.setdefault("CLAUDE_ENV_FILE", f"/tmp/test-env-{os.getpid()}")

    if opts.verbose:
        print("Environment:")
        for key in ("CLAUDE_PROJECT_DIR", "CLAUDE_PLUGIN_ROOT", "CLAUDE_ENV_FILE"):
            print(f"  {key}={env[key]}")
        print()

    print(f"▶️  Running hook (timeout: {opts.timeout}s)...")
    print()

    cmd = _build_cmd(hook_script)
    start = time.monotonic()
    try:
        result = subprocess.run(
            cmd,
            input=input_text,
            capture_output=True,
            text=True,
            timeout=opts.timeout,
            env=env,
        )
        exit_code = result.returncode
        output = (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        exit_code = 124
        output = ""
    duration = int(time.monotonic() - start)

    print(_SEPARATOR)
    print("Results:")
    print()
    print(f"Exit Code: {exit_code}")
    print(f"Duration: {duration}s")
    print()

    status_map = {0: "✅ Hook approved/succeeded", 2: "🚫 Hook blocked/denied",
                  124: f"⏱️  Hook timed out after {opts.timeout}s"}
    print(status_map.get(exit_code, f"⚠️  Hook returned unexpected exit code: {exit_code}"))
    print()
    print("Output:")
    if output:
        print(output)
        print()
        try:
            print("Parsed JSON output:")
            print(json.dumps(json.loads(output), indent=2))
        except json.JSONDecodeError:
            pass
    else:
        print("(no output)")

    env_file = env["CLAUDE_ENV_FILE"]
    if os.path.isfile(env_file):
        print()
        print("Environment file created:")
        with open(env_file) as fh:
            print(fh.read())
        os.remove(env_file)

    print()
    print(_SEPARATOR)

    if exit_code in (0, 2):
        print("✅ Test completed successfully")
        sys.exit(0)
    print("❌ Test failed")
    sys.exit(1)


if __name__ == "__main__":
    main()
