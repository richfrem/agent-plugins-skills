# Procedural Fallback Tree: Vector DB Agent

If the primary database wrappers (`././query.py`, `ingest.py`) fail, execute the following triage steps exactly in order:

## 1. Connection Refused (Server Down)
If the python scripts exit with an HTTP `Connection refused` referencing port `8110`:
- **Action**: Do not attempt to read the database manually. It means the background `chroma` server is not running on the operating system. You must either start the server manually (`vector-db-launch`) or instruct the user they must boot it up according to their profile initialization.

## 2. Invalid Profile Configuration
If `././query.py` or `ingest.py` crash stating the requested `--profile` name does not exist in `.agent/learning/vector_profiles.json`:
- **Action**: Do not attempt to write the profile manually into the configuration JSON. You must execute the `vector-db-init` initialization script to guide the user organically through generating a sanitized profile structure.

## 3. Langchain Classic Storage Missing
If the ingestion tool throws a `ModuleNotFoundError` specifically noting `langchain.storage` or `langchain-classic` is missing:
- **Action**: Do not attempt to rewrite the ingestion logic. You specify that the `langchain-classic` package must be Pip installed because it contains the legacy FileStore components required by the Parent-Child retriever architecture.
