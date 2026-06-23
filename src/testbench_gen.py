#!/usr/bin/env python3
"""
testbench_gen.py -- VHDL testbench generator + GHDL/GTKWave simulation launcher
"""
import glob
import os
import shutil
import subprocess

from vhdl_export import PIN_DIRECTION, _sanitize


# Names that are conventionally active-low — initialise to '1' (inactive) and
# pulse LOW in stimulus rather than pulsing high.
_ACTIVE_LOW_PATTERNS = {"pre", "clr", "nrst", "n_rst", "rst_n", "reset_n",
                        "set_n", "clr_n", "preset_n", "clear_n"}

def _is_active_low(name):
    n = name.lower()
    return (n in _ACTIVE_LOW_PATTERNS or
            n.startswith("n_") or n.startswith("nr") or
            n.endswith("_n") or n.endswith("_b") or n.endswith("_bar"))


def generate_testbench(entity_name, pins):
    """
    Return a VHDL simulation testbench string for the given entity.

    Parameters
    ----------
    entity_name : str   Top-level entity name (must match the entity file)
    pins        : list  Pin objects from BlocksWindow.pins
    """
    # Build ordered port list
    port_list = []  # [(signal_name, direction)]
    seen = set()
    for pin in pins:
        ptype  = pin.pin_type
        direction = PIN_DIRECTION.get(ptype, "in")
        base   = _sanitize(pin.text)
        is_bus = "bus" in ptype.lower()
        if is_bus:
            for i in range(pin.num_pins):
                pname = f"{base}_{i}" if pin.num_pins > 1 else base
                if pname not in seen:
                    seen.add(pname)
                    port_list.append((pname, direction))
        else:
            if base not in seen:
                seen.add(base)
                port_list.append((base, direction))

    clk_ports      = [p for p, d in port_list if d == "in"  and "clk" in p.lower()]
    input_ports    = [(p, d) for p, d in port_list if d == "in"]
    non_clk_inputs = [(p, d) for p, d in input_ports if p not in clk_ports]

    ind = "    "
    lines = [
        "library IEEE;",
        "use IEEE.STD_LOGIC_1164.ALL;",
        "",
        f"entity {entity_name}_tb is",
        "end entity;",
        "",
        f"architecture sim of {entity_name}_tb is",
        "",
    ]

    # Component declaration
    if port_list:
        lines.append(f"{ind}component {entity_name}")
        lines.append(f"{ind}{ind}port (")
        for idx, (pname, direction) in enumerate(port_list):
            sep = ";" if idx < len(port_list) - 1 else ""
            lines.append(f"{ind}{ind}{ind}{pname} : {direction}  STD_LOGIC{sep}")
        lines.append(f"{ind}{ind});")
        lines.append(f"{ind}end component;")
        lines.append("")

    # Signal declarations — active-low signals init to '1' (inactive)
    for pname, direction in port_list:
        if direction == "in":
            init = " := '1'" if _is_active_low(pname) else " := '0'"
        else:
            init = ""
        lines.append(f"{ind}signal {pname} : STD_LOGIC{init};")
    lines.append("")

    lines += ["begin", ""]

    # UUT instantiation
    lines.append(f"{ind}uut : {entity_name} port map (")
    for idx, (pname, _) in enumerate(port_list):
        sep = "," if idx < len(port_list) - 1 else ""
        lines.append(f"{ind}{ind}{pname} => {pname}{sep}")
    lines += [f"{ind});", ""]

    # Clock processes (100 MHz, 10 ns period)
    # Active-low clocks start inactive ('1') and pulse active ('0').
    for cname in clk_ports:
        if _is_active_low(cname):
            lo, hi = "'1'", "'0'"   # inactive first, then active (falling-edge clock)
        else:
            lo, hi = "'0'", "'1'"   # inactive first, then active (rising-edge clock)
        lines += [
            f"{ind}-- 100 MHz clock (10 ns period)",
            f"{ind}{cname}_proc : process",
            f"{ind}begin",
            f"{ind}{ind}{cname} <= {lo}; wait for 5 ns;",
            f"{ind}{ind}{cname} <= {hi}; wait for 5 ns;",
            f"{ind}end process;",
            "",
        ]

    # Stimulus process
    # - Wait 2 clock periods for power-on stabilisation
    # - Active-low signals pulse LOW (assert) then back HIGH (deassert)
    # - Regular inputs pulse HIGH then LOW
    # - Each phase is 20 ns (2 clock periods) so edges are clock-aligned
    lines += [
        f"{ind}stim_proc : process",
        f"{ind}begin",
        f"{ind}{ind}-- power-on hold",
        f"{ind}{ind}wait for 20 ns;",
    ]
    for pname, _ in non_clk_inputs:
        if _is_active_low(pname):
            lines += [
                f"{ind}{ind}-- assert {pname} (active-low)",
                f"{ind}{ind}{pname} <= '0'; wait for 20 ns;",
                f"{ind}{ind}{pname} <= '1'; wait for 20 ns;",
            ]
        else:
            lines += [
                f"{ind}{ind}{pname} <= '1'; wait for 20 ns;",
                f"{ind}{ind}{pname} <= '0'; wait for 20 ns;",
            ]
    lines += [
        f"{ind}{ind}report \"Simulation complete\" severity note;",
        f"{ind}{ind}wait;",
        f"{ind}end process;",
        "",
        f"end architecture sim;",
        "",
    ]

    return "\n".join(lines)


