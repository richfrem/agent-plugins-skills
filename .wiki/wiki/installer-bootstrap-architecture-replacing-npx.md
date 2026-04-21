---
concept: installer-bootstrap-architecture-replacing-npx
source: plugin-code
source_file: plugin-manager/references/installer-bootstrap-architecture.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.662250+00:00
cluster: python
content_hash: 152b2f996ba77213
---

# Installer Bootstrap Architecture: Replacing `npx`

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
- **Zero Local Footprint:** `plugin_add.py` resolves its relative local dependencies (like `plugin_installer.py`) fully isolated from the user's workspace.
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
- Requires engineering a `bootstrap.py` script whose sole job is to download `plugin_add.py` (and its dependency `plugin_installer.py`) into a temporary folder, execute it, and clean up.
- Security optics: IT departments often flag `curl | bash` equivalent patterns as bad practice.

---

## Option 4: Publish to PyPI 

We bundle `plugin_add.py` and `plugin_installer.py` into a lightweight, standalone Python package (e.g., `antigravity-plugins`) and publish it officially to PyPI.

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



*(content truncated)*

## See Also

- [[006-python-native-plugin-bootstrap-installer-replacing-npx]]
- [[006-python-native-plugin-bootstrap-installer-replacing-npx]]
- [[006-python-native-plugin-bootstrap-installer-replacing-npx]]
- [[006-python-native-plugin-bootstrap-installer-replacing-npx]]
- [[session-bootstrap]]
- [[triple-loop-learning-system---architecture-overview]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `plugin-manager/references/installer-bootstrap-architecture.md`
- **Indexed:** 2026-04-17T06:42:09.662250+00:00
