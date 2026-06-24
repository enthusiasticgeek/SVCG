#!/usr/bin/env python3
"""
yosys_importer.py -- import a Yosys JSON synthesis netlist into the SVCG canvas

Usage
-----
Generate the JSON with Yosys:
    yosys -p "synth -flatten; write_json out.json" design.v

Then use File > Import Yosys Netlist... in SVCG.

Supported cell types
--------------------
Yosys primitives: $_{AND,OR,NOT,NAND,NOR,XOR,XNOR,BUF,AND3,OR3,NAND3,NOR3,
  XOR3,AND4,OR4,NAND4,NOR4,MUX,DFF_P,DFF_N,DLATCH_P,DLATCH_N,SR,HA,FA}_
Yosys internal: $and, $or, $not, $nand, $nor, $xor, $xnor, $mux, $dff,
  $dffe, $sdff, $adff, $dlatch, $ha, $fa
SVCG cell library names: AND_GATE, OR_GATE, …, BUF_GATE, AND3_GATE, …,
  DLATCH, SRLATCH, DEC_2TO4, DEC_3TO8, ENC_4TO2, DEMUX_1TO4, DEMUX_1TO8,
  RCA_4BIT, COMP_4BIT, SHREG_4BIT, CNT_4BIT, CNT_4BIT_UD, HA, FA, FA_GC, FA_WC,
  MUX2x1, MUX4x1, MUX8x1, TristateBuffer{,4,8}, DFF, JKFF, SRFF, TFF, DFF_PIPELINE
"""
import json
import math
import random


# ---------------------------------------------------------------------------
# Type mappings
# ---------------------------------------------------------------------------

YOSYS_TO_SVCG = {
    # 2-input primitives
    "$_AND_":   "AND",   "$and":   "AND",
    "$_OR_":    "OR",    "$or":    "OR",
    "$_NOT_":   "NOT",   "$not":   "NOT",
    "$_NAND_":  "NAND",  "$nand":  "NAND",
    "$_NOR_":   "NOR",   "$nor":   "NOR",
    "$_XOR_":   "XOR",   "$xor":   "XOR",
    "$_XNOR_":  "XNOR",  "$xnor":  "XNOR",
    "$_BUF_":   "BUF",
    # 3-input gates (ABC9 tech-mapped)
    "$_AND3_":  "AND3",  "$_OR3_":  "OR3",
    "$_NAND3_": "NAND3", "$_NOR3_": "NOR3",
    "$_XOR3_":  "XOR3",
    # 4-input gates
    "$_AND4_":  "AND4",  "$_OR4_":  "OR4",
    "$_NAND4_": "NAND4", "$_NOR4_": "NOR4",
    # Mux / FF
    "$_MUX_":   "MUX_2X1", "$mux": "MUX_2X1",
    "$_DFF_P_": "DFF",   "$_DFF_N_": "DFF",
    "$dff":     "DFF",   "$dffe":  "DFF",
    "$sdff":    "DFF",   "$adff":  "DFF",
    # Latches (fixed: $dlatch is a D-latch, not a DFF)
    "$dlatch":  "DLATCH", "$_DLATCH_P_": "DLATCH", "$_DLATCH_N_": "DLATCH",
    "$_SR_":    "SRLATCH",
    # Adders
    "$_HA_":    "HA",    "$ha":    "HA",
    "$_FA_":    "FA",    "$fa":    "FA",
    # SVCG module names (when mapped through the SVCG Verilog cell library)
    "AND_GATE":   "AND",   "OR_GATE":   "OR",   "NOT_GATE":  "NOT",
    "NAND_GATE":  "NAND",  "NOR_GATE":  "NOR",  "XOR_GATE":  "XOR",
    "XNOR_GATE":  "XNOR",  "BUF_GATE":  "BUF",
    "AND3_GATE":  "AND3",  "OR3_GATE":  "OR3",  "NAND3_GATE":"NAND3",
    "NOR3_GATE":  "NOR3",  "XOR3_GATE": "XOR3",
    "AND4_GATE":  "AND4",  "OR4_GATE":  "OR4",  "NAND4_GATE":"NAND4",
    "NOR4_GATE":  "NOR4",
    "MUX2x1":     "MUX_2X1", "MUX4x1": "MUX_4X1", "MUX8x1": "MUX_8X1",
    "DFF":        "DFF",   "JKFF":   "JKFF",  "SRFF":  "SRFF",
    "TFF":        "TFF",   "DFF_PIPELINE": "DFF_PIPELINE",
    "DLATCH":     "DLATCH", "SRLATCH": "SRLATCH",
    "DEC_2TO4":   "DEC_2TO4", "DEC_3TO8": "DEC_3TO8", "ENC_4TO2": "ENC_4TO2",
    "DEMUX_1TO4": "DEMUX_1TO4", "DEMUX_1TO8": "DEMUX_1TO8",
    "RCA_4BIT":   "RCA_4BIT", "COMP_4BIT": "COMP_4BIT",
    "SHREG_4BIT": "SHREG_4BIT", "CNT_4BIT": "CNT_4BIT", "CNT_4BIT_UD": "CNT_4BIT_UD",
    "HA":         "HA",    "FA":    "FA",   "FA_GC": "FA_GC", "FA_WC": "FA_WC",
    "TristateBuffer":  "TRISTATEBUF_2",
    "TristateBuffer4": "TRISTATEBUF_4",
    "TristateBuffer8": "TRISTATEBUF_8",
}

