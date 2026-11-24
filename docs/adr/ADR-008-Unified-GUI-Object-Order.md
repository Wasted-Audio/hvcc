# ADR-008: Unified GUI Object Order

Date: 2026-11-24

Issue: https://github.com/Wasted-Audio/hvcc/issues/294

## Context

In Pure Data, graphical objects (`[cnv]`, `[bng]`, `[tgl]`, etc.) and Graph-on-Parent (GoP) subpatches/abstractions are stored in a single canvas list (`gl_list`). Pure Data renders elements strictly in the chronological order they appear in the `.pd` file (from bottom/back to top/front).

In ADR-002, the initial `pd2gui` implementation separated canvas contents into two separate collections:

- `objects: list[GUIObjects]`
- `graphs: list[Graph]`

This separation caused two major issues:

1. **Lost Z-Order**: The relative interleaving of subpatches and normal GUI objects on the same canvas was lost during parsing.
2. **Layer Inversion in Renderers**: Downstream code generators (such as `c2dpf/nanovg_render.py`) rendered all `objects` first and all `graphs` afterwards. As a result, subpatches were always drawn on top of all local objects, making it impossible for a UI object to cover or sit on top of a subpatch.

## Decision

We unify subpatches/graphs and standard GUI objects into a single recursive tree hierarchy:

1. **`Graph` is a `GUIObject`**:
   - `Graph` inherits from `BaseUI` with `type: Literal["graph"] = "graph"`.
   - `gop_size` is unified to `size: Size` across all objects.
   - `Graph.objects` holds an ordered list of `GUIObjects` (which recursively includes `Graph`).
   - `GraphBase` is removed; `GraphRoot` retains root-level document metadata (`id`, `size`, `theme`, `version`) and the top-level `objects: list[GUIObjects]`.

2. **Sequential Canvas Parsing in `PdGUIParser`**:
   - `PdGUIParser.gui_from_canvas` maintains a single `objects: list[GUIObjects]` list.
   - Subpatches (`#N canvas ... #X restore`) and abstractions (`#X obj`) are appended directly into `objects` at the point they are encountered.
   - `filter_invisible_graphs` is merged into `filter_invisible_objects`, which recursively validates bounding box intersections with the local GoP area and discards empty graphs.

3. **Tree-Ordered Rendering in Generators**:
   - Generators like `nanovg_render.py` traverse `objects` in sequence.
   - Standard objects and `PDSubpatch` instances are instantiated and added to the parent widget in the exact order parsed, correctly preserving z-order while keeping child objects clipped inside their respective subpatches.

### Breaking Changes

- **Breaking IR Change**: The top-level `"graphs"` key and nested `"graphs"` keys in the GUI IR JSON are removed. Subpatches now appear inside `"objects"` with `"type": "graph"`.
- **Field Rename**: `gop_size` on subpatches is renamed to `size` to conform to `BaseUI`.

## MVP Definition

Subpatches and standard GUI objects maintain their exact canvas z-order as defined in the `.pd` file. Downstream generators render elements in sequence, allowing UI objects to be placed both behind and in front of subpatches, while maintaining proper Graph-on-Parent clipping for child objects.
