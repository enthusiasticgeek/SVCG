#!/usr/bin/env python3
"""
vhdl_viewer.py -- mixin for per-block VHDL template viewer and error dialogs
"""
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class VhdlViewerMixin:

    def show_error_message(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self, flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def on_view_vhdl_code(self, widget):
        try:
            if not self.selected_block:
                return
            block = self.selected_block
            lang = getattr(self, "hdl_language", "vhdl")

            if block.block_type == "CUSTOM":
                cd = getattr(block, "custom_data", None) or {}
                ename = cd.get("entity_name", "CUSTOM")
                if lang == "verilog":
                    from vhdl_export import generate_custom_v
                    code = generate_custom_v(
                        ename,
                        cd.get("input_names", []),
                        cd.get("output_names", []),
                        cd.get("vhdl", ""),
                    )
                    self.show_vhdl_code_dialog(code,
                        title=f"Verilog — {ename} (Custom RTL)")
                else:
                    from vhdl_export import generate_custom_vhd
                    code = generate_custom_vhd(
                        ename,
                        cd.get("input_names", []),
                        cd.get("output_names", []),
                        cd.get("vhdl", ""),
                    )
                    self.show_vhdl_code_dialog(code,
                        title=f"VHDL — {ename} (Custom RTL)")
                return

            block_type = block.block_type.lower()
            src_dir = os.path.dirname(os.path.abspath(__file__))
            vhdl_file_path = os.path.join(src_dir, "vhdl", f"{block_type}.vhd")
            if os.path.exists(vhdl_file_path):
                with open(vhdl_file_path, "r") as f:
                    vhdl_code = f.read()
                self.show_vhdl_code_dialog(vhdl_code)
            else:
                self.show_error_message(
                    "VHDL Code Not Found",
                    f"No VHDL template found for block type '{block_type}'.",
                )
        except Exception as e:
            print(f"Error in on_view_vhdl_code: {e}")

    def show_vhdl_code_dialog(self, vhdl_code, title="VHDL Code"):
        dialog = Gtk.Dialog(title=title, parent=self, flags=0)
        dialog.set_default_size(600, 400)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        dialog.get_content_area().pack_start(sw, True, True, 0)
        tv = Gtk.TextView()
        tv.set_editable(False)
        tv.set_monospace(True)
        tv.set_wrap_mode(Gtk.WrapMode.NONE)
        tv.get_buffer().set_text(vhdl_code)
        sw.add(tv)
        dialog.show_all()
        dialog.run()
        dialog.destroy()
