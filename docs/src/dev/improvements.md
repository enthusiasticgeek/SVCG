# Improvement History

All planned improvements have been implemented. Below is a summary by priority tier.

## P0 — Correctness / Stability

| Issue | Status |
|---|---|
| `dialog.destroy()` crash on cancelled load | Fixed |
| `on_save_as_file()` AttributeError | Fixed |
| Spurious `break` in `update_points` skipped all blocks after first | Fixed |
| Error dialog fires incorrectly when only a pin is selected | Fixed |
| `if "VDD_5V" or ...` always-true — wrong VDD arrow on CLK/GND pins | Fixed |
| VHDL file path relative — breaks when launched outside `src/` | Fixed |
| Wire label showed UUID instead of user net name | Fixed |
| Dead `astar0`/`heuristic0` methods and trailing string literal | Removed |

## P1 — Core UX / Usability

| Feature | Status |
|---|---|
| Wire label editing (right-click → Rename) | Done |
| Multi-select + group move/delete/copy | Done |
| Zoom in/out (Ctrl+scroll, 0.2×–4.0×) | Done |
| Status bar | Done |
| "New project" clears canvas with save prompt | Done |
| Auto-save / dirty flag (`*` in title bar) | Done |

## P2 — HDL Generation

| Feature | Status |
|---|---|
| Whole-schematic VHDL structural export | Done |
| VHDL syntax check via `ghdl -a` | Done |
| Missing VHDL templates (MUX, tristate, adders, DFF pipeline) | Done |
| Verilog structural export (same schematic, different language) | Done |
| HDL language selector (VHDL / Verilog combo box) | Done |
| Custom RTL blocks with VHDL or Verilog body + AI generation | Done |
| Identifier sanitizer (`_sanitize`) — VHDL + Verilog safe | Done |
| Language-aware code storage (`vhdl_body` / `verilog_body` keys) | Done |

## P3 — Architecture / Code Quality

| Item | Status |
|---|---|
| Replace deprecated `Gtk.UIManager` / `Gtk.Action` | Done |
| Split `main_window.py` into focused mixin modules | Done |
| Replace `Block.init_wires()` elif chain with `_WIRE_COUNTS` dict | Done |
| A* grid clipped to bounding box (faster routing) | Done |
| Manhattan fallback when A* returns empty path | Done |

## P4 — New Features

| Feature | Status |
|---|---|
| Component library (save/re-instantiate sub-circuits) | Done |
| GHDL testbench simulation + GTKWave launcher | Done |
| Auto-generated testbench with active-low detection | Done |
| Active-low CLK port polarity fix | Done |
| Yosys netlist import | Done |
| Dark mode | Done |
| SVG / PNG export | Done |
| EDIF export (experimental) — 3 bugs fixed | Done |

## P5 — Computer Arithmetic Library (ECE 645)

12 computer-arithmetic blocks drawn from ECE 645 course material, each with
VHDL (GHDL-verified) and Verilog (iverilog-verified) source files and GHDL
exhaustive simulation tests.

### Batch 1 — Advanced Adders, Multipliers, Restoring Division

| Block | Algorithm | Status |
|---|---|---|
| CLA4 | 4-bit carry-lookahead adder (group G/P, 2-level) | Done |
| CARRY_SEL4 | 4-bit carry-select adder (dual 2-bit halves, muxed on carry) | Done |
| CSA | 1-bit 3:2 carry-save compressor (SO=A⊕B⊕C, CO=majority) | Done |
| ARRAY_MULT4 | 4×4 unsigned array multiplier (structural HA/FA partial-product grid) | Done |
| BOOTH_MULT4 | 4-bit signed Booth radix-2 multiplier (9-bit accumulator) | Done |
| REST_DIV4 | 4-bit unsigned restoring divider (shift-and-subtract with restore) | Done |

### Batch 2 — Parallel-Prefix, Wallace Tree, Modular, Squarer, Non-Restoring Division

| Block | Algorithm | Status |
|---|---|---|
| KS4 | 4-bit Kogge-Stone parallel-prefix adder (2-level, all-to-all) | Done |
| BK4 | 4-bit Brent-Kung parallel-prefix adder (3-level, half the nodes of KS4) | Done |
| NONREST_DIV4 | 4-bit non-restoring divider (signed-digit {±1} quotient, 6-bit P) | Done |
| WALLACE3_4 | 3-operand 4-bit Wallace tree (CSA stage → ripple CPA, 6-bit sum) | Done |
| MOD_ADD4 | 4-bit modular adder: R = (A+B) mod M | Done |
| SQ4 | 4-bit squarer: P = A² (8-bit output) | Done |
