# Keyboard & Mouse Reference

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| Ctrl+Z | Undo |
| Ctrl+R | Redo |
| Ctrl+C | Copy selected (single or group) |
| Ctrl+X | Cut selected (single or group) |
| Ctrl+V | Paste at cursor |
| Ctrl+D | Delete selected (single or group) |
| Ctrl+P | Rotate 90° CW |
| Ctrl+scroll | Zoom in / out |
| Escape | Clear multi-select |

## Mouse Controls

| Action | Effect |
|---|---|
| Left-click + drag on block/pin | Move element |
| Shift+left-click | Add/remove element from multi-select group |
| Left-click on connection dot | Start drawing a wire |
| Release on another dot | Complete wire connection |
| Left-click + drag on wire midpoint | Reroute wire (turns orange while dragging) |
| Right-click on block body | Context menu: colors, rotate, copy, view HDL… |
| Right-click on block or IO pin dot | Pin menu: **Disconnect (remove wires)** — removes all wires attached to that pin |
| Right-click on wire | Wire menu: rename net, delete |
| Ctrl+scroll-wheel | Zoom in / out (0.2× – 4.0×) |

## Block Type Reference

All 56 library block types, their panel section, and port names.

### Digital Gates

| Block | Inputs | Outputs | Notes |
|-------|--------|---------|-------|
| AND | IN1, IN2 | OUT1 | 2-input AND |
| OR | IN1, IN2 | OUT1 | 2-input OR |
| NOT | IN1 | OUT1 | Inverter |
| NAND | IN1, IN2 | OUT1 | 2-input NAND |
| NOR | IN1, IN2 | OUT1 | 2-input NOR |
| XOR | IN1, IN2 | OUT1 | 2-input XOR |
| XNOR | IN1, IN2 | OUT1 | 2-input XNOR |
| BUF | IN1 | OUT1 | Buffer (non-inverting) |
| AND3 | IN1, IN2, IN3 | OUT1 | 3-input AND |
| OR3 | IN1, IN2, IN3 | OUT1 | 3-input OR |
| NAND3 | IN1, IN2, IN3 | OUT1 | 3-input NAND |
| NOR3 | IN1, IN2, IN3 | OUT1 | 3-input NOR |
| XOR3 | IN1, IN2, IN3 | OUT1 | 3-input XOR |
| AND4 | IN1–IN4 | OUT1 | 4-input AND |
| OR4 | IN1–IN4 | OUT1 | 4-input OR |
| NAND4 | IN1–IN4 | OUT1 | 4-input NAND |
| NOR4 | IN1–IN4 | OUT1 | 4-input NOR |

### Flip-Flops

| Block | Inputs | Outputs | Notes |
|-------|--------|---------|-------|
| DFF | D, CLK, PRE, CLR | Q, Q' | D FF, async active-low preset/clear |
| JKFF | J, CLK, K, PRE, CLR | Q, Q' | JK FF |
| SRFF | S, CLK, R, PRE, CLR | Q, Q' | SR FF |
| TFF | T, CLK, PRE, CLR | Q, Q' | Toggle FF |
| DFF_PIPELINE | D, CLK, N_RST | Q | D FF, sync active-low reset |

### Latches

| Block | Inputs | Outputs | Notes |
|-------|--------|---------|-------|
| DLATCH | D, EN | Q, Q' | D latch (transparent when EN=1) |
| SRLATCH | S, R | Q, Q' | NOR-based SR latch |

### Multiplexers / Buffers

| Block | Inputs | Outputs | Notes |
|-------|--------|---------|-------|
| MUX_2X1 | I0, I1, S0, EN | O0 | 2:1 mux with enable |
| MUX_4X1 | I0–I3, S0, S1, EN | O0 | 4:1 mux |
| MUX_8X1 | I0–I7, S0–S2, EN | O0 | 8:1 mux |
| TRISTATEBUF_2 | I0, I1, EN | O0, O1 | 2-channel tri-state buffer |
| TRISTATEBUF_4 | I0–I3, EN | O0–O3 | 4-channel tri-state buffer |
| TRISTATEBUF_8 | I0–I7, EN | O0–O7 | 8-channel tri-state buffer |

### Arithmetic