# Maps (svcg_block_type, yosys_port_name) -> ("in"|"out", pin_index)
# Port names follow SVCG VHDL/Verilog templates; Yosys ABC alternatives (A/B/Y) also listed.
PORT_MAP = {
    # ── 2-input gates ────────────────────────────────────────────────────────
    ("AND",  "IN1"): ("in", 0), ("AND",  "IN2"): ("in", 1), ("AND",  "OUT1"): ("out", 0),
    ("AND",  "A"):   ("in", 0), ("AND",  "B"):   ("in", 1), ("AND",  "Y"):    ("out", 0),
    ("OR",   "IN1"): ("in", 0), ("OR",   "IN2"): ("in", 1), ("OR",   "OUT1"): ("out", 0),
    ("OR",   "A"):   ("in", 0), ("OR",   "B"):   ("in", 1), ("OR",   "Y"):    ("out", 0),
    ("NOT",  "IN1"): ("in", 0), ("NOT",  "OUT1"): ("out", 0),
    ("NOT",  "A"):   ("in", 0), ("NOT",  "Y"):    ("out", 0),
    ("NAND", "IN1"): ("in", 0), ("NAND", "IN2"): ("in", 1), ("NAND", "OUT1"): ("out", 0),
    ("NAND", "A"):   ("in", 0), ("NAND", "B"):   ("in", 1), ("NAND", "Y"):    ("out", 0),
    ("NOR",  "IN1"): ("in", 0), ("NOR",  "IN2"): ("in", 1), ("NOR",  "OUT1"): ("out", 0),
    ("NOR",  "A"):   ("in", 0), ("NOR",  "B"):   ("in", 1), ("NOR",  "Y"):    ("out", 0),
    ("XOR",  "IN1"): ("in", 0), ("XOR",  "IN2"): ("in", 1), ("XOR",  "OUT1"): ("out", 0),
    ("XOR",  "A"):   ("in", 0), ("XOR",  "B"):   ("in", 1), ("XOR",  "Y"):    ("out", 0),
    ("XNOR", "IN1"): ("in", 0), ("XNOR", "IN2"): ("in", 1), ("XNOR", "OUT1"): ("out", 0),
    ("XNOR", "A"):   ("in", 0), ("XNOR", "B"):   ("in", 1), ("XNOR", "Y"):    ("out", 0),
    # ── Buffer ────────────────────────────────────────────────────────────────
    ("BUF", "IN1"): ("in", 0), ("BUF", "OUT1"): ("out", 0),
    ("BUF", "A"):   ("in", 0), ("BUF", "Y"):    ("out", 0),
    # ── 3-input gates ────────────────────────────────────────────────────────
    ("AND3",  "IN1"): ("in", 0), ("AND3",  "IN2"): ("in", 1), ("AND3",  "IN3"): ("in", 2), ("AND3",  "OUT1"): ("out", 0),
    ("AND3",  "A"):   ("in", 0), ("AND3",  "B"):   ("in", 1), ("AND3",  "C"):   ("in", 2), ("AND3",  "Y"):    ("out", 0),
    ("OR3",   "IN1"): ("in", 0), ("OR3",   "IN2"): ("in", 1), ("OR3",   "IN3"): ("in", 2), ("OR3",   "OUT1"): ("out", 0),
    ("OR3",   "A"):   ("in", 0), ("OR3",   "B"):   ("in", 1), ("OR3",   "C"):   ("in", 2), ("OR3",   "Y"):    ("out", 0),
    ("NAND3", "IN1"): ("in", 0), ("NAND3", "IN2"): ("in", 1), ("NAND3", "IN3"): ("in", 2), ("NAND3", "OUT1"): ("out", 0),
    ("NAND3", "A"):   ("in", 0), ("NAND3", "B"):   ("in", 1), ("NAND3", "C"):   ("in", 2), ("NAND3", "Y"):    ("out", 0),
    ("NOR3",  "IN1"): ("in", 0), ("NOR3",  "IN2"): ("in", 1), ("NOR3",  "IN3"): ("in", 2), ("NOR3",  "OUT1"): ("out", 0),
    ("NOR3",  "A"):   ("in", 0), ("NOR3",  "B"):   ("in", 1), ("NOR3",  "C"):   ("in", 2), ("NOR3",  "Y"):    ("out", 0),
    ("XOR3",  "IN1"): ("in", 0), ("XOR3",  "IN2"): ("in", 1), ("XOR3",  "IN3"): ("in", 2), ("XOR3",  "OUT1"): ("out", 0),
    ("XOR3",  "A"):   ("in", 0), ("XOR3",  "B"):   ("in", 1), ("XOR3",  "C"):   ("in", 2), ("XOR3",  "Y"):    ("out", 0),
    # ── 4-input gates ────────────────────────────────────────────────────────
    ("AND4",  "IN1"): ("in", 0), ("AND4",  "IN2"): ("in", 1), ("AND4",  "IN3"): ("in", 2), ("AND4",  "IN4"): ("in", 3), ("AND4",  "OUT1"): ("out", 0),
    ("AND4",  "A"):   ("in", 0), ("AND4",  "B"):   ("in", 1), ("AND4",  "C"):   ("in", 2), ("AND4",  "D"):   ("in", 3), ("AND4",  "Y"):    ("out", 0),
    ("OR4",   "IN1"): ("in", 0), ("OR4",   "IN2"): ("in", 1), ("OR4",   "IN3"): ("in", 2), ("OR4",   "IN4"): ("in", 3), ("OR4",   "OUT1"): ("out", 0),
    ("OR4",   "A"):   ("in", 0), ("OR4",   "B"):   ("in", 1), ("OR4",   "C"):   ("in", 2), ("OR4",   "D"):   ("in", 3), ("OR4",   "Y"):    ("out", 0),
    ("NAND4", "IN1"): ("in", 0), ("NAND4", "IN2"): ("in", 1), ("NAND4", "IN3"): ("in", 2), ("NAND4", "IN4"): ("in", 3), ("NAND4", "OUT1"): ("out", 0),
    ("NAND4", "A"):   ("in", 0), ("NAND4", "B"):   ("in", 1), ("NAND4", "C"):   ("in", 2), ("NAND4", "D"):   ("in", 3), ("NAND4", "Y"):    ("out", 0),
    ("NOR4",  "IN1"): ("in", 0), ("NOR4",  "IN2"): ("in", 1), ("NOR4",  "IN3"): ("in", 2), ("NOR4",  "IN4"): ("in", 3), ("NOR4",  "OUT1"): ("out", 0),
    ("NOR4",  "A"):   ("in", 0), ("NOR4",  "B"):   ("in", 1), ("NOR4",  "C"):   ("in", 2), ("NOR4",  "D"):   ("in", 3), ("NOR4",  "Y"):    ("out", 0),
    # ── Multiplexers ─────────────────────────────────────────────────────────
    ("MUX_2X1","I0"): ("in", 0), ("MUX_2X1","I1"): ("in", 1), ("MUX_2X1","S0"): ("in", 2),
    ("MUX_2X1","EN"): ("in", 3), ("MUX_2X1","O0"): ("out", 0),
    ("MUX_2X1","A"):  ("in", 0), ("MUX_2X1","B"):  ("in", 1), ("MUX_2X1","S"):  ("in", 2),
    ("MUX_2X1","Y"):  ("out", 0),
    # ── Flip-flops ────────────────────────────────────────────────────────────
    ("DFF", "D"):   ("in", 0), ("DFF", "CLK"): ("in", 1), ("DFF", "C"):  ("in", 1),
    ("DFF", "PRE"): ("in", 2), ("DFF", "CLR"): ("in", 3), ("DFF", "EN"): ("in", 2),
    ("DFF", "Q"):   ("out", 0), ("DFF", "Q_bar"): ("out", 1),
    ("JKFF","J"):   ("in", 0), ("JKFF","CLK"): ("in", 1), ("JKFF","K"):   ("in", 2),
    ("JKFF","PRE"): ("in", 3), ("JKFF","CLR"): ("in", 4),
    ("JKFF","Q"):   ("out", 0), ("JKFF","Q_bar"): ("out", 1),
    ("SRFF","S"):   ("in", 0), ("SRFF","CLK"): ("in", 1), ("SRFF","R"):   ("in", 2),
    ("SRFF","PRE"): ("in", 3), ("SRFF","CLR"): ("in", 4),
    ("SRFF","Q"):   ("out", 0), ("SRFF","Q_bar"): ("out", 1),
    ("TFF", "T"):   ("in", 0), ("TFF", "CLK"): ("in", 1),
    ("TFF", "PRE"): ("in", 2), ("TFF", "CLR"): ("in", 3),
    ("TFF", "Q"):   ("out", 0), ("TFF", "Q_bar"): ("out", 1),
    ("DFF_PIPELINE","D"): ("in", 0), ("DFF_PIPELINE","CLK"): ("in", 1),
    ("DFF_PIPELINE","N_RST"): ("in", 2), ("DFF_PIPELINE","Q"): ("out", 0),
    # ── Latches ───────────────────────────────────────────────────────────────
    ("DLATCH","D"):  ("in", 0), ("DLATCH","EN"):    ("in", 1),
    ("DLATCH","Q"):  ("out", 0), ("DLATCH","Q_bar"): ("out", 1),
    ("SRLATCH","S"): ("in", 0), ("SRLATCH","R"):    ("in", 1),
    ("SRLATCH","Q"): ("out", 0), ("SRLATCH","Q_bar"):("out", 1),
    # ── Decoders / Encoders / Demux ───────────────────────────────────────────
    ("DEC_2TO4","A"): ("in", 0), ("DEC_2TO4","B"): ("in", 1), ("DEC_2TO4","EN"): ("in", 2),
    ("DEC_2TO4","Y0"): ("out", 0), ("DEC_2TO4","Y1"): ("out", 1),
    ("DEC_2TO4","Y2"): ("out", 2), ("DEC_2TO4","Y3"): ("out", 3),
    ("DEC_3TO8","A"): ("in", 0), ("DEC_3TO8","B"): ("in", 1), ("DEC_3TO8","C"): ("in", 2),
    ("DEC_3TO8","EN"): ("in", 3),
    ("DEC_3TO8","Y0"): ("out", 0), ("DEC_3TO8","Y1"): ("out", 1),
    ("DEC_3TO8","Y2"): ("out", 2), ("DEC_3TO8","Y3"): ("out", 3),
    ("DEC_3TO8","Y4"): ("out", 4), ("DEC_3TO8","Y5"): ("out", 5),
    ("DEC_3TO8","Y6"): ("out", 6), ("DEC_3TO8","Y7"): ("out", 7),
    ("ENC_4TO2","I0"): ("in", 0), ("ENC_4TO2","I1"): ("in", 1),
    ("ENC_4TO2","I2"): ("in", 2), ("ENC_4TO2","I3"): ("in", 3),
    ("ENC_4TO2","Y0"): ("out", 0), ("ENC_4TO2","Y1"): ("out", 1),
    ("ENC_4TO2","VALID"): ("out", 2),
    ("DEMUX_1TO4","I"): ("in", 0), ("DEMUX_1TO4","S0"): ("in", 1),
    ("DEMUX_1TO4","S1"): ("in", 2), ("DEMUX_1TO4","EN"): ("in", 3),
    ("DEMUX_1TO4","O0"): ("out", 0), ("DEMUX_1TO4","O1"): ("out", 1),
    ("DEMUX_1TO4","O2"): ("out", 2), ("DEMUX_1TO4","O3"): ("out", 3),
    ("DEMUX_1TO8","I"): ("in", 0), ("DEMUX_1TO8","S0"): ("in", 1),
    ("DEMUX_1TO8","S1"): ("in", 2), ("DEMUX_1TO8","S2"): ("in", 3),
    ("DEMUX_1TO8","EN"): ("in", 4),
    ("DEMUX_1TO8","O0"): ("out", 0), ("DEMUX_1TO8","O1"): ("out", 1),
    ("DEMUX_1TO8","O2"): ("out", 2), ("DEMUX_1TO8","O3"): ("out", 3),
    ("DEMUX_1TO8","O4"): ("out", 4), ("DEMUX_1TO8","O5"): ("out", 5),
    ("DEMUX_1TO8","O6"): ("out", 6), ("DEMUX_1TO8","O7"): ("out", 7),
    # ── Arithmetic ───────────────────────────────────────────────────────────
    ("HA",  "A"):   ("in", 0), ("HA",  "B"):   ("in", 1),
    ("HA",  "SO"):  ("out", 0), ("HA", "CO"):  ("out", 1),
    ("HA",  "SUM"): ("out", 0), ("HA", "Y"):   ("out", 0),
    ("FA",  "A"):   ("in", 0), ("FA",  "B"):   ("in", 1), ("FA",  "SI"): ("in", 2), ("FA",  "CI"): ("in", 3),
    ("FA",  "SO"):  ("out", 0), ("FA", "CO"):  ("out", 1),
    ("FA_GC","A"):  ("in", 0), ("FA_GC","B"):  ("in", 1), ("FA_GC","SI"): ("in", 2), ("FA_GC","CI"): ("in", 3),
    ("FA_GC","SO"): ("out", 0), ("FA_GC","CO"): ("out", 1),
    ("FA_WC","A"):  ("in", 0), ("FA_WC","B"):  ("in", 1), ("FA_WC","SI"): ("in", 2), ("FA_WC","CI"): ("in", 3),
    ("FA_WC","SO"): ("out", 0), ("FA_WC","CO"): ("out", 1),
    ("RCA_4BIT","A0"): ("in", 0), ("RCA_4BIT","A1"): ("in", 1),
    ("RCA_4BIT","A2"): ("in", 2), ("RCA_4BIT","A3"): ("in", 3),
    ("RCA_4BIT","B0"): ("in", 4), ("RCA_4BIT","B1"): ("in", 5),
    ("RCA_4BIT","B2"): ("in", 6), ("RCA_4BIT","B3"): ("in", 7),
    ("RCA_4BIT","CIN"): ("in", 8),
    ("RCA_4BIT","S0"): ("out", 0), ("RCA_4BIT","S1"): ("out", 1),
    ("RCA_4BIT","S2"): ("out", 2), ("RCA_4BIT","S3"): ("out", 3),
    ("RCA_4BIT","COUT"): ("out", 4),
    ("COMP_4BIT","A0"): ("in", 0), ("COMP_4BIT","A1"): ("in", 1),
    ("COMP_4BIT","A2"): ("in", 2), ("COMP_4BIT","A3"): ("in", 3),
    ("COMP_4BIT","B0"): ("in", 4), ("COMP_4BIT","B1"): ("in", 5),
    ("COMP_4BIT","B2"): ("in", 6), ("COMP_4BIT","B3"): ("in", 7),
    ("COMP_4BIT","ALB"): ("out", 0), ("COMP_4BIT","AEB"): ("out", 1), ("COMP_4BIT","AGB"): ("out", 2),
    # ── Sequential ───────────────────────────────────────────────────────────
    ("SHREG_4BIT","SIN"): ("in", 0), ("SHREG_4BIT","CLK"): ("in", 1), ("SHREG_4BIT","RST"): ("in", 2),
    ("SHREG_4BIT","Q0"): ("out", 0), ("SHREG_4BIT","Q1"): ("out", 1),
    ("SHREG_4BIT","Q2"): ("out", 2), ("SHREG_4BIT","Q3"): ("out", 3),
    ("CNT_4BIT","CLK"): ("in", 0), ("CNT_4BIT","RST"): ("in", 1), ("CNT_4BIT","EN"): ("in", 2),
    ("CNT_4BIT","Q0"): ("out", 0), ("CNT_4BIT","Q1"): ("out", 1),
    ("CNT_4BIT","Q2"): ("out", 2), ("CNT_4BIT","Q3"): ("out", 3), ("CNT_4BIT","TC"): ("out", 4),
    ("CNT_4BIT_UD","CLK"): ("in", 0), ("CNT_4BIT_UD","RST"): ("in", 1),
    ("CNT_4BIT_UD","EN"): ("in", 2), ("CNT_4BIT_UD","DIR"): ("in", 3),
    ("CNT_4BIT_UD","Q0"): ("out", 0), ("CNT_4BIT_UD","Q1"): ("out", 1),
    ("CNT_4BIT_UD","Q2"): ("out", 2), ("CNT_4BIT_UD","Q3"): ("out", 3),
    ("CNT_4BIT_UD","TC"): ("out", 4),
}