def run_ghdl_simulation(entity_vhd, tb_vhd, tb_entity_name, workdir, stop_time="2us",
                        custom_vhds=None):
    """
    Run full GHDL simulation: analyse component library + entity + testbench,
    elaborate, run with --vcd.

    Returns
    -------
    success  : bool
    log      : str   Combined stdout/stderr from all steps
    vcd_path : str|None  Path to generated .vcd file, or None on failure
    """
    ghdl = shutil.which("ghdl")
    if not ghdl:
        return False, "ghdl not found on PATH — install GHDL to use simulation.", None

    vcd_path = os.path.join(workdir, f"{tb_entity_name}.vcd")
    log_parts = []

    def _run(label, cmd, fatal=True):
        try:
            r = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            return False, f"[{label}] timed out"
        out = (r.stdout + r.stderr).strip()
        if out:
            log_parts.append(f"[{label}]\n{out}")
        if r.returncode != 0 and fatal:
            return False, "\n".join(log_parts) or f"{label} failed"
        return True, None

    # ── Step 1: compile SVCG component library (src/vhdl/*.vhd) ──────────
    vhdl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vhdl")
    for vhd in sorted(glob.glob(os.path.join(vhdl_dir, "*.vhd"))):
        ok, err = _run(f"analyse {os.path.basename(vhd)}",
                       [ghdl, "-a", "--std=08", vhd], fatal=False)

    # ── Step 1b: compile custom RTL block VHDs ────────────────────────────
    if custom_vhds:
        for ename, vhd_text in custom_vhds:
            vhd_file = os.path.join(workdir, f"custom_{ename}.vhd")
            with open(vhd_file, "w") as fh:
                fh.write(vhd_text)
            ok, err = _run(f"analyse custom_{ename}.vhd",
                           [ghdl, "-a", "--std=08", vhd_file], fatal=True)
            if not ok:
                return False, err, None

    # ── Step 2: analyse top-level entity + testbench ─────────────────────
    for label, path, fatal in [
        ("analyse entity",    entity_vhd, True),
        ("analyse testbench", tb_vhd,     True),
    ]:
        ok, err = _run(label, [ghdl, "-a", "--std=08", path], fatal=fatal)
        if not ok:
            return False, err, None

    # ── Step 3: elaborate + run ───────────────────────────────────────────
    ok, err = _run("elaborate", [ghdl, "-e", "--std=08", tb_entity_name])
    if not ok:
        return False, err, None

    ok, err = _run("run", [ghdl, "-r", "--std=08", tb_entity_name,
                            f"--vcd={vcd_path}", f"--stop-time={stop_time}"])
    if not ok:
        return False, err, None

    vcd = vcd_path if os.path.exists(vcd_path) else None
    return True, "\n".join(log_parts) or "Simulation complete.", vcd


def launch_gtkwave(vcd_path):
    """Launch GTKWave non-blocking with the given VCD file. Returns True if found."""
    gtkwave = shutil.which("gtkwave")
    if gtkwave:
        subprocess.Popen([gtkwave, vcd_path])
        return True
    return False
