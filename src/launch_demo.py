#!/usr/bin/env python3
"""
launch_demo.py -- open SVCG with a pre-built JK flip-flop schematic.

JKFF port geometry (no rotation, block size w×h per cell):
    Row 0 (y):      J  [0]   CLK [1]   K  [2]     ← at (x,y), (x+w,y), (x+2w,y)
    Row 1 (y+h):    PRE[3]             CLR[4]      ← at (x,y+h), (x+2w,y+h)
    Row 2 (y+2h):   Q  [0]             Q' [1]     ← at (x,y+2h), (x+2w,y+2h)

IO pin connection point = bottom-centre = (px + pw/2, py + ph).
All wires are perfectly straight (vertical or horizontal).
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main_window import BlocksWindow
from blocks import Block
from pins import Pin
from wire import Wire
from drawing_area import DrawingArea


def _connect(win, src, si, sr, dst, di, dr, net):
    def pt(obj, idx, role):
        if role == "output": return list(obj.output_points[idx])
        if role == "input":  return list(obj.input_points[idx])
        return list(obj.connection_points[idx])
    w = Wire(net, pt(src, si, sr), pt(dst, di, dr), "wire", win.grid_size, win)
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
    reg(src, si, sr, w.id)
    reg(dst, di, dr, w.id)
    win.wires.append(w)
    return w


def build_demo(win):
    gs = win.grid_size  # 20 px

    win.drawing_area.create_grid(DrawingArea.CANVAS_SIZE, DrawingArea.CANVAS_SIZE, gs)

    # ------------------------------------------------------------------
    # JKFF block  (w=gs*6, h=gs*6 per cell → spans 2w × 2h = gs*12 × gs*12)
    # Placed at (gs*12, gs*8) so ports land on clean grid multiples.
    #
    #   J  (gs*12, gs*8)  = (240,160)
    #   CLK(gs*18, gs*8)  = (360,160)
    #   K  (gs*24, gs*8)  = (480,160)
    #   PRE(gs*12, gs*14) = (240,280)
    #   CLR(gs*24, gs*14) = (480,280)
    #   Q  (gs*12, gs*20) = (240,400)
    #   Q' (gs*24, gs*20) = (480,400)
    # ------------------------------------------------------------------
    jkff = Block(gs*12, gs*8, gs*6, gs*6, "JK Flip-Flop", "JKFF", gs, win)

    # ------------------------------------------------------------------
    # IO pins — each placed so its connection point (px+pw/2, py+ph)
    # lands exactly on the corresponding JKFF port.
    # Vertical wires (J, CLK, K, Q, Q'): pin above/below, 3-grid gap.
    # Horizontal wires (PRE, CLR):        pin left/right, same y row.
    # ------------------------------------------------------------------

    # --- J input  → pin above, connection at (240, 160)
    #     py+ph=160-gs*3=100  ph=gs*2=40  → py=60=gs*3
    #     px+pw/2=240   pw=gs*4=80       → px=200=gs*10
    pJ   = Pin(gs*10, gs*3,  gs*4, gs*2, "J",     "input_pin",  gs, 1, win)

    # --- CLK input → pin above, connection at (360, 160)
    pCLK = Pin(gs*16, gs*3,  gs*4, gs*2, "CLK",   "CLK",        gs, 1, win)

    # --- K input   → pin above, connection at (480, 160)
    pK   = Pin(gs*22, gs*3,  gs*4, gs*2, "K",     "input_pin",  gs, 1, win)

    # --- PRE input → pin on left, horizontal wire to (240, 280)
    #     py+ph=280   ph=gs*2=40  → py=240=gs*12
    #     connection_x = px+pw/2 = 80 (far left, horizontal wire rightward)
    pPRE = Pin(gs*2,  gs*12, gs*4, gs*2, "PRE",   "input_pin",  gs, 1, win)

    # --- CLR (reset) → pin on right, horizontal wire to (480, 280)
    #     py+ph=280   ph=gs*2=40  → py=240=gs*12
    #     connection_x = px+pw/2 = 600 (far right, horizontal wire leftward)
    pCLR = Pin(gs*28, gs*12, gs*4, gs*2, "CLR",   "input_pin",  gs, 1, win)

    # --- Q output  → pin below, connection at (240, 460)
    #     py+ph = 400+gs*3 = 460  ph=gs*2=40  → py=420=gs*21
    #     px+pw/2=240   pw=gs*4=80            → px=200=gs*10
    pQ   = Pin(gs*10, gs*21, gs*4, gs*2, "Q",     "output_pin", gs, 1, win)

    # --- Q' output → pin below, connection at (480, 460)
    pQb  = Pin(gs*22, gs*21, gs*4, gs*2, "Q_bar", "output_pin", gs, 1, win)

    win.blocks.append(jkff)
    win.pins.extend([pJ, pCLK, pK, pPRE, pCLR, pQ, pQb])

    win.drawing_area.create_grid(DrawingArea.CANVAS_SIZE, DrawingArea.CANVAS_SIZE, gs)

    # ------------------------------------------------------------------
    # Wires (all straight: vertical or horizontal)
    # ------------------------------------------------------------------
    _connect(win, pJ,   0, "pin",    jkff, 0, "input",  "J")
    _connect(win, pCLK, 0, "pin",    jkff, 1, "input",  "CLK")
    _connect(win, pK,   0, "pin",    jkff, 2, "input",  "K")
    _connect(win, pPRE, 0, "pin",    jkff, 3, "input",  "PRE")
    _connect(win, pCLR, 0, "pin",    jkff, 4, "input",  "CLR")
    _connect(win, jkff, 0, "output", pQ,   0, "pin",    "Q")
    _connect(win, jkff, 1, "output", pQb,  0, "pin",    "Q_bar")


def main():
    win = BlocksWindow()
    win.show_all()

    def setup():
        build_demo(win)
        win.update_json()
        win.update_status_bar()
        win.drawing_area.queue_draw()
        win.scrolled_window.get_hadjustment().set_value(0)
        win.scrolled_window.get_vadjustment().set_value(0)
        return False

    GLib.timeout_add(400, setup)
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()


if __name__ == "__main__":
    main()
