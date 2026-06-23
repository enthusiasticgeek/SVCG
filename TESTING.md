# SVCG Automated GUI Test Report

**Date:** 2026-06-22 23:02  
**Platform:** Windows 11 / MSYS2 MinGW64  
**Result: 58/58 tests passed**

| # | Test | Result | Notes |
|---|------|--------|-------|
| 1 | Canvas starts empty | PASS |  |
| 2 | Undo/redo stacks empty at start | PASS |  |
| 3 | Create AND block | PASS |  |
| 4 | Create OR block | PASS |  |
| 5 | Create NOT block | PASS |  |
| 6 | Create NAND block | PASS |  |
| 7 | Create NOR block | PASS |  |
| 8 | Create XOR block | PASS |  |
| 9 | Create XNOR block | PASS |  |
| 10 | Create JKFF block | PASS |  |
| 11 | Create SRFF block | PASS |  |
| 12 | Create DFF block | PASS |  |
| 13 | Create TFF block | PASS |  |
| 14 | Create DFF_PIPELINE block | PASS |  |
| 15 | Create MUX_2X1 block | PASS |  |
| 16 | Create MUX_4X1 block | PASS |  |
| 17 | Create MUX_8X1 block | PASS |  |
| 18 | Create FA block | PASS |  |
| 19 | Create HA block | PASS |  |
| 20 | Create FA_GC block | PASS |  |
| 21 | Create FA_WC block | PASS |  |
| 22 | Create input_pin | PASS |  |
| 23 | Create output_pin | PASS |  |
| 24 | Create input_output_pin | PASS |  |
| 25 | Create CLK | PASS |  |
| 26 | Create GND | PASS |  |
| 27 | Create VDD_5V | PASS |  |
| 28 | Wire between AND→OR output/input | PASS |  |
| 29 | Wire with identical start/end (no crash) | PASS |  |
| 30 | Wire starting near canvas origin (regression) | PASS |  |
| 31 | Wire with end to the left of start (reverse direction) | PASS |  |
| 32 | elements_to_json() returns valid JSON list | PASS |  |
| 33 | Save to JSON file | PASS |  |
| 34 | Load from JSON (round-trip count match) | PASS |  |
| 35 | Load malformed JSON (no crash) | PASS |  |
| 36 | Push undo / undo / redo | PASS |  |
| 37 | Undo/redo with empty stacks (no crash) | PASS |  |
| 38 | VHDL output has entity + architecture + end | PASS |  |
| 39 | VHDL export with empty schematic (no crash) | PASS |  |
| 40 | VHDL export with all block types | PASS |  |
| 41 | VHDL sanitizes invalid identifier chars in port names | PASS |  |
| 42 | Testbench has correct entity + architecture | PASS |  |
| 43 | Testbench with no pins (no crash) | PASS |  |
| 44 | Testbench generates clock process for CLK pin | PASS |  |
| 45 | on_draw() light mode completes without crash | PASS |  |
| 46 | on_draw() dark mode completes without crash | PASS |  |
| 47 | _compute_bbox() returns valid rectangle | PASS |  |
| 48 | _compute_bbox() on empty canvas returns fallback rect | PASS |  |
| 49 | SVG export (headless Cairo render) | PASS |  |
| 50 | PNG export (headless Cairo render) | PASS |  |
| 51 | Multi-select + _clear_multi_select() | PASS |  |
| 52 | Copy block (Ctrl+C single) | PASS |  |
| 53 | Rotate block 90° (no wires) | PASS |  |
| 54 | Delete block (Ctrl+D single) | PASS |  |
| 55 | Add 50 blocks, serialize, remove (no crash) | PASS |  |
| 56 | Add 10 vertical wires, serialize, remove (no crash) | PASS |  |
| 57 | update_status_bar() no crash | PASS |  |
| 58 | Dirty flag updates window title with * | PASS |  |

_58/58 passed._
