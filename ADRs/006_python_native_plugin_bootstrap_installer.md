# 006: Python-Native Plugin Bootstrap Installer (Replacing npx)

## Status
Accepted

## Context
Early versions of this repository relied on `npx skills add` to distribute and install plugins. While `npx` provided excellent ergonomics (on-the-fly execution from GitHub without cloning), it caused critical failures on Windows. Git for Windows, without Developer Mode enabled, checks out symlinks as plain text files containing paths. Because `npx` clones the repo into a temporary space, Windows users were left with broken text files in their `.agents/` directories instead of executable scripts.

To solve this cross-platform issue, we wrote a native Python installer (`plugin_add.py`) that implements smart copy/junction fallbacks. However, moving to a pure Python script reintroduced a "Bootstrap Problem": users could no longer run a one-line install command without first cloning the entire repository.

We needed a way to provide `npx`-like ergonomics (remote execution) using only Python tooling, ensuring zero Node.js dependencies while remaining cross-platform compatible.

## Decision
We decided to adopt a two-pronged, native-Python installation architecture:

1. **Primary Path (`uvx`):** We added a minimal `pyproject.toml` to the repository root that maps a `plugin-add` CLI entry point. This allows users of the modern `uv` Python toolchain to run `uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add` to interactively install plugins in an ephemeral, isolated environment, perfectly mirroring `npx` ergonomics.
2. **Fallback / Zero-Dependency Path (`bootstrap.py`):** For users without `uv`, we created a standalone `bootstrap.py` script. This script can be executed directly from GitHub's raw content via `curl` (Mac/Linux) or `Invoke-RestMethod` (PowerShell). It fetches the installer core into memory and executes it.

Additionally, we explicitly delineated the difference between **Initial Install** (bootstrapping the environment) and **Subsequent Installs** (running the `plugin_add.py` copy that was installed locally into `.agents/` during the first pass).

## Consequences

**Positive:**
- Complete removal of Node.js / `npm` / `npx` dependencies from the agent plugin ecosystem.
- Frictionless, one-line initial installations across all operating systems.
- 100% resolution of Windows symlink deployment failures.
- Alignment with the emerging `uv` standard for Python-based agent architectures and MCP servers.

**Negative / Trade-offs:**
- Requires managing and documenting a two-step mental model: "how to bootstrap the installer" vs "how to run the installer locally once you have it". 
- `curl | python` pattern is subject to security optics concerns in strict enterprise environments, though mitigated by `uvx` being the primary supported path.