| Block | Inputs | Outputs | Notes |
|-------|--------|---------|-------|
| HA | A, B | SO, CO | Half adder |
| FA | A, B, SI, CI | SO, CO | Full adder |
| FA_GC | A, B, SI, CI | SO, CO | Full adder Gray Cell (Kogge-Stone) |
| FA_WC | A, B, SI, CI | SO, CO | Full adder White Cell (Kogge-Stone) |
| RCA_4BIT | A0–A3, B0–B3, CIN | S0–S3, COUT | 4-bit ripple-carry adder |
| COMP_4BIT | A0–A3, B0–B3 | ALB, AEB, AGB | 4-bit magnitude comparator |
| CLA4 | A0–A3, B0–B3, CIN | S0–S3, COUT | 4-bit carry-lookahead adder (group generate/propagate) |
| CARRY_SEL4 | A0–A3, B0–B3, CIN | S0–S3, COUT | 4-bit carry-select adder (dual 2-bit halves, muxed) |
| KS4 | A0–A3, B0–B3, CIN | S0–S3, COUT | 4-bit Kogge-Stone parallel-prefix adder (2-level) |
| BK4 | A0–A3, B0–B3, CIN | S0–S3, COUT | 4-bit Brent-Kung parallel-prefix adder (3-level, fewer nodes) |
| CSA | A, B, C | SO, CO | 1-bit 3:2 carry-save compressor |
| WALLACE3_4 | A0–A3, B0–B3, C0–C3 | P0–P5 | 3-operand 4-bit Wallace tree (CSA + ripple CPA, 6-bit sum) |
| MOD_ADD4 | A0–A3, B0–B3, M0–M3 | R0–R3 | 4-bit modular adder: R = (A+B) mod M |
| ARRAY_MULT4 | A0–A3, B0–B3 | P0–P7 | 4×4 unsigned array multiplier (structural HA/FA grid) |
| BOOTH_MULT4 | A0–A3, B0–B3 | P0–P7 | 4-bit signed Booth radix-2 multiplier |
| SQ4 | A0–A3 | P0–P7 | 4-bit squarer: P = A² (8-bit product) |
| REST_DIV4 | N0–N3, D0–D3 | Q0–Q3, R0–R3 | 4-bit unsigned restoring divider |
| NONREST_DIV4 | N0–N3, D0–D3 | Q0–Q3, R0–R3 | 4-bit unsigned non-restoring divider (signed-digit quotient) |

### Decoders / Encoders / Demux

| Block | Inputs | Outputs | Notes |
|-------|--------|---------|-------|
| DEC_2TO4 | A, B, EN | Y0–Y3 | 2-to-4 decoder |
| DEC_3TO8 | A, B, C, EN | Y0–Y7 | 3-to-8 decoder |
| ENC_4TO2 | I0–I3 | Y0, Y1, VALID | 4-to-2 priority encoder (I3 highest) |
| DEMUX_1TO4 | I, S0, S1, EN | O0–O3 | 1-to-4 demultiplexer |
| DEMUX_1TO8 | I, S0–S2, EN | O0–O7 | 1-to-8 demultiplexer |

### Sequential

| Block | Inputs | Outputs | Notes |
|-------|--------|---------|-------|
| SHREG_4BIT | SIN, CLK, RST | Q0–Q3 | 4-bit SIPO shift register |
| CNT_4BIT | CLK, RST, EN | Q0–Q3, TC | 4-bit synchronous up counter |
| CNT_4BIT_UD | CLK, RST, EN, DIR | Q0–Q3, TC | 4-bit up/down counter (DIR=1 up) |

---

## File Menu Actions

| Menu item | Description |
|---|---|
| New SVCG Project | Clear canvas (prompts to save if dirty) |
| Open… | Load a `.json` project file |
| Save | Save to current file |
| Save As… | Save to a new file |
| Generate HDL… | Export structural VHDL or Verilog |
| Generate Testbench + Simulate… | Auto-testbench + GHDL simulation |
| Import Yosys Netlist… | Load a Yosys synthesis JSON |
| Save Selection as Component… | Save multi-select as reusable component |
| Export as SVG… | Render schematic to SVG |
| Export as PNG… | Render schematic to PNG |
| Toggle Dark Mode | Switch dark/light canvas theme (preference saved across sessions) |
| Export EDIF Netlist… (experimental) | Export canvas as EDIF 2.0.0 netlist |
