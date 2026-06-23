#!/usr/bin/env python3
import gi
import os
import re
import tempfile
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from vhdl_export import generate_vhdl, check_vhdl_syntax, generate_custom_vhd
from testbench_gen import generate_testbench, run_ghdl_simulation, launch_gtkwave
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
        file_menu.append(_mi("Generate VHDL...",             self.on_generate_vhdl))
        file_menu.append(_mi("Generate Testbench + Simulate...", self.on_generate_testbench))
        file_menu.append(_mi("Import Yosys Netlist...",      self.on_import_yosys))
        file_menu.append(_mi("Save Selection as Component...", self.on_save_component))
        file_menu.append(Gtk.SeparatorMenuItem())
        file_menu.append(_mi("Export as SVG...",             self.on_export_svg))
        file_menu.append(_mi("Export as PNG...",             self.on_export_png))
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

        # Ask for entity name
        name_dialog = Gtk.MessageDialog(
            transient_for=mw, flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Generate VHDL",
        )
        name_dialog.format_secondary_text("Enter top-level entity name:")
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

        # Generate VHDL
        try:
            vhdl_text = generate_vhdl(entity_name, mw.blocks, mw.pins, mw.wires)
        except Exception as exc:
            self._show_error("VHDL generation failed", str(exc))
            return

        # Save file dialog
        save_dialog = Gtk.FileChooserDialog(
            title="Save VHDL File",
            parent=mw,
            action=Gtk.FileChooserAction.SAVE,
        )
        save_dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,   Gtk.ResponseType.ACCEPT,
        )
        save_dialog.set_current_name(f"{entity_name.lower()}.vhd")
        flt = Gtk.FileFilter()
        flt.set_name("VHDL files (*.vhd, *.vhdl)")
        flt.add_pattern("*.vhd")
        flt.add_pattern("*.vhdl")
        save_dialog.add_filter(flt)
        if mw.current_file_path:
            save_dialog.set_current_folder(os.path.dirname(mw.current_file_path))

        resp = save_dialog.run()
        if resp == Gtk.ResponseType.ACCEPT:
            path = save_dialog.get_filename()
            if not path.lower().endswith((".vhd", ".vhdl")):
                path += ".vhd"
            save_dialog.destroy()
            try:
                with open(path, "w") as f:
                    f.write(vhdl_text)
            except IOError as exc:
                self._show_error("Could not write file", str(exc))
                return

            # GHDL syntax check (optional)
            ghdl_available, ghdl_ok, ghdl_out = check_vhdl_syntax(path)
            if ghdl_available:
                ghdl_banner = "GHDL: syntax OK" if ghdl_ok else "GHDL errors:\n" + (ghdl_out or "(no output)")
            else:
                ghdl_banner = "(ghdl not found on PATH -- install ghdl to enable syntax check)"

            # Preview dialog
            preview = Gtk.Dialog(
                title=f"Generated VHDL -- {os.path.basename(path)}",
                transient_for=mw,
                flags=0,
            )
            preview.add_button("Close", Gtk.ResponseType.CLOSE)
            preview.set_default_size(700, 500)
            sw = Gtk.ScrolledWindow()
            sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            tv = Gtk.TextView()
            tv.set_editable(False)
            tv.set_monospace(True)
            tv.get_buffer().set_text(vhdl_text)
            sw.add(tv)
            preview.get_content_area().pack_start(sw, True, True, 0)
            ghdl_label = Gtk.Label(label=ghdl_banner)
            ghdl_label.set_halign(Gtk.Align.START)
            ghdl_label.set_margin_start(6)
            ghdl_label.set_margin_bottom(4)
            if ghdl_available and not ghdl_ok:
                ghdl_label.set_markup(
                    "<span color='red'>" + ghdl_banner.replace("&", "&amp;").replace("<", "&lt;") + "</span>"
                )
            elif ghdl_available and ghdl_ok:
                ghdl_label.set_markup("<span color='green'>" + ghdl_banner + "</span>")
            preview.get_content_area().pack_start(ghdl_label, False, False, 0)
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
        if not mw.pins:
            self._show_error("Nothing to export", "Add IO pins to define the entity ports first.")
            return

        # Ask for entity name
        name_dialog = Gtk.MessageDialog(
            transient_for=mw, flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Generate Testbench",
        )
        name_dialog.format_secondary_text("Enter top-level entity name:")
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

        # Generate entity + testbench text
        try:
            entity_vhdl = generate_vhdl(entity_name, mw.blocks, mw.pins, mw.wires)
            tb_vhdl     = generate_testbench(entity_name, mw.pins)
        except Exception as exc:
            self._show_error("Generation failed", str(exc))
            return

        # File chooser for testbench save path
        save_dialog = Gtk.FileChooserDialog(
            title="Save Testbench File",
            parent=mw,
            action=Gtk.FileChooserAction.SAVE,
        )
        save_dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,   Gtk.ResponseType.ACCEPT,
        )
        save_dialog.set_current_name(f"{entity_name.lower()}_tb.vhd")
        flt = Gtk.FileFilter()
        flt.set_name("VHDL files (*.vhd, *.vhdl)")
        flt.add_pattern("*.vhd")
        flt.add_pattern("*.vhdl")
        save_dialog.add_filter(flt)
        if mw.current_file_path:
            save_dialog.set_current_folder(os.path.dirname(mw.current_file_path))
        resp = save_dialog.run()
        if resp != Gtk.ResponseType.ACCEPT:
            save_dialog.destroy()
            return
        tb_path = save_dialog.get_filename()
        save_dialog.destroy()
        if not tb_path.lower().endswith((".vhd", ".vhdl")):
            tb_path += ".vhd"

        workdir = os.path.dirname(tb_path)
        entity_path = os.path.join(workdir, f"{entity_name.lower()}.vhd")

        try:
            with open(entity_path, "w") as f:
                f.write(entity_vhdl)
            with open(tb_path, "w") as f:
                f.write(tb_vhdl)
        except IOError as exc:
            self._show_error("Could not write file", str(exc))
            return

        # Collect custom RTL block VHDs for GHDL
        custom_vhds = []
        seen_custom = set()
        for block in mw.blocks:
            if block.block_type == "CUSTOM":
                cd = getattr(block, "custom_data", None) or {}
                ename = cd.get("entity_name", "CUSTOM_BLOCK")
                if ename not in seen_custom:
                    seen_custom.add(ename)
                    vhd = generate_custom_vhd(
                        ename,
                        cd.get("input_names", []),
                        cd.get("output_names", []),
                        cd.get("vhdl", ""),
                    )
                    custom_vhds.append((ename, vhd))

        # Try GHDL simulation
        tb_entity = f"{entity_name.lower()}_tb"
        sim_ok, sim_log, vcd_path = run_ghdl_simulation(
            entity_path, tb_path, tb_entity, workdir,
            custom_vhds=custom_vhds if custom_vhds else None,
        )

        # Preview dialog
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
        tv = Gtk.TextView()
        tv.set_editable(False)
        tv.set_monospace(True)
        tv.get_buffer().set_text(tb_vhdl)
        sw.add(tv)
        preview.get_content_area().pack_start(sw, True, True, 0)

        if sim_log:
            sim_label = Gtk.Label(label=sim_log[:500])
            sim_label.set_halign(Gtk.Align.START)
            sim_label.set_margin_start(6)
            sim_label.set_margin_bottom(4)
            sim_label.set_line_wrap(True)
            if not sim_ok:
                sim_label.set_markup(
                    "<span color='red'>" +
                    sim_log[:500].replace("&", "&amp;").replace("<", "&lt;") +
                    "</span>"
                )
            else:
                sim_label.set_markup("<span color='green'>" + sim_log[:200] + "</span>")
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
