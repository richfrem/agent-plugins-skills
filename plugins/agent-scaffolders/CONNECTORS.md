# CONNECTORS.md — agent-scaffolders

Maps `~~category` capability placeholders to concrete plugin implementations
discovered via the `tool-inventory` capability index.

> **How resolution works:**
> 1. The `tool-inventory` skill reads all `plugin.json` files and builds
>    `plugins/tool-inventory/assets/capability-index.json`.
> 2. When a skill references `~~eval-gate`, this file maps it to the
>    installed plugin that provides that capability.
> 3. If the provider plugin is not installed, the skill degrades gracefully
>    (skips the step) rather than failing hard.

---

## Category Mappings

| Category | Default Provider | Skill / Entry Point | Fallback |
|----------|-----------------|---------------------|----------|
| `~~eval-gate` | `agent-agentic-os` | `os-eval-runner` — autoresearch eval loop, KEEP/DISCARD gate | Skip eval loop; manual quality review |
| `~~skill-improvement` | `agent-agentic-os` | `os-skill-improvement` — RED-GREEN-REFACTOR TDD cycle | Manual skill refinement without score tracking |

---

## Refresh Index

To rebuild the capability index after installing or removing plugins:

```bash
python3 plugins/tool-inventory/scripts/build_capability_index.py
```

Output: `plugins/tool-inventory/assets/capability-index.json`

---

## Notes

- This CONNECTORS.md follows [ADR-004](../../../ADRs/004_self_contained_plugins_no_cross_plugin_dependencies.md):
  `~~category` abstraction only — no cross-plugin script paths.
- Alternative providers: any plugin declaring `"capabilities": ["eval-gate"]` in its
  `plugin.json` can serve as a drop-in replacement. The capability index resolves the
  first available provider at runtime.
