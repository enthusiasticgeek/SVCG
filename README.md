# SVCG — Simple VHDL/Verilog Code Generator

A GTK3-based Python desktop application for visually designing digital circuits and generating **VHDL or Verilog**. Place logic blocks on a schematic canvas, wire them together, and export a complete structural HDL file in your chosen language.

![SVCG — JK flip-flop schematic](SVCG1.png)

*JK flip-flop with J, K, CLK inputs, PRE (preset), CLR (reset), Q and Q̄ outputs. Selected wire shown in orange; drag the mid-point handle to reroute.*

---

## Features

- **Visual schematic editor** — drag-and-drop blocks on a scrollable 5000×5000 canvas with zoom
- **Logic gates** — AND, OR, NOT, NAND, NOR, XOR, XNOR, BUF (44 library blocks total)
  - 3-input: AND3, OR3, NAND3, NOR3, XOR3
  - 4-input: AND4, OR4, NAND4, NOR4
- **Flip-flops** — JK, SR, D (with pipeline variant), T
- **Latches** — D latch (DLATCH), NOR SR latch (SRLATCH)
- **Multiplexers** — 2×1, 4×1, 8×1 MUX
- **Tristate buffers** — 2, 4, 8 channel
- **Arithmetic** — Full Adder (standard, Gray Cell, White Cell), Half Adder, 4-bit ripple-carry adder (RCA_4BIT), 4-bit magnitude comparator (COMP_4BIT)
- **Decoders / Encoders / Demux** — DEC_2TO4, DEC_3TO8, ENC_4TO2 (priority), DEMUX_1TO4, DEMUX_1TO8
- **Sequential** — 4-bit SIPO shift register (SHREG_4BIT), 4-bit up counter (CNT_4BIT), 4-bit up/down counter (CNT_4BIT_UD)
- **I/O primitives** — Input/Output/Bidirectional pins and buses, CLK, VDD (5V/3.3V/1.8V/1.2V), GND
- **Wire routing** — A* pathfinding with Manhattan fallback when path is blocked
- **Wire net names** — right-click a wire to set its net name; names appear on canvas and in generated HDL
- **VHDL export** — produces a complete structural VHDL entity + architecture
- **Verilog export** — produces a complete structural Verilog module (same schematic, different language)
- **HDL language selector** — `HDL: [VHDL ▾]` combo at top of left panel; switches all export and AI generation
- **Custom RTL blocks** — define behavioral blocks inline with VHDL or Verilog; AI can generate the body
- **AI code generation** — "Generate with AI" in the Custom RTL dialog; supports **Ollama (local, free)**, Anthropic, OpenAI, and any OpenAI-compatible endpoint (Cursor, LM Studio, …)
- **VHDL/Verilog viewer** — right-click any block → "View HDL Code" to see the block's VHDL or Verilog template with inline syntax check
- **Syntax checking** — GHDL for VHDL, iverilog for Verilog (optional; shown in the preview dialog and the per-block viewer)
- **Zoom** — Ctrl+scroll-wheel (0.2× – 4.0×)
- **Multi-select** — Shift+click to select multiple blocks/pins/wires; group move, copy, delete
- **Undo/Redo** — Ctrl+Z / Ctrl+R (depth-unlimited JSON snapshots)
- **Copy/Cut/Paste/Delete** — Ctrl+C / Ctrl+X / Ctrl+V / Ctrl+D (works on single or multi-select)
- **Rotation** — 90°/180°/270° on unconnected blocks and pins
- **Per-element styling** — border color, fill color, text color via right-click context menu
- **Dirty flag** — window title shows `*` for unsaved changes; closing prompts Save/Discard/Cancel
- **Status bar** — shows selected element, canvas counts, current filename, and active HDL language
- **Save/Load** — JSON project files via File menu
- **EDIF export** — `File > Export EDIF Netlist...` produces an EDIF 2.0.0 netlist
- **Dark mode** — `File > Toggle Dark Mode`
- **SVG/PNG export** — `File > Export as SVG...` / `Export as PNG...`
- **Component library** — save/re-instantiate sub-circuits with fresh IDs
- **Simulation** — VHDL testbench via GHDL + Verilog testbench via iverilog/vvp; GTKWave waveform viewer
- **Yosys import** — reads `yosys ... write_json` JSON and places mapped cells on the canvas (44 cell types supported)

