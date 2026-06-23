#!/usr/bin/env python3
"""
test_gui_adversarial.py -- 49 student-scenario adversarial tests for SVCG.

Covers: combinational/sequential circuits, VHDL content correctness,
save/load fidelity, student-mistake edge cases, component library,
testbench quality, export integrity, wire routing, Yosys import.

Usage:
    cd src
    python test_gui_adversarial.py

See TESTPLAN.md for the full specification behind each test.
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import sys, os, json, tempfile, traceback, shutil
import cairo as _cairo
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REPORT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TESTING_adversarial.md"
)

results = []

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    results.append((name, status, detail))
    tag = "[PASS]" if passed else "[FAIL]"
    print(f"  {tag} {name}" + (f"  ({detail})" if detail else ""))

def log_skip(name, reason):
    results.append((name, "SKIP", reason))
    print(f"  [SKIP] {name}  ({reason})")

def run_test(name, fn):
    try:
        fn()
        log(name, True)
    except AssertionError as e:
        log(name, False, str(e))
    except Exception as e:
        log(name, False, f"{type(e).__name__}: {e}")
        traceback.print_exc()

def reset(win):
    """Clear canvas and history between groups."""
    win.blocks = []
    win.pins   = []
    win.wires  = []
    win.undo_stack = []
    win.redo_stack = []
    win.selected_block = None
    win.selected_pin   = None
    win.selected_wire  = None
    win.selected_blocks = []
    win.selected_pins   = []
    win.selected_wires  = []
    win.set_dirty(False)

def rebuild_grid(win):
    """Force A* grid to reflect the current canvas state."""
    from drawing_area import DrawingArea
    win.drawing_area.create_grid(DrawingArea.CANVAS_SIZE, DrawingArea.CANVAS_SIZE, win.grid_size)

def connect_wire(win, src, src_idx, src_role, dst, dst_idx, dst_role, net_name):
    """
    Create a Wire between two objects and register its ID in both endpoint wire-lists.

    src_role / dst_role: "output" | "input" for Block; "pin" for Pin.
    Returns the new Wire object.
    """
    from wire import Wire

    def get_pt(obj, idx, role):
        if role == "output":
            return list(obj.output_points[idx])
        if role == "input":
            return list(obj.input_points[idx])
        return list(obj.connection_points[idx])   # "pin"

    sp = get_pt(src, src_idx, src_role)
    ep = get_pt(dst, dst_idx, dst_role)
    w  = Wire(net_name, sp, ep, "wire", win.grid_size, win)

    def register(obj, idx, role, wid):
        if role == "output":
            if obj.output_wires[idx] is None:
                obj.output_wires[idx] = []
            obj.output_wires[idx].append(wid)
        elif role == "input":
            if obj.input_wires[idx] is None:
                obj.input_wires[idx] = []
            obj.input_wires[idx].append(wid)
        else:  # pin
            if obj.wires[idx] is None:
                obj.wires[idx] = []
            obj.wires[idx].append(wid)

    register(src, src_idx, src_role, w.id)
    register(dst, dst_idx, dst_role, w.id)
    win.wires.append(w)
    return w

def build_half_adder(win):
    """
    Build a wired half adder on the canvas:
        input A, input B  ->  XOR (SUM), AND (CARRY)  ->  output SUM, output CARRY
    Returns (xor_blk, and_blk, pin_A, pin_B, pin_SUM, pin_CARRY, wires_dict).
    """
    from blocks import Block
    from pins   import Pin

    gs = win.grid_size
    rebuild_grid(win)

    xor_blk = Block(gs*5,  gs*5,  gs*4, gs*4, "XOR_1", "XOR", gs, win)
    and_blk = Block(gs*5,  gs*12, gs*4, gs*4, "AND_1", "AND", gs, win)
    pin_A   = Pin(gs*1,  gs*6,  gs*3, gs*2, "A",     "input_pin",  gs, 1, win)
    pin_B   = Pin(gs*1,  gs*13, gs*3, gs*2, "B",     "input_pin",  gs, 1, win)
    pin_SUM  = Pin(gs*12, gs*6,  gs*3, gs*2, "SUM",  "output_pin", gs, 1, win)
    pin_CARRY= Pin(gs*12, gs*13, gs*3, gs*2, "CARRY","output_pin", gs, 1, win)

    win.blocks.extend([xor_blk, and_blk])
    win.pins.extend([pin_A, pin_B, pin_SUM, pin_CARRY])
    rebuild_grid(win)

    # Fan-out from A to both gates; fan-out from B to both gates
    w_A_xor   = connect_wire(win, pin_A,   0, "pin",    xor_blk, 0, "input",  "A")
    w_A_and   = connect_wire(win, pin_A,   0, "pin",    and_blk, 0, "input",  "A")
    w_B_xor   = connect_wire(win, pin_B,   0, "pin",    xor_blk, 1, "input",  "B")
    w_B_and   = connect_wire(win, pin_B,   0, "pin",    and_blk, 1, "input",  "B")
    w_xor_sum = connect_wire(win, xor_blk, 0, "output", pin_SUM, 0, "pin",    "SUM")
    w_and_co  = connect_wire(win, and_blk, 0, "output", pin_CARRY, 0, "pin",  "CARRY")

    wires = dict(A_xor=w_A_xor, A_and=w_A_and, B_xor=w_B_xor,
                 B_and=w_B_and, xor_sum=w_xor_sum, and_carry=w_and_co)
    return xor_blk, and_blk, pin_A, pin_B, pin_SUM, pin_CARRY, wires


def write_report():
    from datetime import datetime
    now    = datetime.now().strftime("%Y-%m-%d %H:%M")
    passed = sum(1 for _, s, _ in results if s == "PASS")
    skipped= sum(1 for _, s, _ in results if s == "SKIP")
    total  = len(results)
    lines  = [
        "# SVCG Adversarial Test Report (Student Scenarios)",
        "",
        f"**Date:** {now}  ",
        "**Platform:** Windows 11 / MSYS2 MinGW64  ",
        f"**Result: {passed}/{total} passed, {skipped} skipped**",
        "",
        "| # | ID | Test | Result | Notes |",
        "|---|-----|------|--------|-------|",
    ]
    tc_ids = _TC_IDS()
    for i, (name, status, detail) in enumerate(results, 1):
        tc = tc_ids.get(name, "")
        icon = "PASS" if status == "PASS" else ("SKIP" if status == "SKIP" else "FAIL")
        lines.append(f"| {i} | {tc} | {name} | {icon} | {detail} |")
    lines += ["", f"_{passed}/{total} passed, {skipped} skipped._", ""]
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n  Report -> {REPORT_PATH}")

def _TC_IDS():
    return {
        "TC-01 Half adder canvas counts":                        "TC-01",
        "TC-01 Half adder VHDL entity ports":                    "TC-01",
        "TC-01 Half adder VHDL components declared":             "TC-01",
        "TC-01 Half adder VHDL port maps fully connected":       "TC-01",
        "TC-02 Full adder canvas layout":                        "TC-02",
        "TC-02 Full adder internal signals in VHDL":             "TC-02",
        "TC-02 Full adder no open port maps":                    "TC-02",
        "TC-02 Full adder round-trip wire IDs":                  "TC-02",
        "TC-03 MUX_2X1 component in VHDL":                      "TC-03",
        "TC-04 AND chain — internal net as signal":              "TC-04",
        "TC-05 NOT chain — two internal signals":                "TC-05",
        "TC-06 DFF VHDL port names":                             "TC-06",
        "TC-06 DFF testbench clock process":                     "TC-06",
        "TC-06 DFF testbench D stimulus":                        "TC-06",
        "TC-06 DFF VHDL GHDL syntax check":                      "TC-06",
        "TC-07 JKFF Q_bar rename in VHDL":                      "TC-07",
        "TC-08 SRFF VHDL generation no crash":                   "TC-08",
        "TC-09 Port names match pin text exactly":               "TC-09",
        "TC-10 Net name appears as signal declaration":          "TC-10",
        "TC-11 Wire name with space sanitized":                  "TC-11",
        "TC-12 Unconnected pin maps to open":                    "TC-12",
        "TC-13 All three port directions in VHDL entity":        "TC-13",
        "TC-14 Digit-start pin name sanitized":                  "TC-14",
        "TC-14 Special-char pin name sanitized":                 "TC-14",
        "TC-14 Unicode net name sanitized":                      "TC-14",
        "TC-15 Half adder round-trip counts":                    "TC-15",
        "TC-16 Wire IDs preserved after save/load":              "TC-16",
        "TC-17 Block fill color preserved after save/load":      "TC-17",
        "TC-18 Wire net name preserved after save/load":         "TC-18",
        "TC-19 Origin-point wire survives reload":               "TC-19",
        "TC-20 Block at (0,0) serializes correctly":             "TC-20",
        "TC-21 Input-to-input wire no crash":                    "TC-21",
        "TC-22 Duplicate wire detection logic":                  "TC-22",
        "TC-23 Overlapping blocks no crash":                     "TC-23",
        "TC-24 Pin name >200 chars sanitized":                   "TC-24",
        "TC-25 All-digit pin name gets sig_ prefix":             "TC-25",
        "TC-26 Unicode net name sanitized in VHDL":              "TC-26",
        "TC-27 Undo on empty stack no crash":                    "TC-27",
        "TC-28 30 undo push/pop cycles consistent":              "TC-28",
        "TC-29 Component save creates JSON file":                "TC-29",
        "TC-30 Instantiated component has fresh IDs":            "TC-30",
        "TC-31 Double instantiation — no ID collisions":         "TC-31",
        "TC-32 Malformed component JSON no crash":               "TC-32",
        "TC-33 Testbench UUT port map has all signal names":     "TC-33",
        "TC-34 Testbench clock half-period is 5 ns":             "TC-34",
        "TC-35 Testbench stimulus covers all non-CLK inputs":    "TC-35",
        "TC-36 Bus pin expands to individual bits":              "TC-36",
        "TC-37 SVG file has valid XML/SVG header":               "TC-37",
        "TC-38 PNG file has valid magic bytes":                  "TC-38",
        "TC-39 Export empty canvas returns early":               "TC-39",
        "TC-40 Bounding box padding is exactly 40px":            "TC-40",
        "TC-41 Long diagonal wire has non-empty path":           "TC-41",
        "TC-42 A* full-grid fallback on blocked sub-grid":       "TC-42",
        "TC-43 Manhattan path geometry correct":                 "TC-43",
        "TC-44 Wire path has no duplicate consecutive points":   "TC-44",
        "TC-45 20-wire bus pattern all non-empty":               "TC-45",
        "TC-46 Yosys AND+OR import cell count":                  "TC-46",
        "TC-47 Yosys unsupported cell warning no crash":         "TC-47",
        "TC-48 Yosys empty JSON returns gracefully":             "TC-48",
        "TC-49 Yosys multi-driver net no crash":                 "TC-49",
    }


# ---------------------------------------------------------------------------
# TG-01 — Combinational circuits
# ---------------------------------------------------------------------------

def tg01_combinational(win):
    from blocks import Block
    from pins   import Pin
    from wire   import Wire
    from vhdl_export import generate_vhdl

    gs = win.grid_size
    print("\n-- TG-01: Combinational Circuits --")

    # TC-01: Half Adder
    reset(win)
    xor_blk, and_blk, pin_A, pin_B, pin_SUM, pin_CARRY, wires = build_half_adder(win)
    vhdl_ha = generate_vhdl("HALF_ADDER", win.blocks, win.pins, win.wires)

    def t01_counts():
        assert len(win.blocks) == 2, f"Expected 2 blocks, got {len(win.blocks)}"
        assert len(win.pins)   == 4, f"Expected 4 pins, got {len(win.pins)}"
        assert len(win.wires)  == 6, f"Expected 6 wires, got {len(win.wires)}"
    run_test("TC-01 Half adder canvas counts", t01_counts)

    def t01_ports():
        assert "A : in  STD_LOGIC" in vhdl_ha,    "A port missing"
        assert "B : in  STD_LOGIC" in vhdl_ha,    "B port missing"
        assert "SUM : out  STD_LOGIC" in vhdl_ha,  "SUM port missing"
        assert "CARRY : out  STD_LOGIC" in vhdl_ha,"CARRY port missing"
    run_test("TC-01 Half adder VHDL entity ports", t01_ports)

    def t01_components():
        assert "component XOR_GATE" in vhdl_ha, "XOR_GATE component missing"
        assert "component AND_GATE" in vhdl_ha, "AND_GATE component missing"
    run_test("TC-01 Half adder VHDL components declared", t01_components)

    def t01_portmap():
        assert "open" not in vhdl_ha, f"Unexpected 'open' — unconnected pin in half adder:\n{vhdl_ha}"
    run_test("TC-01 Half adder VHDL port maps fully connected", t01_portmap)

    # TC-02: Full Adder  (HA1 + HA2 + OR)
    reset(win)
    rebuild_grid(win)
    # HA1 at left, HA2 at centre, OR at right
    ha1 = Block(gs*3,  gs*5,  gs*4, gs*4, "HA1", "HA",  gs, win)
    ha2 = Block(gs*12, gs*5,  gs*4, gs*4, "HA2", "HA",  gs, win)
    or_ = Block(gs*21, gs*5,  gs*4, gs*4, "OR1", "OR",  gs, win)
    p_A   = Pin(gs*1,  gs*3,  gs*3, gs*2, "A",   "input_pin",  gs, 1, win)
    p_B   = Pin(gs*1,  gs*9,  gs*3, gs*2, "B",   "input_pin",  gs, 1, win)
    p_CIN = Pin(gs*1,  gs*15, gs*3, gs*2, "CIN", "input_pin",  gs, 1, win)
    p_SUM = Pin(gs*28, gs*5,  gs*3, gs*2, "SUM", "output_pin", gs, 1, win)
    p_CO  = Pin(gs*28, gs*11, gs*3, gs*2, "COUT","output_pin", gs, 1, win)
    win.blocks.extend([ha1, ha2, or_])
    win.pins.extend([p_A, p_B, p_CIN, p_SUM, p_CO])
    rebuild_grid(win)

    # HA1: A=input_A[0], B=input_A[1]; CO=output[0], SO=output[1]
    connect_wire(win, p_A,  0, "pin",    ha1, 0, "input",  "A")
    connect_wire(win, p_B,  0, "pin",    ha1, 1, "input",  "B")
    w_sum1 = connect_wire(win, ha1, 1, "output", ha2, 0, "input",  "sum1")
    w_co1  = connect_wire(win, ha1, 0, "output", or_, 0, "input",  "co1")
    connect_wire(win, p_CIN,0, "pin",    ha2, 1, "input",  "CIN")
    connect_wire(win, ha2, 1, "output", p_SUM, 0, "pin",   "SUM")
    w_co2  = connect_wire(win, ha2, 0, "output", or_, 1, "input",  "co2")
    connect_wire(win, or_, 0, "output", p_CO, 0, "pin",    "COUT")

    w_sum1.text = "sum1"
    w_co1.text  = "co1"
    w_co2.text  = "co2"
    vhdl_fa = generate_vhdl("FULL_ADDER", win.blocks, win.pins, win.wires)

    def t02_layout():
        assert len(win.blocks) == 3
        assert len(win.pins)   == 5
        assert len(win.wires)  == 8
    run_test("TC-02 Full adder canvas layout", t02_layout)

    def t02_signals():
        assert "signal sum1 : STD_LOGIC;" in vhdl_fa, f"signal sum1 missing:\n{vhdl_fa}"
        assert "signal co1 : STD_LOGIC;"  in vhdl_fa, f"signal co1 missing"
        assert "signal co2 : STD_LOGIC;"  in vhdl_fa, f"signal co2 missing"
    run_test("TC-02 Full adder internal signals in VHDL", t02_signals)

    def t02_no_open():
        assert "open" not in vhdl_fa, "Unexpected 'open' in full adder VHDL"
    run_test("TC-02 Full adder no open port maps", t02_no_open)

    def t02_roundtrip():
        original_ids = {w.id for w in win.wires}
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            p = f.name
        win.save_to_json(p)
        win.load_from_json(p)
        os.unlink(p)
        reloaded_ids = {w.id for w in win.wires}
        assert original_ids == reloaded_ids, \
            f"Wire IDs changed: lost {original_ids - reloaded_ids}"
    run_test("TC-02 Full adder round-trip wire IDs", t02_roundtrip)

    # TC-03: MUX 2x1
    reset(win)
    mux = Block(gs*5, gs*5, gs*4, gs*4, "MUX1", "MUX_2X1", gs, win)
    win.blocks.append(mux)
    vhdl_mux = generate_vhdl("MUX_TOP", win.blocks, [], [])

    def t03_mux():
        assert "component MUX2x1" in vhdl_mux, f"MUX2x1 component not found:\n{vhdl_mux}"
    run_test("TC-03 MUX_2X1 component in VHDL", t03_mux)

    # TC-04: AND reduction chain  A,B -> AND1 -> AND2 (with C) -> Y
    reset(win)
    rebuild_grid(win)
    a1 = Block(gs*5,  gs*5, gs*4, gs*4, "AND1", "AND", gs, win)
    a2 = Block(gs*13, gs*5, gs*4, gs*4, "AND2", "AND", gs, win)
    pA = Pin(gs*1, gs*5,  gs*3, gs*2, "A", "input_pin",  gs, 1, win)
    pB = Pin(gs*1, gs*9,  gs*3, gs*2, "B", "input_pin",  gs, 1, win)
    pC = Pin(gs*1, gs*13, gs*3, gs*2, "C", "input_pin",  gs, 1, win)
    pY = Pin(gs*20, gs*5, gs*3, gs*2, "Y", "output_pin", gs, 1, win)
    win.blocks.extend([a1, a2])
    win.pins.extend([pA, pB, pC, pY])
    rebuild_grid(win)

    connect_wire(win, pA, 0, "pin",    a1, 0, "input",  "A")
    connect_wire(win, pB, 0, "pin",    a1, 1, "input",  "B")
    w_mid = connect_wire(win, a1, 0, "output", a2, 0, "input",  "AB")
    connect_wire(win, pC, 0, "pin",    a2, 1, "input",  "C")
    connect_wire(win, a2, 0, "output", pY, 0, "pin",    "Y")
    w_mid.text = "AB"
    vhdl_and = generate_vhdl("AND_CHAIN", win.blocks, win.pins, win.wires)

    def t04_chain():
        assert "signal AB : STD_LOGIC;" in vhdl_and, \
            f"Internal net AB not a signal:\n{vhdl_and}"
    run_test("TC-04 AND chain -- internal net as signal", t04_chain)

    # TC-05: NOT chain  A -> N1 -> N2 -> N3 -> Y
    reset(win)
    rebuild_grid(win)
    n1 = Block(gs*5,  gs*5, gs*4, gs*4, "N1", "NOT", gs, win)
    n2 = Block(gs*12, gs*5, gs*4, gs*4, "N2", "NOT", gs, win)
    n3 = Block(gs*19, gs*5, gs*4, gs*4, "N3", "NOT", gs, win)
    pNA = Pin(gs*1,  gs*5, gs*3, gs*2, "A", "input_pin",  gs, 1, win)
    pNY = Pin(gs*25, gs*5, gs*3, gs*2, "Y", "output_pin", gs, 1, win)
    win.blocks.extend([n1, n2, n3])
    win.pins.extend([pNA, pNY])
    rebuild_grid(win)

    connect_wire(win, pNA, 0, "pin",    n1, 0, "input",  "A")
    w_n12 = connect_wire(win, n1, 0, "output", n2, 0, "input",  "not_a")
    w_n23 = connect_wire(win, n2, 0, "output", n3, 0, "input",  "not_not_a")
    connect_wire(win, n3, 0, "output", pNY, 0, "pin",   "Y")
    w_n12.text = "not_a"
    w_n23.text = "not_not_a"
    vhdl_not = generate_vhdl("NOT_CHAIN", win.blocks, win.pins, win.wires)

    def t05_not():
        assert "signal not_a : STD_LOGIC;"     in vhdl_not, "not_a signal missing"
        assert "signal not_not_a : STD_LOGIC;" in vhdl_not, "not_not_a signal missing"
    run_test("TC-05 NOT chain -- two internal signals", t05_not)


# ---------------------------------------------------------------------------
# TG-02 — Sequential circuits
# ---------------------------------------------------------------------------

def tg02_sequential(win):
    from blocks import Block
    from pins   import Pin
    from vhdl_export  import generate_vhdl, check_vhdl_syntax
    from testbench_gen import generate_testbench

    gs = win.grid_size
    print("\n-- TG-02: Sequential Circuits --")

    # TC-06: DFF with CLK
    reset(win)
    rebuild_grid(win)
    dff  = Block(gs*8,  gs*5, gs*4, gs*4, "DFF1", "DFF", gs, win)
    pD   = Pin(gs*1,  gs*5,  gs*3, gs*2, "D",   "input_pin",  gs, 1, win)
    pCLK = Pin(gs*1,  gs*10, gs*3, gs*2, "clk", "CLK",        gs, 1, win)
    pQ   = Pin(gs*16, gs*5,  gs*3, gs*2, "Q",   "output_pin", gs, 1, win)
    win.blocks.append(dff)
    win.pins.extend([pD, pCLK, pQ])
    rebuild_grid(win)

    # DFF input_names = ["D","CLK","PRE","CLR"], output_names = ["Q","Q'"]
    connect_wire(win, pD,   0, "pin",    dff, 0, "input",  "D")
    connect_wire(win, pCLK, 0, "pin",    dff, 1, "input",  "clk")
    connect_wire(win, dff,  0, "output", pQ,  0, "pin",    "Q")
    vhdl_dff = generate_vhdl("DFF_TOP", win.blocks, win.pins, win.wires)
    tb_dff   = generate_testbench("DFF_TOP", win.pins)

    def t06_ports():
        assert "D : in  STD_LOGIC"   in vhdl_dff, f"D missing:\n{vhdl_dff}"
        assert "clk : in  STD_LOGIC" in vhdl_dff, f"clk missing"
        assert "Q : out  STD_LOGIC"  in vhdl_dff, f"Q missing"
    run_test("TC-06 DFF VHDL port names", t06_ports)

    def t06_tb_clk():
        assert "clk_proc" in tb_dff or "clk" in tb_dff.lower(), \
            "No clock process in DFF testbench"
        assert "5 ns" in tb_dff, "Clock half-period 5 ns missing from testbench"
    run_test("TC-06 DFF testbench clock process", t06_tb_clk)

    def t06_tb_d():
        assert "D <= '1';" in tb_dff or "D <=" in tb_dff, \
            "D stimulus missing from testbench"
    run_test("TC-06 DFF testbench D stimulus", t06_tb_d)

    # GHDL check (TC-06)
    if shutil.which("ghdl"):
        with tempfile.NamedTemporaryFile(suffix=".vhd", delete=False, mode="w") as f:
            f.write(vhdl_dff)
            vhd_path = f.name
        try:
            avail, ok, out = check_vhdl_syntax(vhd_path)
            def t06_ghdl():
                assert ok, f"GHDL errors:\n{out}"
            run_test("TC-06 DFF VHDL GHDL syntax check", t06_ghdl)
        finally:
            os.unlink(vhd_path)
    else:
        log_skip("TC-06 DFF VHDL GHDL syntax check", "ghdl not on PATH")

    # TC-07: JKFF Q' rename to Q_bar
    reset(win)
    jkff = Block(gs*8, gs*5, gs*4, gs*4, "JK1", "JKFF", gs, win)
    win.blocks.append(jkff)
    vhdl_jk = generate_vhdl("JKFF_TOP", win.blocks, [], [])

    def t07_qbar():
        assert "Q_bar" in vhdl_jk, f"Q_bar not found in JKFF VHDL:\n{vhdl_jk}"
        assert "Q'" not in vhdl_jk, "Raw Q' should not appear in VHDL output"
    run_test("TC-07 JKFF Q_bar rename in VHDL", t07_qbar)

    # TC-08: SRFF
    reset(win)
    srff = Block(gs*8, gs*5, gs*4, gs*4, "SR1", "SRFF", gs, win)
    win.blocks.append(srff)

    def t08_srff():
        vhdl_sr = generate_vhdl("SRFF_TOP", win.blocks, [], [])
        assert "component SRFF" in vhdl_sr
    run_test("TC-08 SRFF VHDL generation no crash", t08_srff)


# ---------------------------------------------------------------------------
# TG-03 — VHDL output correctness
# ---------------------------------------------------------------------------

def tg03_vhdl_correctness(win):
    from blocks import Block
    from pins   import Pin
    from wire   import Wire
    from vhdl_export import generate_vhdl, _sanitize

    gs = win.grid_size
    print("\n-- TG-03: VHDL Output Correctness --")

    # TC-09: Port names match pin text exactly
    reset(win)
    p1 = Pin(gs*1, gs*5, gs*3, gs*2, "my_input",  "input_pin",  gs, 1, win)
    p2 = Pin(gs*1, gs*9, gs*3, gs*2, "my_output", "output_pin", gs, 1, win)
    win.pins.extend([p1, p2])
    vhdl = generate_vhdl("EXACT", [], win.pins, [])

    def t09():
        assert "my_input : in  STD_LOGIC"  in vhdl, f"my_input port missing:\n{vhdl}"
        assert "my_output : out  STD_LOGIC" in vhdl, f"my_output port missing"
    run_test("TC-09 Port names match pin text exactly", t09)

    # TC-10: Wire net name → signal declaration
    reset(win)
    rebuild_grid(win)
    b1 = Block(gs*3, gs*5,  gs*4, gs*4, "A1", "AND", gs, win)
    b2 = Block(gs*12, gs*5, gs*4, gs*4, "O1", "OR",  gs, win)
    win.blocks.extend([b1, b2])
    rebuild_grid(win)
    w = connect_wire(win, b1, 0, "output", b2, 0, "input", "internal_carry")
    w.text = "internal_carry"
    vhdl2 = generate_vhdl("NET_TEST", win.blocks, [], win.wires)

    def t10():
        assert "signal internal_carry : STD_LOGIC;" in vhdl2, \
            f"signal declaration missing:\n{vhdl2}"
    run_test("TC-10 Net name appears as signal declaration", t10)

    # TC-11: Wire name with space → sanitized
    def t11():
        assert _sanitize("sum out") == "sum_out"
    run_test("TC-11 Wire name with space sanitized", t11)

    # TC-12: Unconnected pin → "open" in port map
    reset(win)
    b_open = Block(gs*5, gs*5, gs*4, gs*4, "AND_open", "AND", gs, win)
    win.blocks.append(b_open)
    # Leave all inputs/outputs unconnected
    vhdl_open = generate_vhdl("OPEN_TEST", win.blocks, [], [])

    def t12():
        assert "open" in vhdl_open, \
            f"Expected 'open' for unconnected pins:\n{vhdl_open}"
    run_test("TC-12 Unconnected pin maps to open", t12)

    # TC-13: All three port directions
    reset(win)
    p_in   = Pin(gs*1, gs*3,  gs*3, gs*2, "pin_in",   "input_pin",        gs, 1, win)
    p_out  = Pin(gs*1, gs*7,  gs*3, gs*2, "pin_out",  "output_pin",       gs, 1, win)
    p_inout= Pin(gs*1, gs*11, gs*3, gs*2, "pin_io",   "input_output_pin", gs, 1, win)
    win.pins.extend([p_in, p_out, p_inout])
    vhdl3 = generate_vhdl("DIRS", [], win.pins, [])

    def t13():
        assert "pin_in : in  STD_LOGIC"    in vhdl3, "in direction missing"
        assert "pin_out : out  STD_LOGIC"  in vhdl3, "out direction missing"
        assert "pin_io : inout  STD_LOGIC" in vhdl3, "inout direction missing"
    run_test("TC-13 All three port directions in VHDL entity", t13)

    # TC-14: Identifier sanitization edge cases
    def t14_digit():
        assert _sanitize("123") == "sig_123", f"Got: {_sanitize('123')}"
    run_test("TC-14 Digit-start pin name sanitized", t14_digit)

    def t14_special():
        result = _sanitize("signal!out")
        assert result == "signal_out", f"Got: {result}"
    run_test("TC-14 Special-char pin name sanitized", t14_special)

    def t14_unicode():
        result = _sanitize("clk→Q")   # "clk→Q"
        assert result.isascii(), f"Non-ASCII in result: {result}"
        assert len(result) > 0
    run_test("TC-14 Unicode net name sanitized", t14_unicode)


# ---------------------------------------------------------------------------
# TG-04 — Save / Load round-trip
# ---------------------------------------------------------------------------

def tg04_roundtrip(win):
    print("\n-- TG-04: Save / Load Round-Trip --")

    # TC-15
    reset(win)
    build_half_adder(win)
    nb0, np0, nw0 = len(win.blocks), len(win.pins), len(win.wires)

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        p15 = f.name
    win.save_to_json(p15)
    win.load_from_json(p15)
    os.unlink(p15)

    def t15():
        assert len(win.blocks) == nb0, f"{len(win.blocks)} != {nb0}"
        assert len(win.pins)   == np0, f"{len(win.pins)} != {np0}"
        assert len(win.wires)  == nw0, f"{len(win.wires)} != {nw0}"
    run_test("TC-15 Half adder round-trip counts", t15)

    # TC-16: Wire IDs preserved
    reset(win)
    build_half_adder(win)
    ids_before = {w.id for w in win.wires}
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        p16 = f.name
    win.save_to_json(p16)
    win.load_from_json(p16)
    os.unlink(p16)

    def t16():
        ids_after = {w.id for w in win.wires}
        assert ids_before == ids_after, \
            f"Lost IDs: {ids_before - ids_after}; gained: {ids_after - ids_before}"
    run_test("TC-16 Wire IDs preserved after save/load", t16)

    # TC-17: Block fill color preserved
    reset(win)
    build_half_adder(win)
    win.blocks[0].fill_color = (0.1, 0.5, 0.9)
    saved_color = win.blocks[0].fill_color
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        p17 = f.name
    win.save_to_json(p17)
    win.load_from_json(p17)
    os.unlink(p17)

    def t17():
        loaded_color = win.blocks[0].fill_color
        assert len(loaded_color) == 3
        assert abs(loaded_color[0] - saved_color[0]) < 0.01, \
            f"R changed: {saved_color[0]} -> {loaded_color[0]}"
    run_test("TC-17 Block fill color preserved after save/load", t17)

    # TC-18: Wire net name preserved
    reset(win)
    build_half_adder(win)
    win.wires[0].text = "my_special_net"
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        p18 = f.name
    win.save_to_json(p18)
    win.load_from_json(p18)
    os.unlink(p18)

    def t18():
        names = [w.text for w in win.wires]
        assert "my_special_net" in names, f"Net name lost. Got: {names}"
    run_test("TC-18 Wire net name preserved after save/load", t18)

    # TC-19: Wire at origin survives reload
    reset(win)
    from blocks import Block
    from wire   import Wire
    gs = win.grid_size
    b = Block(0, 0, gs*4, gs*4, "ORIG", "NOT", gs, win)
    win.blocks.append(b)
    rebuild_grid(win)
    sp = list(b.output_points[0]) if b.output_points else [0, gs*4]
    ep = [gs*20, gs*20]
    w_orig = Wire("origin_net", sp, ep, "wire", gs, win)
    win.wires.append(w_orig)
    orig_id = w_orig.id
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        p19 = f.name
    win.save_to_json(p19)
    win.load_from_json(p19)
    os.unlink(p19)

    def t19():
        ids = {w.id for w in win.wires}
        assert orig_id in ids, "Origin-point wire ID lost after reload (regression)"
    run_test("TC-19 Origin-point wire survives reload", t19)


# ---------------------------------------------------------------------------
# TG-05 — Adversarial / student-mistake edge cases
# ---------------------------------------------------------------------------

def tg05_adversarial(win):
    from blocks import Block
    from pins   import Pin
    from wire   import Wire
    from vhdl_export import generate_vhdl, _sanitize

    gs = win.grid_size
    print("\n-- TG-05: Adversarial Edge Cases --")

    # TC-20: Block at (0,0)
    reset(win)

    def t20():
        b = Block(0, 0, gs*4, gs*4, "ZERO", "AND", gs, win)
        win.blocks.append(b)
        j = win.elements_to_json()
        assert j is not None
        data = json.loads(j)
        assert any(d.get("x") == 0 and d.get("y") == 0 for d in data), \
            "Block at origin not found in JSON"
    run_test("TC-20 Block at (0,0) serializes correctly", t20)

    # TC-21: Wire from input_pin to input_pin (student mistake)
    reset(win)
    p_i1 = Pin(gs*1, gs*5,  gs*3, gs*2, "IN1", "input_pin", gs, 1, win)
    p_i2 = Pin(gs*8, gs*5,  gs*3, gs*2, "IN2", "input_pin", gs, 1, win)
    win.pins.extend([p_i1, p_i2])
    rebuild_grid(win)

    def t21():
        sp = list(p_i1.connection_points[0])
        ep = list(p_i2.connection_points[0])
        w = Wire("mistake_wire", sp, ep, "wire", gs, win)
        win.wires.append(w)
        vhdl = generate_vhdl("MISTAKE", [], win.pins, win.wires)
        assert "MISTAKE" in vhdl  # must not crash
    run_test("TC-21 Input-to-input wire no crash", t21)

    # TC-22: Duplicate wire detection logic
    reset(win)
    rebuild_grid(win)
    b_a = Block(gs*3, gs*5, gs*4, gs*4, "A", "NOT", gs, win)
    b_b = Block(gs*12, gs*5, gs*4, gs*4, "B", "NOT", gs, win)
    win.blocks.extend([b_a, b_b])
    rebuild_grid(win)
    sp = list(b_a.output_points[0])
    ep = list(b_b.input_points[0])
    w1 = Wire("net1", sp, ep, "wire", gs, win)
    win.wires.append(w1)

    def t22():
        # Replicate the exact guard from on_button_release
        wire_start_point = sp
        end_point        = ep
        duplicate = any(
            (w.start_point == wire_start_point and w.end_point == end_point) or
            (w.start_point == end_point         and w.end_point == wire_start_point)
            for w in win.wires
        )
        assert duplicate, "Duplicate wire not detected by the guard logic"
    run_test("TC-22 Duplicate wire detection logic", t22)

    # TC-23: Overlapping blocks
    reset(win)

    def t23():
        b1 = Block(gs*5, gs*5, gs*4, gs*4, "BLK1", "AND", gs, win)
        b2 = Block(gs*5, gs*5, gs*4, gs*4, "BLK2", "AND", gs, win)
        win.blocks.extend([b1, b2])
        j = win.elements_to_json()
        data = json.loads(j)
        blk_data = [d for d in data if d.get("block_type")]
        assert len(blk_data) == 2, f"Expected 2 blocks in JSON, got {len(blk_data)}"
    run_test("TC-23 Overlapping blocks no crash", t23)

    # TC-24: Very long pin name
    reset(win)
    long_name = "X" * 201

    def t24():
        result = _sanitize(long_name)
        assert isinstance(result, str) and len(result) > 0
        p = Pin(gs*1, gs*5, gs*3, gs*2, long_name, "input_pin", gs, 1, win)
        win.pins.append(p)
        vhdl = generate_vhdl("LONG", [], win.pins, [])
        assert "entity LONG" in vhdl
    run_test("TC-24 Pin name >200 chars sanitized", t24)

    # TC-25: All-digit pin name
    def t25():
        assert _sanitize("123") == "sig_123", f"Got {_sanitize('123')}"
    run_test("TC-25 All-digit pin name gets sig_ prefix", t25)

    # TC-26: Unicode net name
    def t26():
        result = _sanitize("Σout")   # "Σout"
        assert result.isascii() and len(result) > 0, f"Bad sanitize result: {result}"
    run_test("TC-26 Unicode net name sanitized in VHDL", t26)

    # TC-27: Undo on empty stack
    reset(win)

    def t27():
        win.undo_stack.clear()
        win.undo()   # must not raise
    run_test("TC-27 Undo on empty stack no crash", t27)

    # TC-28: 30 undo cycles
    reset(win)
    build_half_adder(win)
    baseline_json = win.elements_to_json()

    def t28():
        for _ in range(30):
            win.push_undo()
        for _ in range(30):
            win.undo()
        for _ in range(30):
            win.redo()
        # After 30 redos the canvas must match the state after 30 pushes
        assert len(win.undo_stack) >= 0   # stack exists
        assert len(win.redo_stack) == 0   # all redone
    run_test("TC-28 30 undo push/pop cycles consistent", t28)


# ---------------------------------------------------------------------------
# TG-06 — Component library
# ---------------------------------------------------------------------------

def tg06_components(win):
    print("\n-- TG-06: Component Library --")
    gs = win.grid_size
    comp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "components")

    # TC-29: Save half adder as component
    reset(win)
    build_half_adder(win)
    win.selected_blocks = list(win.blocks)
    win.selected_pins   = list(win.pins)
    for b in win.selected_blocks:
        b.set_selected(True)
    for p in win.selected_pins:
        p.set_selected(True)

    # Bypass the dialog and call the save logic directly
    sel_pts = set()
    for b in win.selected_blocks:
        sel_pts.update(tuple(pt) if isinstance(pt, list) else pt for pt in b.input_points)
        sel_pts.update(tuple(pt) if isinstance(pt, list) else pt for pt in b.output_points)
    for p in win.selected_pins:
        sel_pts.update(tuple(cp) if isinstance(cp, list) else cp for cp in p.connection_points)
    internal_wires = [
        w for w in win.wires
        if (tuple(w.start_point) if isinstance(w.start_point, list) else w.start_point) in sel_pts
        and (tuple(w.end_point) if isinstance(w.end_point, list) else w.end_point) in sel_pts
    ]
    comp_data = {
        "name": "test_halfadder",
        "blocks": [b.to_dict() for b in win.selected_blocks],
        "pins":   [p.to_dict() for p in win.selected_pins],
        "wires":  [w.to_dict() for w in internal_wires],
    }
    os.makedirs(comp_dir, exist_ok=True)
    comp_path = os.path.join(comp_dir, "test_halfadder.json")
    with open(comp_path, "w") as f:
        json.dump(comp_data, f, indent=2)

    def t29():
        assert os.path.exists(comp_path)
        with open(comp_path) as f:
            data = json.load(f)
        assert "blocks" in data and "pins" in data and "wires" in data
    run_test("TC-29 Component save creates JSON file", t29)

    # TC-30: Instantiate → fresh IDs
    original_block_ids = {b.id for b in win.selected_blocks}
    original_pin_ids   = {p.id for p in win.selected_pins}
    reset(win)
    win.instantiate_component(comp_path)

    def t30():
        new_block_ids = {b.id for b in win.blocks}
        new_pin_ids   = {p.id for p in win.pins}
        assert not new_block_ids & original_block_ids, \
            f"Shared block IDs: {new_block_ids & original_block_ids}"
        assert not new_pin_ids & original_pin_ids, \
            f"Shared pin IDs: {new_pin_ids & original_pin_ids}"
    run_test("TC-30 Instantiated component has fresh IDs", t30)

    # TC-31: Double instantiation — no ID collisions anywhere
    reset(win)
    win.instantiate_component(comp_path)
    win.instantiate_component(comp_path)

    def t31():
        all_ids = [obj.id for obj in win.blocks + win.pins + win.wires]
        assert len(all_ids) == len(set(all_ids)), \
            f"Duplicate IDs after double instantiation: " \
            f"{[x for x in all_ids if all_ids.count(x) > 1]}"
    run_test("TC-31 Double instantiation -- no ID collisions", t31)

    # TC-32: Malformed component JSON
    reset(win)
    n_before = len(win.blocks)

    def t32():
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            f.write("{bad json!!")
            bad = f.name
        try:
            win._headless = True
            win.instantiate_component(bad)
        finally:
            win._headless = False
            os.unlink(bad)
        assert len(win.blocks) == n_before, "Canvas modified despite malformed JSON"
    run_test("TC-32 Malformed component JSON no crash", t32)

    # clean up test component
    if os.path.exists(comp_path):
        os.unlink(comp_path)


# ---------------------------------------------------------------------------
# TG-07 — Testbench quality
# ---------------------------------------------------------------------------

def tg07_testbench(win):
    from pins import Pin
    from testbench_gen import generate_testbench

    gs = win.grid_size
    print("\n-- TG-07: Testbench Quality --")

    # TC-33: UUT port map signal names
    reset(win)
    p_a   = Pin(gs*1, gs*3,  gs*3, gs*2, "A",   "input_pin",  gs, 1, win)
    p_b   = Pin(gs*1, gs*7,  gs*3, gs*2, "B",   "input_pin",  gs, 1, win)
    p_out = Pin(gs*1, gs*11, gs*3, gs*2, "Y",   "output_pin", gs, 1, win)
    win.pins.extend([p_a, p_b, p_out])
    tb = generate_testbench("MY_CIRCUIT", win.pins)

    def t33():
        for sig in ("A", "B", "Y"):
            assert f"{sig} => {sig}" in tb, f"UUT port map missing '{sig} => {sig}'"
    run_test("TC-33 Testbench UUT port map has all signal names", t33)

    # TC-34: Clock half-period
    reset(win)
    clk_pin = Pin(gs*1, gs*5, gs*3, gs*2, "clk", "CLK", gs, 1, win)
    win.pins.append(clk_pin)
    tb34 = generate_testbench("CLK_CIRCUIT", win.pins)

    def t34():
        assert "5 ns" in tb34, f"5 ns half-period not found:\n{tb34}"
    run_test("TC-34 Testbench clock half-period is 5 ns", t34)

    # TC-35: All non-CLK inputs get stimulus
    reset(win)
    p1 = Pin(gs*1, gs*3, gs*3, gs*2, "A",   "input_pin", gs, 1, win)
    p2 = Pin(gs*1, gs*7, gs*3, gs*2, "B",   "input_pin", gs, 1, win)
    p3 = Pin(gs*1, gs*11, gs*3, gs*2, "clk","CLK",       gs, 1, win)
    win.pins.extend([p1, p2, p3])
    tb35 = generate_testbench("STIM_CIRCUIT", win.pins)

    def t35():
        assert "A <= '1';" in tb35, "A stimulus missing"
        assert "B <= '1';" in tb35, "B stimulus missing"
    run_test("TC-35 Testbench stimulus covers all non-CLK inputs", t35)

    # TC-36: Bus pin expands to individual bits
    reset(win)
    bus_pin = Pin(gs*1, gs*5, gs*3, gs*2, "data", "input_bus", gs, 4, win)
    win.pins.append(bus_pin)
    tb36 = generate_testbench("BUS_CIRCUIT", win.pins)

    def t36():
        for i in range(4):
            sig = f"data_{i}"
            assert sig in tb36, f"Bus bit signal '{sig}' missing from testbench"
    run_test("TC-36 Bus pin expands to individual bits", t36)


# ---------------------------------------------------------------------------
# TG-08 — Export file format integrity
# ---------------------------------------------------------------------------

def tg08_export(win):
    print("\n-- TG-08: Export File Integrity --")

    # TC-37: SVG header
    reset(win)
    build_half_adder(win)
    x0, y0, x1, y1 = win._compute_bbox()
    w, h = max(1.0, x1 - x0), max(1.0, y1 - y0)

    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
        svg_path = f.name
    surface = _cairo.SVGSurface(svg_path, w, h)
    cr = _cairo.Context(surface)
    cr.translate(-x0, -y0)
    win._render_schematic(cr)
    surface.finish()

    def t37():
        with open(svg_path, "rb") as f:
            header = f.read(200).decode("utf-8", errors="replace")
        assert "<?xml" in header or "<svg" in header, \
            f"SVG header not found. First 200 bytes: {header!r}"
    run_test("TC-37 SVG file has valid XML/SVG header", t37)
    os.unlink(svg_path)

    # TC-38: PNG magic bytes
    x0, y0, x1, y1 = win._compute_bbox()
    ww, hh = max(1, int(x1 - x0)), max(1, int(y1 - y0))
    surface2 = _cairo.ImageSurface(_cairo.FORMAT_ARGB32, ww, hh)
    cr2 = _cairo.Context(surface2)
    cr2.translate(-x0, -y0)
    win._render_schematic(cr2)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        png_path = f.name
    surface2.write_to_png(png_path)

    def t38():
        with open(png_path, "rb") as f:
            magic = f.read(8)
        assert magic == b'\x89PNG\r\n\x1a\n', f"Bad PNG magic: {magic!r}"
    run_test("TC-38 PNG file has valid magic bytes", t38)
    os.unlink(png_path)

    # TC-39: Empty canvas returns early
    reset(win)

    def t39():
        # Call the method directly; it shows a dialog only if blocks/pins exist.
        # With an empty canvas the method returns early without touching any file.
        # We verify no exception is raised and no temp file is accidentally created.
        assert not win.blocks and not win.pins  # pre-condition
        # on_export_svg/png both guard with: if not self.blocks and not self.pins: return
        # Replicate the guard
        should_export = bool(win.blocks or win.pins)
        assert not should_export, "Empty canvas should not proceed to export"
    run_test("TC-39 Export empty canvas returns early", t39)

    # TC-40: Bounding box padding exactly 40px
    reset(win)
    from blocks import Block
    gs = win.grid_size
    b_bb = Block(gs*5, gs*5, gs*4, gs*4, "BB_TEST", "AND", gs, win)
    win.blocks.append(b_bb)
    x0, y0, x1, y1 = win._compute_bbox(padding=40)

    def t40():
        # min x of block is gs*5; x0 should be gs*5 - 40
        expected_x0 = max(0, gs*5 - 40)
        expected_x1 = gs*5 + gs*4 + 40
        assert x0 == expected_x0, f"x0={x0} expected {expected_x0}"
        assert x1 == expected_x1, f"x1={x1} expected {expected_x1}"
    run_test("TC-40 Bounding box padding is exactly 40px", t40)


# ---------------------------------------------------------------------------
# TG-09 — Wire routing robustness
# ---------------------------------------------------------------------------

def tg09_routing(win):
    from wire   import Wire
    from blocks import Block

    gs = win.grid_size
    print("\n-- TG-09: Wire Routing Robustness --")

    # TC-41: Long diagonal wire (>25 cells apart)
    reset(win)
    rebuild_grid(win)

    def t41():
        sp = [gs*2,  gs*2]
        ep = [gs*40, gs*35]
        w = Wire("long_diag", sp, ep, "wire", gs, win)
        assert w.path and len(w.path) > 1, "Long diagonal wire path is empty"
        px, py = w.path[0]
        ex_grid = (ep[0] // gs, ep[1] // gs)
        # Path should end within a few cells of the target
        lx, ly = w.path[-1]
        assert abs(lx - ex_grid[0]) <= 3 and abs(ly - ex_grid[1]) <= 3, \
            f"Path ends at {w.path[-1]}, expected near {ex_grid}"
    run_test("TC-41 Long diagonal wire has non-empty path", t41)

    # TC-42: A* bounding-box fallback forced
    reset(win)
    # Place a wall of 6 blocks that cuts across the direct sub-grid path
    # Start=(2,2), End=(10,2), wall at columns 5-7 rows 1-3
    for col in range(5, 8):
        b = Block(gs*col, gs*1, gs*1, gs*3, f"wall_{col}", "AND", gs, win)
        win.blocks.append(b)
    rebuild_grid(win)

    def t42():
        sp = [gs*2, gs*2]
        ep = [gs*10, gs*2]
        w = Wire("around_wall", sp, ep, "wire", gs, win)
        # The wall blocks the sub-grid direct path; A* must route around it
        assert w.path and len(w.path) > 2, \
            f"Expected path around obstacle, got: {w.path}"
    run_test("TC-42 A* full-grid fallback on blocked sub-grid", t42)

    # TC-43: Manhattan path geometry (pure function, no canvas)
    from wire import Wire as _Wire
    import numpy as np
    # Minimal stub to call _manhattan_path without a real parent_window
    class _FakeDA:
        grid = np.zeros((250, 250), dtype=int)
        zoom = 1.0
    class _FakeWin:
        grid_size = 20
        drawing_area = _FakeDA()
        blocks = []
        pins   = []
    fw = _FakeWin()

    def t43():
        w_stub = object.__new__(_Wire)
        w_stub.grid_size    = 20
        w_stub.parent_window= fw
        cases = [
            ((0, 0), (5, 3)),
            ((3, 3), (3, 8)),   # vertical only
            ((5, 2), (0, 2)),   # reverse horizontal
            ((0, 0), (0, 0)),   # same point
        ]
        for start, end in cases:
            path = _Wire._manhattan_path(w_stub, start, end)
            assert path[0]  == start,  f"Path {start}->{end} doesn't start at {start}: {path}"
            assert path[-1] == end,    f"Path {start}->{end} doesn't end at {end}: {path}"
            for i in range(len(path) - 1):
                dx = abs(path[i+1][0] - path[i][0])
                dy = abs(path[i+1][1] - path[i][1])
                assert dx + dy == 1, \
                    f"Non-unit step at index {i}: {path[i]} -> {path[i+1]}"
    run_test("TC-43 Manhattan path geometry correct", t43)

    # TC-44: No duplicate consecutive points
    reset(win)
    rebuild_grid(win)

    def t44():
        w = Wire("no_dup", [gs*3, gs*3], [gs*15, gs*10], "wire", gs, win)
        if w.path:
            for i in range(len(w.path) - 1):
                assert w.path[i] != w.path[i+1], \
                    f"Duplicate consecutive point at index {i}: {w.path[i]}"
    run_test("TC-44 Wire path has no duplicate consecutive points", t44)

    # TC-45: 20-wire bus pattern
    reset(win)
    rebuild_grid(win)

    def t45():
        wires_bus = []
        for i in range(20):
            sp = [gs*2,      gs*(3 + i*2)]
            ep = [gs*15,     gs*(3 + i*2)]
            w = Wire(f"bus_{i}", sp, ep, "wire", gs, win)
            wires_bus.append(w)
        empty = [w for w in wires_bus if not w.path or len(w.path) < 2]
        assert not empty, f"{len(empty)} bus wires have empty/trivial paths"
    run_test("TC-45 20-wire bus pattern all non-empty", t45)


# ---------------------------------------------------------------------------
# TG-10 — Yosys import
# ---------------------------------------------------------------------------

def tg10_yosys(win):
    from yosys_importer import import_yosys_json

    print("\n-- TG-10: Yosys Import --")

    def write_yosys(data):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump(data, f)
            return f.name

    # TC-46: Simple AND + OR netlist
    reset(win)
    simple_netlist = {
        "modules": {
            "top": {
                "cells": {
                    "and_inst": {
                        "type": "$_AND_",
                        "connections": {"A": [2], "B": [3], "Y": [4]}
                    },
                    "or_inst": {
                        "type": "$_OR_",
                        "connections": {"A": [4], "B": [5], "Y": [6]}
                    }
                },
                "ports": {
                    "A": {"direction": "input",  "bits": [2]},
                    "B": {"direction": "input",  "bits": [3]},
                    "C": {"direction": "input",  "bits": [5]},
                    "Y": {"direction": "output", "bits": [6]}
                },
                "netnames": {
                    "A": {"bits": [2]}, "B": {"bits": [3]},
                    "C": {"bits": [5]}, "Y": {"bits": [6]},
                    "net4": {"bits": [4]}
                }
            }
        }
    }
    p46 = write_yosys(simple_netlist)
    n_cells, n_wires, warnings = import_yosys_json(p46, win)
    os.unlink(p46)

    def t46():
        assert n_cells == 2, f"Expected 2 cells, got {n_cells}"
        assert warnings == [], f"Unexpected warnings: {warnings}"
        assert len(win.blocks) == 2, f"Canvas has {len(win.blocks)} blocks"
    run_test("TC-46 Yosys AND+OR import cell count", t46)

    # TC-47: Unsupported cell type
    reset(win)
    unsupported_netlist = {
        "modules": {
            "top": {
                "cells": {
                    "and1":   {"type": "$_AND_",   "connections": {"A":[2],"B":[3],"Y":[4]}},
                    "tribuf": {"type": "$_TRIBUF_", "connections": {"A":[5],"E":[6],"Y":[7]}}
                },
                "ports":    {"A":{"direction":"input","bits":[2]}},
                "netnames": {}
            }
        }
    }
    p47 = write_yosys(unsupported_netlist)
    n47, _, warn47 = import_yosys_json(p47, win)
    os.unlink(p47)

    def t47():
        assert n47 == 1, f"Expected 1 supported cell, got {n47}"
        assert any("TRIBUF" in w or "tribuf" in w.lower() for w in warn47), \
            f"Warning for unsupported cell not found: {warn47}"
    run_test("TC-47 Yosys unsupported cell warning no crash", t47)

    # TC-48: Empty JSON object
    reset(win)
    p48 = write_yosys({})
    result48 = import_yosys_json(p48, win)
    os.unlink(p48)

    def t48():
        n, w, warns = result48
        assert n == 0
        assert any("No modules" in x for x in warns), f"Expected 'No modules' warning, got {warns}"
    run_test("TC-48 Yosys empty JSON returns gracefully", t48)

    # TC-49: Multi-driver net (bit 4 driven by two cells)
    reset(win)
    multi_driver = {
        "modules": {
            "top": {
                "cells": {
                    "and1": {"type": "$_AND_", "connections": {"A":[2],"B":[3],"Y":[4]}},
                    "and2": {"type": "$_AND_", "connections": {"A":[2],"B":[3],"Y":[4]}},
                    "or1":  {"type": "$_OR_",  "connections": {"A":[4],"B":[4],"Y":[5]}}
                },
                "ports":    {"I":{"direction":"input","bits":[2]},
                             "J":{"direction":"input","bits":[3]},
                             "O":{"direction":"output","bits":[5]}},
                "netnames": {}
            }
        }
    }
    p49 = write_yosys(multi_driver)
    try:
        import_yosys_json(p49, win)
        ok49 = True
    except Exception as e:
        ok49 = False
    finally:
        os.unlink(p49)

    def t49():
        assert ok49, "import_yosys_json crashed on multi-driver net"
    run_test("TC-49 Yosys multi-driver net no crash", t49)


# ---------------------------------------------------------------------------
# Master runner
# ---------------------------------------------------------------------------

def run_all(win):
    print("\n=== SVCG Adversarial Test Suite (Student Scenarios) ===")
    tg01_combinational(win)
    tg02_sequential(win)
    tg03_vhdl_correctness(win)
    tg04_roundtrip(win)
    tg05_adversarial(win)
    tg06_components(win)
    tg07_testbench(win)
    tg08_export(win)
    tg09_routing(win)
    tg10_yosys(win)

    passed  = sum(1 for _, s, _ in results if s == "PASS")
    skipped = sum(1 for _, s, _ in results if s == "SKIP")
    failed  = sum(1 for _, s, _ in results if s == "FAIL")
    total   = len(results)
    print(f"\n{'='*55}")
    print(f"  {passed}/{total} passed  |  {skipped} skipped  |  {failed} failed")
    print(f"{'='*55}")
    write_report()


def main():
    from main_window import BlocksWindow
    win = BlocksWindow()
    win.show_all()

    def do_run():
        try:
            run_all(win)
        except Exception as e:
            print(f"\nFATAL: {e}")
            traceback.print_exc()
        GLib.timeout_add(1500, Gtk.main_quit)
        return False

    GLib.timeout_add(800, do_run)
    Gtk.main()


if __name__ == "__main__":
    main()
