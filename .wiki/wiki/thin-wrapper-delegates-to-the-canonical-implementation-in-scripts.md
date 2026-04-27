---
concept: thin-wrapper-delegates-to-the-canonical-implementation-in-scripts
source: plugin-code
source_file: agent-agentic-os/hooks/scripts/post_run_metrics.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.690978+00:00
cluster: target
content_hash: 330f7a6a40b2a3dd
---

# Thin wrapper — delegates to the canonical implementation in scripts/

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
# Thin wrapper — delegates to the canonical implementation in scripts/
import sys
import os
from pathlib import Path

# Resolve CLAUDE_PLUGIN_ROOT or fall back to two levels up from this file
plugin_root = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).parent.parent.parent))
target = plugin_root / "scripts" / "post_run_metrics.py"

if not target.exists():
    print(f"ERROR: post_run_metrics.py not found at {target}", file=sys.stderr)
    sys.exit(1)

# Re-exec the real script so it runs in its own context
os.execv(sys.executable, [sys.executable, str(target)] + sys.argv[1:])


## See Also

- [[add-the-parent-directory-to-syspath-so-we-can-import-parserpy]]
- [[add-the-scripts-directory-so-we-can-import-rlm-config]]
- [[match-pythonexecution-paths-that-are-hardcoded-to-the-repo-root-plugins-folder]]
- [[only-include-those-appearing-in-2-of-the-last-n-traces]]
- [[patterns-to-find-file-references-in-code]]
- [[result-type-tells-downstream-tools-how-to-parse-the-entry]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/hooks/scripts/post_run_metrics.py`
- **Indexed:** 2026-04-27T05:21:03.690978+00:00
