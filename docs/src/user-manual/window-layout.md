# Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│  File  Edit  [toolbar ▸]                                    │  ← Menu bar
├──────────────┬──────────────────────────────────────────────┤
│ HDL: [VHDL▾] │                                              │
│ Cursor:(x,y) │                                              │
│              │                                              │
│ ▸ Clk/Vdd/Gnd│           CANVAS  (5000 × 5000 px)          │
│ ▸ IO Pins    │         scroll with scrollbars               │
│ ▸ Digital    │         zoom with Ctrl+scroll-wheel          │
│   Gates      │                                              │
│ ▸ Flip-Flops │                                              │
│ ▸ Muxes/Buf  │                                              │
│ ▸ Arithmetic │                                              │
│ ▸ Custom RTL │                                              │
│ ▸ Components │                                              │
│ ▸ Edit Ops   │                                              │
│              │                                              │
├──────────────┴──────────────────────────────────────────────┤
│  Status bar — selected element · counts · filename · lang   │
└─────────────────────────────────────────────────────────────┘
```

**Left panel** — click any expander label to expand/collapse that section. The `HDL:` combo at the top switches between VHDL and Verilog for all export and AI generation.

**Canvas** — all design work happens here. 5000×5000 pixels, scrollable, zoomable (0.2×–4.0×).

**Status bar** — shows the selected element, block/pin/wire counts, current filename, and active HDL language. The title bar shows `*` when there are unsaved changes.

## HDL Language Selector

The **`HDL:`** combo box switches between **VHDL** and **Verilog**:

| Setting | Generate HDL… saves | AI generates | Viewer shows |
|---|---|---|---|
| VHDL | `.vhd` — structural VHDL entity | VHDL architecture body | VHDL |
| Verilog | `.v` — structural Verilog module | Verilog module body | Verilog |

The active language is also shown in the window title bar, e.g. `SVCG [VHDL]`.
