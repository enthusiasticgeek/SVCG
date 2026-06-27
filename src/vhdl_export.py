#!/usr/bin/env python3
"""
vhdl_export.py -- full-schematic VHDL structural generator

Translates a SVCG canvas (blocks + IO pins + wires) into a single VHDL file
with entity + architecture (Structural).
"""

import re
import shutil
import subprocess
import tempfile
import os


def check_vhdl_syntax(vhd_path):
    """
    Run 'ghdl -a <file>' if ghdl is on PATH.
    Returns (available, success, output_text).
      available : bool  -- False if ghdl is not installed
      success   : bool  -- True if ghdl exited 0
      output    : str   -- combined stdout+stderr from ghdl
    """
    ghdl = shutil.which("ghdl")
    if not ghdl:
        return False, False, ""
    try:
        # Use a temp workdir so ghdl doesn't litter the project dir
        with tempfile.TemporaryDirectory() as workdir:
            result = subprocess.run(
                [ghdl, "-a", "--std=08", vhd_path],
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=15,
            )
        output = (result.stdout + result.stderr).strip()
        return True, result.returncode == 0, output
    except Exception as exc:
        return True, False, str(exc)

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
    # 3-input gates
    "AND3":         "AND3_GATE",
    "OR3":          "OR3_GATE",
    "NAND3":        "NAND3_GATE",
    "NOR3":         "NOR3_GATE",
    "XOR3":         "XOR3_GATE",
    # 4-input gates
    "AND4":         "AND4_GATE",
    "OR4":          "OR4_GATE",
    "NAND4":        "NAND4_GATE",
    "NOR4":         "NOR4_GATE",
    # buffer
    "BUF":          "BUF_GATE",
    # latches
    "DLATCH":       "DLATCH",
    "SRLATCH":      "SRLATCH",
    # decoders / encoders
    "DEC_2TO4":     "DEC_2TO4",
    "DEC_3TO8":     "DEC_3TO8",
    "ENC_4TO2":     "ENC_4TO2",
    # demux
    "DEMUX_1TO4":   "DEMUX_1TO4",
    "DEMUX_1TO8":   "DEMUX_1TO8",
    # arithmetic
    "RCA_4BIT":     "RCA_4BIT",
    "COMP_4BIT":    "COMP_4BIT",
    "CLA4":         "CLA4",
    "CARRY_SEL4":   "CARRY_SEL4",
    "KS4":          "KS4",
    "BK4":          "BK4",
    "CSA":          "CSA",
    "WALLACE3_4":   "WALLACE3_4",
    "MOD_ADD4":     "MOD_ADD4",
    "ARRAY_MULT4":  "ARRAY_MULT4",
    "BOOTH_MULT4":  "BOOTH_MULT4",
    "SQ4":          "SQ4",
    "REST_DIV4":    "REST_DIV4",
    "NONREST_DIV4": "NONREST_DIV4",
    "SRT_DIV4":     "SRT_DIV4",
    "GF_ADD4":      "GF_ADD4",
    "GF_MUL4":      "GF_MUL4",
    "BOOTH4_MULT4": "BOOTH4_MULT4",
    "DADDA4":       "DADDA4",
    "BSR4":         "BSR4",
    "MOD_MUL4":     "MOD_MUL4",
    # sequential
    "SHREG_4BIT":   "SHREG_4BIT",
    "CNT_4BIT":     "CNT_4BIT",
    "CNT_4BIT_UD":  "CNT_4BIT_UD",
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


# VHDL-2008 reserved words — identifiers that collide with these cause parse errors
_VHDL_RESERVED = frozenset({
    "abs","access","after","alias","all","and","architecture","array","assert",
    "attribute","begin","block","body","buffer","bus","case","component",
    "configuration","constant","disconnect","downto","else","elsif","end",
    "entity","exit","file","for","function","generate","generic","group",
    "guarded","if","impure","in","inertial","inout","is","label","library",
    "linkage","literal","loop","map","mod","nand","new","next","nor","not",
    "null","of","on","open","or","others","out","package","port","postponed",
    "procedure","process","protected","pure","range","record","register",
    "reject","rem","report","return","rol","ror","select","severity","signal",
    "shared","sla","sll","sra","srl","subtype","then","to","transport","type",
    "unaffected","units","until","use","variable","wait","when","while","with",
    "xnor","xor",
})

