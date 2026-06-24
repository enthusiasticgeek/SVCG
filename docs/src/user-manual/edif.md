# EDIF Export (Experimental)

SVCG can convert a saved project JSON to an EDIF 2.0.0 netlist using the standalone converter in `src/experimental/`.

## Usage

```bash
cd src/experimental
python3 edif_convertor.py ../my_design.json my_design.edf
```

## What it produces

The EDIF file contains:

- A cell entry for each block (logic gate, flip-flop, etc.) with `INPUT` / `OUTPUT` ports derived from block port names.
- A cell entry for each IO pin with an `INOUT` port.
- A net entry for each wire, with `portRef` connections to the correct port of each block or pin.

## Known limitations

- Bus pins (multi-bit) generate numbered ports (`D_0`, `D_1`, …) which may not match the naming convention expected by downstream tools.
- The EDIF structure places all declarations inside a single cell interface section rather than separate library / design sections — sufficient for many import flows but not strictly valid EDIF 2.0.0 hierarchy.
- Simulation (GHDL) is not available from the EDIF path; use `File > Generate Testbench + Simulate...` for simulation.