# ---------------------------------------------------------------------------
# Placement helpers
# ---------------------------------------------------------------------------

def _topo_levels(cells, port_connections):
    """
    Assign each cell a depth level (0 = driven only by primary inputs).
    Returns dict cell_name -> level.
    """
    # nets driven by each cell's outputs
    cell_drives = {}   # net_bit -> cell_name
    for cname, (btype, connections) in cells.items():
        pmap = {k: v for k, v in PORT_MAP.items() if k[0] == btype}
        for port, bits in connections.items():
            info = pmap.get((btype, port))
            if info and info[0] == "out":
                for b in bits:
                    if b not in (0, 1):
                        cell_drives[b] = cname

    levels = {c: 0 for c in cells}
    changed = True
    while changed:
        changed = False
        for cname, (btype, connections) in cells.items():
            pmap = {k: v for k, v in PORT_MAP.items() if k[0] == btype}
            for port, bits in connections.items():
                info = pmap.get((btype, port))
                if info and info[0] == "in":
                    for b in bits:
                        if b not in (0, 1) and b in cell_drives:
                            driver_level = levels.get(cell_drives[b], 0)
                            if driver_level + 1 > levels[cname]:
                                levels[cname] = driver_level + 1
                                changed = True
    return levels


def _place_cells(cells, port_connections, grid_size):
    """
    Return dict cell_name -> (x, y) canvas coordinates.
    Columns = topo level, rows = position within column.
    """
    levels = _topo_levels(cells, port_connections)
    by_level = {}
    for cname, lvl in levels.items():
        by_level.setdefault(lvl, []).append(cname)

    cell_w = grid_size * 4   # block width in canvas pixels
    cell_h = grid_size * 4
    col_gap = grid_size * 8  # horizontal spacing between columns
    row_gap = grid_size * 6  # vertical spacing within a column
    margin  = grid_size * 3  # top-left margin

    positions = {}
    for lvl, names in sorted(by_level.items()):
        x = margin + lvl * (cell_w + col_gap)
        for row, cname in enumerate(names):
            y = margin + row * (cell_h + row_gap)
            positions[cname] = (x, y)
    return positions, cell_w, cell_h


