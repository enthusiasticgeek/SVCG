# Simulation (GHDL / iverilog + GTKWave)

`File > Generate Testbench + Simulate...` does the following in one step:

The active HDL language (set by the `HDL:` combo at the top of the left panel) determines which simulator is used.

## VHDL path (GHDL)

1. Generates a structural VHDL entity from the schematic.
2. Auto-generates a VHDL simulation testbench.
3. If [GHDL](https://github.com/ghdl/ghdl) is on `PATH`, runs `ghdl -a / -e / -r --vcd` and shows the log inline.
4. A **Launch GTKWave** button appears if simulation produced a `.vcd` waveform file.

## Verilog path (iverilog + vvp)

1. Generates a structural Verilog module from the schematic.
2. Auto-generates a Verilog simulation testbench (`\`timescale 1ns/1ps`, named port map, `$dumpfile`/`$dumpvars`, `$finish`).
3. If [iverilog](https://github.com/steveicarus/iverilog) is on `PATH`, compiles all library primitives + top module + testbench in a single `iverilog` call, then runs `vvp` to produce a `.vcd` file.
4. A **Launch GTKWave** button appears if simulation produced a `.vcd` file.

## Auto-generated testbench

The testbench is fully auto-generated from the schematic's IO pins.  The VHDL testbench entity is named `entity_name_tb`; the Verilog testbench module is named `module_name_tb`.

### Clock detection

Any input port whose name contains `clk` (case-insensitive — e.g. `CLK`, `sys_clk`, `Clk_in`) gets a dedicated **100 MHz clock process** (5 ns inactive / 5 ns active, repeating forever).

Active-low clock ports (e.g. `clk_n`) start `'1'` (inactive) and pulse `'0'` (active edge) — the correct polarity for a falling-edge clock.

### Active-low signal detection

Ports matching any of the following patterns are initialised to `'1'` (inactive) and pulsed `'0'` (asserted) in the stimulus process instead of pulsed high:

| Pattern | Examples |
|---|---|
| Exact names | `pre`, `clr`, `nrst`, `n_rst`, `rst_n`, `reset_n`, `set_n`, `clr_n`, `preset_n`, `clear_n` |
| Starts with `n_` | `n_reset`, `n_enable` |
| Starts with `nr` | `nrst`, `nreset` |
| Ends with `_n` | `rst_n`, `oe_n` |
| Ends with `_b` | `cs_b` |
| Ends with `_bar` | `set_bar` |

### Stimulus process

For every non-clock input port:

- **Active-low**: asserts `'0'` for 20 ns, then deasserts `'1'` for 20 ns.
- **Regular**: drives `'1'` for 20 ns, then `'0'` for 20 ns.
- Ends with `report "Simulation complete" severity note; wait;`.

### Output / inout ports

Appear in the component declaration and UUT `port map` but are never driven by the stimulus process.

### Stop time

Simulation runs for **2 µs** by default.

## Example VHDL testbench snippet (half-adder)

```vhdl
-- VHDL testbench (GHDL path)
entity half_adder_tb is
end entity;

architecture sim of half_adder_tb is
    component half_adder
        port (
            A   : in  STD_LOGIC;
            B   : in  STD_LOGIC;
            SUM : out STD_LOGIC;
            CO  : out STD_LOGIC
        );
    end component;

    signal A   : STD_LOGIC := '0';
    signal B   : STD_LOGIC := '0';
    signal SUM : STD_LOGIC;
    signal CO  : STD_LOGIC;
begin
    uut : half_adder port map (A => A, B => B, SUM => SUM, CO => CO);

    stim_proc : process
    begin
        wait for 20 ns;
        A <= '1'; wait for 20 ns;
        A <= '0'; wait for 20 ns;
        B <= '1'; wait for 20 ns;
        B <= '0'; wait for 20 ns;
        report "Simulation complete" severity note;
        wait;
    end process;
end architecture sim;
```

## Example Verilog testbench snippet (half-adder)

```verilog
// Verilog testbench (iverilog + vvp path)
`timescale 1ns/1ps

module half_adder_tb;
    reg  A = 1'b0;
    reg  B = 1'b0;
    wire SUM;
    wire CO;

    half_adder uut (.A(A), .B(B), .SUM(SUM), .CO(CO));

    initial begin
        $dumpfile("half_adder_tb.vcd");
        $dumpvars(0, half_adder_tb);

        // Stimulus
        #20 A = 1'b1;
        #20 A = 1'b0;
        #20 B = 1'b1;
        #20 B = 1'b0;
        #20;
        $finish;
    end
endmodule
```

## Testbench stimulus coverage

> **Important limitation:** The auto-generated testbench drives each input port **sequentially** — one port high for 20 ns, then low for 20 ns, then the next port, and so on.  It never asserts two inputs simultaneously.
>
> For purely combinational circuits this means the all-inputs-high case is **never exercised**.  For a half-adder, the `A=1, B=1 → CO=1` case is not present in the auto-generated stimulus, even though the UUT logic is correct.

### What this means in practice

| Scenario | Auto-TB covers it? |
|---|---|
| Single-input toggle (NOT gate) | Yes |
| Two inputs driven one at a time | Yes |
| Two inputs high simultaneously (carry-out) | **No** |
| Clock-edge capture with simultaneous data | **No** |

### Exhaustive coverage via G26 / G27 simulation tests

The automated test suite (`test_hdl_adversarial.py`) groups **G26** (T157–T164) and **G27** (T165–T172) run exhaustive testbenches via GHDL and iverilog respectively, covering every combination including the CO=1 case for the half-adder.  These tests verify:

- **Primitives** (AND, OR, NOT, XOR) — all truth-table entries via VCD inspection
- **Half-adder** — all 4 input combinations including `A=1, B=1 → CO=1`
- **D flip-flop** — async CLR/PRE and rising-edge capture
- **Full-adder** — 5 carry-propagation cases
- **Full SVCG pipeline** — structural netlist generated from the GUI canvas, compiled by GHDL/iverilog, VCD verified exhaustively (T164, T172)

Run the suite headlessly:

```bash
cd src
python test_hdl_adversarial.py
```

SKIP results for G26/G27 tests indicate the corresponding simulator is not on `PATH` — install GHDL or iverilog (see table below) and rerun.

## Installing simulators

| Simulator | Install (MSYS2 MinGW64) | Install (Ubuntu/Debian) |
|---|---|---|
| GHDL | `pacman -S mingw-w64-x86_64-ghdl` | `apt install ghdl` |
| iverilog | `pacman -S mingw-w64-x86_64-iverilog` | `apt install iverilog` |
| GTKWave | `pacman -S mingw-w64-x86_64-gtkwave` | `apt install gtkwave` |
