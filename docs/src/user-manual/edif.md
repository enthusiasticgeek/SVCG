# EDIF Export

SVCG can export your schematic as an EDIF 2.0.0 netlist for import into downstream EDA tools such as Quartus Prime, Vivado, or Synopsys Design Compiler.

Export is available two ways:

- **GUI**: `File > Export EDIF Netlist…` — saves directly from the current canvas.
- **CLI**: run the converter standalone (useful for scripting or CI):

```bash
cd src/experimental
python3 edif_convertor.py ../my_design.json my_design.edf
```

## What it produces

The EDIF file contains:

- A cell entry for each block (logic gate, flip-flop, etc.) with `INPUT` / `OUTPUT` ports derived from block port names.
- A cell entry for each IO pin with an `INOUT` port.
- A net entry for each wire, with `portRef` connections to the correct port of each block or pin.

## Worked example — importing into Quartus Prime

1. **Export from SVCG**: `File > Export EDIF Netlist…` → save as `my_design.edf`.
2. **Create a Quartus project** targeting your FPGA family (e.g. Cyclone IV).
3. **Add the EDIF file**: Project → Add/Remove Files → add `my_design.edf`.
4. **Set the top-level entity**: Assignments → Settings → General → Top-level entity → enter the cell name from the EDIF (matches the JSON filename base by default).
5. **Compile**: Processing → Start Compilation.  Quartus reads the EDIF netlist, maps cells to FPGA primitives, and runs place-and-route.
6. **Program**: use the Programmer to download the resulting `.sof` / `.pof` to the device.

> **Tip:** Standard SVCG gates (AND, OR, NOT, XOR, …) map cleanly to Quartus primitives.  If Quartus reports unknown cell types, check that the EDIF cell names match those in the Quartus primitive library or add a Technology Mapping step.

## Worked example — importing into Vivado

1. Export `my_design.edf` from SVCG as above.
2. In Vivado, create a new RTL project and select **Add or create design sources**.
3. Add `my_design.edf`; set file type to **EDIF**.
4. Run **Synthesis** (Vivado reads EDIF natively during the synthesis step).
5. Continue with implementation and bitstream generation as normal.

## Known limitations

- Bus pins (multi-bit) generate numbered ports (`D_0`, `D_1`, …) which may not match the naming convention expected by downstream tools.
- The EDIF structure places all declarations inside a single cell interface section rather than separate library / design sections — sufficient for many import flows but not strictly valid EDIF 2.0.0 hierarchy.
- Simulation is not available from the EDIF path; use `File > Generate Testbench + Simulate…` for simulation.
