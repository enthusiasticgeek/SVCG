# Workflow: Schematic to VHDL or Verilog

## Step-by-step

1. **Select HDL language** — choose VHDL or Verilog from the `HDL:` combo at the top of the left panel.
2. **Add IO pins** from the left panel (Input Pin, Output Pin, etc.) — these become module/entity ports.
3. **Add blocks** (gates, flip-flops, muxes, etc.) from the left panel.
4. **Draw wires** by clicking a connection dot and releasing on another dot.
5. **Name wires** with right-click → "Rename" — the net name appears on canvas and maps to a `signal` (VHDL) or `wire` (Verilog).
6. **Generate HDL** via `File > Generate HDL (VHDL/Verilog)...`:
   - Enter the top-level entity/module name.
   - Choose a save path (`.vhd` for VHDL, `.v` for Verilog).
   - A preview of the generated HDL opens with an optional syntax check result.

## VHDL output

```vhdl
entity my_circuit is
    port (
        A   : in  STD_LOGIC;
        B   : in  STD_LOGIC;
        SUM : out STD_LOGIC
    );
end entity;

architecture Structural of my_circuit is
    component XOR_GATE port ( A : in STD_LOGIC; B : in STD_LOGIC; Y : out STD_LOGIC ); end component;
    signal net_sum : STD_LOGIC;
begin
    U0 : XOR_GATE port map ( A => A, B => B, Y => net_sum );
    SUM <= net_sum;
end architecture Structural;
```

The VHDL file contains:
- `entity` with ports derived from IO pins
- `architecture Structural` with `component` declarations, `signal`s, and structural `port map`s

## Verilog output

```verilog
module my_circuit (
    input  wire A,
    input  wire B,
    output wire SUM
);
    wire net_sum;
    XOR_GATE U0 ( .A(A), .B(B), .Y(net_sum) );
    assign SUM = net_sum;
endmodule
```

The Verilog file contains:
- `module` with `input wire` / `output wire` / `inout wire` ports
- `wire` declarations for internal nets
- Named module instantiations with `.port(signal)` connections

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
| Right-click on block body | Context menu (colors, rotate, copy, HDL…) |
| Right-click on wire | Wire menu (rename net, delete) |
| Ctrl+scroll-wheel | Zoom in / out (0.2× – 4.0×) |
