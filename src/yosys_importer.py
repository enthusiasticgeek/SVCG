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
Standard-cell mapped ($_{AND,OR,NOT,NAND,NOR,XOR,XNOR,MUX,DFF}_ etc.)
and Yosys internal ($and, $or, $not, $mux, $dff, etc.)
"""
import json
import math
import random


# ---------------------------------------------------------------------------
# Type mappings
# ---------------------------------------------------------------------------

YOSYS_TO_SVCG = {
    "$_AND_":   "AND",   "$and":   "AND",
    "$_OR_":    "OR",    "$or":    "OR",
    "$_NOT_":   "NOT",   "$not":   "NOT",
    "$_NAND_":  "NAND",  "$nand":  "NAND",
    "$_NOR_":   "NOR",   "$nor":   "NOR",
    "$_XOR_":   "XOR",   "$xor":   "XOR",
    "$_XNOR_":  "XNOR",  "$xnor":  "XNOR",
    "$_MUX_":   "MUX_2X1", "$mux": "MUX_2X1",
    "$_DFF_P_": "DFF",   "$_DFF_N_": "DFF",
    "$dff":     "DFF",   "$dffe":  "DFF",
    "$sdff":    "DFF",   "$adff":  "DFF",
    "$dlatch":  "DFF",
    "$_HA_":    "HA",    "$ha":    "HA",
    "$_FA_":    "FA",    "$fa":    "FA",
}

# Maps (svcg_block_type, yosys_port_name) -> ("in"|"out", pin_index)
PORT_MAP = {
    ("AND",    "A"): ("in", 0), ("AND",    "B"): ("in", 1), ("AND",    "Y"): ("out", 0),
    ("OR",     "A"): ("in", 0), ("OR",     "B"): ("in", 1), ("OR",     "Y"): ("out", 0),
    ("NOT",    "A"): ("in", 0), ("NOT",    "Y"): ("out", 0),
    ("NAND",   "A"): ("in", 0), ("NAND",   "B"): ("in", 1), ("NAND",   "Y"): ("out", 0),
    ("NOR",    "A"): ("in", 0), ("NOR",    "B"): ("in", 1), ("NOR",    "Y"): ("out", 0),
    ("XOR",    "A"): ("in", 0), ("XOR",    "B"): ("in", 1), ("XOR",    "Y"): ("out", 0),
    ("XNOR",   "A"): ("in", 0), ("XNOR",   "B"): ("in", 1), ("XNOR",   "Y"): ("out", 0),
    ("MUX_2X1","A"): ("in", 0), ("MUX_2X1","B"): ("in", 1), ("MUX_2X1","S"): ("in", 2),
    ("MUX_2X1","Y"): ("out", 0),
    # DFF standard ports
    ("DFF", "D"): ("in", 0), ("DFF", "C"): ("in", 1), ("DFF", "CLK"): ("in", 1),
    ("DFF", "EN"): ("in", 2), ("DFF", "Q"): ("out", 0),
    ("HA",  "A"): ("in", 0), ("HA",  "B"): ("in", 1),
    ("HA",  "CO"): ("out", 0), ("HA", "SUM"): ("out", 1), ("HA", "Y"): ("out", 1),
    ("FA",  "A"): ("in", 0), ("FA",  "B"): ("in", 1), ("FA",  "CI"): ("in", 2),
    ("FA",  "CO"): ("out", 0), ("FA", "SUM"): ("out", 1),
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
                    src_obj.output_wires[idx].append(w.id)
            elif hasattr(src_obj, "connection_points") and src_pt in src_obj.connection_points:
                idx = src_obj.connection_points.index(src_pt)
                if idx < len(src_obj.wires):
                    src_obj.wires[idx].append(w.id)
            # Register wire in destination block/pin
            if hasattr(dst_obj, "input_points") and dst_pt in dst_obj.input_points:
                idx = dst_obj.input_points.index(dst_pt)
                if idx < len(dst_obj.input_wires):
                    dst_obj.input_wires[idx].append(w.id)
            elif hasattr(dst_obj, "connection_points") and dst_pt in dst_obj.connection_points:
                idx = dst_obj.connection_points.index(dst_pt)
                if idx < len(dst_obj.wires):
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