---

## Prerequisites

### Required — Python + GTK3

#### Windows (MSYS2 MinGW64)  *(recommended)*

1. Install [MSYS2](https://www.msys2.org/).
2. Open the **MSYS2 MinGW64** shell and run:

```bash
pacman -S mingw-w64-x86_64-python-gobject \
          mingw-w64-x86_64-gtk3 \
          mingw-w64-x86_64-python-cairo \
          mingw-w64-x86_64-python-numpy
```

> **Note:** Always launch SVCG from the **MSYS2 MinGW64** terminal.  
> Standard Windows PowerShell/CMD does not have GTK3 Python bindings.

#### Linux (Debian/Ubuntu)

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-numpy
```

#### Linux (Fedora/RHEL)

```bash
sudo dnf install python3-gobject gtk3 python3-cairo python3-numpy
```

---

### Optional — VHDL simulation (GHDL)

Required for `File > Generate Testbench + Simulate...` and the in-preview VHDL syntax check.

#### Windows (MSYS2 MinGW64)

```bash
pacman -S mingw-w64-x86_64-ghdl-llvm
```

#### Linux (Debian/Ubuntu)

```bash
sudo apt install ghdl
```

#### Linux (Fedora/RHEL)

```bash
sudo dnf install ghdl
```

---

### Optional — Verilog syntax check (Icarus Verilog / iverilog)

Used by the `Generate HDL...` preview to syntax-check Verilog output.  
Without it the preview still works — syntax checking is simply skipped.

#### Windows (MSYS2 MinGW64)

```bash
pacman -S mingw-w64-x86_64-iverilog
```

#### Linux (Debian/Ubuntu)

```bash
sudo apt install iverilog
```

#### Linux (Fedora/RHEL)

```bash
sudo dnf install iverilog
```

---

### Optional — AI code generation (Ollama + phi3:mini)

Used by the **"Generate with AI"** button in the Custom RTL Block dialog.  
Ollama runs entirely locally — no API key needed.

#### Windows

```powershell
winget install Ollama.Ollama
```

Then pull the default model (Microsoft Phi-3 Mini, ~2.2 GB):

```bash
ollama pull phi3:mini
```

#### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull phi3:mini
```

> **Other AI backends** (all optional):  
> - **Anthropic** — set `ANTHROPIC_API_KEY` env var; select "Anthropic (cloud)" in the dialog  
> - **OpenAI** — set `OPENAI_API_KEY`; select "OpenAI (cloud)"  
> - **Cursor / any OpenAI-compatible server** — select "Cursor / Custom", enter the endpoint URL

---

## Running

```bash
cd src
python3 main.py
```

---

## HDL Language Selection

The **`HDL:` combo box** at the top of the left panel (above the block palette) switches between **VHDL** and **Verilog**:

| Setting | Generate HDL… saves | Custom block AI generates | Viewer shows |
|---|---|---|---|
| VHDL | `.vhd` — structural VHDL entity | VHDL architecture body | VHDL |
| Verilog | `.v` — structural Verilog module | Verilog module body | Verilog |

The active language is shown in brackets in the window title bar, e.g. `SVCG [VHDL]`.

---

## Keyboard Shortcuts

| Shortcut     | Action                          |
|--------------|---------------------------------|
| Ctrl+Z       | Undo                            |
| Ctrl+R       | Redo                            |
| Ctrl+C       | Copy selected (single or group) |
| Ctrl+X       | Cut selected (single or group)  |
| Ctrl+V       | Paste at cursor                 |
| Ctrl+D       | Delete selected (single or group)|
| Ctrl+P       | Rotate 90° CW                   |
| Ctrl+scroll  | Zoom in / out                   |
| Escape       | Clear multi-select              |

---

## Mouse Controls

| Action                              | Effect                                        |
|-------------------------------------|-----------------------------------------------|
| Left-click + drag on block/pin      | Move element                                  |
| Shift+left-click                    | Add/remove element from multi-select group    |
| Left-click on connection dot        | Start drawing a wire                          |
| Release on another dot              | Complete wire connection                      |
| Left-click + drag on wire midpoint  | Reroute wire (wire turns orange while dragging)|
| Right-click on block body           | Context menu (colors, rotate, copy, HDL…)    |
| Right-click on block pin dot        | Pin connection menu                           |
| Right-click on wire                 | Wire menu (rename net, delete)                |
| Ctrl+scroll-wheel                   | Zoom in / out (0.2× – 4.0×)                  |

---

## Workflow: Schematic to VHDL or Verilog

1. **Select HDL language** — choose VHDL or Verilog from the `HDL:` combo at the top of the left panel.
2. **Add IO pins** from the left panel (Input Pin, Output Pin, etc.) — these become module/entity ports.
3. **Add blocks** (gates, flip-flops, muxes, etc.) from the left panel.
4. **Draw wires** by clicking a connection dot and releasing on another dot.
5. **Name wires** with right-click → "Rename" — the net name appears on canvas and maps to a `signal` (VHDL) or `wire` (Verilog).
6. **Generate HDL** via `File > Generate HDL (VHDL/Verilog)...`:
   - Enter the top-level entity/module name.
   - Choose a save path (`.vhd` for VHDL, `.v` for Verilog).
   - A preview of the generated HDL opens with an optional syntax check result.

### VHDL output contains:
- `entity` with ports derived from IO pins
- `architecture Structural` with `component` declarations, `signal`s, and structural `port map`s

### Verilog output contains:
- `module` with `input wire` / `output wire` / `inout wire` ports
- `wire` declarations for internal nets
- Named module instantiations with `.port(signal)` connections

---

## Custom RTL Blocks

Add behavioral or RTL blocks that go beyond the standard gate library:

1. Open **Custom RTL** expander in the left panel → **Add Custom RTL Block**.
2. Enter entity/module name, input ports, output ports.
3. Optionally describe the behavior and click **"Generate with AI"** — the AI writes the HDL body.
4. Edit the generated code as needed.
5. Place the block on the canvas and wire it like any other block.

The entity/module declaration is auto-generated; you write only the architecture body (VHDL) or module body (Verilog).

### AI Backend selection

The Custom RTL dialog has a **AI Backend** dropdown:

| Backend | Model picker | Needs |
|---|---|---|
| Auto-detect | Ollama models (live) | nothing — falls back automatically |
| Ollama (local, free) | all pulled Ollama models | `ollama serve` running |
| Anthropic (cloud) | haiku / sonnet | `ANTHROPIC_API_KEY` env var |
| OpenAI (cloud) | gpt-4o-mini / gpt-4o / … | `OPENAI_API_KEY` env var |
| Cursor / Custom (OpenAI-compatible) | configurable + endpoint URL field | `CURSOR_API_KEY` or `OPENAI_API_KEY` |

---

## Simulation (GHDL + GTKWave)

`File > Generate Testbench + Simulate...` does the following in one step:

1. Generates a structural VHDL entity from the schematic.
2. Generates a simulation testbench (see details below).
3. If [GHDL](https://github.com/ghdl/ghdl) is on `PATH`, runs `ghdl -a / -e / -r --vcd` and shows the log inline.
4. A **Launch GTKWave** button appears if simulation produced a `.vcd` waveform file.

> Simulation currently uses VHDL regardless of the HDL language selector (GHDL is a VHDL simulator).

### Auto-generated testbench

The testbench (`entity_name_tb`) is fully auto-generated from the schematic's IO pins:

**Clock detection** — any input port whose name contains `clk` (case-insensitive, e.g. `CLK`, `sys_clk`, `Clk_in`) gets a dedicated **100 MHz clock process** (5 ns low / 5 ns high, repeating forever).

**Active-low signal detection** — ports matching any of the following patterns are initialised to `'1'` (inactive) and pulsed `'0'` (asserted) in the stimulus rather than pulsed high:

| Pattern | Examples |
|---------|---------|
| Exact names | `pre`, `clr`, `nrst`, `n_rst`, `rst_n`, `reset_n`, `set_n`, `clr_n`, `preset_n`, `clear_n` |
| Starts with `n_` | `n_reset`, `n_enable` |
| Starts with `nr` | `nrst`, `nreset` |
| Ends with `_n` | `rst_n`, `oe_n` |
| Ends with `_b` | `cs_b` |
| Ends with `_bar` | `set_bar` |

**Stimulus process** — for every non-clock input port:
- Active-low: assert `'0'` for 20 ns, then deassert `'1'` for 20 ns.
- Regular: drive `'1'` for 20 ns, then `'0'` for 20 ns.
- Ends with `report "Simulation complete" severity note; wait;`.

**Output / inout ports** — appear in the component declaration and UUT `port map` but are never driven by the stimulus.

**Stop time** — simulation runs for 2 µs by default.

---

## Yosys Netlist Import

`File > Import Yosys Netlist...` imports a synthesis JSON produced by [Yosys](https://github.com/YosysHQ/yosys):

```bash
yosys -p "synth -flatten; write_json out.json" design.v
```

Supported cell types: `$_AND_`, `$_OR_`, `$_NOT_`, `$_NAND_`, `$_NOR_`, `$_XOR_`, `$_XNOR_`, `$_MUX_`, `$_DFF_P_/N_`, `$_HA_`, `$_FA_` and their Yosys-internal equivalents.

---

## Component Library

Save any Shift+click selection as a reusable component:

1. Shift+click the blocks/pins you want to save.
2. `File > Save Selection as Component...` — enter a name.
3. The component appears in the **Components** expander in the left panel.
4. Click its button to drop a fresh copy (new UUIDs, shifted position) onto the canvas.

Components are stored as JSON files in `src/components/`.

---

## Project File Format

Designs are stored as JSON arrays. Each element is one of:

- **Block** — `block_type`, position, size, colors, rotation, `input_wires`, `output_wires`, `custom_data` (for Custom RTL blocks)
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
│   ├── main.py                  # Entry point
│   ├── main_window.py           # GTK window + HDL language selector
│   ├── project_manager.py       # Mixin: save/load/undo/redo
│   ├── event_handler.py         # Mixin: mouse/keyboard events, wire routing
│   ├── vhdl_viewer.py           # Mixin: per-block HDL template dialog
│   ├── component_library.py     # Mixin: save/load sub-circuit components
│   ├── drawing_area.py          # GTK DrawingArea, zoom, grid
│   ├── blocks.py                # Block model and drawing
│   ├── pins.py                  # Pin/bus model and drawing
│   ├── wire.py                  # Wire model, A* routing, Manhattan fallback
│   ├── astar.py                 # A* pathfinding on numpy grid
│   ├── menu.py                  # GTK menu/toolbar actions
│   ├── context_menu.py          # Right-click context menus
│   ├── vhdl_export.py           # VHDL + Verilog structural generator
│   ├── custom_block_dialog.py   # Custom RTL block dialog + AI generation
│   ├── testbench_gen.py         # VHDL testbench generator + GHDL/GTKWave launcher
│   ├── yosys_importer.py        # Yosys JSON netlist importer
│   ├── vhdl/                    # VHDL templates (one .vhd per block type)
│   └── components/              # User-saved component sub-circuits (JSON)
├── src/experimental/
│   └── edif_convertor.py        # JSON -> EDIF netlist converter
│   ├── test_gui.py              # Automated GUI test suite (60 tests)
│   ├── test_gui_adversarial.py  # Student-scenario adversarial tests (49 tests)
│   └── test_hdl_adversarial.py  # VHDL + Verilog + EDIF generation tests (114 tests)
```

---

## Running the Test Suites

```bash
cd src
python test_gui.py                 # 60 general GUI tests  → TESTING.md
python test_gui_adversarial.py     # 49 student-scenario tests → TESTING_adversarial.md
python test_hdl_adversarial.py     # 114 VHDL + Verilog + EDIF tests → TESTING_hdl_adversarial.md
```

---

## License

MIT — see [LICENSE](LICENSE).
