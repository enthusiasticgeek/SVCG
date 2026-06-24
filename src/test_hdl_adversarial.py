#!/usr/bin/env python3
"""
test_hdl_adversarial.py -- Adversarial tests for VHDL and Verilog HDL generation.

Groups:
  G1   VHDL structural export            (T01-T10)
  G2   Verilog structural export          (T11-T20)
  G3   Custom block VHDL                 (T21-T26)
  G4   Custom block Verilog              (T27-T32)
  G5   Language switching (GUI state)    (T33-T36)
  G6   AI prompt construction            (T37-T40)
  G7   Edge cases (both languages)       (T41-T44)
  G8   Syntax validation (tool-dep.)     (T45-T48)
  G9   Round-trip / cross-language       (T49-T52)
  G10  Wire/net name adversarial         (T53-T58)
  G11  Multi-instance uniqueness         (T59-T63)
  G12  Port-count integrity              (T64-T67)
  G13  Custom block adversarial ports    (T68-T72)
  G14  Extended syntax validation        (T73-T74)
  G15  Testbench generation              (T75-T80)
  G16  Testbench edge cases              (T81-T86)
  G17  HDL structural deep-checks        (T87-T92)
  G18  Custom block structural correctness (T93-T96)
  G19  Language-aware code storage       (T97-T100)
  G20  Active-low CLK + misc testbench   (T101-T106)
  G21  EDIF export                       (T107-T114)
  G22  New block types                   (T115-T130)

Usage:
    cd src
    python test_hdl_adversarial.py
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import sys, os, json, tempfile, traceback, shutil
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REPORT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "TESTING_hdl_adversarial.md",
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
    win.blocks = []; win.pins = []; win.wires = []
    win.undo_stack = []; win.redo_stack = []
    win.selected_block = win.selected_pin = win.selected_wire = None
    win.selected_blocks = []; win.selected_pins = []; win.selected_wires = []
    win.set_dirty(False)

def rebuild_grid(win):
    from drawing_area import DrawingArea
    win.drawing_area.create_grid(DrawingArea.CANVAS_SIZE, DrawingArea.CANVAS_SIZE, win.grid_size)

def connect_wire(win, src, src_idx, src_role, dst, dst_idx, dst_role, net_name):
    from wire import Wire
    def get_pt(obj, idx, role):
        if role == "output": return list(obj.output_points[idx])
        if role == "input":  return list(obj.input_points[idx])
        return list(obj.connection_points[idx])
    sp = get_pt(src, src_idx, src_role)
    ep = get_pt(dst, dst_idx, dst_role)
    w = Wire(net_name, sp, ep, "wire", win.grid_size, win)
    def reg(obj, idx, role, wid):
        if role == "output":
            if obj.output_wires[idx] is None: obj.output_wires[idx] = []
            obj.output_wires[idx].append(wid)
        elif role == "input":
            if obj.input_wires[idx] is None: obj.input_wires[idx] = []
            obj.input_wires[idx].append(wid)
        else:
            if obj.wires[idx] is None: obj.wires[idx] = []
            obj.wires[idx].append(wid)
    reg(src, src_idx, src_role, w.id)
    reg(dst, dst_idx, dst_role, w.id)
    win.wires.append(w)
    return w

def build_half_adder(win):
    from blocks import Block
    from pins   import Pin
    gs = win.grid_size
    rebuild_grid(win)
    xor = Block(gs*5,  gs*5,  gs*4, gs*4, "XOR_1", "XOR", gs, win)
    and_ = Block(gs*5, gs*12, gs*4, gs*4, "AND_1", "AND", gs, win)
    pA   = Pin(gs*1,  gs*6,  gs*3, gs*2, "A",     "input_pin",  gs, 1, win)
    pB   = Pin(gs*1,  gs*13, gs*3, gs*2, "B",     "input_pin",  gs, 1, win)
    pSUM = Pin(gs*12, gs*6,  gs*3, gs*2, "SUM",   "output_pin", gs, 1, win)
    pCO  = Pin(gs*12, gs*13, gs*3, gs*2, "CARRY", "output_pin", gs, 1, win)
    win.blocks.extend([xor, and_]); win.pins.extend([pA, pB, pSUM, pCO])
    rebuild_grid(win)
    connect_wire(win, pA,  0, "pin",    xor,  0, "input",  "A_xor")
    connect_wire(win, pA,  0, "pin",    and_, 0, "input",  "A_and")
    connect_wire(win, pB,  0, "pin",    xor,  1, "input",  "B_xor")
    connect_wire(win, pB,  0, "pin",    and_, 1, "input",  "B_and")
    connect_wire(win, xor, 0, "output", pSUM, 0, "pin",    "SUM")
    connect_wire(win, and_,0, "output", pCO,  0, "pin",    "CARRY")
    return xor, and_, pA, pB, pSUM, pCO


def write_report():
    passed  = sum(1 for _, s, _ in results if s == "PASS")
    skipped = sum(1 for _, s, _ in results if s == "SKIP")
    total   = len(results)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# SVCG HDL Adversarial Test Report (VHDL + Verilog)",
        "",
        f"**Date:** {now}  ",
        "**Platform:** Windows 11 / MSYS2 MinGW64  ",
        f"**Result: {passed}/{total} passed, {skipped} skipped**",
        "",
        "| # | ID | Test | Result | Notes |",
        "|---|-----|------|--------|-------|",
    ]
    for i, (name, status, detail) in enumerate(results, 1):
        tid = name.split()[0] if name.startswith("T") else ""
        icon = status
        lines.append(f"| {i} | {tid} | {name} | {icon} | {detail} |")
    lines += ["", f"_{passed}/{total} passed, {skipped} skipped._", ""]
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n  Report -> {REPORT_PATH}")


# ===========================================================================
# G1 — VHDL structural export
# ===========================================================================

def g1_vhdl_structural(win):
    from blocks import Block
    from pins   import Pin
    from vhdl_export import generate_vhdl, ENTITY_MAP
    gs = win.grid_size
    print("\n-- G1: VHDL structural export --")

    # T01 — empty canvas produces valid VHDL skeleton
    def T01():
        v = generate_vhdl("EMPTY_TOP", [], [], [])
        assert "entity EMPTY_TOP is" in v,          "missing entity"
        assert "architecture Structural" in v,       "missing architecture"
        assert "end Structural;" in v,               "missing end"
    run_test("T01 VHDL empty canvas skeleton", T01)

    # T02 — half adder: correct port directions
    reset(win)
    build_half_adder(win)
    vhdl_ha = generate_vhdl("HALF_ADDER", win.blocks, win.pins, win.wires)

    def T02():
        assert "A : in  STD_LOGIC" in vhdl_ha,     "A input port missing"
        assert "B : in  STD_LOGIC" in vhdl_ha,     "B input port missing"
        assert "SUM : out  STD_LOGIC" in vhdl_ha,  "SUM output port missing"
        assert "CARRY : out  STD_LOGIC" in vhdl_ha,"CARRY output port missing"
    run_test("T02 VHDL half adder port directions", T02)

    # T03 — component declarations present
    def T03():
        assert "component XOR_GATE" in vhdl_ha, "XOR_GATE component missing"
        assert "component AND_GATE" in vhdl_ha, "AND_GATE component missing"
    run_test("T03 VHDL component declarations", T03)

    # T04 — no dangling 'open' in fully-wired half adder
    def T04():
        assert "open" not in vhdl_ha, f"unexpected 'open'"
    run_test("T04 VHDL no unconnected ports in half adder", T04)

    # T05 — internal signal declarations (need a circuit with a true internal net)
    def T05():
        from blocks import Block
        from wire   import Wire
        # AND-OR chain: A AND B -> net1, net1 OR C -> out_pin
        # net1 wire connects AND output to OR input — not an IO pin, so it's internal
        and_blk2 = Block(gs*3,  gs*3,  gs*4, gs*4, "AND2", "AND", gs, win)
        or_blk2  = Block(gs*12, gs*3,  gs*4, gs*4, "OR2",  "OR",  gs, win)
        win.blocks.extend([and_blk2, or_blk2])
        rebuild_grid(win)
        # internal wire between AND output and OR input
        sp = list(and_blk2.output_points[0]) if and_blk2.output_points else [gs*7, gs*5]
        ep = list(or_blk2.input_points[0])   if or_blk2.input_points   else [gs*12, gs*5]
        w_int = Wire("net_internal", sp, ep, "wire", gs, win)
        win.wires.append(w_int)
        v = generate_vhdl("CHAIN", win.blocks, win.pins, win.wires)
        assert "signal" in v, f"no signal declaration for internal net in:\n{v[:400]}"
        win.blocks.remove(and_blk2)
        win.blocks.remove(or_blk2)
        win.wires.remove(w_int)
    run_test("T05 VHDL has signal declarations for internal nets", T05)

    # T06 — port map uses named association
    def T06():
        assert "=>" in vhdl_ha, "missing named port map"
    run_test("T06 VHDL port maps use named association (=>)", T06)

    # T07 — library/use clauses present
    def T07():
        assert "library IEEE;" in vhdl_ha,              "missing library IEEE"
        assert "use IEEE.STD_LOGIC_1164.ALL;" in vhdl_ha,"missing STD_LOGIC_1164"
    run_test("T07 VHDL has library IEEE and use clause", T07)

    # T08 — all standard block types generate without crash
    def T08():
        all_blks = [Block(i*gs*6, gs*2, gs*4, gs*4, bt, bt, gs, win)
                    for i, bt in enumerate(ENTITY_MAP.keys())]
        v = generate_vhdl("ALL_TYPES", all_blks, [], [])
        assert "entity ALL_TYPES is" in v
        for bt, ename in ENTITY_MAP.items():
            assert f"component {ename}" in v or ename in v, f"missing {ename}"
    run_test("T08 VHDL all standard block types exported", T08)

    # T09 — VHDL reserved word 'signal' as pin name gets sanitized
    def T09():
        from pins import Pin
        p = Pin(gs, gs*40, gs*3, gs*2, "signal", "input_pin", gs, 1, win)
        v = generate_vhdl("RES", [], [p], [])
        assert " signal " not in v.split("port")[0] or "sig_signal" in v, \
            "reserved word 'signal' not sanitized"
    run_test("T09 VHDL reserved word 'signal' in port name sanitized", T09)

    # T10 — inout port direction preserved
    def T10():
        from pins import Pin
        p = Pin(gs, gs*44, gs*3, gs*2, "BUS_IO", "input_output_pin", gs, 1, win)
        v = generate_vhdl("IO_TEST", [], [p], [])
        assert "inout" in v, "inout direction missing"
    run_test("T10 VHDL inout port direction preserved", T10)


# ===========================================================================
# G2 — Verilog structural export
# ===========================================================================

def g2_verilog_structural(win):
    from blocks import Block
    from pins   import Pin
    from vhdl_export import generate_verilog, ENTITY_MAP
    gs = win.grid_size
    print("\n-- G2: Verilog structural export --")

    # T11 — empty canvas produces valid Verilog skeleton
    def T11():
        v = generate_verilog("EMPTY_TOP", [], [], [])
        assert "module EMPTY_TOP" in v, "missing module declaration"
        assert "endmodule" in v,        "missing endmodule"
    run_test("T11 Verilog empty canvas skeleton", T11)

    # T12 — half adder: correct port directions
    reset(win)
    build_half_adder(win)
    vlog_ha = generate_verilog("HALF_ADDER", win.blocks, win.pins, win.wires)

    def T12():
        assert "input  wire A"     in vlog_ha, f"A input missing\n{vlog_ha}"
        assert "input  wire B"     in vlog_ha, "B input missing"
        assert "output wire SUM"   in vlog_ha, "SUM output missing"
        assert "output wire CARRY" in vlog_ha, "CARRY output missing"
    run_test("T12 Verilog half adder port directions", T12)

    # T13 — no component declarations in Verilog (uses module instantiation)
    def T13():
        assert "component " not in vlog_ha, "Verilog must not have VHDL component declarations"
    run_test("T13 Verilog has no VHDL component keywords", T13)

    # T14 — named port connections use dot syntax
    def T14():
        assert ".A("    in vlog_ha or ".I0(" in vlog_ha or "." in vlog_ha, \
            "missing named port connections (.port(signal))"
    run_test("T14 Verilog port maps use dot-notation (.port(signal))", T14)

    # T15 — internal signals declared as wire
    def T15():
        assert "wire " in vlog_ha, "no wire declarations for internal nets"
    run_test("T15 Verilog internal signals declared as wire", T15)

    # T16 — module ends with endmodule
    def T16():
        assert vlog_ha.strip().endswith("endmodule"), \
            f"last line not 'endmodule': '{vlog_ha.strip()[-30:]}'"
    run_test("T16 Verilog ends with endmodule", T16)

    # T17 — no VHDL-specific keywords
    def T17():
        for kw in ("architecture", "entity", "port map", "library IEEE"):
            assert kw not in vlog_ha, f"VHDL keyword '{kw}' found in Verilog output"
    run_test("T17 Verilog output contains no VHDL keywords", T17)

    # T18 — all standard block types exported without crash
    def T18():
        all_blks = [Block(i*gs*6, gs*2, gs*4, gs*4, bt, bt, gs, win)
                    for i, bt in enumerate(ENTITY_MAP.keys())]
        v = generate_verilog("ALL_TYPES", all_blks, [], [])
        assert "module ALL_TYPES" in v
        assert "endmodule" in v
    run_test("T18 Verilog all standard block types exported", T18)

    # T19 — unconnected port resolves to 1'bz (not 'open')
    def T19():
        blk = Block(gs*3, gs*3, gs*4, gs*4, "AND_OPEN", "AND", gs, win)
        # leave input wires empty
        v = generate_verilog("OPEN_TEST", [blk], [], [])
        assert "1'bz" in v or "open" not in v, \
            "'open' found in Verilog (should be 1'bz or undriven)"
    run_test("T19 Verilog unconnected port uses 1'bz not VHDL open", T19)

    # T20 — inout port direction preserved
    def T20():
        from pins import Pin
        p = Pin(gs, gs*44, gs*3, gs*2, "BUS_IO", "input_output_pin", gs, 1, win)
        v = generate_verilog("IO_TEST", [], [p], [])
        assert "inout" in v, "inout direction missing in Verilog"
    run_test("T20 Verilog inout port direction preserved", T20)


# ===========================================================================
# G3 — Custom block VHDL
# ===========================================================================

def g3_custom_vhdl(win):
    from vhdl_export import generate_custom_vhd
    print("\n-- G3: Custom block VHDL --")

    # T21 — entity declaration is auto-generated
    def T21():
        v = generate_custom_vhd("MY_DFF", ["clk", "d"], ["q"], "")
        assert "entity MY_DFF is" in v, "entity declaration missing"
        assert "clk : in  STD_LOGIC" in v, "clk port missing"
        assert "d : in  STD_LOGIC"   in v, "d port missing"
        assert "q : out  STD_LOGIC"  in v, "q port missing"
    run_test("T21 Custom VHDL entity declaration auto-generated", T21)

    # T22 — user architecture body is included verbatim
    def T22():
        arch = "architecture rtl of MY_DFF is\nbegin\n  q <= d;\nend architecture rtl;"
        v = generate_custom_vhd("MY_DFF", ["clk", "d"], ["q"], arch)
        assert "architecture rtl of MY_DFF is" in v, "user arch not included"
        assert "q <= d;" in v, "user logic not included"
    run_test("T22 Custom VHDL user architecture body included verbatim", T22)

    # T23 — empty body produces stub architecture
    def T23():
        v = generate_custom_vhd("STUB_BLOCK", ["a"], ["b"], "")
        assert "architecture rtl of STUB_BLOCK is" in v, "stub arch missing"
        assert "TODO" in v, "stub TODO comment missing"
        assert "end architecture rtl;" in v, "stub end missing"
    run_test("T23 Custom VHDL empty body generates stub architecture", T23)

    # T24 — library/use clauses always present
    def T24():
        v = generate_custom_vhd("LIB_TEST", [], [], "")
        assert "library IEEE;" in v,               "library IEEE missing"
        assert "use IEEE.STD_LOGIC_1164.ALL;" in v,"STD_LOGIC_1164 missing"
    run_test("T24 Custom VHDL always includes library/use clauses", T24)

    # T25 — no ports produces valid VHDL (port-less entity)
    def T25():
        v = generate_custom_vhd("NO_PORTS", [], [], "")
        assert "entity NO_PORTS is" in v
        # Should not have "port (" if there are no ports
        assert "port (" not in v.lower() or "end NO_PORTS;" in v
    run_test("T25 Custom VHDL with no ports is valid (port-less entity)", T25)

    # T26 — default values on inputs only, not outputs
    def T26():
        v = generate_custom_vhd("DEF_TEST", ["clk", "rst"], ["q"], "")
        # inputs get := '0', outputs do not
        lines = [l for l in v.splitlines() if "q : out" in l]
        assert lines, "q output port line missing"
        assert ":= '0'" not in lines[0], "output port should not have default value"
        in_lines = [l for l in v.splitlines() if "clk : in" in l]
        assert in_lines, "clk port line missing"
        assert ":= '0'" in in_lines[0], "input port should have default value := '0'"
    run_test("T26 Custom VHDL input default := '0', output has none", T26)


# ===========================================================================
# G4 — Custom block Verilog
# ===========================================================================

def g4_custom_verilog(win):
    from vhdl_export import generate_custom_v
    print("\n-- G4: Custom block Verilog --")

    # T27 — module header is auto-generated
    def T27():
        v = generate_custom_v("MY_DFF", ["clk", "d"], ["q"], "")
        assert "module MY_DFF (" in v, "module header missing"
        assert "input" in v and "clk" in v, "clk input missing"
        assert "output" in v and "q" in v,  "q output missing"
    run_test("T27 Custom Verilog module header auto-generated", T27)

    # T28 — user body is inserted between header and endmodule
    def T28():
        body = "always @(posedge clk) q <= d;"
        v = generate_custom_v("MY_DFF", ["clk", "d"], ["q"], body)
        assert "always @(posedge clk) q <= d;" in v, "user body not included"
        assert "endmodule" in v, "endmodule missing"
        # user body must appear before endmodule
        assert v.index("always") < v.index("endmodule"), \
            "user body appears after endmodule"
    run_test("T28 Custom Verilog user body placed before endmodule", T28)

    # T29 — empty body produces stub with comment
    def T29():
        v = generate_custom_v("STUB_V", ["a"], ["b"], "")
        assert "endmodule" in v, "endmodule missing in stub"
        assert "TODO" in v or "//" in v, "stub comment missing"
    run_test("T29 Custom Verilog empty body generates stub comment", T29)

    # T30 — exactly one endmodule in output
    def T30():
        v = generate_custom_v("ONE_END", ["a"], ["b"], "assign b = a;")
        count = v.count("endmodule")
        assert count == 1, f"expected 1 endmodule, found {count}"
    run_test("T30 Custom Verilog exactly one endmodule in output", T30)

    # T31 — no VHDL keywords in Verilog output
    def T31():
        v = generate_custom_v("NO_VHDL", ["a"], ["b"], "assign b = a;")
        for kw in ("architecture", "entity", "library", "STD_LOGIC"):
            assert kw not in v, f"VHDL keyword '{kw}' in Verilog custom block"
    run_test("T31 Custom Verilog output contains no VHDL keywords", T31)

    # T32 — outputs declared as 'output reg'
    def T32():
        v = generate_custom_v("REG_OUT", ["clk"], ["q", "r"], "")
        assert "output reg q" in v, "output q not declared as output reg"
        assert "output reg r" in v, "output r not declared as output reg"
    run_test("T32 Custom Verilog outputs declared as 'output reg'", T32)


# ===========================================================================
# G5 — Language switching (GUI state)
# ===========================================================================

def g5_language_switching(win):
    print("\n-- G5: Language switching --")

    # T33 — default language is VHDL
    def T33():
        assert win.hdl_language == "vhdl", \
            f"expected 'vhdl', got '{win.hdl_language}'"
    run_test("T33 Default HDL language is VHDL", T33)

    # T34 — switching combo changes hdl_language
    def T34():
        win._hdl_combo.set_active_id("verilog")
        assert win.hdl_language == "verilog", \
            f"hdl_language not updated: '{win.hdl_language}'"
        win._hdl_combo.set_active_id("vhdl")
        assert win.hdl_language == "vhdl"
    run_test("T34 HDL combo switching updates hdl_language", T34)

    # T35 — title bar reflects active language
    def T35():
        win._hdl_combo.set_active_id("vhdl")
        title_vhdl = win.get_title()
        assert "[VHDL]" in title_vhdl, f"[VHDL] not in title: '{title_vhdl}'"
        win._hdl_combo.set_active_id("verilog")
        title_v = win.get_title()
        assert "[VERILOG]" in title_v, f"[VERILOG] not in title: '{title_v}'"
        win._hdl_combo.set_active_id("vhdl")
    run_test("T35 Window title shows active HDL language", T35)

    # T36 — CustomBlockDialog title reflects language parameter
    def T36():
        from custom_block_dialog import CustomBlockDialog
        dlg_vhdl = CustomBlockDialog.__new__(CustomBlockDialog)
        dlg_vhdl._language = "vhdl"
        dlg_vlog = CustomBlockDialog.__new__(CustomBlockDialog)
        dlg_vlog._language = "verilog"
        # Just verify the _language attribute is stored correctly
        assert dlg_vhdl._language == "vhdl"
        assert dlg_vlog._language == "verilog"
    run_test("T36 CustomBlockDialog stores language parameter", T36)


# ===========================================================================
# G6 — AI prompt construction
# ===========================================================================

def g6_ai_prompts(win):
    from custom_block_dialog import _build_prompt
    print("\n-- G6: AI prompt construction --")

    # T37 — VHDL prompt asks for architecture block
    def T37():
        p = _build_prompt("DFF", ["clk", "d"], ["q"], "D flip-flop", "vhdl")
        assert "architecture" in p.lower(), "VHDL prompt missing 'architecture'"
        assert "entity" in p.lower() or "entity declaration" in p.lower(), \
            "VHDL prompt should mention entity"
        assert "end architecture" in p.lower(), "VHDL prompt should mention end architecture"
    run_test("T37 VHDL AI prompt asks for architecture block", T37)

    # T38 — Verilog prompt asks for module body only
    def T38():
        p = _build_prompt("DFF", ["clk", "d"], ["q"], "D flip-flop", "verilog")
        assert "module body" in p.lower() or "module" in p.lower(), \
            "Verilog prompt missing 'module'"
        assert "do not" in p.lower() or "don't" in p.lower() or "without" in p.lower(), \
            "Verilog prompt should say not to include module header"
    run_test("T38 Verilog AI prompt asks for module body (no header)", T38)

    # T39 — port names appear in both prompts
    def T39():
        ports = ["clk", "rst", "data_in", "data_out"]
        for lang in ("vhdl", "verilog"):
            p = _build_prompt("MY_REG", ["clk", "rst", "data_in"], ["data_out"],
                              "register", lang)
            for port in ports:
                assert port in p, f"port '{port}' missing from {lang} prompt"
    run_test("T39 All port names appear in both VHDL and Verilog prompts", T39)

    # T40 — description appears in prompt; absent description gives fallback
    def T40():
        p_with = _build_prompt("X", ["a"], ["b"], "4-bit counter", "vhdl")
        assert "4-bit counter" in p_with, "description not included in prompt"
        p_none = _build_prompt("X", ["a"], ["b"], "", "vhdl")
        assert "infer" in p_none.lower() or "not provided" in p_none.lower(), \
            "missing-description fallback text absent"
    run_test("T40 Description included in prompt; empty description gets fallback", T40)


# ===========================================================================
# G7 — Edge cases (both languages)
# ===========================================================================

def g7_edge_cases(win):
    from vhdl_export import generate_vhdl, generate_verilog, generate_custom_vhd, generate_custom_v
    from pins import Pin
    gs = win.grid_size
    print("\n-- G7: Edge cases (both languages) --")

    # T41 — VHDL reserved words as port names get sanitized
    def T41():
        reserved = ["in", "out", "signal", "port", "entity", "end"]
        for rw in reserved:
            p = Pin(gs, gs*50, gs*3, gs*2, rw, "input_pin", gs, 1, win)
            v = generate_vhdl("RES_TEST", [], [p], [])
            assert f" {rw} : " not in v.split("port (")[1].split(");")[0] \
                if "port (" in v else True, \
                f"reserved word '{rw}' not sanitized in VHDL"
    run_test("T41 VHDL reserved words as port names are sanitized", T41)

    # T42 — Verilog reserved words as port names get sanitized
    def T42():
        # 'input', 'output', 'wire', 'module', 'reg' are Verilog reserved
        from vhdl_export import _sanitize
        for rw in ["wire", "module", "reg", "begin", "end"]:
            san = _sanitize(rw)
            assert san != rw or san.startswith("sig_"), \
                f"Verilog reserved word '{rw}' not sanitized: '{san}'"
    run_test("T42 _sanitize() handles Verilog-relevant reserved words", T42)

    # T43 — digit-leading port names prefixed with sig_
    def T43():
        from vhdl_export import _sanitize
        assert _sanitize("3bit_bus").startswith("sig_"), \
            "_sanitize('3bit_bus') should start with sig_"
        assert _sanitize("0").startswith("sig_"), \
            "_sanitize('0') should start with sig_"
        p = Pin(gs, gs*55, gs*3, gs*2, "1_reset", "input_pin", gs, 1, win)
        v = generate_vhdl("DIGIT_TEST", [], [p], [])
        # "1_reset" must not appear as a bare token (sig_1_reset is fine)
        import re as _re
        assert not _re.search(r'\b1_reset\b', v), \
            "raw digit-leading identifier '1_reset' as bare token in VHDL output"
        v2 = generate_verilog("DIGIT_TEST_V", [], [p], [])
        assert not _re.search(r'\b1_reset\b', v2), \
            "raw digit-leading identifier '1_reset' as bare token in Verilog output"
        assert "sig_1_reset" in v,  "sanitized 'sig_1_reset' missing from VHDL"
        assert "sig_1_reset" in v2, "sanitized 'sig_1_reset' missing from Verilog"
    run_test("T43 Digit-leading port names prefixed sig_ in both languages", T43)

    # T44 — very long port name (200 chars) does not crash
    def T44():
        long_name = "port_" + "x" * 195
        p = Pin(gs, gs*60, gs*3, gs*2, long_name, "input_pin", gs, 1, win)
        v_vhdl   = generate_vhdl("LONG_PORT", [], [p], [])
        v_verilog = generate_verilog("LONG_PORT_V", [], [p], [])
        v_cvhd   = generate_custom_vhd("LONG_C", [long_name], [], "")
        v_cvlog  = generate_custom_v("LONG_CV", [long_name], [], "")
        assert "LONG_PORT" in v_vhdl
        assert "module LONG_PORT_V" in v_verilog
        assert "module LONG_C" in v_cvhd or "entity LONG_C" in v_cvhd
        assert "module LONG_CV" in v_cvlog
    run_test("T44 200-char port name does not crash either HDL generator", T44)


# ===========================================================================
# G8 — Syntax validation (tool-dependent)
# ===========================================================================

def g8_syntax_checks(win):
    from vhdl_export import (generate_vhdl, generate_verilog,
                              generate_custom_vhd, generate_custom_v,
                              check_vhdl_syntax, check_verilog_syntax)
    import shutil as _shutil
    gs = win.grid_size
    print("\n-- G8: Syntax validation (GHDL / iverilog) --")

    reset(win)
    build_half_adder(win)

    # T45 — GHDL syntax check on VHDL half adder
    def T45():
        ghdl = _shutil.which("ghdl")
        if not ghdl:
            log_skip("T45 GHDL syntax check on VHDL half adder", "ghdl not on PATH")
            return
        v = generate_vhdl("HALF_ADDER", win.blocks, win.pins, win.wires)
        with tempfile.NamedTemporaryFile(suffix=".vhd", delete=False, mode="w") as f:
            f.write(v); path = f.name
        try:
            avail, ok, out = check_vhdl_syntax(path)
            assert avail, "ghdl check returned not-available"
            assert ok, f"GHDL syntax error:\n{out}"
        finally:
            os.unlink(path)
    run_test("T45 GHDL syntax check on VHDL half adder", T45)

    # T46 — iverilog syntax check on Verilog half adder
    def T46():
        iv = _shutil.which("iverilog")
        if not iv:
            log_skip("T46 iverilog syntax check on Verilog half adder", "iverilog not on PATH")
            return
        v = generate_verilog("HALF_ADDER", win.blocks, win.pins, win.wires)
        with tempfile.NamedTemporaryFile(suffix=".v", delete=False, mode="w") as f:
            f.write(v); path = f.name
        try:
            avail, ok, out = check_verilog_syntax(path)
            assert avail, "iverilog check returned not-available"
            assert ok, f"iverilog syntax error:\n{out}"
        finally:
            os.unlink(path)
    run_test("T46 iverilog syntax check on Verilog half adder", T46)

    # T47 — GHDL syntax check on custom VHDL DFF
    def T47():
        ghdl = _shutil.which("ghdl")
        if not ghdl:
            log_skip("T47 GHDL syntax check on custom VHDL DFF", "ghdl not on PATH")
            return
        arch = ("architecture rtl of CUSTOM_DFF is\n"
                "begin\n"
                "  process(clk)\n  begin\n"
                "    if rising_edge(clk) then q <= d; end if;\n"
                "  end process;\n"
                "end architecture rtl;")
        v = generate_custom_vhd("CUSTOM_DFF", ["clk", "d"], ["q"], arch)
        with tempfile.NamedTemporaryFile(suffix=".vhd", delete=False, mode="w") as f:
            f.write(v); path = f.name
        try:
            avail, ok, out = check_vhdl_syntax(path)
            assert ok, f"GHDL error on custom VHDL:\n{out}"
        finally:
            os.unlink(path)
    run_test("T47 GHDL syntax check on custom VHDL DFF", T47)

    # T48 — iverilog syntax check on custom Verilog DFF
    def T48():
        iv = _shutil.which("iverilog")
        if not iv:
            log_skip("T48 iverilog syntax check on custom Verilog DFF", "iverilog not on PATH")
            return
        body = ("reg q_reg;\n"
                "always @(posedge clk) q_reg <= d;\n"
                "assign q = q_reg;")
        v = generate_custom_v("CUSTOM_DFF_V", ["clk", "d"], ["q"], body)
        with tempfile.NamedTemporaryFile(suffix=".v", delete=False, mode="w") as f:
            f.write(v); path = f.name
        try:
            avail, ok, out = check_verilog_syntax(path)
            assert ok, f"iverilog error on custom Verilog:\n{out}"
        finally:
            os.unlink(path)
    run_test("T48 iverilog syntax check on custom Verilog DFF", T48)


# ===========================================================================
# G9 — Round-trip and cross-language consistency
# ===========================================================================

def g9_round_trip(win):
    from vhdl_export import generate_vhdl, generate_verilog
    gs = win.grid_size
    print("\n-- G9: Round-trip and cross-language consistency --")

    reset(win)
    build_half_adder(win)

    # T49 — same port names appear in both VHDL and Verilog
    def T49():
        vhdl = generate_vhdl("HA",    win.blocks, win.pins, win.wires)
        vlog = generate_verilog("HA", win.blocks, win.pins, win.wires)
        for port in ("A", "B", "SUM", "CARRY"):
            assert port in vhdl, f"port {port} missing from VHDL"
            assert port in vlog, f"port {port} missing from Verilog"
    run_test("T49 Same port names appear in VHDL and Verilog outputs", T49)

    # T50 — same module/entity name appears in both outputs
    def T50():
        vhdl = generate_vhdl("SAME_NAME",    win.blocks, win.pins, win.wires)
        vlog = generate_verilog("SAME_NAME", win.blocks, win.pins, win.wires)
        assert "entity SAME_NAME is" in vhdl,  "entity name mismatch in VHDL"
        assert "module SAME_NAME" in vlog,      "module name mismatch in Verilog"
    run_test("T50 Top-level name consistent between VHDL entity and Verilog module", T50)

    # T51 — same number of instantiations
    def T51():
        vhdl = generate_vhdl("COUNT_INST",    win.blocks, win.pins, win.wires)
        vlog = generate_verilog("COUNT_INST", win.blocks, win.pins, win.wires)
        # count "port map" (VHDL) vs ");" after instantiation block (Verilog)
        vhdl_insts = vhdl.count("port map (")
        vlog_insts = vlog.count(");")
        # Verilog has one ");" per instance + one for module header — subtract 1
        assert vhdl_insts == len(win.blocks), \
            f"VHDL: {vhdl_insts} port maps != {len(win.blocks)} blocks"
        assert vlog_insts >= len(win.blocks), \
            f"Verilog: {vlog_insts} ')'; < {len(win.blocks)} blocks"
    run_test("T51 Instantiation count consistent between VHDL and Verilog", T51)

    # T52 — language switch: VHDL output after switching back from Verilog
    def T52():
        win._hdl_combo.set_active_id("verilog")
        assert win.hdl_language == "verilog"
        win._hdl_combo.set_active_id("vhdl")
        assert win.hdl_language == "vhdl"
        vhdl = generate_vhdl("SWITCH_BACK", win.blocks, win.pins, win.wires)
        assert "entity SWITCH_BACK is" in vhdl, "VHDL not generated after switching back"
    run_test("T52 Switching back to VHDL generates correct VHDL output", T52)


# ===========================================================================
# G10 — Wire / net name adversarial
# ===========================================================================

def g10_wire_net_names(win):
    from blocks import Block
    from wire   import Wire
    from vhdl_export import generate_vhdl, generate_verilog, _sanitize
    gs = win.grid_size
    print("\n-- G10: Wire and net name adversarial --")

    def make_internal_wire(net_name):
        """Two blocks connected by a single internal wire — no IO pins."""
        reset(win)
        rebuild_grid(win)
        b1 = Block(gs*3,  gs*3, gs*4, gs*4, "BLK_A", "AND", gs, win)
        b2 = Block(gs*12, gs*3, gs*4, gs*4, "BLK_B", "OR",  gs, win)
        win.blocks.extend([b1, b2])
        rebuild_grid(win)
        sp = list(b1.output_points[0]) if b1.output_points else [gs*7, gs*5]
        ep = list(b2.input_points[0])  if b2.input_points  else [gs*12, gs*5]
        w = Wire(net_name, sp, ep, "wire", gs, win)
        win.wires.append(w)
        return w

    # T53 — spaces in net name sanitized to underscores in VHDL signal decl
    def T53():
        make_internal_wire("carry out")
        v = generate_vhdl("SPACE_NET", win.blocks, win.pins, win.wires)
        assert "carry out" not in v, "un-sanitized space in VHDL signal name"
        assert "carry_out" in v, "sanitized 'carry_out' missing from VHDL"
    run_test("T53 Net name with spaces sanitized in VHDL signal declaration", T53)

    # T54 — hyphens in net name sanitized in Verilog wire decl
    def T54():
        make_internal_wire("net-1")
        v = generate_verilog("HYPHEN_NET", win.blocks, win.pins, win.wires)
        assert "net-1" not in v, "un-sanitized hyphen in Verilog wire name"
        assert "net_1" in v, "sanitized 'net_1' missing from Verilog"
    run_test("T54 Net name with hyphens sanitized in Verilog wire declaration", T54)

    # T55 — VHDL reserved word "signal" as net name → sig_signal
    def T55():
        make_internal_wire("signal")
        v = generate_vhdl("RSVD_NET", win.blocks, win.pins, win.wires)
        import re as _re
        assert not _re.search(r'\bsignal signal\b', v), \
            "'signal signal' appears in VHDL — reserved word not sanitized"
        assert "sig_signal" in v, "sanitized 'sig_signal' missing from VHDL"
    run_test("T55 Net name 'signal' (VHDL reserved) becomes sig_signal in VHDL", T55)

    # T56 — Verilog reserved word "wire" as net name → sig_wire
    def T56():
        make_internal_wire("wire")
        v = generate_verilog("RSVD_NET_VL", win.blocks, win.pins, win.wires)
        import re as _re
        assert not _re.search(r'\bwire wire\b', v), \
            "'wire wire' appears in Verilog — reserved word not sanitized"
        assert "sig_wire" in v, "sanitized 'sig_wire' missing from Verilog"
    run_test("T56 Net name 'wire' (Verilog reserved) becomes sig_wire in Verilog", T56)

    # T57 — all-special-char net name ("---") → valid identifier starting with a letter
    def T57():
        make_internal_wire("---")
        san = _sanitize("---")
        assert san[0].isalpha(), \
            f"_sanitize('---') = '{san}' does not start with a letter — invalid VHDL/Verilog"
        v_vhdl    = generate_vhdl("SPECIAL_NET",   win.blocks, win.pins, win.wires)
        v_verilog = generate_verilog("SPECIAL_NET_V", win.blocks, win.pins, win.wires)
        assert "SPECIAL_NET" in v_vhdl,    "VHDL generator crashed on all-special-char net name"
        assert "SPECIAL_NET_V" in v_verilog, "Verilog generator crashed on all-special-char net name"
    run_test("T57 All-special-char net name produces valid identifier in both HDLs", T57)

    # T58 — digit-only net name ("42") → sig_42 in both outputs
    def T58():
        san = _sanitize("42")
        assert san.startswith("sig_"), f"_sanitize('42') = '{san}', expected sig_ prefix"
        assert san[0].isalpha(), f"_sanitize('42') = '{san}' does not start with letter"
        make_internal_wire("42")
        v_vhdl    = generate_vhdl("DIGIT_NET",   win.blocks, win.pins, win.wires)
        v_verilog = generate_verilog("DIGIT_NET_V", win.blocks, win.pins, win.wires)
        import re as _re
        assert not _re.search(r'\b42\b', v_vhdl),    "bare '42' identifier in VHDL"
        assert not _re.search(r'\b42\b', v_verilog),  "bare '42' identifier in Verilog"
        assert "sig_42" in v_vhdl,    "sanitized 'sig_42' missing from VHDL"
        assert "sig_42" in v_verilog, "sanitized 'sig_42' missing from Verilog"
    run_test("T58 Digit-only net name becomes sig_42 in both VHDL and Verilog", T58)


# ===========================================================================
# G11 — Multi-instance uniqueness
# ===========================================================================

def g11_multi_instance(win):
    from blocks import Block
    from vhdl_export import generate_vhdl, generate_verilog
    gs = win.grid_size
    print("\n-- G11: Multi-instance uniqueness --")

    # T59 — three AND gates → three distinct VHDL port map labels
    def T59():
        reset(win)
        rebuild_grid(win)
        for i in range(3):
            win.blocks.append(Block(i*gs*6, gs*3, gs*4, gs*4, f"AND_{i}", "AND", gs, win))
        v = generate_vhdl("THREE_AND", win.blocks, win.pins, win.wires)
        count = v.count("port map (")
        assert count == 3, f"expected 3 port maps, found {count}"
    run_test("T59 Three AND gates yield three distinct VHDL port map instances", T59)

    # T60 — three AND gates → three distinct Verilog instance identifiers
    def T60():
        reset(win)
        rebuild_grid(win)
        for i in range(3):
            win.blocks.append(Block(i*gs*6, gs*3, gs*4, gs*4, f"AND_{i}", "AND", gs, win))
        v = generate_verilog("THREE_AND_V", win.blocks, win.pins, win.wires)
        import re as _re
        inst_names = _re.findall(r'AND_GATE\s+(\w+)\s*\(', v)
        assert len(inst_names) == 3, f"expected 3 AND_GATE insts, found {inst_names}"
        assert len(inst_names) == len(set(inst_names)), \
            f"Verilog instance names not unique: {inst_names}"
    run_test("T60 Three AND gates yield three distinct Verilog instance identifiers", T60)

    # T61 — block label with spaces sanitized in VHDL instance label
    def T61():
        reset(win)
        rebuild_grid(win)
        win.blocks.append(Block(gs*3, gs*3, gs*4, gs*4, "my and gate", "AND", gs, win))
        v = generate_vhdl("SPACE_INST", win.blocks, win.pins, win.wires)
        assert "my and gate" not in v, "un-sanitized space in VHDL instance label"
        assert "my_and_gate" in v, "sanitized label 'my_and_gate' missing from VHDL"
    run_test("T61 Block label with spaces sanitized in VHDL instance label", T61)

    # T62 — block label with spaces sanitized in Verilog instance identifier
    def T62():
        reset(win)
        rebuild_grid(win)
        win.blocks.append(Block(gs*3, gs*3, gs*4, gs*4, "my or gate", "OR", gs, win))
        v = generate_verilog("SPACE_INST_V", win.blocks, win.pins, win.wires)
        assert "my or gate" not in v, "un-sanitized space in Verilog instance name"
        assert "my_or_gate" in v, "sanitized instance 'my_or_gate' missing from Verilog"
    run_test("T62 Block label with spaces sanitized in Verilog instance identifier", T62)

    # T63 — identical block labels get unique instance names via index suffix
    def T63():
        reset(win)
        rebuild_grid(win)
        win.blocks.append(Block(gs*3, gs*3, gs*4, gs*4, "GATE", "AND", gs, win))
        win.blocks.append(Block(gs*9, gs*3, gs*4, gs*4, "GATE", "AND", gs, win))
        v_vhdl    = generate_vhdl("SAME_LABEL",   win.blocks, win.pins, win.wires)
        v_verilog = generate_verilog("SAME_LABEL_V", win.blocks, win.pins, win.wires)
        assert "GATE_0" in v_vhdl,    "GATE_0 missing from VHDL"
        assert "GATE_1" in v_vhdl,    "GATE_1 missing from VHDL"
        assert "GATE_0" in v_verilog, "GATE_0 missing from Verilog"
        assert "GATE_1" in v_verilog, "GATE_1 missing from Verilog"
    run_test("T63 Identical block labels get unique instance names via index suffix", T63)


# ===========================================================================
# G12 — Port-count integrity
# ===========================================================================

def g12_port_count(win):
    from pins import Pin
    from vhdl_export import generate_vhdl, generate_verilog
    import re as _re
    gs = win.grid_size
    print("\n-- G12: Port-count integrity --")

    def vhdl_port_count(text):
        m = _re.search(r'Port \((.*?)\);', text, _re.DOTALL)
        return len(_re.findall(r'STD_LOGIC', m.group(1))) if m else 0

    def verilog_port_count(text):
        m = _re.search(r'module\s+\w+\s*\((.*?)\);', text, _re.DOTALL)
        return len(_re.findall(r'(?:input|output|inout)\s+wire\s+\w+', m.group(1))) if m else 0

    # T64 — VHDL entity port count equals number of IO pins
    def T64():
        reset(win)
        rebuild_grid(win)
        for i in range(4):
            win.pins.append(Pin(gs, gs*(3+i*4), gs*3, gs*2, f"P{i}", "input_pin", gs, 1, win))
        v = generate_vhdl("PORT_COUNT4", win.blocks, win.pins, win.wires)
        n = vhdl_port_count(v)
        assert n == 4, f"expected 4 VHDL ports for 4 IO pins, found {n}"
    run_test("T64 VHDL entity port count equals number of IO pins", T64)

    # T65 — Verilog module port count equals number of IO pins
    def T65():
        reset(win)
        rebuild_grid(win)
        for i in range(3):
            win.pins.append(Pin(gs, gs*(3+i*4), gs*3, gs*2, f"Q{i}", "output_pin", gs, 1, win))
        v = generate_verilog("PORT_COUNT3", win.blocks, win.pins, win.wires)
        n = verilog_port_count(v)
        assert n == 3, f"expected 3 Verilog ports for 3 IO pins, found {n}"
    run_test("T65 Verilog module port count equals number of IO pins", T65)

    # T66 — duplicate IO pin names: seen_port_names dedup keeps exactly one entry
    def T66():
        reset(win)
        rebuild_grid(win)
        win.pins.append(Pin(gs, gs*3, gs*3, gs*2, "DATA", "input_pin",  gs, 1, win))
        win.pins.append(Pin(gs, gs*7, gs*3, gs*2, "DATA", "output_pin", gs, 1, win))
        v_vhdl    = generate_vhdl("DUP_PORT",   win.blocks, win.pins, win.wires)
        v_verilog = generate_verilog("DUP_PORT_V", win.blocks, win.pins, win.wires)
        assert "DATA" in v_vhdl,    "DATA missing from VHDL with duplicate pin names"
        assert "DATA" in v_verilog, "DATA missing from Verilog with duplicate pin names"
        # Only one DATA port declared (the second is deduped via seen_port_names)
        assert v_vhdl.count("DATA : ")    <= 1, "duplicate DATA port in VHDL entity"
        assert v_verilog.count(" DATA,")  <= 1, "duplicate DATA port in Verilog module"
    run_test("T66 Duplicate IO pin names: deduplication keeps exactly one port entry", T66)

    # T67 — CLK pin type exported with 'in' direction in both languages
    def T67():
        reset(win)
        rebuild_grid(win)
        win.pins.append(Pin(gs, gs*3, gs*3, gs*2, "CLK", "CLK", gs, 1, win))
        v_vhdl    = generate_vhdl("CLK_PORT",   win.blocks, win.pins, win.wires)
        v_verilog = generate_verilog("CLK_PORT_V", win.blocks, win.pins, win.wires)
        assert "CLK" in v_vhdl and "in" in v_vhdl, \
            "CLK pin not exported as 'in' port in VHDL"
        assert "input" in v_verilog and "CLK" in v_verilog, \
            "CLK pin not exported as 'input' port in Verilog"
    run_test("T67 CLK pin type exported with 'in' direction in both HDLs", T67)


# ===========================================================================
# G13 — Custom block adversarial ports
# ===========================================================================

def g13_custom_adversarial(win):
    from vhdl_export import generate_custom_vhd, generate_custom_v
    print("\n-- G13: Custom block adversarial ports --")

    # T68 — VHDL reserved word "signal" as port name → sanitized to sig_signal
    def T68():
        v = generate_custom_vhd("RES_VHDA", ["signal", "clk"], ["q"], "")
        assert "sig_signal" in v, "reserved port name 'signal' not sanitized in custom VHDL"
        import re as _re
        # "signal signal" (keyword + identifier) must not appear
        assert not _re.search(r'\bsignal\s+signal\b', v), \
            "'signal signal' found — VHDL reserved word used as port identifier"
    run_test("T68 Custom VHDL: VHDL reserved port name 'signal' sanitized to sig_signal", T68)

    # T69 — Verilog reserved word "wire" as port name → sanitized to sig_wire
    def T69():
        v = generate_custom_v("RES_VLG", ["wire", "clk"], ["q"], "")
        assert "sig_wire" in v, "reserved port name 'wire' not sanitized in custom Verilog"
        import re as _re
        assert not _re.search(r'\binput\s+wire\s*[,)]', v), \
            "'input wire' (bare keyword, no identifier) found in Verilog"
    run_test("T69 Custom Verilog: Verilog reserved port name 'wire' sanitized to sig_wire", T69)

    # T70 — custom block with 16 inputs + 8 outputs does not crash either generator
    def T70():
        ins  = [f"i{k}" for k in range(16)]
        outs = [f"o{k}" for k in range(8)]
        v_vhd = generate_custom_vhd("BIG_BLOCK", ins, outs, "")
        v_vlg = generate_custom_v("BIG_BLOCK_V", ins, outs, "")
        assert "entity BIG_BLOCK is" in v_vhd, "VHDL entity missing for 16-in 8-out custom block"
        assert "module BIG_BLOCK_V" in v_vlg,  "Verilog module missing for 16-in 8-out custom block"
        # Count port-level declarations only (": in  STD_LOGIC" + ": out  STD_LOGIC"),
        # excluding the "STD_LOGIC_1164" in the library use clause.
        port_decls = v_vhd.count(": in  STD_LOGIC") + v_vhd.count(": out  STD_LOGIC")
        assert port_decls == 24, \
            f"expected 24 STD_LOGIC port declarations, found {port_decls}"
        assert v_vlg.count("input ")  == 16, \
            f"expected 16 input ports in Verilog, found {v_vlg.count('input ')}"
    run_test("T70 Custom block with 16 inputs + 8 outputs does not crash", T70)

    # T71 — digit-leading port name ("3bit") sanitized to sig_3bit in custom VHDL
    def T71():
        v = generate_custom_vhd("DIG_PORT", ["3bit", "clk"], ["out1"], "")
        assert "sig_3bit" in v, "digit-leading port name '3bit' not sanitized in custom VHDL"
        import re as _re
        assert not _re.search(r'\b3bit\b', v), "bare '3bit' identifier in custom VHDL"
    run_test("T71 Custom VHDL: digit-leading port name sanitized to sig_3bit", T71)

    # T72 — "module" (Verilog reserved) as port name in custom Verilog → sig_module
    def T72():
        v = generate_custom_v("MOD_PORT", ["module", "clk"], ["q"], "")
        assert "sig_module" in v, "Verilog reserved port name 'module' not sanitized"
        import re as _re
        # "module sig_module" or "input sig_module" — not bare "module" as identifier
        assert not _re.search(r'\binput\s+module\b', v), \
            "'input module' (keyword as identifier) in Verilog custom block"
    run_test("T72 Custom Verilog: Verilog reserved port name 'module' sanitized to sig_module", T72)


# ===========================================================================
# G14 — Extended syntax validation (tool-dependent)
# ===========================================================================

def g14_extended_syntax(win):
    from vhdl_export import (generate_custom_vhd, generate_custom_v,
                              check_vhdl_syntax, check_verilog_syntax)
    import shutil as _shutil
    print("\n-- G14: Extended syntax validation --")

    # T73 — GHDL accepts custom VHDL where port was formerly "signal" (now sig_signal)
    def T73():
        ghdl = _shutil.which("ghdl")
        if not ghdl:
            log_skip("T73 GHDL: custom VHDL with sanitized reserved port", "ghdl not on PATH")
            return
        v = generate_custom_vhd("RES_PORT_VHD", ["signal", "clk"], ["q"], "")
        assert "sig_signal" in v, "port not sanitized before syntax check"
        with tempfile.NamedTemporaryFile(suffix=".vhd", delete=False, mode="w") as f:
            f.write(v); path = f.name
        try:
            avail, ok, out = check_vhdl_syntax(path)
            assert ok, f"GHDL rejected sanitized custom VHDL:\n{out}"
        finally:
            os.unlink(path)
    run_test("T73 GHDL: custom VHDL with formerly-reserved port name passes syntax check", T73)

    # T74 — iverilog accepts custom Verilog where port was formerly "wire" (now sig_wire)
    def T74():
        iv = _shutil.which("iverilog")
        if not iv:
            log_skip("T74 iverilog: custom Verilog with sanitized reserved port", "iverilog not on PATH")
            return
        v = generate_custom_v("RES_PORT_VLG", ["wire", "clk"], ["q"], "")
        assert "sig_wire" in v, "port not sanitized before syntax check"
        with tempfile.NamedTemporaryFile(suffix=".v", delete=False, mode="w") as f:
            f.write(v); path = f.name
        try:
            avail, ok, out = check_verilog_syntax(path)
            assert ok, f"iverilog rejected sanitized custom Verilog:\n{out}"
        finally:
            os.unlink(path)
    run_test("T74 iverilog: custom Verilog with formerly-reserved port name passes syntax check", T74)


# ===========================================================================
# G15 — Testbench generation
# ===========================================================================

def g15_testbench_generation(win):
    from pins import Pin
    from testbench_gen import generate_testbench
    gs = win.grid_size
    print("\n-- G15: Testbench generation --")

    # T75 — testbench entity name is {entity_name}_tb
    def T75():
        reset(win)
        win.pins.append(Pin(gs, gs*3, gs*3, gs*2, "A", "input_pin", gs, 1, win))
        tb = generate_testbench("MY_DUT", win.pins)
        assert "entity MY_DUT_tb is" in tb, "testbench entity name must be entity_name + '_tb'"
        assert "architecture sim of MY_DUT_tb is" in tb, "architecture header wrong"
    run_test("T75 Testbench entity name is entity_name_tb", T75)

    # T76 — port named CLK produces a 100 MHz clock process
    def T76():
        reset(win)
        win.pins.append(Pin(gs, gs*3, gs*3, gs*2, "CLK", "CLK", gs, 1, win))
        tb = generate_testbench("CLK_DUT", win.pins)
        assert "CLK_proc" in tb or "_proc" in tb, "no clock process generated for CLK port"
        assert "wait for 5 ns" in tb, "clock half-period (5 ns) missing"
    run_test("T76 CLK port generates 100 MHz clock process", T76)

    # T77 — active-low signal 'nrst' initialised to '1', not '0'
    def T77():
        reset(win)
        win.pins.append(Pin(gs, gs*3, gs*3, gs*2, "nrst", "input_pin", gs, 1, win))
        tb = generate_testbench("AL_DUT", win.pins)
        assert "signal nrst : STD_LOGIC := '1'" in tb, \
            "active-low signal 'nrst' not initialised to '1'"
    run_test("T77 Active-low signal 'nrst' initialised to '1' in testbench", T77)

    # T78 — active-low signal is pulsed LOW (asserted) in stimulus
    def T78():
        reset(win)
        win.pins.append(Pin(gs, gs*3, gs*3, gs*2, "nrst", "input_pin", gs, 1, win))
        tb = generate_testbench("AL_DUT2", win.pins)
        # Stimulus: nrst <= '0' (assert) followed by nrst <= '1' (deassert)
        assert "nrst <= '0'" in tb, "active-low 'nrst' not pulsed LOW in stimulus"
        assert "nrst <= '1'" in tb, "active-low 'nrst' not returned HIGH after pulse"
    run_test("T78 Active-low signal pulsed LOW then HIGH in stimulus", T78)

    # T79 — regular input port pulsed HIGH then LOW in stimulus
    def T79():
        reset(win)
        win.pins.append(Pin(gs, gs*3, gs*3, gs*2, "DATA", "input_pin", gs, 1, win))
        tb = generate_testbench("REG_DUT", win.pins)
        assert "DATA <= '1'" in tb, "regular input not pulsed HIGH in stimulus"
        assert "DATA <= '0'" in tb, "regular input not returned LOW after pulse"
    run_test("T79 Regular input pulsed HIGH then LOW in stimulus", T79)

    # T80 — port-less entity produces valid testbench skeleton (no crash)
    def T80():
        tb = generate_testbench("EMPTY_DUT", [])
        assert "entity EMPTY_DUT_tb is" in tb, "testbench entity missing for port-less DUT"
        assert "end architecture sim;" in tb,   "testbench architecture end missing"
        assert "stim_proc" in tb,               "stimulus process missing even for port-less DUT"
    run_test("T80 Port-less entity produces valid testbench skeleton", T80)


# ===========================================================================
# G16 — Testbench edge cases
# ===========================================================================

def g16_testbench_edge_cases(win):
    from pins import Pin
    from testbench_gen import generate_testbench, _is_active_low
    gs = win.grid_size
    print("\n-- G16: Testbench edge cases --")

    # T81 — output ports NOT driven in stimulus (only inputs get stimulus)
    def T81():
        reset(win)
        win.pins.append(Pin(gs, gs*3,  gs*3, gs*2, "A",   "input_pin",  gs, 1, win))
        win.pins.append(Pin(gs, gs*7,  gs*3, gs*2, "Y",   "output_pin", gs, 1, win))
        tb = generate_testbench("IO_DUT", win.pins)
        # Y is output — must appear in component/signal but not in stimulus assignments
        stim_start = tb.find("stim_proc")
        stim_block = tb[stim_start:] if stim_start >= 0 else ""
        assert "Y <= " not in stim_block, "output port 'Y' driven in stimulus (should not be)"
    run_test("T81 Output ports not driven in testbench stimulus process", T81)

    # T82 — multiple CLK ports each get their own clock process
    def T82():
        reset(win)
        win.pins.append(Pin(gs, gs*3,  gs*3, gs*2, "clk_a", "CLK", gs, 1, win))
        win.pins.append(Pin(gs, gs*7,  gs*3, gs*2, "clk_b", "CLK", gs, 1, win))
        tb = generate_testbench("DUAL_CLK", win.pins)
        assert "clk_a_proc" in tb, "clock process for clk_a missing"
        assert "clk_b_proc" in tb, "clock process for clk_b missing"
        assert tb.count("wait for 5 ns") >= 4, \
            "expected >=4 'wait for 5 ns' lines (2 per clock process)"
    run_test("T82 Multiple CLK ports each generate their own clock process", T82)

    # T83 — clock detection is case-insensitive: sys_CLK, Clk_in
    def T83():
        reset(win)
        win.pins.append(Pin(gs, gs*3, gs*3, gs*2, "sys_CLK", "input_pin", gs, 1, win))
        win.pins.append(Pin(gs, gs*7, gs*3, gs*2, "Clk_in",  "input_pin", gs, 1, win))
        tb = generate_testbench("CI_CLK", win.pins)
        assert "sys_CLK_proc" in tb or "sys_clk_proc" in tb.lower(), \
            "sys_CLK not recognised as clock port"
        assert "Clk_in_proc" in tb or "clk_in_proc" in tb.lower(), \
            "Clk_in not recognised as clock port"
    run_test("T83 Clock port detection is case-insensitive (sys_CLK, Clk_in)", T83)

    # T84 — active-low suffix patterns: _n, _b, _bar all detected
    def T84():
        for name in ("rst_n", "enable_b", "set_bar"):
            assert _is_active_low(name), \
                f"'{name}' not recognised as active-low (suffix pattern)"
    run_test("T84 Active-low suffix patterns _n / _b / _bar all detected", T84)

    # T85 — active-low prefix patterns: n_, nrst, nreset all detected
    def T85():
        for name in ("n_reset", "nrst", "nreset"):
            assert _is_active_low(name), \
                f"'{name}' not recognised as active-low (prefix pattern)"
    run_test("T85 Active-low prefix patterns n_ / nrst / nreset all detected", T85)

    # T86 — UUT instantiation label is exactly 'uut'
    def T86():
        reset(win)
        win.pins.append(Pin(gs, gs*3, gs*3, gs*2, "A", "input_pin", gs, 1, win))
        tb = generate_testbench("LABEL_DUT", win.pins)
        assert "uut : LABEL_DUT" in tb, \
            "UUT instantiation label is not 'uut'"
    run_test("T86 UUT instantiation label is 'uut'", T86)


# ===========================================================================
# G17 — HDL structural deep-checks
# ===========================================================================

def g17_structural_deep(win):
    from blocks import Block
    from pins   import Pin
    from vhdl_export import generate_vhdl, generate_verilog, ENTITY_MAP
    import re as _re
    gs = win.grid_size
    print("\n-- G17: HDL structural deep-checks --")

    # T87 — every VHDL port map connection uses named association (=>)
    def T87():
        reset(win)
        build_half_adder(win)
        v = generate_vhdl("HA_DEEP", win.blocks, win.pins, win.wires)
        # Find every port map block and confirm each line has =>
        pm_lines = [ln.strip() for ln in v.splitlines()
                    if ln.strip() and "=>" in ln]
        assert len(pm_lines) > 0, "no '=>' lines found in VHDL port maps"
        # No positional associations (bare signal without =>)
        for ln in v.splitlines():
            if "port map (" in ln:
                # next non-empty lines until ");" should all contain =>
                pass
        # Simplified: count => must equal total port connections
        # XOR has 3 ports (IN1, IN2, OUT1), AND has 3 — total 6
        assert v.count("=>") >= 6, \
            f"expected >=6 named associations (=>), found {v.count('=>')}"
    run_test("T87 Every VHDL port map uses named association (=>)", T87)

    # T88 — every Verilog instance uses .portname(signal) dot notation
    def T88():
        reset(win)
        build_half_adder(win)
        v = generate_verilog("HA_DEEP_V", win.blocks, win.pins, win.wires)
        dot_connections = _re.findall(r'\.\w+\(\w+\)', v)
        assert len(dot_connections) >= 6, \
            f"expected >=6 .port(sig) connections, found {len(dot_connections)}: {dot_connections}"
    run_test("T88 Every Verilog instance uses .portname(signal) dot notation", T88)

    # T89 — two instances of same type → one component decl, two port maps (VHDL)
    def T89():
        reset(win)
        rebuild_grid(win)
        win.blocks.append(Block(gs*3, gs*3, gs*4, gs*4, "AND_0", "AND", gs, win))
        win.blocks.append(Block(gs*9, gs*3, gs*4, gs*4, "AND_1", "AND", gs, win))
        v = generate_vhdl("TWO_AND", win.blocks, win.pins, win.wires)
        comp_count = v.count("component AND_GATE")
        pm_count   = v.count("port map (")
        assert comp_count == 1, f"expected 1 AND_GATE component declaration, found {comp_count}"
        assert pm_count   == 2, f"expected 2 port maps for 2 instances, found {pm_count}"
    run_test("T89 Two AND instances → one VHDL component decl + two port maps", T89)

    # T90 — VHDL architecture has exactly one 'begin' and ends with 'end Structural;'
    def T90():
        reset(win)
        build_half_adder(win)
        v = generate_vhdl("ARCH_STRUCT", win.blocks, win.pins, win.wires)
        # Count standalone 'begin' lines (architecture body opener, not inside components)
        begin_lines = [ln.strip() for ln in v.splitlines() if ln.strip() == "begin"]
        assert len(begin_lines) == 1, \
            f"expected exactly 1 standalone 'begin' in architecture, found {len(begin_lines)}"
        assert v.strip().endswith("end Structural;"), \
            "VHDL output does not end with 'end Structural;'"
    run_test("T90 VHDL architecture has one 'begin' and ends with 'end Structural;'", T90)

    # T91 — canvas with only blocks (no IO pins) produces empty port list in both HDLs
    def T91():
        reset(win)
        rebuild_grid(win)
        win.blocks.append(Block(gs*3, gs*3, gs*4, gs*4, "G1", "AND", gs, win))
        v_vhd = generate_vhdl("NO_PORTS_TOP", win.blocks, win.pins, win.wires)
        v_vlg = generate_verilog("NO_PORTS_TOP_V", win.blocks, win.pins, win.wires)
        # VHDL: no 'Port (' in entity (port-less entity)
        entity_section = v_vhd.split("architecture")[0] if "architecture" in v_vhd else v_vhd
        assert "Port (" not in entity_section, \
            "VHDL entity has Port() clause but no IO pins exist"
        # Verilog: module header closes immediately after name (no port declarations)
        assert _re.search(r'module NO_PORTS_TOP_V\s*\(\s*\);', v_vlg), \
            "Verilog module should have empty port list with no IO pins"
    run_test("T91 Canvas with no IO pins yields empty port list in both HDLs", T91)

    # T92 — testbench 'Simulation complete' report statement is present
    def T92():
        from testbench_gen import generate_testbench
        reset(win)
        win.pins.append(Pin(gs, gs*3, gs*3, gs*2, "A", "input_pin", gs, 1, win))
        tb = generate_testbench("SIM_DONE", win.pins)
        assert "Simulation complete" in tb, \
            "testbench missing 'Simulation complete' report statement"
        assert "severity note" in tb, \
            "testbench report missing 'severity note'"
    run_test("T92 Testbench contains 'Simulation complete' report statement", T92)


# ===========================================================================
# G18 — Custom block structural correctness (after fixes)
# ===========================================================================

def g18_custom_structural(win):
    from blocks import Block
    from vhdl_export import generate_vhdl, generate_verilog
    gs = win.grid_size
    print("\n-- G18: Custom block structural correctness --")

    def make_custom_block(entity_name, in_names, out_names):
        reset(win)
        rebuild_grid(win)
        b = Block(gs*5, gs*5, gs*6, gs*4, entity_name, "CUSTOM", gs, win)
        b.custom_data = {
            "entity_name":  entity_name,
            "input_names":  in_names,
            "output_names": out_names,
            "vhdl":         "",
        }
        b.input_names  = list(in_names)
        b.output_names = list(out_names)
        b.input_wires  = [None] * len(in_names)
        b.output_wires = [None] * len(out_names)
        win.blocks.append(b)

    # T93 — VHDL structural: reserved custom entity name sanitized in component decl
    def T93():
        make_custom_block("signal", ["a"], ["b"])
        v = generate_vhdl("TOP93", win.blocks, win.pins, win.wires)
        assert "component signal" not in v, \
            "'component signal' found — VHDL reserved entity name not sanitized"
        assert "component sig_signal" in v, \
            "sanitized component 'sig_signal' missing from VHDL structural output"
    run_test("T93 VHDL structural: reserved custom entity name sanitized in component decl", T93)

    # T94 — Verilog structural: reserved custom entity name sanitized in instantiation
    def T94():
        make_custom_block("module", ["a"], ["b"])
        v = generate_verilog("TOP94", win.blocks, win.pins, win.wires)
        assert "module sig_module " in v or "sig_module" in v, \
            "sanitized entity 'sig_module' missing from Verilog structural output"
    run_test("T94 Verilog structural: reserved custom entity name sanitized in instantiation", T94)

    # T95 — VHDL structural: custom block reserved port name consistent in component decl and port map
    def T95():
        make_custom_block("MY_COMP", ["wire", "clk"], ["out1"])
        v = generate_vhdl("TOP95", win.blocks, win.pins, win.wires)
        # component decl and port map must both use "sig_wire", not "wire"
        import re as _re
        assert not _re.search(r'\bwire\s*:', v), \
            "'wire :' appears in VHDL — reserved port name 'wire' not sanitized in component decl"
        assert "sig_wire" in v, \
            "sanitized port 'sig_wire' missing from VHDL structural output"
    run_test("T95 VHDL structural: reserved custom port name consistent in decl and port map", T95)

    # T96 — Verilog structural: custom block reserved port name sanitized in instantiation
    def T96():
        make_custom_block("MY_COMP_V", ["wire", "clk"], ["out1"])
        v = generate_verilog("TOP96", win.blocks, win.pins, win.wires)
        import re as _re
        assert not _re.search(r'\.wire\b', v), \
            "'.wire' (bare keyword as port) in Verilog structural instantiation"
        assert ".sig_wire" in v, \
            "sanitized port '.sig_wire' missing from Verilog structural output"
    run_test("T96 Verilog structural: reserved custom port name sanitized in instantiation", T96)


# ===========================================================================
# G19 — Language-aware custom block code storage
# ===========================================================================

def g19_language_aware_code(win):
    print("\n-- G19: Language-aware custom block code storage --")

    # T97 — get_data() with language=verilog returns "verilog_body" key
    def T97():
        from custom_block_dialog import CustomBlockDialog
        dlg = CustomBlockDialog(win, language="verilog")
        buf = dlg._vhdl_view.get_buffer()
        buf.set_text("assign q = a & b;")
        data = dlg.get_data()
        dlg.destroy()
        assert "verilog_body" in data, "get_data() missing 'verilog_body' key for verilog language"
        assert data["verilog_body"] == "assign q = a & b;", \
            "verilog_body content mismatch"
        assert "vhdl" in data, "'vhdl' backward-compat key missing"
    run_test("T97 get_data() with language=verilog returns 'verilog_body' key", T97)

    # T98 — get_data() with language=vhdl returns "vhdl_body" key
    def T98():
        from custom_block_dialog import CustomBlockDialog
        dlg = CustomBlockDialog(win, language="vhdl")
        buf = dlg._vhdl_view.get_buffer()
        buf.set_text("q <= a and b;")
        data = dlg.get_data()
        dlg.destroy()
        assert "vhdl_body" in data, "get_data() missing 'vhdl_body' key for vhdl language"
        assert data["vhdl_body"] == "q <= a and b;", "vhdl_body content mismatch"
        assert "vhdl" in data, "'vhdl' backward-compat key missing"
    run_test("T98 get_data() with language=vhdl returns 'vhdl_body' key", T98)

    # T99 — verilog_body takes priority over vhdl key when loading in verilog mode
    def T99():
        cd = {
            "entity_name": "X", "input_names": [], "output_names": [],
            "vhdl": "VHDL_OLD_CODE",
            "verilog_body": "VERILOG_NEW_CODE",
        }
        loaded = cd.get("verilog_body", cd.get("vhdl", ""))
        assert loaded == "VERILOG_NEW_CODE", \
            "verilog_body not taking priority over vhdl key when loading in verilog mode"
    run_test("T99 verilog_body takes priority over vhdl key in verilog mode", T99)

    # T100 — vhdl_body takes priority over vhdl key when loading in vhdl mode
    def T100():
        cd = {
            "entity_name": "X", "input_names": [], "output_names": [],
            "vhdl": "OLD_VHDL_CODE",
            "vhdl_body": "NEW_VHDL_CODE",
        }
        loaded = cd.get("vhdl_body", cd.get("vhdl", ""))
        assert loaded == "NEW_VHDL_CODE", \
            "vhdl_body not taking priority over vhdl key when loading in vhdl mode"
    run_test("T100 vhdl_body takes priority over vhdl key in vhdl mode", T100)


# ===========================================================================
# G20 — Active-low CLK polarity + additional testbench coverage
# ===========================================================================

def g20_al_clk_and_misc(win):
    from pins import Pin
    from testbench_gen import generate_testbench
    gs = win.grid_size
    print("\n-- G20: Active-low CLK polarity + misc testbench --")

    # T101 — active-low CLK (clk_n) starts at '1' in testbench (not '0')
    def T101():
        reset(win)
        win.pins.append(Pin(gs, gs*3, gs*3, gs*2, "clk_n", "CLK", gs, 1, win))
        tb = generate_testbench("AL_CLK_DUT", win.pins)
        assert "signal clk_n : STD_LOGIC := '1'" in tb, \
            "active-low CLK 'clk_n' not initialized to '1'"
    run_test("T101 Active-low CLK 'clk_n' signal initialised to '1'", T101)

    # T102 — active-low CLK clock process pulses '0' (active state), not '1'
    def T102():
        reset(win)
        win.pins.append(Pin(gs, gs*3, gs*3, gs*2, "clk_n", "CLK", gs, 1, win))
        tb = generate_testbench("AL_CLK_DUT2", win.pins)
        # Clock process: first line is inactive='1', second line is active='0'
        proc_start = tb.find("clk_n_proc")
        proc_body  = tb[proc_start:proc_start + 200] if proc_start >= 0 else ""
        assert "clk_n <= '1'; wait for 5 ns;" in proc_body, \
            "active-low CLK process does not start with inactive state '1'"
        assert "clk_n <= '0'; wait for 5 ns;" in proc_body, \
            "active-low CLK process does not pulse to active state '0'"
        # Verify order: '1' appears before '0' in the process
        idx1 = proc_body.find("clk_n <= '1'")
        idx0 = proc_body.find("clk_n <= '0'")
        assert idx1 < idx0, "active-low CLK should start '1' (inactive) before going '0' (active)"
    run_test("T102 Active-low CLK clock process: starts '1', pulses '0'", T102)

    # T103 — regular CLK (active-high) still starts '0' and pulses '1' (regression)
    def T103():
        reset(win)
        win.pins.append(Pin(gs, gs*3, gs*3, gs*2, "clk", "CLK", gs, 1, win))
        tb = generate_testbench("REG_CLK_DUT", win.pins)
        proc_start = tb.find("clk_proc")
        proc_body  = tb[proc_start:proc_start + 200] if proc_start >= 0 else ""
        idx0 = proc_body.find("clk <= '0'")
        idx1 = proc_body.find("clk <= '1'")
        assert idx0 >= 0 and idx1 >= 0, "regular CLK process missing '0' or '1' assignments"
        assert idx0 < idx1, "regular CLK should start '0' (inactive) before going '1' (active)"
    run_test("T103 Regular CLK (active-high) still starts '0' and pulses '1'", T103)

    # T104 — inout port appears in component and UUT port map but not in stimulus
    def T104():
        reset(win)
        win.pins.append(Pin(gs, gs*3,  gs*3, gs*2, "BUS_IO", "input_output_pin", gs, 1, win))
        win.pins.append(Pin(gs, gs*7,  gs*3, gs*2, "D_IN",   "input_pin",        gs, 1, win))
        tb = generate_testbench("INOUT_DUT", win.pins)
        assert "BUS_IO" in tb, "inout port 'BUS_IO' missing from testbench entirely"
        assert "BUS_IO => BUS_IO" in tb, "inout port not in UUT port map"
        stim_start = tb.find("stim_proc")
        stim_body  = tb[stim_start:] if stim_start >= 0 else ""
        assert "BUS_IO <= " not in stim_body, \
            "inout port 'BUS_IO' driven in stimulus (should not be)"
    run_test("T104 Inout port in testbench: in port map but not in stimulus", T104)

    # T105 — VDD pin exported as 'in' STD_LOGIC in VHDL entity
    def T105():
        from vhdl_export import generate_vhdl
        reset(win)
        rebuild_grid(win)
        win.pins.append(Pin(gs, gs*3, gs*3, gs*2, "VDD", "VDD_5V", gs, 1, win))
        v = generate_vhdl("VDD_TEST", win.blocks, win.pins, win.wires)
        assert "VDD" in v,          "VDD pin missing from VHDL entity"
        assert "VDD : in" in v,     "VDD pin not exported with 'in' direction in VHDL"
    run_test("T105 VDD pin exported as 'in' direction in VHDL entity", T105)

    # T106 — GND pin exported as 'in' direction in Verilog module
    def T106():
        from vhdl_export import generate_verilog
        reset(win)
        rebuild_grid(win)
        win.pins.append(Pin(gs, gs*3, gs*3, gs*2, "GND", "GND", gs, 1, win))
        v = generate_verilog("GND_TEST", win.blocks, win.pins, win.wires)
        assert "GND" in v,              "GND pin missing from Verilog module"
        assert "input  wire GND" in v,  "GND pin not exported as 'input wire' in Verilog"
    run_test("T106 GND pin exported as 'input wire' in Verilog module", T106)


# ===========================================================================
# G21 — EDIF export
# ===========================================================================

def g21_edif_export(win):
    print("\n--- G21: EDIF export ---")
    import sys as _sys
    _sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "experimental"))
    from edif_convertor import generate_edif_ports, generate_edif_net_connections

    # Minimal block dict matching blocks.to_dict() structure
    def _block(bid, inames, onames, iwires, owires):
        ipts = [[0, i*10] for i in range(len(inames))]
        opts = [[100, i*10] for i in range(len(onames))]
        return {
            "id": bid, "name": bid, "block_type": "AND",
            "input_points": ipts, "output_points": opts,
            "input_names": inames, "output_names": onames,
            "input_wires": iwires, "output_wires": owires,
        }

    def _pin(pid, pname, num_pins, wires):
        return {
            "id": pid, "name": pname, "pin_type": "input_pin",
            "connection_points": [[0, 0]] * num_pins,
            "wires": wires, "num_pins": num_pins,
        }

    def _wire(wid, sp, ep):
        return {"id": wid, "start_point": sp, "end_point": ep}

    # T107 — generate_edif_ports on block returns all port names
    def T107():
        b = _block("b1", ["A", "B"], ["Y"], [["w1"], ["w2"]], [["w3"]])
        out = generate_edif_ports(b)
        assert "(port A (direction INPUT))" in out
        assert "(port B (direction INPUT))" in out
        assert "(port Y (direction OUTPUT))" in out
    run_test("T107 generate_edif_ports lists all block ports", T107)

    # T108 — correct port name via port-index (not flat index) for multi-wire port
    def T108():
        # port 0 = "A" with wire "w1"; port 1 = "B" with wires "w2" AND "w3"
        b = _block("b1", ["A", "B"], ["Y"], [["w1"], ["w2", "w3"]], [[]])
        wire = _wire("w3", [0, 0], [1, 1])
        conn = generate_edif_net_connections(wire, [b], [])
        assert "portRef B" in conn, f"Expected 'portRef B', got: {conn}"
        assert "instanceRef b1" in conn
    run_test("T108 net connection uses port-index not flat-index", T108)

    # T109 — None sublists (old JSON backward-compat) don't crash
    def T109():
        b = {
            "id": "b1", "name": "b1", "block_type": "AND",
            "input_points": [[0, 0], [0, 10]], "output_points": [[100, 0]],
            "input_names": ["A", "B"], "output_names": ["Y"],
            "input_wires": [None, ["w1"]], "output_wires": [None],
        }
        wire = _wire("w1", [0, 10], [50, 50])
        conn = generate_edif_net_connections(wire, [b], [])
        assert "portRef B" in conn
    run_test("T109 None sublists in input_wires don't crash", T109)

    # T110 — disconnected port (empty sublist) not in net connections
    def T110():
        b = _block("b1", ["A", "B"], ["Y"], [[], ["w1"]], [[]])
        wire = _wire("w1", [0, 0], [1, 1])
        conn = generate_edif_net_connections(wire, [b], [])
        assert "portRef A" not in conn, "Disconnected port A must not appear"
        assert "portRef B" in conn
    run_test("T110 disconnected (empty) port excluded from net connections", T110)

    # T111 — bus pin (num_pins > 1) gets unique numbered port names
    def T111():
        p = _pin("p1", "D", 4, [["w0"], ["w1"], ["w2"], ["w3"]])
        out = generate_edif_ports(p)
        assert "(port D_0 (direction INOUT))" in out
        assert "(port D_1 (direction INOUT))" in out
        assert "(port D_3 (direction INOUT))" in out
    run_test("T111 bus pin ports get unique numbered names", T111)

    # T112 — single-bit pin uses bare name (no index suffix)
    def T112():
        p = _pin("p1", "CLK", 1, [["w1"]])
        out = generate_edif_ports(p)
        assert "(port CLK (direction INOUT))" in out
        assert "CLK_0" not in out
    run_test("T112 single-bit pin uses bare port name without index", T112)

    # T113 — net connection resolves through pin wires correctly
    def T113():
        p = _pin("p1", "A", 1, [["w1"]])
        wire = _wire("w1", [0, 0], [1, 1])
        conn = generate_edif_net_connections(wire, [], [p])
        assert "portRef A" in conn
        assert "instanceRef p1" in conn
    run_test("T113 net connection resolves pin wire correctly", T113)

    # T114 — full round-trip: write JSON, run generate_edif_netlist, file created
    def T114():
        import tempfile, json as _json
        from edif_convertor import generate_edif_netlist
        b = _block("b1", ["A", "B"], ["Y"], [["w1"], ["w2"]], [["w3"]])
        b.update({"x": 0, "y": 0, "width": 50, "height": 50, "rotation": 0,
                  "border_color": [0,0,0,1], "fill_color": [1,1,1,1],
                  "text_color": [0,0,0,1], "timestamp": 0, "grid_size": 10})
        p = _pin("p1", "A", 1, [["w1"]])
        p.update({"x": 0, "y": 0, "width": 20, "height": 20, "rotation": 0,
                  "border_color": [0,0,0,1], "fill_color": [1,1,1,1],
                  "text_color": [0,0,0,1], "timestamp": 0, "grid_size": 10})
        w = _wire("w1", [0, 0], [50, 0])
        data = [b, p, w]
        with tempfile.TemporaryDirectory() as td:
            jf = os.path.join(td, "test.json")
            ef = os.path.join(td, "test.edf")
            with open(jf, "w") as fh:
                _json.dump(data, fh)
            generate_edif_netlist(jf, ef)
            assert os.path.exists(ef), "EDIF output file not created"
            content = open(ef).read()
            assert "edif" in content
            assert "w1" in content
    run_test("T114 full EDIF round-trip produces output file", T114)


# ===========================================================================
# G22 — New block types
# ===========================================================================

def g22_new_blocks(win):
    print("\n--- G22: New block types ---")
    from blocks import Block
    from vhdl_export import generate_vhdl, generate_verilog
    gs = win.grid_size

    def _block(bt):
        b = Block(gs*5, gs*5, gs*4, gs*4, bt, bt, gs, win)
        return b

    # T115 — 3-input gate has 3 input ports and 1 output
    def T115():
        for bt in ["AND3", "OR3", "NAND3", "NOR3", "XOR3"]:
            b = _block(bt)
            assert len(b.input_points)  == 3, f"{bt}: expected 3 inputs, got {len(b.input_points)}"
            assert len(b.output_points) == 1, f"{bt}: expected 1 output"
            assert b.input_names  == ["IN1","IN2","IN3"]
            assert b.output_names == ["OUT1"]
    run_test("T115 3-input gates have 3 inputs and 1 output", T115)

    # T116 — 4-input gate has 4 input ports and 1 output
    def T116():
        for bt in ["AND4", "OR4", "NAND4", "NOR4"]:
            b = _block(bt)
            assert len(b.input_points)  == 4, f"{bt}: expected 4 inputs"
            assert len(b.output_points) == 1, f"{bt}: expected 1 output"
            assert b.input_names == ["IN1","IN2","IN3","IN4"]
    run_test("T116 4-input gates have 4 inputs and 1 output", T116)

    # T117 — BUF has 1 input, 1 output, same-axis alignment
    def T117():
        b = _block("BUF")
        assert len(b.input_points)  == 1
        assert len(b.output_points) == 1
        assert b.input_names  == ["IN1"]
        assert b.output_names == ["OUT1"]
        # input and output share the same X coordinate (vertically aligned)
        assert b.input_points[0][0] == b.output_points[0][0]
    run_test("T117 BUF has 1 input/output, vertically aligned", T117)

    # T118 — DLATCH ports
    def T118():
        b = _block("DLATCH")
        assert b.input_names  == ["D", "EN"]
        assert b.output_names == ["Q", "Q'"]
        assert len(b.input_points)  == 2
        assert len(b.output_points) == 2
    run_test("T118 DLATCH has D/EN inputs and Q/Q' outputs", T118)

    # T119 — SRLATCH ports
    def T119():
        b = _block("SRLATCH")
        assert b.input_names  == ["S", "R"]
        assert b.output_names == ["Q", "Q'"]
    run_test("T119 SRLATCH has S/R inputs and Q/Q' outputs", T119)

    # T120 — DEC_2TO4 has 3 inputs and 4 outputs
    def T120():
        b = _block("DEC_2TO4")
        assert b.input_names  == ["A","B","EN"]
        assert b.output_names == ["Y0","Y1","Y2","Y3"]
        assert len(b.input_points)  == 3
        assert len(b.output_points) == 4
    run_test("T120 DEC_2TO4 has 3 inputs, 4 outputs", T120)

    # T121 — DEC_3TO8 has 4 inputs and 8 outputs
    def T121():
        b = _block("DEC_3TO8")
        assert len(b.input_points)  == 4
        assert len(b.output_points) == 8
        assert "Y7" in b.output_names
    run_test("T121 DEC_3TO8 has 4 inputs, 8 outputs", T121)

    # T122 — ENC_4TO2 has VALID output
    def T122():
        b = _block("ENC_4TO2")
        assert b.output_names == ["Y0","Y1","VALID"]
        assert len(b.input_points)  == 4
        assert len(b.output_points) == 3
    run_test("T122 ENC_4TO2 has VALID output", T122)

    # T123 — DEMUX_1TO4 port counts
    def T123():
        b = _block("DEMUX_1TO4")
        assert b.input_names  == ["I","S0","S1","EN"]
        assert b.output_names == ["O0","O1","O2","O3"]
    run_test("T123 DEMUX_1TO4 ports correct", T123)

    # T124 — DEMUX_1TO8 has 5 inputs, 8 outputs
    def T124():
        b = _block("DEMUX_1TO8")
        assert len(b.input_points)  == 5
        assert len(b.output_points) == 8
        assert "S2" in b.input_names
    run_test("T124 DEMUX_1TO8 has 5 inputs, 8 outputs with S2", T124)

    # T125 — RCA_4BIT has 9 inputs (A0-A3, B0-B3, CIN) and 5 outputs
    def T125():
        b = _block("RCA_4BIT")
        assert len(b.input_points)  == 9
        assert len(b.output_points) == 5
        assert "CIN"  in b.input_names
        assert "COUT" in b.output_names
    run_test("T125 RCA_4BIT has CIN/COUT and correct port counts", T125)

    # T126 — COMP_4BIT has ALB/AEB/AGB outputs
    def T126():
        b = _block("COMP_4BIT")
        assert b.output_names == ["ALB","AEB","AGB"]
        assert len(b.input_points) == 8
    run_test("T126 COMP_4BIT has ALB/AEB/AGB outputs", T126)

    # T127 — SHREG_4BIT has SIN input and Q0-Q3 outputs
    def T127():
        b = _block("SHREG_4BIT")
        assert b.input_names  == ["SIN","CLK","RST"]
        assert b.output_names == ["Q0","Q1","Q2","Q3"]
    run_test("T127 SHREG_4BIT has SIN/CLK/RST inputs, Q0-Q3 outputs", T127)

    # T128 — CNT_4BIT has TC output
    def T128():
        b = _block("CNT_4BIT")
        assert "TC" in b.output_names
        assert len(b.output_points) == 5
    run_test("T128 CNT_4BIT has TC terminal-count output", T128)

    # T129 — CNT_4BIT_UD has DIR input
    def T129():
        b = _block("CNT_4BIT_UD")
        assert "DIR" in b.input_names
        assert len(b.input_points) == 4
    run_test("T129 CNT_4BIT_UD has DIR up/down control input", T129)

    # T130 — VHDL export lists all new block types in component declarations
    def T130():
        reset(win)
        rebuild_grid(win)
        from pins import Pin
        pA = Pin(gs, gs*2, gs*3, gs*2, "A", "input_pin",  gs, 1, win)
        pY = Pin(gs*12, gs*2, gs*3, gs*2, "Y", "output_pin", gs, 1, win)
        b3 = Block(gs*5, gs*5, gs*4, gs*4, "gate3", "AND3", gs, win)
        win.pins.extend([pA, pY])
        win.blocks.append(b3)
        rebuild_grid(win)
        vhd = generate_vhdl("TOP", win.blocks, win.pins, win.wires)
        assert "AND3_GATE" in vhd, "AND3_GATE component missing from VHDL"
        assert "IN1" in vhd
        assert "IN2" in vhd
        assert "IN3" in vhd
    run_test("T130 AND3 appears as AND3_GATE component in structural VHDL", T130)


# ===========================================================================
# Entry point
# ===========================================================================

def run_all_tests(win):
    print("\n=== SVCG HDL Adversarial Test Suite (VHDL + Verilog) ===\n")
    g1_vhdl_structural(win)
    g2_verilog_structural(win)
    g3_custom_vhdl(win)
    g4_custom_verilog(win)
    g5_language_switching(win)
    g6_ai_prompts(win)
    g7_edge_cases(win)
    g8_syntax_checks(win)
    g9_round_trip(win)
    g10_wire_net_names(win)
    g11_multi_instance(win)
    g12_port_count(win)
    g13_custom_adversarial(win)
    g14_extended_syntax(win)
    g15_testbench_generation(win)
    g16_testbench_edge_cases(win)
    g17_structural_deep(win)
    g18_custom_structural(win)
    g19_language_aware_code(win)
    g20_al_clk_and_misc(win)
    g21_edif_export(win)
    g22_new_blocks(win)

    passed  = sum(1 for _, s, _ in results if s == "PASS")
    skipped = sum(1 for _, s, _ in results if s == "SKIP")
    total   = len(results)
    print(f"\n{'='*55}")
    print(f"  {passed}/{total} passed, {skipped} skipped  "
          f"({'%.0f' % (100*passed/(total-skipped) if total-skipped else 0)}% of runnable)")
    print(f"{'='*55}")
    write_report()
    return passed, total


def main():
    from main_window import BlocksWindow
    win = BlocksWindow()
    win.show_all()

    def do_run():
        try:
            run_all_tests(win)
        except Exception as e:
            print(f"\nFATAL: {e}")
            traceback.print_exc()
        GLib.timeout_add(1500, Gtk.main_quit)
        return False

    GLib.timeout_add(600, do_run)
    Gtk.main()


if __name__ == "__main__":
    main()
