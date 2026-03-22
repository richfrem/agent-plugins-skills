# Dependency Management Policy — Detailed Reference

## Service Inventory (Example)

All isolated services that own a lockfile:

| Service | Path | Notes |
|---------|------|-------|
| Core | `src/requirements-core.in` | Baseline for all services |
| Auth | `src/services/auth_service/requirements.in` | Authentication layer |
| Database | `src/services/db_service/requirements.in` | Database connections |
| Payments | `src/services/payments_service/requirements.in` | Payment gateways |

### Acknowledged Advisories (No Fix Available)
- `diskcache==5.6.3` — Inherent pickle deserialization risk.
  Latest version is 5.6.3. Mitigations: avoid storing untrusted data in cache, or use `JSONDisk` serialization.

## Parity Requirement

The execution environment (Docker, Podman, `.venv`) must not change the dependency logic.
Install from the same locked artifact regardless of where the code runs:

```dockerfile
# Dockerfile pattern
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app
```

## pip-compile Options

Recommended flags for reproducible builds:

```bash
pip-compile \
  --no-emit-index-url \
  --strip-extras \
  --allow-unsafe \
  requirements.in \
  --output-file requirements.txt
```

When a vulnerability exists in a transitive dependency:

1. Identify which direct dependency pulls it in:
   ```bash
   grep -B2 "package-name" src/requirements-core.txt
   # Look for "# via" comments
   ```

2. Add a floor pin in the `.in` file that owns the ancestor:
   ```
   # SECURITY: Force patched transitive dep
   vulnerable-package>=X.Y.Z
   ```

3. Recompile. The resolver will satisfy both the ancestor's constraint and your floor pin.
