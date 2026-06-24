# Test Suites

All test suites live in `src/` and are run from that directory.

```bash
cd src
python test_gui.py                 # 60 general GUI tests
python test_gui_adversarial.py     # 49 student-scenario adversarial tests
python test_hdl_adversarial.py     # 114 VHDL + Verilog + EDIF tests
```

Each suite writes a Markdown report to the project root.

## test_gui.py — General GUI (60 tests)

Covers core schematic operations: block placement, pin placement, wire connection, undo/redo, save/load round-trip, multi-select group operations, zoom, component library, dark mode, SVG/PNG export.

Report: `TESTING.md`

## test_gui_adversarial.py — Student scenarios (49 tests)

Simulates the kinds of mistakes and edge cases that students encounter: placing blocks off-grid, double-connecting ports, loading corrupted JSON, rotating connected blocks, copy-paste of multi-block selections.

Report: `TESTING_adversarial.md`

## test_hdl_adversarial.py — HDL generation (114 tests in 21 groups)

| Group | Tests | Topic |
|---|---|---|
| G1 | T01–T10 | VHDL structural export |
| G2 | T11–T20 | Verilog structural export |
| G3 | T21–T26 | Custom block VHDL |
| G4 | T27–T32 | Custom block Verilog |
| G5 | T33–T36 | Language switching |
| G6 | T37–T40 | AI prompt construction |
| G7 | T41–T44 | Edge cases (both languages) |
| G8 | T45–T48 | Syntax validation (tool-dependent) |
| G9 | T49–T52 | Round-trip / cross-language |
| G10 | T53–T58 | Wire/net name adversarial |
| G11 | T59–T63 | Multi-instance uniqueness |
| G12 | T64–T67 | Port-count integrity |
| G13 | T68–T72 | Custom block adversarial ports |
| G14 | T73–T74 | Extended syntax validation |
| G15 | T75–T80 | Testbench generation |
| G16 | T81–T86 | Testbench edge cases |
| G17 | T87–T92 | HDL structural deep-checks |
| G18 | T93–T96 | Custom block structural correctness |
| G19 | T97–T100 | Language-aware code storage |
| G20 | T101–T106 | Active-low CLK + misc testbench |
| G21 | T107–T114 | EDIF export |

Report: `TESTING_hdl_adversarial.md`
