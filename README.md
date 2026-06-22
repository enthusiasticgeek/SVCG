# SVCG — Simple VHDL Code Generator

A GTK3-based Python desktop application for visually designing digital circuits and generating VHDL. Place logic blocks on a schematic canvas, wire them together, and export a complete structural VHDL file.

---

## Features

- **Visual schematic editor** — drag-and-drop blocks on a scrollable 5000×5000 canvas with zoom
- **Logic gates** — AND, OR, NOT, NAND, NOR, XOR, XNOR
- **Flip-flops** — JK, SR, D (with pipeline variant), T
- **Multiplexers** — 2×1, 4×1, 8×1 MUX
- **Tristate buffers** — 2, 4, 8 channel
- **Arithmetic** — Full Adder (standard, Gray Cell, White Cell), Half Adder
- **I/O primitives** — Input/Output/Bidirectional pins and buses, CLK, VDD (5V/3.3V/1.8V/1.2V), GND
- **Wire routing** — A* pathfinding with Manhattan fallback when path is blocked
- **Wire net names** — right-click a wire to set its net name; names appear on canvas and in generated VHDL
- **VHDL export** — `File > Generate VHDL...` produces a complete structural VHDL entity + architecture
- **VHDL viewer** — right-click any gate block to read its per-block VHDL template
- **Zoom** — Ctrl+scroll-wheel (0.2× – 4.0×)
- **Multi-select** — Shift+click to select multiple blocks/pins/wires; group move, copy, delete
- **Undo/Redo** — Ctrl+Z / Ctrl+R (depth-unlimited JSON snapshots)
- **Copy/Cut/Paste/Delete** — Ctrl+C / Ctrl+X / Ctrl+V / Ctrl+D (works on single or multi-select)
- **Rotation** — 90°/180°/270° on unconnected blocks and pins
- **Per-element styling** — border color, fill color, text color via right-click context menu
- **Dirty flag** — window title shows `*` for unsaved changes; closing prompts Save/Discard/Cancel
- **Status bar** — shows selected element, canvas counts, and current filename
- **Save/Load** — JSON project files via File menu
- **EDIF export** (experimental) — `src/experimental/edif_convertor.py`

---

## Prerequisites

### Windows (MSYS2 MINGW64)

Open the **MSYS2 MINGW64** shell and run:

```bash
pacman -S mingw-w64-x86_64-python-gobject \
          mingw-w64-x86_64-gtk3 \
          mingw-w64-x86_64-python-cairo \
          mingw-w64-x86_64-python-numpy
```

### Linux (Debian/Ubuntu)

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-numpy
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install python3-gobject gtk3 python3-cairo python3-numpy
```

---

## Running

```bash
cd src
python3 main.py
```

---

## Keyboard Shortcuts

| Shortcut     | Action                         |
|--------------|--------------------------------|
| Ctrl+Z       | Undo                           |
| Ctrl+R       | Redo                           |
| Ctrl+C       | Copy selected (single or group)|
| Ctrl+X       | Cut selected (single or group) |
| Ctrl+V       | Paste at cursor                |
| Ctrl+D       | Delete selected (single or group)|
| Ctrl+P       | Rotate 90° CW                  |
| Ctrl+scroll  | Zoom in / out                  |
| Escape       | Clear multi-select             |

---

## Mouse Controls

| Action                              | Effect                                        |
|-------------------------------------|-----------------------------------------------|
| Left-click + drag on block/pin      | Move element                                  |
| Shift+left-click                    | Add/remove element from multi-select group    |
| Left-click on connection dot        | Start drawing a wire                          |
| Release on another dot              | Complete wire connection                      |
| Right-click on block body           | Context menu (colors, rotate, copy, VHDL...)  |
| Right-click on block pin dot        | Pin connection menu                           |
| Right-click on wire                 | Wire menu (rename net, delete)                |
| Ctrl+scroll-wheel                   | Zoom in / out (0.2× – 4.0×)                  |

---

## Workflow: Schematic to VHDL

1. **Add IO pins** from the left panel (Input Pin, Output Pin, etc.) — these become entity ports.
2. **Add blocks** (gates, flip-flops, muxes, etc.) from the left panel.
3. **Draw wires** by clicking a connection dot (green circle) and releasing on another dot.
4. **Name wires** with right-click → "Rename" — the net name appears on canvas and maps to a VHDL `signal`.
5. **Generate VHDL** via `File > Generate VHDL...`:
   - Enter the top-level entity name (defaults to the JSON filename).
   - Choose a `.vhd` save path.
   - A preview of the generated VHDL opens automatically.

The generated file contains:
- `entity` with ports derived from your IO pins
- `architecture Structural` with `component` declarations, internal `signal`s, and structural `port map`s

---

## Project File Format

Designs are stored as JSON arrays. Each element is one of:

- **Block** — `block_type`, position, size, colors, rotation, `input_wires`, `output_wires`
- **Pin** — `pin_type`, position, `connection_points`, `wires`
- **Wire** — `id`, `text` (net name), `start_point`, `end_point`, A* `path`

---

## EDIF Export (Experimental)

```bash
cd src/experimental
python3 edif_convertor.py ../my_design.json my_design.edf
```

---

## Directory Structure

```
SVCG/
├── src/
│   ├── main.py             # Entry point
│   ├── main_window.py      # GTK window, event handlers, undo/redo
│   ├── drawing_area.py     # GTK DrawingArea, zoom, grid
│   ├── blocks.py           # Block model and drawing
│   ├── pins.py             # Pin/bus model and drawing
│   ├── wire.py             # Wire model, A* routing, Manhattan fallback
│   ├── astar.py            # A* pathfinding on numpy grid
│   ├── menu.py             # GTK menu/toolbar actions
│   ├── context_menu.py     # Right-click context menus
│   ├── vhdl_export.py      # Full-schematic VHDL generator
│   └── vhdl/               # VHDL templates (one .vhd per block type)
└── src/experimental/
    └── edif_convertor.py   # JSON -> EDIF netlist converter
```

---

## License

MIT — see [LICENSE](LICENSE).
