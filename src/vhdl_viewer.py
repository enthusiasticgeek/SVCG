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
                        cd.get("verilog_body", cd.get("vhdl", "")),
                    )
                    self.show_vhdl_code_dialog(code,
                        title=f"Verilog — {ename} (Custom RTL)")
                else:
                    from vhdl_export import generate_custom_vhd
                    code = generate_custom_vhd(
                        ename,
                        cd.get("input_names", []),
                        cd.get("output_names", []),
                        cd.get("vhdl_body", cd.get("vhdl", "")),
                    )
                    self.show_vhdl_code_dialog(code,
                        title=f"VHDL — {ename} (Custom RTL)")
                return

            block_type = block.block_type.lower()
            src_dir = os.path.dirname(os.path.abspath(__file__))
            if lang == "verilog":
                tmpl_path = os.path.join(src_dir, "verilog", f"{block_type}.v")
                if os.path.exists(tmpl_path):
                    with open(tmpl_path, "r") as f:
                        code = f.read()
                    self.show_vhdl_code_dialog(code,
                        title=f"Verilog — {block.block_type}")
                else:
                    self.show_error_message(
                        "Verilog Template Not Found",
                        f"No Verilog template found for block type '{block_type}'.",
                    )
            else:
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
        import tempfile
        dialog = Gtk.Dialog(title=title, parent=self, flags=0)
        dialog.set_default_size(600, 420)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        dialog.get_content_area().pack_start(sw, True, True, 0)
        tv = Gtk.TextView()
        tv.set_editable(False)
        tv.set_monospace(True)
        tv.set_wrap_mode(Gtk.WrapMode.NONE)
        tv.get_buffer().set_text(vhdl_code)
        sw.add(tv)

        # Syntax check on a temp file
        is_verilog = "module " in vhdl_code and "endmodule" in vhdl_code
        suffix = ".v" if is_verilog else ".vhd"
        chk_label = Gtk.Label()
        chk_label.set_halign(Gtk.Align.START)
        chk_label.set_margin_start(6)
        chk_label.set_margin_bottom(4)
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=suffix,
                                             delete=False) as tf:
                tf.write(vhdl_code)
                tmp_path = tf.name
            from vhdl_export import check_verilog_syntax, check_vhdl_syntax
            if is_verilog:
                avail, ok, out = check_verilog_syntax(tmp_path)
                tool = "iverilog"
            else:
                avail, ok, out = check_vhdl_syntax(tmp_path)
                tool = "ghdl"
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            if avail:
                safe = (out or "").replace("&", "&amp;").replace("<", "&lt;")
                if ok:
                    chk_label.set_markup(f"<span color='green'>{tool}: syntax OK</span>")
                else:
                    chk_label.set_markup(
                        f"<span color='red'>{tool} errors:\n{safe[:300]}</span>")
            else:
                chk_label.set_text(f"({tool} not on PATH — install it for syntax check)")
        except Exception as e:
            chk_label.set_text(f"(syntax check error: {e})")
        dialog.get_content_area().pack_start(chk_label, False, False, 0)

        dialog.show_all()
        dialog.run()
        dialog.destroy()
