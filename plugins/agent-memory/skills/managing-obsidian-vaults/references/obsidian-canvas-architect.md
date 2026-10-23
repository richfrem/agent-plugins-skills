# Obsidian Canvas Architect (obsidian-canvas-architect)

Programmatically creates and manipulates Obsidian Canvas (`.canvas`) files using JSON Canvas Spec 1.0.

## Contents
- [Critical Constraints](#critical-constraints)
- [Dependencies](#dependencies)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- All canvas mutations must route through atomic write operations with schema validation.
- Node and edge identifiers must be generated dynamically via UUIDs to prevent collisions.
- Every node requires explicit positioning coordinates (`x`, `y`, `width`, `height`).

## Dependencies

Requires Python 3.8+ and standard library modules.

## Quick start
```bash
# Create empty canvas
python3 scripts/canvas_ops.py create --file <path.canvas>

# Add node to canvas
python3 scripts/canvas_ops.py add-node --file <path.canvas> --type text --text "Node Title" --x 100 --y 200

# Add directed edge between nodes
python3 scripts/canvas_ops.py add-edge --file <path.canvas> --from-node id1 --to-node id2
```

## Workflow
1. **Canvas Initialization**: Verify or create the target `.canvas` file with empty nodes and edges arrays.
2. **Node Creation**: Add text, file reference, link, or group visual containers with coordinate bounding boxes.
3. **Edge Routing**: Connect nodes with directional edges specifying source and target side ports.
4. **Validation & Persistence**: Stage JSON writes atomically and validate against JSON Canvas Spec 1.0.

## Verification
```bash
# Inspect canvas structure and node validity
python3 scripts/canvas_ops.py read --file <path.canvas>

```

## References
- [acceptance-criteria.md](obsidian-canvas-architect-acceptance-criteria.md) - Canvas architect invariants and validation criteria.
- [fallback-tree.md](obsidian-canvas-architect-fallback-tree.md) - Recovery procedures for malformed JSON and canvas write errors.
