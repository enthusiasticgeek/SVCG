# Test Suites

All test suites live in `src/` and are run from that directory.

```bash
cd src
python test_gui.py                 # 65 general GUI tests
python test_gui_adversarial.py     # 61 student-scenario adversarial tests
python test_hdl_adversarial.py     # 172 VHDL + Verilog + EDIF + simulation tests
bash test_arith2_spot.sh           # GHDL exhaustive tests for 6 ECE 645 batch-2 blocks
```

The Python suites write Markdown reports to the project root. The GHDL spot-test
script requires GHDL on `PATH` and must be run from an MSYS2 MinGW64 shell (or any
bash with GHDL available); it exits non-zero if any block fails.

## test_gui.py — General GUI (65 tests)

Covers core schematic operations: block placement, pin placement, wire connection, undo/redo, save/load round-trip, multi-select group operations, zoom, component library, dark mode, SVG/PNG export, Verilog structural export, and bus port syntax for custom blocks.

Report: `TESTING.md`

## test_gui_adversarial.py — Student scenarios (61 tests)

Simulates the kinds of mistakes and edge cases that students encounter: placing blocks off-grid, double-connecting ports, loading corrupted JSON, rotating connected blocks, copy-paste of multi-block selections.

Report: `TESTING_adversarial.md`

## test_hdl_adversarial.py — HDL generation (172 tests in 27 groups)

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
| G22 | T115–T130 | New block types (MUX, FA, HA, counters…) |
| G23 | T131–T140 | Verilog template library files |
| G24 | T141–T148 | Verilog testbench generator |
| G25 | T149–T156 | Yosys importer new block types |
| G26 | T157–T164 | VHDL waveform simulation (GHDL) |
| G27 | T165–T172 | Verilog waveform simulation (iverilog+vvp) |

Report: `TESTING_hdl_adversarial.md`

### G26 / G27 — Simulation correctness

G26 and G27 verify that the HDL primitives and SVCG-generated structural netlists produce **correct waveform output** when simulated:

- AND, OR, NOT, XOR — full truth table via VCD inspection
- Half-adder — all 4 input combinations including `A=1, B=1 → CO=1`
- D flip-flop — async CLR/PRE and rising-edge data capture
- Full-adder — 5 carry-propagation cases
- Full pipeline (T164, T172) — structural netlist generated from the GUI canvas, compiled by GHDL/iverilog, VCD verified exhaustively

These tests require GHDL and iverilog to be on `PATH`; otherwise they are automatically marked SKIP.  See [Simulation](../user-manual/simulation.md) for installation instructions.

## test_arith2_spot.sh — ECE 645 computer arithmetic (6 blocks)

Exhaustively simulates the batch-2 computer-arithmetic blocks using GHDL:

| Block | Test coverage |
|---|---|
| KS4 | All 512 combinations of A[0..15], B[0..15], CIN∈{0,1} |
| BK4 | Same as KS4 |
| NONREST_DIV4 | All 240 pairs N∈[0..15], D∈[1..15]; checks Q=N/D and R=N mod D |
| WALLACE3_4 | All 4096 triples A,B,C∈[0..15]; checks P=A+B+C |
| MOD_ADD4 | All pairs for M=13 and M=7; checks R=(A+B) mod M |
| SQ4 | All A∈[0..15]; checks P=A² |

Requires GHDL on `PATH`. Run from an MSYS2 MinGW64 shell or any bash with GHDL available.