# Verilog-2001 / SystemVerilog reserved words that would cause syntax errors
# if used as port/signal identifiers in generated Verilog
_VERILOG_RESERVED = frozenset({
    "always","and","assign","automatic","begin","buf","bufif0","bufif1",
    "case","casex","casez","cell","cmos","config","deassign","default",
    "defparam","design","disable","edge","else","end","endcase","endconfig",
    "endfunction","endgenerate","endmodule","endprimitive","endspecify",
    "endtable","endtask","event","for","force","forever","fork","function",
    "generate","genvar","highz0","highz1","if","ifnone","incdir","include",
    "initial","inout","input","instance","integer","join","large","liblist",
    "library","localparam","macromodule","medium","module","nand","negedge",
    "nmos","nor","noshowcancelled","not","notif0","notif1","or","output",
    "parameter","pmos","posedge","primitive","pull0","pull1","pulldown",
    "pullup","pulsestyle_onevent","pulsestyle_ondetect","rcmos","real",
    "realtime","reg","release","repeat","rnmos","rpmos","rtran","rtranif0",
    "rtranif1","scalared","showcancelled","signed","small","specify",
    "specparam","strong0","strong1","supply0","supply1","table","task",
    "time","tran","tranif0","tranif1","tri","tri0","tri1","triand","trior",
    "trireg","unsigned","use","uwire","vectored","wait","wand","weak0",
    "weak1","while","wire","wor","xnor","xor",
})


def _sanitize(name):
    """Make a valid VHDL and Verilog identifier from an arbitrary string."""
    n = re.sub(r"[^A-Za-z0-9_]", "_", str(name))
    if n and not n[0].isalpha():  # leading digit or underscore — invalid in both VHDL and Verilog
        n = "sig_" + n
    if n.lower() in _VHDL_RESERVED or n.lower() in _VERILOG_RESERVED:
        n = "sig_" + n
    return n or "sig_unknown"


def _parse_bus(name):
    """
    Parse optional bus/vector notation from a port name string.

    Accepted formats:
      data[7:0]   ->  ("data", 7, 0)
      data[3:3]   ->  ("data", 3, 3)
      data:8      ->  ("data", 7, 0)   # :N means [N-1:0]
      data        ->  ("data", None, None)  # scalar

    Returns (base_name, high, low).  high/low are None for scalar ports.
    """
    s = str(name).strip()
    # data[N:M]
    m = re.search(r'\[(\d+):(\d+)\]', s)
    if m:
        base = s[:m.start()].strip()
        return base, int(m.group(1)), int(m.group(2))
    # data:N  (width shorthand)
    m = re.match(r'^([A-Za-z_]\w*):(\d+)$', s)
    if m:
        width = int(m.group(2))
        return m.group(1), max(0, width - 1), 0
    return s, None, None


def _vhdl_port_name(block_pin_label):
    """Map block pin label to VHDL port name (Q' -> Q_bar)."""
    return "Q_bar" if block_pin_label == "Q'" else block_pin_label


def check_verilog_syntax(v_path):
    """
    Run 'iverilog -t null <file>' if iverilog is on PATH.
    Returns (available, success, output_text).

    Structural netlists reference external library modules that iverilog
    cannot elaborate.  "Unknown module type" and "modules were missing"
    lines are elaboration-only issues, not syntax errors — filter them out
    so that a syntactically valid structural file still reports success.
    """
    iverilog = shutil.which("iverilog")
    if not iverilog:
        return False, False, ""
    try:
        result = subprocess.run(
            [iverilog, "-g2012", "-t", "null", v_path],
            capture_output=True, text=True, timeout=15,
        )
        output = (result.stdout + result.stderr).strip()

        if result.returncode != 0:
            _elab_patterns = (
                "unknown module type",
                "these modules were missing",
                "referenced",
                "error(s) during elaboration",
            )
            real_errors = [
                ln for ln in output.splitlines()
                if ln.strip()
                and not ln.strip().strip("*") == ""   # bare *** delimiters
                and not any(p in ln.lower() for p in _elab_patterns)
            ]
            if not real_errors:
                note = "OK (elaboration skipped — external library modules not resolved)"
                return True, True, note

        return True, result.returncode == 0, output
    except Exception as exc:
        return True, False, str(exc)


