# SVCG — Simple VHDL Code Generator

A GTK3-based Python desktop application for visually designing digital circuits and generating VHDL. Place logic blocks on a schematic canvas, wire them together, save/load designs as JSON, and inspect per-block VHDL templates.

---

## Features

- **Visual schematic editor** — drag-and-drop blocks on a 5000×5000 pixel scrollable canvas
- **Logic gates** — AND, OR, NOT, NAND, NOR, XOR, XNOR
- **Flip-flops** — JK, SR, D (with pipeline variant), T
- **Multiplexers** — 2×1, 4×1, 8×1 MUX
- **Tristate buffers** — 2, 4, 8 channel
- **Arithmetic** — Full Adder (standard, Gray Cell, White Cell), Half Adder
- **I/O primitives** — Input/Output/Bidirectional pins and buses, CLK, VDD (5V/3.3V/1.8V/1.2V), GND
- **Wire routing** — A* pathfinding with obstacle avoidance
- **VHDL viewer** — right-click any gate block to read its VHDL template
- **Undo/Redo** — Ctrl+Z / Ctrl+R (also buttons in left panel)
- **Copy/Cut/Paste/Delete** — Ctrl+C / Ctrl+X / Ctrl+V / Ctrl+D
- **Rotation** — 90°/180°/270° on unconnected blocks and pins
- **Per-element styling** — border color, fill color, text color
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

> **Note:** always launch from the `src/` directory.

---

## Keyboard Shortcuts

| Shortcut | Action            |
|----------|-------------------|
| Ctrl+Z   | Undo              |
| Ctrl+R   | Redo              |
| Ctrl+C   | Copy selected     |
| Ctrl+X   | Cut selected      |
| Ctrl+V   | Paste at cursor   |
| Ctrl+D   | Delete selected   |
| Ctrl+P   | Rotate 90° CW     |

---

## Mouse Controls

| Action                        | Effect                                   |
|-------------------------------|------------------------------------------|
| Left-click + drag on block    | Move block                               |
| Left-click on connection dot  | Start drawing a wire                     |
| Release on another dot        | Complete wire connection                 |
| Right-click on block          | Context menu (colors, rotate, VHDL, ...) |
| Right-click on block pin dot  | Pin connection menu                      |
| Right-click on wire           | Delete wire                              |

---

## Project File Format

Designs are stored as JSON arrays. Each element is one of:

- **Block** — `block_type`, position, size, colors, `input_wires`, `output_wires`
- **Pin** — `pin_type`, position, `connection_points`, `wires`
- **Wire** — `start_point`, `end_point`, A* `path`

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
│   ├── main_window.py      # GTK window, event handlers
│   ├── drawing_area.py     # GTK DrawingArea, grid creation
│   ├── blocks.py           # Block model and drawing
│   ├── pins.py             # Pin/bus model and drawing
│   ├── wire.py             # Wire model, A* routing, drawing
│   ├── astar.py            # A* pathfinding on numpy grid
│   ├── menu.py             # GTK menu/toolbar actions
│   ├── context_menu.py     # Right-click context menus
│   └── vhdl/               # VHDL templates (one .vhd per block type)
└── src/experimental/
    └── edif_convertor.py   # JSON → EDIF netlist converter
```

---

## License

MIT — see [LICENSE](LICENSE).
