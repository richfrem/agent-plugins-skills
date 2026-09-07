# Fallback Tree for os-memory-manager

1. Read/write via kernel.py memory API -> 2. If kernel.py unavailable, fall back to direct file read/append on the target memory markdown file.