def generate_custom_vhd(entity_name, input_names, output_names, user_arch_text):
    """
    Build a complete VHDL source file for a Custom RTL block.

    The entity declaration is generated from the port lists; `user_arch_text`
    is the user-written architecture body (must start with 'architecture ...').
    If it is empty a stub architecture is produced so GHDL can still elaborate.
    """
    lines = [
        "library IEEE;",
        "use IEEE.STD_LOGIC_1164.ALL;",
        "",
        "entity %s is" % entity_name,
    ]
    all_ports = []
    for n in input_names:
        base, hi, lo = _parse_bus(n)
        all_ports.append((_sanitize(base), "in", hi, lo))
    for n in output_names:
        base, hi, lo = _parse_bus(n)
        all_ports.append((_sanitize(base), "out", hi, lo))
    if all_ports:
        lines.append("  port (")
        for idx, (pname, pdir, hi, lo) in enumerate(all_ports):
            sep = ";" if idx < len(all_ports) - 1 else ""
            if hi is not None:
                ptype = "STD_LOGIC_VECTOR(%d downto %d)" % (hi, lo)
                default = " := (others => '0')" if pdir == "in" else ""
            else:
                ptype = "STD_LOGIC"
                default = " := '0'" if pdir == "in" else ""
            lines.append("    %s : %s  %s%s%s" % (pname, pdir, ptype, default, sep))
        lines.append("  );")
    lines += ["end %s;" % entity_name, ""]

    body = (user_arch_text or "").strip()
    if body:
        lines.append(body)
        lines.append("")
    else:
        lines += [
            "architecture rtl of %s is" % entity_name,
            "begin",
            "  -- TODO: implement %s" % entity_name,
            "end architecture rtl;",
            "",
        ]
    return "\n".join(lines)


def generate_custom_v(module_name, input_names, output_names, user_body_text):
    """
    Build a complete Verilog source file for a Custom RTL block.

    The module header (port list) is generated; `user_body_text` is the
    user-written module body (signal/reg declarations + combinational/sequential
    logic, without the `module` header and without `endmodule`).
    If empty a stub is produced.
    """
    all_ports = []
    for n in input_names:
        base, hi, lo = _parse_bus(n)
        width = f"[{hi}:{lo}] " if hi is not None else ""
        all_ports.append((_sanitize(base), f"input wire {width}"))
    for n in output_names:
        base, hi, lo = _parse_bus(n)
        width = f"[{hi}:{lo}] " if hi is not None else ""
        all_ports.append((_sanitize(base), f"output reg {width}"))
    lines = [f"module {module_name} ("]
    if all_ports:
        for idx, (pname, pdir) in enumerate(all_ports):
            sep = "," if idx < len(all_ports) - 1 else ""
            lines.append(f"    {pdir}{pname}{sep}")
    lines += [");", ""]

    body = (user_body_text or "").strip()
    if body:
        lines.append(body)
        lines.append("")
    else:
        lines += [
            f"// TODO: implement {module_name}",
            "",
        ]
    lines += ["endmodule", ""]
    return "\n".join(lines)


