# SVCG — Improvement Plan

Prioritized roadmap from highest-impact to nice-to-have.

---

## P0 — Correctness / Stability (do first)

These are bugs that cause silent data loss or crashes during normal use.

| # | File | Issue | Fix |
|---|------|-------|-----|
| 1 | `menu.py:181,205` | `dialog.destroy()` on undefined variable crashes when user cancels a load | ✅ Fixed — removed invalid call |
| 2 | `menu.py:259` | `on_save_as_file()` AttributeError on File > Save | ✅ Fixed — corrected method name |
| 3 | `main_window.py:update_points` | Spurious `break` exits loop after first block/pin — wire endpoints not updated on rotate for all other blocks | ✅ Fixed — removed `break` |
| 4 | `main_window.py:on_rotate_*` | Error dialog fires incorrectly when only a pin (not a block) is selected and has wires | ✅ Fixed — corrected boolean guard |
| 5 | `pins.py:100` | `if "VDD_5V" or ...` always True — every CLK/GND pin unnecessarily draws VDD arrow on top | ✅ Fixed — `any(v in ...)` |
| 6 | `main_window.py:1447` | VHDL file path is relative — breaks when app launched from any directory other than `src/` | ✅ Fixed — `os.path.abspath(__file__)` |
| 7 | `wire.py:96` | Wire label shows UUID instead of user-visible name | ✅ Fixed — `show_text(self.text)` |
| 8 | `astar.py` | Dead `astar0`/`heuristic0` methods + trailing `""` string | ✅ Fixed — removed |

---

## P1 — Core UX / Usability (high value, moderate effort)

### 1.1 Wire label editing ✅
Right-click a wire → "Rename (set net name)" dialog. Wire text is saved to JSON and displayed on canvas. Net names will carry into VHDL `signal` declarations.

### 1.2 Multi-select and group operations
Hold Shift and click to select multiple blocks/pins/wires. Enable group move, group delete, group copy.
Without this, rearranging a complex circuit requires many individual drags.

### 1.3 Zoom in/out ✅
Ctrl+scroll-wheel zoom (0.2×–4.0×). Canvas coordinates are correctly transformed; A* grid and mouse hit-testing both account for zoom level.

### 1.4 Status bar ✅
One-line status bar at the bottom showing: selected element name + type, block/pin/wire counts, and current filename. Updates on every click and selection change.

### 1.5 "New project" actually clears the canvas ✅
`File > New SVCG Project` now asks to save unsaved changes, then clears all blocks/pins/wires, resets the file path, and refreshes the canvas.

### 1.6 Auto-save / dirty flag ✅
Window title shows `*` prefix when unsaved changes exist. Closing the window with unsaved changes prompts "Save / Discard / Cancel". Title updates to show filename on save/load.

---

## P2 — VHDL Generation (the core value proposition)

### 2.1 Whole-schematic VHDL export
Generate a complete VHDL entity + architecture from the wired-up canvas:
- Infer port names from the IO pins
- Infer `signal` declarations from wires (using wire `text` as net name)
- Instantiate each block as a component using the existing per-block `.vhd` templates
- Write `port map` connections from the wire topology

This is the main missing feature — the per-block VHDL viewer exists but there is no end-to-end generator yet.

### 2.2 VHDL syntax check / preview
After generation, run `ghdl -a` (if installed) to verify the output compiles. Display errors inline.

### 2.3 Add missing VHDL templates
Currently only basic gates and flip-flops have templates. Needed:
- MUX 2×1, 4×1, 8×1
- Tristate buffer 2, 4, 8
- Full/Half adder
- DFF pipeline

---

## P3 — Architecture / Code Quality (pay down tech debt)

### 3.1 Replace deprecated `Gtk.UIManager` / `Gtk.Action`
`menu.py` uses `Gtk.UIManager` and `Gtk.Action` which were deprecated in GTK 3.10 and removed in GTK 4. Migrate to `Gio.SimpleAction` + `Gio.Menu` for future-proofing and to eliminate deprecation warnings at startup.

### 3.2 Split `main_window.py` into focused modules
`main_window.py` is ~1500 lines covering event handling, JSON I/O, undo/redo, VHDL display, and UI construction. Suggested split:
- `project_manager.py` — save/load/undo/redo
- `event_handler.py` — mouse/keyboard events
- `vhdl_viewer.py` — VHDL display dialog

### 3.3 Replace `Block.init_wires()` lookup table with data-driven config
`blocks.py:init_wires` is a 30-branch `elif` chain. Replace with a dict mapping `block_type` → `(num_inputs, num_outputs)`.

### 3.4 A* grid resolution
The A* grid maps 1 cell per `grid_size` pixel (20px → 1 cell). On a 5000×5000 canvas this is a 250×250 grid — manageable, but wire routing still blocks on complex schematics. Consider limiting A* to a bounding box around the start/end points, or switching to a rectilinear Steiner tree for multi-segment routes.

### 3.5 Wire routing — Manhattan fallback
When A* fails to find a path (returns `[]`), the wire silently disappears. Add a Manhattan routing fallback so the user always gets a visible (if imperfect) connection.

---

## P4 — New Features (after P1–P3 are stable)

### 4.1 Component library panel
Allow saving a selected sub-circuit as a named reusable component. Drag from library to instantiate.

### 4.2 Simulation integration
Connect to an open-source HDL simulator (GHDL or Icarus Verilog via a Verilog export path). Add waveform viewer widget.

### 4.3 Netlist import
Import EDIF or JSON netlists from third-party tools and auto-place blocks on the canvas.

### 4.4 Dark mode / theme support
Respect the GTK theme. Currently all colors are hardcoded (green grid, black borders, gray fills).

### 4.5 Export canvas as SVG/PNG
Right-click → "Export as image" using Cairo's SVG/PDF surface.

---

## Suggested Sprint Order

```
Sprint 1  P0 fixes (done) + P1.5 New project + P1.6 dirty flag
Sprint 2  P1.1 Wire rename + P1.2 Multi-select + P1.3 Zoom
Sprint 3  P2.1 Full VHDL export + P2.3 Missing templates
Sprint 4  P3.1 Gtk.UIManager migration + P3.2 module split
Sprint 5  P4 features based on user feedback
```
