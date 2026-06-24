# Directory Structure

```
SVCG/
├── book.toml                    # mdBook configuration
├── docs/
│   └── src/                    # mdBook source (this documentation)
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
│   ├── test_gui.py              # Automated GUI test suite (60 tests)
│   ├── test_gui_adversarial.py  # Student-scenario adversarial tests (49 tests)
│   ├── test_hdl_adversarial.py  # VHDL + Verilog + EDIF generation tests (114 tests)
│   ├── vhdl/                    # VHDL templates (one .vhd per block type)
│   └── components/              # User-saved component sub-circuits (JSON)
└── src/experimental/
    └── edif_convertor.py        # JSON → EDIF netlist converter
```

## Key module relationships

```
BlocksWindow (main_window.py)
  ├── inherits ProjectManagerMixin   (project_manager.py)
  ├── inherits EventHandlerMixin     (event_handler.py)
  ├── inherits VhdlViewerMixin       (vhdl_viewer.py)
  └── inherits ComponentLibraryMixin (component_library.py)

menu.py (MenuBar)
  ├── calls vhdl_export.generate_vhdl / generate_verilog
  ├── calls testbench_gen.generate_testbench / run_ghdl_simulation
  └── calls yosys_importer.import_yosys_netlist

vhdl_export.py
  ├── generate_vhdl()          → structural VHDL entity + architecture
  ├── generate_verilog()       → structural Verilog module
  ├── generate_custom_vhd()    → standalone custom block VHDL
  ├── generate_custom_v()      → standalone custom block Verilog
  ├── check_vhdl_syntax()      → ghdl -a syntax check
  ├── check_verilog_syntax()   → iverilog -t null syntax check
  └── _sanitize()              → identifier sanitizer (VHDL + Verilog safe)
```
