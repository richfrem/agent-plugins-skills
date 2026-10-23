# Vector runtime dependencies

## Contents

- [Ownership](#ownership)
- [Install and regenerate](#install-and-regenerate)
- [SQLite runtime](#sqlite-runtime)
- [Validation limits](#validation-limits)

## Ownership

This skill owns its requirements.in and compiled requirements.txt. The original
agent-memory vector dependency set and its version floors are preserved here.
No requirement file imports a sibling skill's requirements. APM copies the skill
but does not install its Python dependencies.

| Runtime purpose | Distribution or runtime |
|---|---|
| Persistent vector collections / local store | chromadb |
| Parent-child documents and chunking | langchain-core, langchain-text-splitters |
| Chroma adapter | langchain-chroma |
| Embedding adapter/model runtime | langchain-huggingface, sentence-transformers, einops |
| Storage compatibility interfaces | langchain, langchain-classic, langchain-community |
| Metadata/frontmatter validation | python-frontmatter, pydantic and pydantic-settings |
| Local SQLite engine | Python's sqlite3 runtime; not a pip sqlite3 package |

The lockfile also includes all transitive packages and original security floors.
LangChain Core and Classic are explicit intent declarations because the scripts
import them directly; their existing locked versions were preserved.

## Install and regenerate

Use the selected consumer Python environment. From this skill folder, install only
the reviewed lockfile within the authorized setup scope:

```bash
python -m pip install -r requirements.txt
```

Dependency changes follow the dependency-management rule: edit requirements.in,
then compile and review requirements.txt together. Do not hand-edit the lockfile
or substitute ad-hoc pip package lists. Regenerate from this skill folder:

```bash
python -m piptools compile --strip-extras --output-file requirements.txt requirements.in
```

## SQLite runtime

SQLite support is supplied with the Python interpreter and checked by Chroma.
Do not add a nonexistent pip sqlite3 dependency or silently swap modules. Inspect
the interpreter and Chroma import before configuring a database:

```bash
python -c "import sqlite3; import chromadb; print('SQLite:', sqlite3.sqlite_version); print('Chroma:', chromadb.__version__)"
```

If the installed Chroma rejects the interpreter's SQLite version, choose a compatible
Python build/environment and recheck it before ingestion. Server mode still binds
only to localhost; collection access uses the supported API, not raw SQLite edits.

## Validation limits

Compare installed package versions with this skill's lockfile before claiming the
locked environment is tested. A working workstation import proves availability in
that environment; it does not prove a fresh lockfile installation. Initial embedding
model downloads and actual ingestion are separate from configuration checks.
