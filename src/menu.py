#!/usr/bin/env python3
import gi
import os
import re
import tempfile
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from vhdl_export import (generate_vhdl, generate_verilog,
                          check_vhdl_syntax, check_verilog_syntax,
                          generate_custom_vhd, generate_custom_v)
from testbench_gen import (generate_testbench, run_ghdl_simulation, launch_gtkwave,
                           generate_verilog_testbench, run_iverilog_simulation)
from yosys_importer import import_yosys_json


def _mi(label, handler):
    """Create a Gtk.MenuItem with a single activate handler."""
    item = Gtk.MenuItem(label=label)
    item.connect("activate", handler)
    return item


class MenuBar:
    def __init__(self, main_window):
        self.main_window = main_window
        self.menubar = self._build_menubar()
        self.toolbar  = self._build_toolbar()
        self.popup    = self._build_popup()

    # ------------------------------------------------------------------
    # Widget builders
    # ------------------------------------------------------------------

    def _build_menubar(self):
        menubar = Gtk.MenuBar()

        # ── File ──────────────────────────────────────────────────────
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="File")
        file_item.set_submenu(file_menu)

        # File > Open/Save submenu
        open_menu = Gtk.Menu()
        open_item = Gtk.MenuItem(label="Open / Save")
        open_item.set_submenu(open_menu)
        open_menu.append(_mi("New SVCG Project",             self.on_menu_file_new_generic_svcg))
        open_menu.append(_mi("Load SVCG Project",            self.on_menu_file_load_generic_svcg))
        open_menu.append(Gtk.SeparatorMenuItem())
        open_menu.append(_mi("Import SVCG JSON file",        self.on_menu_file_load_generic_json))
        open_menu.append(_mi("Export / Save As SVCG JSON",   self.on_menu_file_new_generic_json))

        file_menu.append(open_item)
        file_menu.append(Gtk.SeparatorMenuItem())
        file_menu.append(_mi("Generate HDL (VHDL/Verilog)...", self.on_generate_vhdl))
        file_menu.append(_mi("Generate Testbench + Simulate...", self.on_generate_testbench))
        file_menu.append(_mi("Import Yosys Netlist...",      self.on_import_yosys))
        file_menu.append(_mi("Save Selection as Component...", self.on_save_component))
        file_menu.append(Gtk.SeparatorMenuItem())
        file_menu.append(_mi("Export as SVG...",             self.on_export_svg))
        file_menu.append(_mi("Export as PNG...",             self.on_export_png))
        file_menu.append(_mi("Export EDIF Netlist… (experimental)", self.on_export_edif))
        file_menu.append(Gtk.SeparatorMenuItem())
        file_menu.append(_mi("Toggle Dark Mode",             self.on_toggle_dark_mode))
        file_menu.append(Gtk.SeparatorMenuItem())
        file_menu.append(_mi("Quit",                         self.on_menu_file_quit))

        menubar.append(file_item)

        # ── Edit ──────────────────────────────────────────────────────
        edit_menu = Gtk.Menu()
        edit_item = Gtk.MenuItem(label="Edit")
        edit_item.set_submenu(edit_menu)
        edit_menu.append(_mi("Copy  Ctrl+C",   self._noop))
        edit_menu.append(_mi("Paste Ctrl+V",   self._noop))
        edit_menu.append(_mi("Cut   Ctrl+X",   self._noop))
        edit_menu.append(_mi("Delete Ctrl+D",  self._noop))
        menubar.append(edit_item)

        return menubar

    def _build_toolbar(self):
        toolbar = Gtk.Toolbar()
        toolbar.set_style(Gtk.ToolbarStyle.BOTH_HORIZ)

        btn_new = Gtk.ToolButton(icon_name="document-new", label="New")
        btn_new.set_tooltip_text("New SVCG Project")
        btn_new.connect("clicked", self.on_menu_file_new_generic_svcg)
        toolbar.insert(btn_new, -1)

        btn_quit = Gtk.ToolButton(icon_name="application-exit", label="Quit")
        btn_quit.set_tooltip_text("Quit")
        btn_quit.connect("clicked", self.on_menu_file_quit)
        toolbar.insert(btn_quit, -1)

        return toolbar

    def _build_popup(self):
        popup = Gtk.Menu()
        popup.append(_mi("Copy  Ctrl+C",  self._noop))
        popup.append(_mi("Paste Ctrl+V",  self._noop))
        popup.append(_mi("Cut   Ctrl+X",  self._noop))
        popup.show_all()
        return popup

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _noop(self, widget):
        pass

    def on_generate_vhdl(self, widget):
        mw = self.main_window
        if not mw.blocks and not mw.pins:
            self._show_error("Nothing to export", "Add some blocks and IO pins to the canvas first.")
            return

        lang = getattr(mw, "hdl_language", "vhdl")
        lang_upper = lang.upper()

        # Ask for top-level module/entity name
        name_dialog = Gtk.MessageDialog(
            transient_for=mw, flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=f"Generate {lang_upper}",
        )
        name_dialog.format_secondary_text(
            f"Enter top-level {'module' if lang == 'verilog' else 'entity'} name:")
        entry = Gtk.Entry()
        default_name = "SCHEMATIC"
        if mw.current_file_path:
            base = os.path.splitext(os.path.basename(mw.current_file_path))[0]
            default_name = re.sub(r"[^A-Za-z0-9_]", "_", base).upper() or "SCHEMATIC"
        entry.set_text(default_name)
        entry.set_activates_default(True)
        name_dialog.get_content_area().pack_end(entry, False, False, 6)
        name_dialog.set_default_response(Gtk.ResponseType.OK)
        name_dialog.show_all()
        resp = name_dialog.run()
        entity_name = entry.get_text().strip() or default_name
        name_dialog.destroy()
        if resp != Gtk.ResponseType.OK:
            return

        # Generate HDL
        try:
            if lang == "verilog":
                hdl_text = generate_verilog(entity_name, mw.blocks, mw.pins, mw.wires)
            else:
                hdl_text = generate_vhdl(entity_name, mw.blocks, mw.pins, mw.wires)
        except Exception as exc:
            self._show_error(f"{lang_upper} generation failed", str(exc))
            return

        # Save file dialog
        ext      = ".v"   if lang == "verilog" else ".vhd"
        flt_name = "Verilog files (*.v)" if lang == "verilog" else "VHDL files (*.vhd, *.vhdl)"
        save_dialog = Gtk.FileChooserDialog(
            title=f"Save {lang_upper} File", parent=mw,
            action=Gtk.FileChooserAction.SAVE,
        )
        save_dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,   Gtk.ResponseType.ACCEPT,
        )
        save_dialog.set_current_name(f"{entity_name.lower()}{ext}")
        flt = Gtk.FileFilter()
        flt.set_name(flt_name)
        flt.add_pattern(f"*{ext}")
        if lang == "vhdl":
            flt.add_pattern("*.vhdl")
        save_dialog.add_filter(flt)
        if mw.current_file_path:
            save_dialog.set_current_folder(os.path.dirname(mw.current_file_path))

        resp = save_dialog.run()
        if resp == Gtk.ResponseType.ACCEPT:
            path = save_dialog.get_filename()
            if lang == "verilog":
                if not path.lower().endswith(".v"):
                    path += ".v"
            else:
                if not path.lower().endswith((".vhd", ".vhdl")):
                    path += ".vhd"
            save_dialog.destroy()
            try:
                with open(path, "w") as f:
                    f.write(hdl_text)
            except IOError as exc:
                self._show_error("Could not write file", str(exc))
                return

            # Syntax check (GHDL for VHDL, iverilog for Verilog)
            if lang == "verilog":
                chk_avail, chk_ok, chk_out = check_verilog_syntax(path)
                tool_name = "iverilog"
            else:
                chk_avail, chk_ok, chk_out = check_vhdl_syntax(path)
                tool_name = "ghdl"

            if chk_avail:
                chk_banner = f"{tool_name}: syntax OK" if chk_ok else f"{tool_name} errors:\n" + (chk_out or "(no output)")
            else:
                chk_banner = f"({tool_name} not found on PATH — install it to enable syntax check)"

            # Preview dialog
            preview = Gtk.Dialog(
                title=f"Generated {lang_upper} — {os.path.basename(path)}",
                transient_for=mw, flags=0,
            )
            preview.add_button("Close", Gtk.ResponseType.CLOSE)
            preview.set_default_size(700, 500)
            sw = Gtk.ScrolledWindow()
            sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            tv = Gtk.TextView()
            tv.set_editable(False)
            tv.set_monospace(True)
            tv.get_buffer().set_text(hdl_text)
            sw.add(tv)
            preview.get_content_area().pack_start(sw, True, True, 0)
            chk_label = Gtk.Label(label=chk_banner)
            chk_label.set_halign(Gtk.Align.START)
            chk_label.set_margin_start(6)
            chk_label.set_margin_bottom(4)
            if chk_avail and not chk_ok:
                chk_label.set_markup(
                    "<span color='red'>" + chk_banner.replace("&", "&amp;").replace("<", "&lt;") + "</span>"
                )
            elif chk_avail and chk_ok:
                chk_label.set_markup(f"<span color='green'>{chk_banner}</span>")
            preview.get_content_area().pack_start(chk_label, False, False, 0)
            preview.show_all()
            preview.run()
            preview.destroy()
        else:
            save_dialog.destroy()

    # ------------------------------------------------------------------
    # Testbench generation + simulation (P4.2)
    # ------------------------------------------------------------------

    def on_generate_testbench(self, widget):
        mw = self.main_window
        lang = getattr(mw, "hdl_language", "vhdl")
        if not mw.pins:
            self._show_error("Nothing to export", "Add IO pins to define the entity ports first.")
            return

        # Ask for entity/module name
        name_dialog = Gtk.MessageDialog(
            transient_for=mw, flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Generate Testbench",
        )
        lbl = "module" if lang == "verilog" else "entity"
        name_dialog.format_secondary_text(f"Enter top-level {lbl} name:")
        entry = Gtk.Entry()
        default_name = "SCHEMATIC"
        if mw.current_file_path:
            base = os.path.splitext(os.path.basename(mw.current_file_path))[0]
            default_name = re.sub(r"[^A-Za-z0-9_]", "_", base).upper() or "SCHEMATIC"
        entry.set_text(default_name)
        entry.set_activates_default(True)
        name_dialog.get_content_area().pack_end(entry, False, False, 6)
        name_dialog.set_default_response(Gtk.ResponseType.OK)
        name_dialog.show_all()
        resp = name_dialog.run()
        entity_name = entry.get_text().strip() or default_name
        name_dialog.destroy()
        if resp != Gtk.ResponseType.OK:
            return

        if lang == "verilog":
            self._run_verilog_testbench(mw, entity_name)
        else:
            self._run_vhdl_testbench(mw, entity_name)

    def _run_vhdl_testbench(self, mw, entity_name):
        try:
            entity_vhdl = generate_vhdl(entity_name, mw.blocks, mw.pins, mw.wires)
            tb_vhdl     = generate_testbench(entity_name, mw.pins)
        except Exception as exc:
            self._show_error("Generation failed", str(exc))
            return

        save_dialog = Gtk.FileChooserDialog(
            title="Save VHDL Testbench", parent=mw,
            action=Gtk.FileChooserAction.SAVE,
        )
        save_dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                Gtk.STOCK_SAVE,   Gtk.ResponseType.ACCEPT)
        save_dialog.set_current_name(f"{entity_name.lower()}_tb.vhd")
        flt = Gtk.FileFilter(); flt.set_name("VHDL files (*.vhd)"); flt.add_pattern("*.vhd")
        save_dialog.add_filter(flt)
        if mw.current_file_path:
            save_dialog.set_current_folder(os.path.dirname(mw.current_file_path))
        resp = save_dialog.run()
        if resp != Gtk.ResponseType.ACCEPT:
            save_dialog.destroy(); return
        tb_path = save_dialog.get_filename()
        save_dialog.destroy()
        if not tb_path.lower().endswith((".vhd", ".vhdl")):
            tb_path += ".vhd"

        workdir = os.path.dirname(tb_path)
        entity_path = os.path.join(workdir, f"{entity_name.lower()}.vhd")
        try:
            with open(entity_path, "w") as f: f.write(entity_vhdl)
            with open(tb_path,     "w") as f: f.write(tb_vhdl)
        except IOError as exc:
            self._show_error("Could not write file", str(exc)); return

        custom_vhds = []
        seen_custom = set()
        for block in mw.blocks:
            if block.block_type == "CUSTOM":
                cd = getattr(block, "custom_data", None) or {}
                ename = cd.get("entity_name", "CUSTOM_BLOCK")
                if ename not in seen_custom:
                    seen_custom.add(ename)
                    vhd = generate_custom_vhd(ename, cd.get("input_names", []),
                                              cd.get("output_names", []),
                                              cd.get("vhdl_body", cd.get("vhdl", "")))
                    custom_vhds.append((ename, vhd))

        tb_entity = f"{entity_name.lower()}_tb"
        sim_ok, sim_log, vcd_path = run_ghdl_simulation(
            entity_path, tb_path, tb_entity, workdir,
            custom_vhds=custom_vhds if custom_vhds else None,
        )
        self._show_tb_preview(mw, tb_vhdl, tb_path, sim_ok, sim_log, vcd_path)

    def _run_verilog_testbench(self, mw, module_name):
        try:
            entity_v = generate_verilog(module_name, mw.blocks, mw.pins, mw.wires)
            tb_v     = generate_verilog_testbench(module_name, mw.pins)
        except Exception as exc:
            self._show_error("Generation failed", str(exc))
            return

        save_dialog = Gtk.FileChooserDialog(
            title="Save Verilog Testbench", parent=mw,
            action=Gtk.FileChooserAction.SAVE,
        )
        save_dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                Gtk.STOCK_SAVE,   Gtk.ResponseType.ACCEPT)
        save_dialog.set_current_name(f"{module_name.lower()}_tb.v")
        flt = Gtk.FileFilter(); flt.set_name("Verilog files (*.v)"); flt.add_pattern("*.v")
        save_dialog.add_filter(flt)
        if mw.current_file_path:
            save_dialog.set_current_folder(os.path.dirname(mw.current_file_path))
        resp = save_dialog.run()
        if resp != Gtk.ResponseType.ACCEPT:
            save_dialog.destroy(); return
        tb_path = save_dialog.get_filename()
        save_dialog.destroy()
        if not tb_path.lower().endswith(".v"):
            tb_path += ".v"

        workdir = os.path.dirname(tb_path)
        entity_path = os.path.join(workdir, f"{module_name.lower()}.v")
        try:
            with open(entity_path, "w") as f: f.write(entity_v)
            with open(tb_path,     "w") as f: f.write(tb_v)
        except IOError as exc:
            self._show_error("Could not write file", str(exc)); return

        custom_vs = []
        seen_custom = set()
        for block in mw.blocks:
            if block.block_type == "CUSTOM":
                cd = getattr(block, "custom_data", None) or {}
                ename = cd.get("entity_name", "CUSTOM_BLOCK")
                if ename not in seen_custom:
                    seen_custom.add(ename)
                    v = generate_custom_v(ename, cd.get("input_names", []),
                                         cd.get("output_names", []),
                                         cd.get("verilog_body", cd.get("vhdl", "")))
                    custom_vs.append((ename, v))

        tb_module = f"{module_name.lower()}_tb"
        sim_ok, sim_log, vcd_path = run_iverilog_simulation(
            entity_path, tb_path, tb_module, workdir,
            custom_vs=custom_vs if custom_vs else None,
        )
        self._show_tb_preview(mw, tb_v, tb_path, sim_ok, sim_log, vcd_path)

    def _show_tb_preview(self, mw, tb_text, tb_path, sim_ok, sim_log, vcd_path):
        preview = Gtk.Dialog(
            title=f"Testbench — {os.path.basename(tb_path)}",
            transient_for=mw, flags=0,
        )
        if vcd_path:
            preview.add_button("Launch GTKWave", Gtk.ResponseType.APPLY)
        preview.add_button("Close", Gtk.ResponseType.CLOSE)
        preview.set_default_size(700, 500)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        tv = Gtk.TextView(); tv.set_editable(False); tv.set_monospace(True)
        tv.get_buffer().set_text(tb_text)
        sw.add(tv)
        preview.get_content_area().pack_start(sw, True, True, 0)
        if sim_log:
            sim_label = Gtk.Label(label=sim_log[:500])
            sim_label.set_halign(Gtk.Align.START)
            sim_label.set_margin_start(6)
            sim_label.set_margin_bottom(4)
            sim_label.set_line_wrap(True)
            safe = sim_log[:500].replace("&", "&amp;").replace("<", "&lt;")
            if not sim_ok:
                sim_label.set_markup(f"<span color='red'>{safe}</span>")
            else:
                sim_label.set_markup(f"<span color='green'>{safe[:200]}</span>")
            preview.get_content_area().pack_start(sim_label, False, False, 0)
        preview.show_all()
        while True:
            resp = preview.run()
            if resp == Gtk.ResponseType.APPLY and vcd_path:
                if not launch_gtkwave(vcd_path):
                    self._show_error("GTKWave not found",
                                     "Install GTKWave and ensure it is on PATH.")
            else:
                break
        preview.destroy()

    # ------------------------------------------------------------------
    # EDIF Netlist export
    # ------------------------------------------------------------------

    def on_export_edif(self, widget):
        mw = self.main_window
        if not mw.blocks and not mw.pins:
            self._show_error("Nothing to export", "Add blocks to the canvas first.")
            return

        save_dialog = Gtk.FileChooserDialog(
            title="Export EDIF Netlist", parent=mw,
            action=Gtk.FileChooserAction.SAVE,
        )
        save_dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                Gtk.STOCK_SAVE,   Gtk.ResponseType.ACCEPT)
        save_dialog.set_current_name("netlist.edf")
        flt = Gtk.FileFilter()
        flt.set_name("EDIF files (*.edf, *.edif)")
        flt.add_pattern("*.edf"); flt.add_pattern("*.edif")
        save_dialog.add_filter(flt)
        if mw.current_file_path:
            save_dialog.set_current_folder(os.path.dirname(mw.current_file_path))
        resp = save_dialog.run()
        if resp != Gtk.ResponseType.ACCEPT:
            save_dialog.destroy(); return
        edif_path = save_dialog.get_filename()
        save_dialog.destroy()
        if not edif_path.lower().endswith((".edf", ".edif")):
            edif_path += ".edf"

        import tempfile
        try:
            json_str = mw.elements_to_json()
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                             delete=False) as tf:
                tf.write(json_str)
                tmp_json = tf.name
        except Exception as exc:
            self._show_error("EDIF export failed", f"Could not serialize canvas: {exc}")
            return

        try:
            import sys as _sys
            _sys.path.insert(0, os.path.join(os.path.dirname(
                os.path.abspath(__file__)), "experimental"))
            from edif_convertor import generate_edif_netlist
            generate_edif_netlist(tmp_json, edif_path)
        except Exception as exc:
            self._show_error("EDIF export failed", str(exc))
            return
        finally:
            try:
                os.unlink(tmp_json)
            except OSError:
                pass

        info = Gtk.MessageDialog(
            transient_for=mw, flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="EDIF Export Complete",
        )
        info.format_secondary_text(f"Saved to:\n{edif_path}")
        info.run()
        info.destroy()

    # ------------------------------------------------------------------
    # Yosys JSON netlist import (P4.3)
    # ------------------------------------------------------------------

    def on_import_yosys(self, widget):
        mw = self.main_window
        dialog = Gtk.FileChooserDialog(
            title="Import Yosys Netlist",
            parent=mw,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,   Gtk.ResponseType.ACCEPT,
        )
        flt = Gtk.FileFilter()
        flt.set_name("JSON files (*.json)")
        flt.add_pattern("*.json")
        dialog.add_filter(flt)
        resp = dialog.run()
        if resp != Gtk.ResponseType.ACCEPT:
            dialog.destroy()
            return
        path = dialog.get_filename()
        dialog.destroy()

        try:
            n_cells, n_wires, warnings = import_yosys_json(path, mw)
        except Exception as exc:
            self._show_error("Import failed", str(exc))
            return

        msg = f"Imported {n_cells} cells and {n_wires} wires."
        if warnings:
            msg += "\n\nWarnings:\n" + "\n".join(warnings[:10])
        info = Gtk.MessageDialog(
            transient_for=mw, flags=0,
            message_type=Gtk.MessageType.INFO if not warnings else Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text="Yosys Import Complete",
        )
        info.format_secondary_text(msg)
        info.run()
        info.destroy()

    def _show_error(self, title, message):
        d = Gtk.MessageDialog(
            transient_for=self.main_window, flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        d.format_secondary_text(message)
        d.run()
        d.destroy()

    def on_menu_file_new_generic_svcg(self, widget):
        if self.main_window.dirty:
            save_dialog = Gtk.MessageDialog(
                transient_for=self.main_window, flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.NONE,
                text="You have unsaved changes.",
            )
            save_dialog.format_secondary_text("Save before creating a new project?")
            save_dialog.add_button("Discard", Gtk.ResponseType.NO)
            save_dialog.add_button("Cancel",  Gtk.ResponseType.CANCEL)
            save_dialog.add_button("Save",    Gtk.ResponseType.YES)
            save_dialog.set_default_response(Gtk.ResponseType.YES)
            resp = save_dialog.run()
            save_dialog.destroy()
            if resp == Gtk.ResponseType.YES:
                if self.main_window.current_file_path:
                    self.main_window.save_to_json(self.main_window.current_file_path)
                else:
                    self.on_save_as_json_file(widget)
            elif resp == Gtk.ResponseType.CANCEL:
                return

        self.main_window.blocks = []
        self.main_window.pins   = []
        self.main_window.wires  = []
        self.main_window.current_file_path = None
        self.main_window.undo_stack = []
        self.main_window.redo_stack = []
        self.main_window.selected_block = None
        self.main_window.selected_pin   = None
        self.main_window.selected_wire  = None
        self.main_window.update_undo_redo_buttons()
        self.main_window.drawing_area.queue_draw()
        self.main_window.set_dirty(False)
        self.main_window.update_status_bar()

    def on_menu_file_load_generic_svcg(self, widget):
        confirm_dialog = Gtk.MessageDialog(
            transient_for=self.main_window, flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Replace working SVCG JSON/Project?",
        )
        confirm_dialog.format_secondary_text(
            "This operation will replace the existing SVCG project. Do you want to proceed?"
        )
        confirm_response = confirm_dialog.run()
        confirm_dialog.destroy()
        if confirm_response != Gtk.ResponseType.YES:
            return
        self.on_load_json_file(widget)

    def on_menu_file_new_generic_json(self, widget):
        self.on_save_as_json_file(widget)

    def on_menu_file_load_generic_json(self, widget):
        confirm_dialog = Gtk.MessageDialog(
            transient_for=self.main_window, flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Replace working SVCG JSON/Project?",
        )
        confirm_dialog.format_secondary_text(
            "This operation will replace the existing SVCG project. Do you want to proceed?"
        )
        confirm_response = confirm_dialog.run()
        confirm_dialog.destroy()
        if confirm_response != Gtk.ResponseType.YES:
            return
        self.on_load_json_file(widget)

    def on_save_component(self, widget):
        self.main_window.on_save_component(widget)

    def on_export_svg(self, widget):
        self.main_window.on_export_svg(widget)

    def on_export_png(self, widget):
        self.main_window.on_export_png(widget)

    def on_toggle_dark_mode(self, widget):
        mw = self.main_window
        mw.dark_mode = not mw.dark_mode
        Gtk.Settings.get_default().set_property(
            "gtk-application-prefer-dark-theme", mw.dark_mode
        )
        mw.drawing_area.queue_draw()
        mw.save_config()

    def on_menu_file_quit(self, widget):
        Gtk.main_quit()

    def on_button_press_event(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.popup.popup(None, None, None, None, event.button, event.time)
            return True

    def on_load_json_file(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Load File",
            parent=self.main_window,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,   Gtk.ResponseType.ACCEPT,
        )
        flt = Gtk.FileFilter()
        flt.set_name("JSON files")
        flt.add_mime_type("application/json")
        flt.add_pattern("*.json")
        dialog.add_filter(flt)
        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            self.main_window.load_from_json(dialog.get_filename())
        dialog.destroy()

    def on_save_json_file(self, widget):
        if self.main_window.current_file_path:
            self.main_window.save_to_json(self.main_window.current_file_path)
        else:
            self.on_save_as_json_file(widget)

    def on_save_as_json_file(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Save As File",
            parent=self.main_window,
            action=Gtk.FileChooserAction.SAVE,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,   Gtk.ResponseType.ACCEPT,
        )
        flt = Gtk.FileFilter()
        flt.set_name("JSON files")
        flt.add_mime_type("application/json")
        flt.add_pattern("*.json")
        dialog.add_filter(flt)

        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            file_path = dialog.get_filename()
            if not file_path.lower().endswith(".json"):
                file_path += ".json"
            if os.path.exists(file_path):
                confirm = Gtk.MessageDialog(
                    transient_for=self.main_window, flags=0,
                    message_type=Gtk.MessageType.WARNING,
                    buttons=Gtk.ButtonsType.YES_NO,
                    text="File already exists",
                )
                confirm.format_secondary_text(f"Replace '{file_path}'?")
                resp = confirm.run()
                confirm.destroy()
                if resp != Gtk.ResponseType.YES:
                    dialog.destroy()
                    return
            self.main_window.save_to_json(file_path)
            self.main_window.current_file_path = file_path
        dialog.destroy()
