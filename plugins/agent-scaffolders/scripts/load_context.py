#!/usr/bin/env python
"""
load_context.py
=====================================

Purpose:
    SessionStart hook that detects the current project type (Node.js, Rust, Go,
    Python, Java/Maven, Java/Gradle) by inspecting well-known marker files and
    writes the detected environment variables to CLAUDE_ENV_FILE for pickup by
    the agent session.

Layer: Retrieve

Usage:
    echo '<session-start-json>' | python load_context.py
"""
import sys
import os

# Ordered list of (marker_files, label, env_vars) for project type detection
_PROJECT_DETECTORS: list = [
    (["package.json"],              "📦 Node.js",          [("PROJECT_TYPE", "nodejs")]),
    (["Cargo.toml"],                "🦀 Rust",             [("PROJECT_TYPE", "rust")]),
    (["go.mod"],                    "🐹 Go",               [("PROJECT_TYPE", "go")]),
    (["pyproject.toml", "setup.py"], "🐍 Python",          [("PROJECT_TYPE", "python")]),
    (["pom.xml"],                   "☕ Java (Maven)",     [("PROJECT_TYPE", "java"),
                                                            ("BUILD_SYSTEM", "maven")]),
    (["build.gradle", "build.gradle.kts"], "☕ Java/Kotlin (Gradle)",
                                                           [("PROJECT_TYPE", "java"),
                                                            ("BUILD_SYSTEM", "gradle")]),
]

# CI configuration marker paths used to set HAS_CI
_CI_MARKERS: list = [".github/workflows", ".gitlab-ci.yml", ".circleci/config.yml"]


# Write a shell export line to the Claude environment file
def _write_env(env_file: str, var: str, value: str) -> None:
    """
    Append an `export VAR=value` line to the Claude environment file.

    Args:
        env_file: Path to CLAUDE_ENV_FILE (may be empty string if not set).
        var: Environment variable name.
        value: Environment variable value.
    """
    if env_file:
        with open(env_file, "a") as fh:
            fh.write(f"export {var}={value}\n")


# Detect project type by checking marker files and write results to env file
def _detect_project(env_file: str) -> None:
    """
    Inspect the current directory for project type markers and emit env vars.

    Iterates _PROJECT_DETECTORS in order and writes all env vars for the first
    matching detector. Falls back to PROJECT_TYPE=unknown if nothing matches.

    Args:
        env_file: Path to CLAUDE_ENV_FILE for writing detected variables.
    """
    for markers, label, env_vars in _PROJECT_DETECTORS:
        if any(os.path.isfile(m) for m in markers):
            print(f"{label} project detected")
            for var, val in env_vars:
                _write_env(env_file, var, val)
            # TypeScript sub-check for Node projects
            if "nodejs" in dict(env_vars).get("PROJECT_TYPE", "") and os.path.isfile("tsconfig.json"):
                _write_env(env_file, "USES_TYPESCRIPT", "true")
            return

    print("❓ Unknown project type")
    _write_env(env_file, "PROJECT_TYPE", "unknown")


# Entry point: load and emit project context for a Claude Code SessionStart hook
def main() -> None:
    """
    Detect project type and write environment variables to CLAUDE_ENV_FILE.

    Raises:
        SystemExit: Code 1 if CLAUDE_PROJECT_DIR cannot be entered; code 0 on success.
    """
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    env_file = os.environ.get("CLAUDE_ENV_FILE", "")

    try:
        os.chdir(project_dir)
    except OSError as exc:
        print(f"❌ Cannot change to project directory: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Loading project context...")

    _detect_project(env_file)

    # Check for CI configuration
    if any(os.path.exists(m) for m in _CI_MARKERS):
        _write_env(env_file, "HAS_CI", "true")

    print("Project context loaded successfully")
    sys.exit(0)


if __name__ == "__main__":
    main()
