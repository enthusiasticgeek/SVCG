#!/usr/bin/env python3
"""
vhdl_export.py -- full-schematic VHDL structural generator

Translates a SVCG canvas (blocks + IO pins + wires) into a single VHDL file
with entity + architecture (Structural).
"""

import re

# Maps block_type -> VHDL entity name
ENTITY_MAP = {
    "AND":          "AND_GATE",
    "OR":           "OR_GATE",
    "NOT":          "NOT_GATE",
    "NAND":         "NAND_GATE",
    "NOR":          "NOR_GATE",
    "XOR":          "XOR_GATE",
    "XNOR":         "XNOR_GATE",
    "JKFF":         "JKFF",
    "SRFF":         "SRFF",
    "DFF":          "DFF",
    "TFF":          "TFF",
    "DFF_PIPELINE": "DFF_PIPELINE",
    "MUX_2X1":      "MUX2x1",
    "MUX_4X1":      "MUX4x1",
    "MUX_8X1":      "MUX8x1",
    "TRISTATEBUF_2": "TristateBuffer",
    "TRISTATEBUF_4": "TristateBuffer4",
    "TRISTATEBUF_8": "TristateBuffer8",
    "FA":           "FA",
    "FA_GC":        "FA_GC",
    "FA_WC":        "FA_WC",
    "HA":           "HA",
}

# IO pin type -> VHDL port direction
PIN_DIRECTION = {
    "input_pin":        "in",
    "output_pin":       "out",
    "input_output_pin": "inout",
    "input_bus":        "in",
    "output_bus":       "out",
    "input_output_bus": "inout",
    "CLK":              "in",
    "GND":              "in",
    "VDD_5V":           "in",
    "VDD_3V3":          "in",
    "VDD_1V8":          "in",
    "VDD_1V2":          "in",
}


def _sanitize(name):
    """Make a valid VHDL identifier from an arbitrary string."""
    n = re.sub(r"[^A-Za-z0-9_]", "_", str(name))
    if n and n[0].isdigit():
        n = "sig_" + n
    return n or "sig_unknown"


def _vhdl_port_name(block_pin_label):
    """Map block pin label to VHDL port name (Q' -> Q_bar)."""
    return "Q_bar" if block_pin_label == "Q'" else block_pin_label


def generate_vhdl(entity_name, blocks, pins, wires):
    """
    Returns a VHDL source string for the schematic.

    Parameters
    ----------
    entity_name : str   Top-level entity name (e.g. "MY_CIRCUIT")
    blocks      : list  Block objects from BlocksWindow.blocks
    pins        : list  Pin objects from BlocksWindow.pins
    wires       : list  Wire objects from BlocksWindow.wires
    """
    lines = []
    indent = "    "

    # Wire ID -> Wire object
    wire_by_id = {w.id: w for w in wires}

    # IO pins -> entity port declarations
    # wire_id -> port signal name
    wire_to_port = {}
    # ordered list of (port_name, direction, is_vector, width)
    port_list = []
    seen_port_names = set()

    for pin in pins:
        ptype = pin.pin_type
        is_bus = "bus" in ptype.lower()
        direction = PIN_DIRECTION.get(ptype, "in")
        base = _sanitize(pin.text)

        if is_bus:
            for i, wire_list in enumerate(pin.wires):
                pname = "%s_%d" % (base, i) if pin.num_pins > 1 else base
                if pname not in seen_port_names:
                    seen_port_names.add(pname)
                    port_list.append((pname, direction, False, 1))
                for wid in wire_list:
                    wire_to_port[wid] = pname
        else:
            pname = base
            if pname not in seen_port_names:
                seen_port_names.add(pname)
                port_list.append((pname, direction, False, 1))
            for wire_list in pin.wires:
                for wid in wire_list:
                    wire_to_port[wid] = pname

    # Helper: wire ID -> signal/port name
    def resolve(wire_id):
        if not wire_id:
            return "open"
        if wire_id in wire_to_port:
            return wire_to_port[wire_id]
        w = wire_by_id.get(wire_id)
        return _sanitize(w.text) if w else "open"

    # Internal signals (wires not bound to IO pins)
    internal_signals = {}
    for w in wires:
        if w.id not in wire_to_port:
            sig = _sanitize(w.text)
            internal_signals[sig] = True

    # Unique component types
    seen_btypes = {}
    for block in blocks:
        if block.block_type not in seen_btypes:
            seen_btypes[block.block_type] = block

    # Library header
    lines += [
        "library IEEE;",
        "use IEEE.STD_LOGIC_1164.ALL;",
        "",
    ]

    # Entity
    lines.append("entity %s is" % entity_name)
    if port_list:
        lines.append(indent + "Port (")
        for idx, (pname, direction, is_vec, width) in enumerate(port_list):
            comma = ";" if idx < len(port_list) - 1 else ""
            if is_vec:
                lines.append("%s%s%s : %s  STD_LOGIC_VECTOR(%d downto 0)%s" % (
                    indent, indent, pname, direction, width - 1, comma))
            else:
                lines.append("%s%s%s : %s  STD_LOGIC%s" % (
                    indent, indent, pname, direction, comma))
        lines.append(indent + ");")
    lines += ["end %s;" % entity_name, ""]

    # Architecture
    lines.append("architecture Structural of %s is" % entity_name)
    lines.append("")

    # Component declarations
    for btype, proto in seen_btypes.items():
        entity = ENTITY_MAP.get(btype, btype)
        lines.append("%scomponent %s" % (indent, entity))
        lines.append("%s%sPort (" % (indent, indent))
        all_ports = (
            [(n, "in")  for n in proto.input_names] +
            [(n, "out") for n in proto.output_names]
        )
        for j, (pname, pdir) in enumerate(all_ports):
            vname = _vhdl_port_name(pname)
            comma = ";" if j < len(all_ports) - 1 else ""
            lines.append("%s%s%s%s : %s  STD_LOGIC%s" % (
                indent, indent, indent, vname, pdir, comma))
        lines.append("%s%s);" % (indent, indent))
        lines.append("%send component;" % indent)
        lines.append("")

    # Internal signal declarations
    for sig in internal_signals:
        lines.append("%ssignal %s : STD_LOGIC;" % (indent, sig))
    if internal_signals:
        lines.append("")

    lines.append("begin")
    lines.append("")

    # Component instantiations
    for idx, block in enumerate(blocks):
        entity = ENTITY_MAP.get(block.block_type, block.block_type)
        inst = "%s_%d" % (_sanitize(block.text), idx)
        lines.append("%s%s : %s" % (indent, inst, entity))
        lines.append("%s%sport map (" % (indent, indent))

        pm = []
        for pname, wire_list in zip(block.input_names, block.input_wires):
            wid = wire_list[0] if wire_list else None
            pm.append((_vhdl_port_name(pname), resolve(wid)))
        for pname, wire_list in zip(block.output_names, block.output_wires):
            wid = wire_list[0] if wire_list else None
            pm.append((_vhdl_port_name(pname), resolve(wid)))

        for j, (vname, sig) in enumerate(pm):
            comma = "," if j < len(pm) - 1 else ""
            lines.append("%s%s%s%s => %s%s" % (
                indent, indent, indent, vname, sig, comma))
        lines.append("%s%s);" % (indent, indent))
        lines.append("")

    lines.append("end Structural;")
    lines.append("")

    return "\n".join(lines)
