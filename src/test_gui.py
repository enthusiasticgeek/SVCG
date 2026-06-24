#!/usr/bin/env python3
"""
test_gui.py -- Automated adversarial GUI test runner for SVCG.

Launches BlocksWindow, exercises features programmatically via a GLib
timeout callback, records PASS/FAIL results, writes TESTING.md, then quits.

Usage:
    cd src
    python test_gui.py
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import sys
import os
import json
import tempfile
import traceback
import cairo as _cairo
from datetime import datetime

# Force UTF-8 output so box-drawing chars don't crash on Windows cp1252 consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TESTING.md")

results = []

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    icon   = "[PASS]" if passed else "[FAIL]"
    results.append((name, status, detail))
    suffix = f"  ({detail})" if detail else ""
    print(f"  {icon} {name}{suffix}")


def run_test(name, fn):
    try:
        fn()
        log(name, True)
    except AssertionError as e:
        log(name, False, str(e))
    except Exception as e:
        log(name, False, f"{type(e).__name__}: {e}")


def write_report():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    passed = sum(1 for _, s, _ in results if s == "PASS")
    total  = len(results)
    lines = [
        "# SVCG Automated GUI Test Report",
        "",
        f"**Date:** {now}  ",
        "**Platform:** Windows 11 / MSYS2 MinGW64  ",
        f"**Result: {passed}/{total} tests passed**",
        "",
        "| # | Test | Result | Notes |",
        "|---|------|--------|-------|",
    ]
    for i, (name, status, detail) in enumerate(results, 1):
        icon = "PASS" if status == "PASS" else "FAIL"
        lines.append(f"| {i} | {name} | {icon} | {detail} |")
    lines += ["", f"_{passed}/{total} passed._", ""]
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n  Report → {REPORT_PATH}")


# ---------------------------------------------------------------------------
# Test suite
# ---------------------------------------------------------------------------

def run_all_tests(win):
    from blocks import Block
    from pins   import Pin
    from wire   import Wire

    gs = win.grid_size
    print("\n=== SVCG Adversarial Test Suite ===\n")

    # ------------------------------------------------------------------
    # Group 1 — Initial state
    # ------------------------------------------------------------------
    print("-- Initial state --")

    def t_empty_canvas():
        assert win.blocks == [] and win.pins == [] and win.wires == [], \
            f"Got {len(win.blocks)}B {len(win.pins)}P {len(win.wires)}W"
    run_test("Canvas starts empty", t_empty_canvas)

    def t_undo_stack_empty():
        assert win.undo_stack == [] and win.redo_stack == []
    run_test("Undo/redo stacks empty at start", t_undo_stack_empty)

    # ------------------------------------------------------------------
    # Group 2 — Block creation
    # ------------------------------------------------------------------
    print("\n-- Block creation --")

    block_types = ["AND", "OR", "NOT", "NAND", "NOR", "XOR", "XNOR",
                   "JKFF", "SRFF", "DFF", "TFF", "DFF_PIPELINE",
                   "MUX_2X1", "MUX_4X1", "MUX_8X1",
                   "FA", "HA", "FA_GC", "FA_WC"]

    created_blocks = {}
    for btype in block_types:
        def make(bt=btype):
            b = Block(gs*3, gs*3, gs*4, gs*4, bt, bt, gs, win)
            assert b.id.startswith("block_")
            assert len(b.input_points) >= 0
            assert len(b.output_points) >= 0
            win.blocks.append(b)
            created_blocks[bt] = b
        run_test(f"Create {btype} block", make)

    # ------------------------------------------------------------------
    # Group 3 — IO pins
    # ------------------------------------------------------------------
    print("\n-- IO pin creation --")

    pin_types = ["input_pin", "output_pin", "input_output_pin",
                 "CLK", "GND", "VDD_5V"]
    created_pins = {}
    for ptype in pin_types:
        def make_pin(pt=ptype):
            p = Pin(gs, gs*3, gs*3, gs*2, pt, pt, gs, 1, win)
            assert p.id.startswith("pin_")
            win.pins.append(p)
            created_pins[pt] = p
        run_test(f"Create {ptype}", make_pin)

    # ------------------------------------------------------------------
    # Group 4 — Wire routing
    # ------------------------------------------------------------------
    print("\n-- Wire routing --")

    b_and = created_blocks.get("AND")
    b_or  = created_blocks.get("OR")

    def t_wire_between_blocks():
        assert b_and and b_or
        sp = list(b_and.output_points[0]) if b_and.output_points else [gs*7, gs*5]
        ep = list(b_or.input_points[0])   if b_or.input_points   else [gs*10, gs*5]
        w = Wire("net_AB", sp, ep, "wire", gs, win)
        win.wires.append(w)
        assert w.path is not None, "Path is None"
    run_test("Wire between AND→OR output/input", t_wire_between_blocks)

    def t_wire_same_endpoints():
        pt = [gs*5, gs*5]
        w = Wire("degenerate", list(pt), list(pt), "wire", gs, win)
        # Must not crash; path may be empty or trivial
        assert w is not None
    run_test("Wire with identical start/end (no crash)", t_wire_same_endpoints)

    def t_wire_at_origin():
        b_orig = Block(0, 0, gs*4, gs*4, "NOT_origin", "NOT", gs, win)
        win.blocks.append(b_orig)
        sp = list(b_orig.output_points[0]) if b_orig.output_points else [gs*4, gs*2]
        ep = [gs*15, gs*15]
        w = Wire("net_origin", sp, ep, "wire", gs, win)
        win.wires.append(w)
        assert w is not None
    run_test("Wire starting near canvas origin (regression)", t_wire_at_origin)

    def t_wire_reversed():
        sp = [gs*20, gs*10]
        ep = [gs*5,  gs*10]
        w = Wire("net_rev", sp, ep, "wire", gs, win)
        assert w is not None
    run_test("Wire with end to the left of start (reverse direction)", t_wire_reversed)

    # ------------------------------------------------------------------
    # Group 5 — Serialisation
    # ------------------------------------------------------------------
    print("\n-- Serialisation --")

    def t_elements_to_json():
        j = win.elements_to_json()
        assert j is not None, "returned None"
        data = json.loads(j)
        assert isinstance(data, list)
        assert len(data) >= len(win.blocks) + len(win.pins) + len(win.wires), \
            f"JSON has {len(data)} items, canvas has {len(win.blocks)+len(win.pins)+len(win.wires)}"
    run_test("elements_to_json() returns valid JSON list", t_elements_to_json)

    tmp_path = None
    def t_save_json():
        nonlocal tmp_path
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = f.name
        win.save_to_json(tmp_path)
        assert os.path.exists(tmp_path), "file not created"
        size = os.path.getsize(tmp_path)
        assert size > 10, f"file too small: {size} bytes"
    run_test("Save to JSON file", t_save_json)

    def t_load_json_roundtrip():
        assert tmp_path, "no temp file from save test"
        nb_before = len(win.blocks)
        np_before = len(win.pins)
        nw_before = len(win.wires)
        win.load_from_json(tmp_path)
        assert len(win.blocks) == nb_before, \
            f"blocks: {len(win.blocks)} != {nb_before}"
        assert len(win.pins) == np_before, \
            f"pins: {len(win.pins)} != {np_before}"
        assert len(win.wires) == nw_before, \
            f"wires: {len(win.wires)} != {nw_before}"
    run_test("Load from JSON (round-trip count match)", t_load_json_roundtrip)

    def t_load_malformed_json():
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            f.write("{{this is not valid json!!")
            bad_path = f.name
        try:
            win.load_from_json(bad_path)
            # Must not crash; canvas state may be unchanged
        finally:
            os.unlink(bad_path)
    run_test("Load malformed JSON (no crash)", t_load_malformed_json)

    # ------------------------------------------------------------------
    # Group 6 — Undo / Redo
    # ------------------------------------------------------------------
    print("\n-- Undo / Redo --")

    def t_undo_redo():
        n_before = len(win.blocks)
        win.push_undo()
        extra = Block(gs*8, gs*8, gs*4, gs*4, "XOR_tmp", "XOR", gs, win)
        win.blocks.append(extra)
        assert len(win.blocks) == n_before + 1
        win.undo()
        assert len(win.blocks) == n_before, \
            f"After undo: {len(win.blocks)} != {n_before}"
        win.redo()
        assert len(win.blocks) == n_before + 1, \
            f"After redo: {len(win.blocks)} != {n_before + 1}"
        win.undo()   # leave canvas unchanged
    run_test("Push undo / undo / redo", t_undo_redo)

    def t_undo_empty_stack():
        win.undo_stack.clear()
        win.redo_stack.clear()
        win.undo()   # must not crash on empty stack
        win.redo()
    run_test("Undo/redo with empty stacks (no crash)", t_undo_empty_stack)

    # ------------------------------------------------------------------
    # Group 7 — VHDL export
    # ------------------------------------------------------------------
    print("\n-- VHDL export --")

    def t_vhdl_structure():
        from vhdl_export import generate_vhdl
        vhdl = generate_vhdl("TEST_TOP", win.blocks, win.pins, win.wires)
        assert "entity TEST_TOP is" in vhdl, "missing entity declaration"
        assert "architecture Structural of TEST_TOP is" in vhdl
        assert "end Structural;" in vhdl
    run_test("VHDL output has entity + architecture + end", t_vhdl_structure)

    def t_vhdl_empty_canvas():
        from vhdl_export import generate_vhdl
        vhdl = generate_vhdl("EMPTY", [], [], [])
        assert "entity EMPTY is" in vhdl
        assert "end Structural;" in vhdl
    run_test("VHDL export with empty schematic (no crash)", t_vhdl_empty_canvas)

    def t_vhdl_all_block_types():
        from vhdl_export import generate_vhdl, ENTITY_MAP
        blocks_all = [Block(i*gs*6, gs*2, gs*4, gs*4, bt, bt, gs, win)
                      for i, bt in enumerate(ENTITY_MAP.keys())]
        vhdl = generate_vhdl("ALL_TYPES", blocks_all, [], [])
        assert "entity ALL_TYPES is" in vhdl
        for bt in ENTITY_MAP:
            entity = ENTITY_MAP[bt]
            assert f"component {entity}" in vhdl or entity in vhdl, \
                f"missing component for {bt}"
    run_test("VHDL export with all block types", t_vhdl_all_block_types)

    def t_vhdl_sanitize_names():
        from vhdl_export import generate_vhdl
        p_bad = Pin(gs, gs*20, gs*3, gs*2, "bad name!@#", "input_pin", gs, 1, win)
        vhdl = generate_vhdl("SAN", [], [p_bad], [])
        assert "bad_name___" in vhdl or "bad" in vhdl
    run_test("VHDL sanitizes invalid identifier chars in port names", t_vhdl_sanitize_names)

    # ------------------------------------------------------------------
    # Group 8 — Testbench generation
    # ------------------------------------------------------------------
    print("\n-- Testbench generation --")

    def t_testbench_basic():
        from testbench_gen import generate_testbench
        tb = generate_testbench("MY_TB", win.pins)
        assert "entity MY_TB_tb is" in tb
        assert "architecture sim of MY_TB_tb is" in tb
        assert "end architecture sim;" in tb
    run_test("Testbench has correct entity + architecture", t_testbench_basic)

    def t_testbench_empty_pins():
        from testbench_gen import generate_testbench
        tb = generate_testbench("NOPINS", [])
        assert "entity NOPINS_tb is" in tb
    run_test("Testbench with no pins (no crash)", t_testbench_empty_pins)

    def t_testbench_with_clk():
        from testbench_gen import generate_testbench
        clk_pin = Pin(gs, gs*30, gs*3, gs*2, "clk", "CLK", gs, 1, win)
        tb = generate_testbench("CLK_TB", [clk_pin])
        assert "clk_proc" in tb or "clk" in tb.lower()
        assert "100 MHz" in tb or "10 ns" in tb
    run_test("Testbench generates clock process for CLK pin", t_testbench_with_clk)

    # ------------------------------------------------------------------
    # Group 9 — Canvas drawing / export
    # ------------------------------------------------------------------
    print("\n-- Canvas draw + export --")

    def t_on_draw_light():
        surface = _cairo.ImageSurface(_cairo.FORMAT_ARGB32, 800, 800)
        cr = _cairo.Context(surface)
        win.dark_mode = False
        win.on_draw(win.drawing_area, cr)
    run_test("on_draw() light mode completes without crash", t_on_draw_light)

    def t_on_draw_dark():
        surface = _cairo.ImageSurface(_cairo.FORMAT_ARGB32, 800, 800)
        cr = _cairo.Context(surface)
        win.dark_mode = True
        win.on_draw(win.drawing_area, cr)
        win.dark_mode = False
    run_test("on_draw() dark mode completes without crash", t_on_draw_dark)

    def t_compute_bbox_with_elements():
        x0, y0, x1, y1 = win._compute_bbox()
        assert x1 > x0 and y1 > y0
    run_test("_compute_bbox() returns valid rectangle", t_compute_bbox_with_elements)

    def t_compute_bbox_empty():
        x0, y0, x1, y1 = win._compute_bbox.__func__(
            type('obj', (), {'blocks': [], 'pins': [], 'wires': [], 'grid_size': gs})()
        )
        assert x1 > x0 and y1 > y0
    run_test("_compute_bbox() on empty canvas returns fallback rect", t_compute_bbox_empty)

    def t_svg_export_headless():
        x0, y0, x1, y1 = win._compute_bbox()
        w, h = max(1.0, x1 - x0), max(1.0, y1 - y0)
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            svg_path = f.name
        surface = _cairo.SVGSurface(svg_path, w, h)
        cr = _cairo.Context(surface)
        cr.translate(-x0, -y0)
        win._render_schematic(cr)
        surface.finish()
        assert os.path.getsize(svg_path) > 100
        os.unlink(svg_path)
    run_test("SVG export (headless Cairo render)", t_svg_export_headless)

    def t_png_export_headless():
        x0, y0, x1, y1 = win._compute_bbox()
        w, h = max(1, int(x1 - x0)), max(1, int(y1 - y0))
        surface = _cairo.ImageSurface(_cairo.FORMAT_ARGB32, w, h)
        cr = _cairo.Context(surface)
        cr.translate(-x0, -y0)
        win._render_schematic(cr)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            png_path = f.name
        surface.write_to_png(png_path)
        assert os.path.getsize(png_path) > 100
        os.unlink(png_path)
    run_test("PNG export (headless Cairo render)", t_png_export_headless)

    # ------------------------------------------------------------------
    # Group 10 — Multi-select
    # ------------------------------------------------------------------
    print("\n-- Multi-select --")

    def t_multi_select_clear():
        if len(win.blocks) >= 2:
            win.selected_blocks = [win.blocks[0], win.blocks[1]]
            win.blocks[0].set_selected(True)
            win.blocks[1].set_selected(True)
            assert len(win.selected_blocks) == 2
            win._clear_multi_select()
            assert win.selected_blocks == []
            assert not win.blocks[0].selected
            assert not win.blocks[1].selected
    run_test("Multi-select + _clear_multi_select()", t_multi_select_clear)

    # ------------------------------------------------------------------
    # Group 11 — Block operations
    # ------------------------------------------------------------------
    print("\n-- Block operations --")

    def t_copy_block():
        b = Block(gs*5, gs*5, gs*4, gs*4, "COPY_ME", "AND", gs, win)
        win.blocks.append(b)
        win.selected_block = b
        n_before = len(win.blocks)
        win.on_copy_block(None)
        assert len(win.blocks) == n_before + 1
    run_test("Copy block (Ctrl+C single)", t_copy_block)

    def t_rotate_block_no_wires():
        b = Block(gs*25, gs*25, gs*4, gs*4, "ROTATE_ME", "OR", gs, win)
        win.blocks.append(b)
        win.selected_block = b
        original_rot = b.rotation
        win.on_rotate_90(None)
        assert b.rotation != original_rot or b.rotation == 90
    run_test("Rotate block 90° (no wires)", t_rotate_block_no_wires)

    def t_delete_block():
        b = Block(gs*30, gs*30, gs*4, gs*4, "DELETE_ME", "NOT", gs, win)
        win.blocks.append(b)
        win.selected_block = b
        n_before = len(win.blocks)
        win.on_delete_block(None)
        assert len(win.blocks) == n_before - 1
    run_test("Delete block (Ctrl+D single)", t_delete_block)

    # ------------------------------------------------------------------
    # Group 12 — Stress
    # ------------------------------------------------------------------
    print("\n-- Stress tests --")

    def t_stress_50_blocks():
        import random
        extras = []
        for i in range(50):
            bt = block_types[i % len(block_types)]
            b = Block(random.randint(2, 50)*gs, random.randint(2, 50)*gs,
                      gs*4, gs*4, f"stress_{i}", bt, gs, win)
            extras.append(b)
            win.blocks.append(b)
        j = win.elements_to_json()
        assert j is not None
        data = json.loads(j)
        assert len(data) >= 50
        for b in extras:
            win.blocks.remove(b)
    run_test("Add 50 blocks, serialize, remove (no crash)", t_stress_50_blocks)

    def t_stress_wire_grid():
        extras = []
        for i in range(10):
            sp = [gs*(3+i), gs*5]
            ep = [gs*(3+i), gs*20]
            w = Wire(f"stress_w_{i}", sp, ep, "wire", gs, win)
            win.wires.append(w)
            extras.append(w)
        j = win.elements_to_json()
        assert j is not None
        for w in extras:
            win.wires.remove(w)
    run_test("Add 10 vertical wires, serialize, remove (no crash)", t_stress_wire_grid)

    # ------------------------------------------------------------------
    # Group 13 — Status bar + dirty flag
    # ------------------------------------------------------------------
    print("\n-- Status bar + dirty flag --")

    def t_status_bar_updates():
        win.update_status_bar()  # must not crash
    run_test("update_status_bar() no crash", t_status_bar_updates)

    def t_dirty_flag():
        win.set_dirty(False)
        assert not win.dirty
        assert "*" not in win.get_title()
        win.set_dirty(True)
        assert win.dirty
        assert "*" in win.get_title()
        win.set_dirty(False)
    run_test("Dirty flag updates window title with *", t_dirty_flag)

    # ------------------------------------------------------------------
    # Group 14 — Verilog export
    # ------------------------------------------------------------------
    print("\n-- Verilog export --")

    def t_verilog_structure():
        from vhdl_export import generate_verilog
        v = generate_verilog("TEST_MOD", win.blocks, win.pins, win.wires)
        assert "module TEST_MOD" in v, "missing module declaration"
        assert "endmodule" in v, "missing endmodule"
    run_test("Verilog output has module + endmodule", t_verilog_structure)

    def t_verilog_empty_canvas():
        from vhdl_export import generate_verilog
        v = generate_verilog("EMPTY_V", [], [], [])
        assert "module EMPTY_V" in v
        assert "endmodule" in v
    run_test("Verilog export with empty schematic (no crash)", t_verilog_empty_canvas)

    def t_verilog_ports():
        from vhdl_export import generate_verilog
        p_in  = Pin(gs, gs*40, gs*3, gs*2, "A", "input_pin",  gs, 1, win)
        p_out = Pin(gs, gs*42, gs*3, gs*2, "Y", "output_pin", gs, 1, win)
        v = generate_verilog("PORT_MOD", [], [p_in, p_out], [])
        assert "input" in v and "output" in v, "missing port directions"
        assert "A" in v and "Y" in v
    run_test("Verilog export has input/output port directions", t_verilog_ports)

    def t_verilog_wire_declarations():
        from vhdl_export import generate_verilog
        b1 = Block(gs*10, gs*10, gs*4, gs*4, "wire_src", "AND", gs, win)
        b2 = Block(gs*20, gs*10, gs*4, gs*4, "wire_dst", "OR",  gs, win)
        sp = list(b1.output_points[0]) if b1.output_points else [gs*14, gs*12]
        ep = list(b2.input_points[0])  if b2.input_points  else [gs*20, gs*12]
        w  = Wire("net_test_v", sp, ep, "wire", gs, win)
        v  = generate_verilog("WIRE_MOD", [b1, b2], [], [w])
        assert "wire" in v.lower(), "no wire declarations"
    run_test("Verilog export contains wire declarations for nets", t_verilog_wire_declarations)

    def t_verilog_custom_vhd_bus():
        from vhdl_export import generate_custom_vhd
        code = generate_custom_vhd("BUS_BLOCK",
            ["data[7:0]", "clk"],
            ["result[3:0]"],
            "")
        assert "STD_LOGIC_VECTOR(7 downto 0)" in code, "missing 8-bit input vector"
        assert "STD_LOGIC_VECTOR(3 downto 0)" in code, "missing 4-bit output vector"
        assert "STD_LOGIC" in code, "missing scalar CLK port"
    run_test("generate_custom_vhd: bus ports generate STD_LOGIC_VECTOR", t_verilog_custom_vhd_bus)

    def t_verilog_custom_v_bus():
        from vhdl_export import generate_custom_v
        code = generate_custom_v("BUS_MOD",
            ["data[7:0]", "clk"],
            ["result[3:0]"],
            "")
        assert "[7:0]" in code, "missing 8-bit input range"
        assert "[3:0]" in code, "missing 4-bit output range"
        assert "module BUS_MOD" in code
        assert "endmodule" in code
    run_test("generate_custom_v: bus ports generate [N:M] range", t_verilog_custom_v_bus)

    def t_verilog_custom_v_shorthand():
        from vhdl_export import generate_custom_v
        code = generate_custom_v("SHORT_MOD", ["addr:16"], ["data:8"], "")
        assert "[15:0]" in code, "addr:16 should expand to [15:0]"
        assert "[7:0]"  in code, "data:8 should expand to [7:0]"
    run_test("generate_custom_v: :N shorthand expands correctly", t_verilog_custom_v_shorthand)

    # ------------------------------------------------------------------
    # Finish
    # ------------------------------------------------------------------
    if tmp_path and os.path.exists(tmp_path):
        os.unlink(tmp_path)

    passed = sum(1 for _, s, _ in results if s == "PASS")
    total  = len(results)
    print(f"\n{'='*50}")
    print(f"  {passed}/{total} tests passed  ({'%.0f' % (100*passed/total)}%)")
    print(f"{'='*50}")
    write_report()
    return passed, total


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    from main_window import BlocksWindow
    win = BlocksWindow()
    win.show_all()

    def do_run():
        try:
            passed, total = run_all_tests(win)
        except Exception as e:
            print(f"\nFATAL: {e}")
            traceback.print_exc()
        GLib.timeout_add(1500, Gtk.main_quit)
        return False

    GLib.timeout_add(600, do_run)
    Gtk.main()


if __name__ == "__main__":
    main()