# ---------------------------------------------------------------------------
# Main import function
# ---------------------------------------------------------------------------

def import_yosys_json(path, parent_window):
    """
    Parse a Yosys JSON netlist and add blocks/pins/wires to parent_window.

    Returns (n_cells_added, n_wires_added, warnings_list).
    """
    from blocks import Block
    from pins import Pin
    from wire import Wire
    from datetime import datetime

    with open(path) as f:
        data = json.load(f)

    modules = data.get("modules", {})
    if not modules:
        return 0, 0, ["No modules found in JSON."]

    # Use the first (or only) module
    mod_name, mod = next(iter(modules.items()))
    cells_raw = mod.get("cells", {})
    ports_raw = mod.get("ports", {})
    netnames  = mod.get("netnames", {})

    gs = parent_window.grid_size
    warnings = []

    # Build reverse netname lookup: bit -> name
    bit_to_name = {}
    for name, info in netnames.items():
        for bit in info.get("bits", []):
            if isinstance(bit, int) and bit not in (0, 1):
                bit_to_name[bit] = name

    # Parse cells into (svcg_type, {port: [bits]})
    cells = {}
    for cname, cell in cells_raw.items():
        ctype = cell.get("type", "")
        svcg = YOSYS_TO_SVCG.get(ctype)
        if svcg is None:
            warnings.append(f"Unsupported cell type '{ctype}' ({cname}) — skipped.")
            continue
        cells[cname] = (svcg, cell.get("connections", {}))

    if not cells and not ports_raw:
        return 0, 0, warnings + ["No supported cells found."]

    # Placement
    positions, cell_w, cell_h = _place_cells(cells, {}, gs)

    # Port columns: IO pins sit one column left of level-0 cells
    port_x = max(0, gs * 3 - (cell_w + gs * 8))
    if port_x < gs:
        port_x = gs

    # Create Block objects
    new_blocks = {}  # cell_name -> Block
    ts = datetime.now().isoformat(' ', 'seconds')
    for cname, (btype, _) in cells.items():
        x, y = positions.get(cname, (random.randint(2, 20) * gs, random.randint(2, 20) * gs))
        b = Block(x, y, cell_w, cell_h, f"{cname}", btype, gs, parent_window)
        new_blocks[cname] = b

    # Create Pin objects for module ports
    new_pins = {}   # port_name -> Pin
    pin_y = gs * 3
    for pname, pinfo in ports_raw.items():
        direction = pinfo.get("direction", "input")
        ptype = "input_pin" if direction == "input" else "output_pin"
        pin = Pin(port_x, pin_y, cell_w, gs * 2, pname, ptype, gs, 1, parent_window)
        new_pins[pname] = pin
        pin_y += gs * 6

    # Build net -> connection-point map
    # net_point: bit -> list of (block_or_pin_obj, point_xy, "in"|"out")
    net_endpoints = {}

    def add_ep(bit, obj, pt, direction):
        if bit in (0, 1):
            return
        net_endpoints.setdefault(bit, []).append((obj, pt, direction))

    for cname, (btype, connections) in cells.items():
        blk = new_blocks[cname]
        for port, bits in connections.items():
            info = PORT_MAP.get((btype, port))
            if info is None:
                continue
            direction, idx = info
            pts = blk.input_points if direction == "in" else blk.output_points
            if idx < len(pts):
                for bit in bits:
                    add_ep(bit, blk, pts[idx], direction)

    for pname, pin in new_pins.items():
        pinfo = ports_raw[pname]
        direction = pinfo.get("direction", "input")
        pin_dir = "out" if direction == "input" else "in"  # outputs of input ports drive nets
        bits = pinfo.get("bits", [])
        for i, bit in enumerate(bits):
            if i < len(pin.connection_points):
                add_ep(bit, pin, pin.connection_points[i], pin_dir)

    # Create wires
    new_wires = []
    ts = datetime.now().isoformat(' ', 'seconds')
    wired_nets = set()
    for bit, endpoints in net_endpoints.items():
        if bit in wired_nets:
            continue
        outputs = [(obj, pt) for obj, pt, d in endpoints if d == "out"]
        inputs  = [(obj, pt) for obj, pt, d in endpoints if d == "in"]
        if not outputs:
            continue
        src_obj, src_pt = outputs[0]
        net_name = bit_to_name.get(bit, f"net_{bit}")
        for dst_obj, dst_pt in inputs:
            w = Wire(net_name, list(src_pt), list(dst_pt), "wire", gs, parent_window)
            w.text = net_name
            # Register wire in source block/pin
            if hasattr(src_obj, "output_points") and src_pt in src_obj.output_points:
                idx = src_obj.output_points.index(src_pt)
                if idx < len(src_obj.output_wires):
                    if src_obj.output_wires[idx] is None:
                        src_obj.output_wires[idx] = []
                    src_obj.output_wires[idx].append(w.id)
            elif hasattr(src_obj, "connection_points") and src_pt in src_obj.connection_points:
                idx = src_obj.connection_points.index(src_pt)
                if idx < len(src_obj.wires):
                    if src_obj.wires[idx] is None:
                        src_obj.wires[idx] = []
                    src_obj.wires[idx].append(w.id)
            # Register wire in destination block/pin
            if hasattr(dst_obj, "input_points") and dst_pt in dst_obj.input_points:
                idx = dst_obj.input_points.index(dst_pt)
                if idx < len(dst_obj.input_wires):
                    if dst_obj.input_wires[idx] is None:
                        dst_obj.input_wires[idx] = []
                    dst_obj.input_wires[idx].append(w.id)
            elif hasattr(dst_obj, "connection_points") and dst_pt in dst_obj.connection_points:
                idx = dst_obj.connection_points.index(dst_pt)
                if idx < len(dst_obj.wires):
                    if dst_obj.wires[idx] is None:
                        dst_obj.wires[idx] = []
                    dst_obj.wires[idx].append(w.id)
            new_wires.append(w)
        wired_nets.add(bit)

    # Commit to canvas
    parent_window.push_undo()
    parent_window.blocks.extend(new_blocks.values())
    parent_window.pins.extend(new_pins.values())
    parent_window.wires.extend(new_wires)
    parent_window.drawing_area.queue_draw()
    parent_window.update_json()
    parent_window.update_status_bar()

    return len(new_blocks), len(new_wires), warnings
