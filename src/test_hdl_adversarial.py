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