def generate_verilog(module_name, blocks, pins, wires):
    """
    Returns a Verilog (SystemVerilog-2012 compatible) structural netlist string.

    Parameters match generate_vhdl() exactly so callers can switch between them.
    """
    indent = "    "

    wire_by_id = {w.id: w for w in wires}
    wire_to_port = {}
    port_list = []   # (name, direction_str)  direction_str = "input" / "output" / "inout"
    seen_port_names = set()

    _vdir = {
        "in":    "input  wire",
        "out":   "output wire",
        "inout": "inout  wire",
    }

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
                    port_list.append((pname, direction, None, None))
                for wid in wire_list:
                    wire_to_port[wid] = pname
        else:
            base_raw, hi, lo = _parse_bus(pin.text)
            pname = _sanitize(base_raw)
            if pname not in seen_port_names:
                seen_port_names.add(pname)
                port_list.append((pname, direction, hi, lo))
            for wire_list in pin.wires:
                for wid in wire_list:
                    wire_to_port[wid] = pname

    def resolve(wire_id):
        if not wire_id:
            return "1'bz"
        if wire_id in wire_to_port:
            return wire_to_port[wire_id]
        w = wire_by_id.get(wire_id)
        return _sanitize(w.text) if w else "1'bz"

    internal_signals = {}
    for w in wires:
        if w.id not in wire_to_port:
            sig = _sanitize(w.text)
            internal_signals[sig] = True

    lines = [f"module {module_name} ("]
    for idx, (pname, direction, hi, lo) in enumerate(port_list):
        sep = "," if idx < len(port_list) - 1 else ""
        width_str = f"[{hi}:{lo}] " if hi is not None else ""
        lines.append(f"{indent}{_vdir.get(direction, 'input wire')} {width_str}{pname}{sep}")
    lines += [");", ""]

    for sig in internal_signals:
        lines.append(f"{indent}wire {sig};")
    if internal_signals:
        lines.append("")

    for idx, block in enumerate(blocks):
        if block.block_type == "CUSTOM":
            cd = getattr(block, "custom_data", None) or {}
            entity = _sanitize(cd.get("entity_name", "CUSTOM_BLOCK"))
        else:
            entity = ENTITY_MAP.get(block.block_type, block.block_type)
        inst = "%s_%d" % (_sanitize(block.text), idx)
        lines.append(f"{indent}{entity} {inst} (")

        pm = []
        for pname, wire_list in zip(block.input_names, block.input_wires):
            wid = wire_list[0] if wire_list else None
            pm.append((_sanitize(_vhdl_port_name(pname)), resolve(wid)))
        for pname, wire_list in zip(block.output_names, block.output_wires):
            wid = wire_list[0] if wire_list else None
            pm.append((_sanitize(_vhdl_port_name(pname)), resolve(wid)))

        for j, (vname, sig) in enumerate(pm):
            sep = "," if j < len(pm) - 1 else ""
            lines.append(f"{indent}{indent}.{vname}({sig}){sep}")
        lines.append(f"{indent});")
        lines.append("")

    lines += ["endmodule", ""]
    return "\n".join(lines)


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
                    port_list.append((pname, direction, None, None))
                for wid in wire_list:
                    wire_to_port[wid] = pname
        else:
            base_raw, hi, lo = _parse_bus(pin.text)
            pname = _sanitize(base_raw)
            if pname not in seen_port_names:
                seen_port_names.add(pname)
                port_list.append((pname, direction, hi, lo))
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

    # Unique component types (non-custom) and unique custom entities
    seen_btypes = {}
    seen_custom = {}  # entity_name -> Block
    for block in blocks:
        if block.block_type == "CUSTOM":
            cd = getattr(block, "custom_data", None) or {}
            ename = _sanitize(cd.get("entity_name", "CUSTOM_BLOCK"))
            if ename not in seen_custom:
                seen_custom[ename] = block
        elif block.block_type not in seen_btypes:
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
        for idx, (pname, direction, hi, lo) in enumerate(port_list):
            comma = ";" if idx < len(port_list) - 1 else ""
            if hi is not None:
                lines.append("%s%s%s : %s  STD_LOGIC_VECTOR(%d downto %d)%s" % (
                    indent, indent, pname, direction, hi, lo, comma))
            else:
                lines.append("%s%s%s : %s  STD_LOGIC%s" % (
                    indent, indent, pname, direction, comma))
        lines.append(indent + ");")
    lines += ["end %s;" % entity_name, ""]

    # Architecture
    lines.append("architecture Structural of %s is" % entity_name)
    lines.append("")

    # Component declarations — standard library components
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
            default = " := '0'" if pdir == "in" else ""
            lines.append("%s%s%s%s : %s  STD_LOGIC%s%s" % (
                indent, indent, indent, vname, pdir, default, comma))
        lines.append("%s%s);" % (indent, indent))
        lines.append("%send component;" % indent)
        lines.append("")

    # Component declarations — custom RTL blocks
    for ename, proto in seen_custom.items():
        cd = getattr(proto, "custom_data", None) or {}
        in_names  = cd.get("input_names",  [])
        out_names = cd.get("output_names", [])
        all_ports = ([(_sanitize(n), "in")  for n in in_names] +
                     [(_sanitize(n), "out") for n in out_names])
        lines.append("%scomponent %s" % (indent, ename))
        if all_ports:
            lines.append("%s%sPort (" % (indent, indent))
            for j, (pname, pdir) in enumerate(all_ports):
                comma = ";" if j < len(all_ports) - 1 else ""
                default = " := '0'" if pdir == "in" else ""
                lines.append("%s%s%s%s : %s  STD_LOGIC%s%s" % (
                    indent, indent, indent, pname, pdir, default, comma))
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
        if block.block_type == "CUSTOM":
            cd = getattr(block, "custom_data", None) or {}
            entity = _sanitize(cd.get("entity_name", "CUSTOM_BLOCK"))
        else:
            entity = ENTITY_MAP.get(block.block_type, block.block_type)
        inst = "%s_%d" % (_sanitize(block.text), idx)
        lines.append("%s%s : %s" % (indent, inst, entity))
        lines.append("%s%sport map (" % (indent, indent))

        pm = []
        for pname, wire_list in zip(block.input_names, block.input_wires):
            wid = wire_list[0] if wire_list else None
            pm.append((_sanitize(_vhdl_port_name(pname)), resolve(wid)))
        for pname, wire_list in zip(block.output_names, block.output_wires):
            wid = wire_list[0] if wire_list else None
            pm.append((_sanitize(_vhdl_port_name(pname)), resolve(wid)))

        for j, (vname, sig) in enumerate(pm):
            comma = "," if j < len(pm) - 1 else ""
            lines.append("%s%s%s%s => %s%s" % (
                indent, indent, indent, vname, sig, comma))
        lines.append("%s%s);" % (indent, indent))
        lines.append("")

    lines.append("end Structural;")
    lines.append("")

    return "\n".join(lines)
