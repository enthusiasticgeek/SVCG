# Yosys Netlist Import

`File > Import Yosys Netlist...` imports a synthesis JSON produced by [Yosys](https://github.com/YosysHQ/yosys) and places the mapped cells on the canvas.

## Producing the JSON

```bash
yosys -p "synth -flatten; write_json out.json" design.v
```

## Supported cell types

| Yosys cell | SVCG block |
|---|---|
| `$_AND_` | AND gate |
| `$_OR_` | OR gate |
| `$_NOT_` | NOT gate |
| `$_NAND_` | NAND gate |
| `$_NOR_` | NOR gate |
| `$_XOR_` | XOR gate |
| `$_XNOR_` | XNOR gate |
| `$_MUX_` | 2×1 MUX |
| `$_DFF_P_` / `$_DFF_N_` | D flip-flop |
| `$_HA_` | Half adder |
| `$_FA_` | Full adder |

Unsupported cell types are listed in the import summary dialog.

## Layout

Cells are auto-placed in columns by topological depth — cells driven solely by primary inputs appear on the left, and cells driving primary outputs appear on the right. IO pins are created for each module port.
