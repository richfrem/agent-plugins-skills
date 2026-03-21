# Procedural Fallback Tree: Env-Helper Resolution

If the primary scanning engine (`./../scripts/env_helper.py`) fails to resolve a key and exits with code `1`, execute the following triage steps exactly in order:

## 1. Missing `.env` File
If the script exits with `1` claiming a required key (like `HF_TOKEN` or `HF_USERNAME`) is missing:
- **Action**: Check if a `.env` file literally exists at the root of the user's workspace repository (`ls -la .env`).
- If it does not exist, you must create it for the user using their provided values or instruct them to define the keys:
```bash
HF_TOKEN=""
HF_USERNAME=""
```

## 2. Unregistered Key
If the script exits with `1` for a key that *is* defined in the `.env` file, the `./../scripts/env_helper.py` script may need the key added to its internal `REQUIRED` or `DEFAULTS` list, or it may not be exporting the variables correctly. Read the script implementation.
