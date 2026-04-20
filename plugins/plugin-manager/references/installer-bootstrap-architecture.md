# Installer Bootstrap Architecture: Replacing `npx`

## The Problem Statement

Our transition to the GitHub-native, cross-platform `plugin_add.py` script successfully resolved the Windows symlink failures caused by legacy installation methods. However, we've traded one problem for another: **The Bootstrap Problem**.

`npx` has an immense ergonomic advantage: it downloads and executes code from a remote registry on the fly. Consumers don't need to clone a repository to run a script inside it. Right now, `plugin_add.py` requires the user to either clone the `agent-plugins-skills` repository or run from within it.

We need a frictionless, one-line installation mechanism for consumers to trigger our Python-based plugin installer *without* having the repository cloned locally.

Below is an analysis of architectural options to achieve this.

---

## Option 1: `uv` and `uvx` (The Modern Python Standard)

[uv](https://docs.astral.sh/uv/) is a blazingly fast Rust-based Python package manager that is rapidly becoming the industry standard. It mimics the ergonomics of `npx` via `uvx`.

By adding a simple `pyproject.toml` to the root of our repository, consumers can run:

```bash
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills
```

**Pros:**
- **Exact `npx` Equivalent:** It creates a temporary, isolated environment, downloads the repo, runs the mapped entry script (`plugin_add.py`), and tears it down.
- **Zero Local Footprint:** `plugin_add.py` resolves its relative local dependencies (like `bridge_installer.py`) fully isolated from the user's workspace.
- **No PyPI Required:** Works directly from the GitHub URL.

**Cons:**
- Requires the consumer to have `uv` installed.

---

## Option 2: `pipx` (The Classic Sandbox)

Similar to `uvx`, `pipx` allows executing Python CLIs securely without polluting the global environment. The `pyproject.toml` modification from Option 1 makes this work out of the box.

```bash
pipx run --spec git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills
```

**Pros:**
- Heavily adopted across the Python ecosystem.
- Does not require publishing anything to PyPI.

**Cons:**
- `pipx install git+https://...` is significantly slower than `uvx`.

---

## Option 3: "curl-to-python" (The Zero-Dependency Path)

Since `plugin_add.py` is written in standard library Python, we can provide a universally compatible one-liner that fetches a "bootstrap" script from GitHub's raw user content and executes it within the user's local Python environment.

**Mac / Linux:**
```bash
curl -sL https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main/bootstrap.py | python - richfrem/agent-plugins-skills
```

**Windows (PowerShell):**
```powershell
Invoke-RestMethod https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main/bootstrap.py | python - richfrem/agent-plugins-skills
```

**Pros:**
- Absolute zero friction. Requires only native Python (which agent developers already have installed). No package managers (`npm`, `uv`, `pipx`) required.

**Cons:**
- Requires engineering a `bootstrap.py` script whose sole job is to download `plugin_add.py` (and its dependency `bridge_installer.py`) into a temporary folder, execute it, and clean up.
- Security optics: IT departments often flag `curl | bash` equivalent patterns as bad practice.

---

## Option 4: Publish to PyPI 

We bundle `plugin_add.py` and `bridge_installer.py` into a lightweight, standalone Python package (e.g., `antigravity-plugins`) and publish it officially to PyPI.

```bash
pip install antigravity-plugins
antigravity-plugins add richfrem/agent-plugins-skills
```

**Pros:**
- The most standard, "clean" installation method for Python tooling.
- Shortest command syntax without requiring package manager flags.

**Cons:**
- Introduces operational overhead: we must maintain a PyPI package and trigger deployment pipelines on every change to the installer logic.

---

## Option 5: Build a lightweight `npx` wrapper

We publish a tiny stub package to NPM (`@agent-plugins/cli`) whose ONLY job is to execute a `fetch()` call, download the Python `plugin_add.py` script to a temp folder, and spawn `python temp_script.py`.

```bash
npx @agent-plugins/cli add richfrem/agent-plugins-skills
```

**Pros:**
- Retains the exact ergonomic feel of universal one-liner installers.

**Cons:**
- Philosophically contradicts our effort to remove Node.js as a dependency to fix Windows compatibility. (Though technically, executing a Node script that calls Python would work, it's an unnecessary architectural loop).

---

## Technical Recommendation

The most robust architectural path is **Hybrid Support (Option 1 + Option 3)**.

1. **Add `pyproject.toml`:** This requires ~15 lines of configuration declaring the project and mapping the `[project.scripts]` entry points. This immediately unlocks both `uvx` and `pip` support directly from GitHub. It is the cheapest implementation pattern with massive scaling upside.
2. **Author `bootstrap.py`:** Create a tiny script at the repo root for absolute beginners. It guarantees a frictionless installation for anyone who does not yet use `uv` or `pipx`.
