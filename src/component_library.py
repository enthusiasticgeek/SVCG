#!/usr/bin/env python3
"""
component_library.py -- mixin for saving/loading user-defined component sub-circuits
"""
import json
import os
import random
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from blocks import Block
from pins import Pin
from wire import Wire


class ComponentLibraryMixin:

    def _comp_dir(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "components")

    def on_save_component(self, widget):
        blocks = list(self.selected_blocks) or ([self.selected_block] if self.selected_block else [])
        pins   = list(self.selected_pins)   or ([self.selected_pin]   if self.selected_pin   else [])
        if not blocks and not pins:
            self.show_error_message(
                "Nothing selected",
                "Shift+click to select blocks/pins, then use File > Save Selection as Component."
            )
            return

        dialog = Gtk.MessageDialog(
            transient_for=self, flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Save as Component",
        )
        dialog.format_secondary_text("Enter a name for this component:")
        entry = Gtk.Entry()
        entry.set_text("my_component")
        entry.set_activates_default(True)
        dialog.get_content_area().pack_end(entry, False, False, 6)
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.show_all()
        resp = dialog.run()
        name = entry.get_text().strip()
        dialog.destroy()
        if resp != Gtk.ResponseType.OK or not name:
            return

        # Collect connection points belonging to selected elements
        sel_pts = set()
        for b in blocks:
            sel_pts.update(tuple(p) if isinstance(p, list) else p for p in b.input_points)
            sel_pts.update(tuple(p) if isinstance(p, list) else p for p in b.output_points)
        for p in pins:
            sel_pts.update(tuple(cp) if isinstance(cp, list) else cp for cp in p.connection_points)

        # Internal wires: both endpoints on selected elements
        internal_wires = []
        for w in self.wires:
            sp = tuple(w.start_point) if isinstance(w.start_point, list) else w.start_point
            ep = tuple(w.end_point)   if isinstance(w.end_point,   list) else w.end_point
            if sp in sel_pts and ep in sel_pts:
                internal_wires.append(w)

        comp_data = {
            "name": name,
            "blocks": [b.to_dict() for b in blocks],
            "pins":   [p.to_dict() for p in pins],
            "wires":  [w.to_dict() for w in internal_wires],
        }
        comp_dir = self._comp_dir()
        os.makedirs(comp_dir, exist_ok=True)
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        path = os.path.join(comp_dir, f"{safe}.json")
        try:
            with open(path, "w") as f:
                json.dump(comp_data, f, indent=2)
        except IOError as e:
            self.show_error_message("Save failed", str(e))
            return
        self.refresh_component_panel()

    def instantiate_component(self, path):
        try:
            with open(path) as f:
                comp = json.load(f)
        except Exception as e:
            if not getattr(self, '_headless', False):
                self.show_error_message("Load failed", str(e))
            return

        block_dicts = comp.get("blocks", [])
        pin_dicts   = comp.get("pins",   [])
        wire_dicts  = comp.get("wires",  [])
        if not block_dicts and not pin_dicts:
            return

        # Compute offset to place component at a random canvas position
        xs = [d["x"] for d in block_dicts + pin_dicts]
        ys = [d["y"] for d in block_dicts + pin_dicts]
        min_x, min_y = min(xs), min(ys)
        ox = round(random.randint(60, 300) // self.grid_size) * self.grid_size - min_x
        oy = round(random.randint(60, 300) // self.grid_size) * self.grid_size - min_y

        def shift(pt):
            return [pt[0] + ox, pt[1] + oy]

        def remap(wire_lists, mapping):
            result = []
            for wl in (wire_lists or []):
                if wl is None:
                    result.append([])
                else:
                    result.append([mapping.get(wid, wid) for wid in wl])
            return result

        # Create wires first to build old→new ID mapping
        old_to_new = {}
        new_wires = []
        for wd in wire_dicts:
            w = Wire(wd.get("text", "wire"), shift(wd["start_point"]), shift(wd["end_point"]),
                     wd["wire_type"], self.grid_size, self)
            old_to_new[wd["id"]] = w.id
            w.text = wd.get("text", "wire")
            new_wires.append(w)

        new_blocks = []
        for bd in block_dicts:
            d = dict(bd)
            d["x"] = bd["x"] + ox
            d["y"] = bd["y"] + oy
            d["input_points"]  = [shift(p) for p in bd.get("input_points",  [])]
            d["output_points"] = [shift(p) for p in bd.get("output_points", [])]
            d["input_wires"]   = remap(bd.get("input_wires",  []), old_to_new)
            d["output_wires"]  = remap(bd.get("output_wires", []), old_to_new)
            d.pop("id", None)   # let Block.from_dict generate a fresh UUID
            new_blocks.append(Block.from_dict(d, self))

        new_pins = []
        for pd in pin_dicts:
            d = dict(pd)
            d["x"] = pd["x"] + ox
            d["y"] = pd["y"] + oy
            d["connection_points"] = [shift(p) for p in pd.get("connection_points", [])]
            d["wires"] = remap(pd.get("wires", []), old_to_new)
            d.pop("id", None)
            new_pins.append(Pin.from_dict(d, self))

        self.push_undo()
        self.blocks.extend(new_blocks)
        self.pins.extend(new_pins)
        self.wires.extend(new_wires)
        self.drawing_area.queue_draw()
        self.update_json()
        self.update_status_bar()

    def refresh_component_panel(self):
        for child in self.comp_box.get_children():
            self.comp_box.remove(child)

        comp_dir = self._comp_dir()
        all_files = sorted(f for f in os.listdir(comp_dir) if f.endswith(".json")) \
                    if os.path.isdir(comp_dir) else []

        query = ""
        if hasattr(self, "comp_search"):
            query = (self.comp_search.get_text() or "").lower().strip()
        files = [f for f in all_files if query in os.path.splitext(f)[0].lower()] \
                if query else all_files

        if not all_files:
            lbl = Gtk.Label(label="No components yet.\nUse File > Save Selection as Component.")
            lbl.set_line_wrap(True)
            lbl.set_justify(Gtk.Justification.LEFT)
            lbl.set_halign(Gtk.Align.START)
            lbl.set_margin_start(4)
            self.comp_box.pack_start(lbl, False, False, 0)
        elif not files:
            lbl = Gtk.Label(label=f'No match for "{query}".')
            lbl.set_halign(Gtk.Align.START)
            lbl.set_margin_start(4)
            self.comp_box.pack_start(lbl, False, False, 0)
        else:
            for fname in files:
                name = os.path.splitext(fname)[0]
                path = os.path.join(comp_dir, fname)
                btn = Gtk.Button(label=name)
                btn.set_tooltip_text(f"Instantiate: {name}")
                btn.connect("clicked", lambda _w, p=path: self.instantiate_component(p))
                self.comp_box.pack_start(btn, False, False, 0)

        self.comp_box.show_all()
