#!/usr/bin/env python3
import gi
import os
import re
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from vhdl_export import generate_vhdl

UI_INFO = """
<ui>
  <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menu action='FileNew'>
        <menuitem action='FileNewSVCGProject' />
        <menuitem action='FileLoadSVCGProject' />
        <menuitem action='ImportSVCGJsonFile' />
        <menuitem action='ExportSVCGJsonFile' />
      </menu>
      <separator />
      <menuitem action='GenerateVHDL' />
      <separator />
      <menuitem action='FileQuit' />
    </menu>
    <menu action='EditMenu'>
      <menuitem action='EditCopy' />
      <menuitem action='EditPaste' />
      <menuitem action='EditSomething' />
    </menu>
    <menu action='ChoicesMenu'>
      <menuitem action='ChoiceOne'/>
      <menuitem action='ChoiceTwo'/>
      <separator />
      <menuitem action='ChoiceThree'/>
    </menu>
  </menubar>
  <toolbar name='ToolBar'>
    <toolitem action='FileNewSVCGProject' />
    <toolitem action='FileQuit' />
  </toolbar>
  <popup name='PopupMenu'>
    <menuitem action='EditCopy' />
    <menuitem action='EditPaste' />
    <menuitem action='EditSomething' />
  </popup>
</ui>
"""

class MenuBar:
    def __init__(self, main_window):
        self.main_window = main_window
        self.uimanager = self.create_ui_manager()
        action_group = Gtk.ActionGroup(name="my_actions")
        self.add_file_menu_actions(action_group)
        self.add_edit_menu_actions(action_group)
        self.add_choices_menu_actions(action_group)
        self.uimanager.insert_action_group(action_group)
        menubar = self.uimanager.get_widget("/MenuBar")
        toolbar = self.uimanager.get_widget("/ToolBar")
        self.popup = self.uimanager.get_widget("/PopupMenu")

        """
        # Create a file menu
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="File")
        file_item.set_submenu(file_menu)
        menubar.append(file_item)

        # Create load file menu item
        load_file_item = Gtk.MenuItem(label="Load File")
        load_file_item.connect("activate", self.on_load_json_file)
        file_menu.append(load_file_item)

        # Create save file menu item
        save_file_item = Gtk.MenuItem(label="Save File")
        save_file_item.connect("activate", self.on_save_json_file)
        file_menu.append(save_file_item)

        # Create save as file menu item
        save_as_file_item = Gtk.MenuItem(label="Save As File")
        save_as_file_item.connect("activate", self.on_save_as_json_file)
        file_menu.append(save_as_file_item)
        """

    def create_ui_manager(self):
        uimanager = Gtk.UIManager()
        # Throws exception if something went wrong
        uimanager.add_ui_from_string(UI_INFO)
        # Add the accelerator group to the toplevel window
        accelgroup = uimanager.get_accel_group()
        return uimanager

    def add_file_menu_actions(self, action_group):
        action_filemenu = Gtk.Action(name="FileMenu", label="File")
        action_group.add_action(action_filemenu)
        action_filenewmenu = Gtk.Action(name="FileNew", stock_id=Gtk.STOCK_NEW)
        action_group.add_action(action_filenewmenu)
        action_new = Gtk.Action(
            name="FileNewSVCGProject",
            label="_New SVCG Project",
            tooltip="Create a new SVCG Project",
            stock_id=Gtk.STOCK_NEW,
        )
        action_new.connect("activate", self.on_menu_file_new_generic_svcg)
        action_load = Gtk.Action(
            name="FileLoadSVCGProject",
            label="_Load SVCG Project",
            tooltip="Load an existing SVCG Project",
            stock_id=Gtk.STOCK_OPEN,
        )
        action_load.connect("activate", self.on_menu_file_load_generic_svcg)
        action_group.add_action_with_accel(action_new, None)
        action_group.add_action_with_accel(action_load, None)
        action_group.add_actions(
            [
                (
                    "ImportSVCGJsonFile",
                    None,
                    "Import SVCG wire diagram/schematic JSON file",
                    None,
                    "Import SVCG JSON file",
                    self.on_menu_file_load_generic_json,
                ),
                (
                    "ExportSVCGJsonFile",
                    None,
                    "Export SVCG wire diagram/schematic JSON file",
                    None,
                    "Export SVCG JSON file",
                    self.on_menu_file_new_generic_json,
                ),
            ]
        )
        action_gen_vhdl = Gtk.Action(
            name="GenerateVHDL",
            label="Generate VHDL...",
            tooltip="Generate VHDL entity+architecture from schematic",
        )
        action_gen_vhdl.connect("activate", self.on_generate_vhdl)
        action_group.add_action(action_gen_vhdl)

        action_filequit = Gtk.Action(name="FileQuit", stock_id=Gtk.STOCK_QUIT)
        action_filequit.connect("activate", self.on_menu_file_quit)
        action_group.add_action(action_filequit)

    def add_edit_menu_actions(self, action_group):
        action_group.add_actions(
            [
                ("EditMenu", None, "Edit"),
                ("EditCopy", Gtk.STOCK_COPY, None, None, None, self.on_menu_others),
                ("EditPaste", Gtk.STOCK_PASTE, None, None, None, self.on_menu_others),
                (
                    "EditSomething",
                    None,
                    "Something",
                    "<control><alt>S",
                    None,
                    self.on_menu_others,
                ),
            ]
        )

    def add_choices_menu_actions(self, action_group):
        action_group.add_action(Gtk.Action(name="ChoicesMenu", label="Choices"))
        action_group.add_radio_actions(
            [
                ("ChoiceOne", None, "One", None, None, 1),
                ("ChoiceTwo", None, "Two", None, None, 2),
            ],
            1,
            self.on_menu_choices_changed,
        )
        three = Gtk.ToggleAction(name="ChoiceThree", label="Three")
        three.connect("toggled", self.on_menu_choices_toggled)
        action_group.add_action(three)

    def on_generate_vhdl(self, widget):
        mw = self.main_window
        if not mw.blocks and not mw.pins:
            self._show_error("Nothing to export", "Add some blocks and IO pins to the canvas first.")
            return

        # ── Ask for entity name ──────────────────────────────────────────────
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

        # ── Generate VHDL ────────────────────────────────────────────────────
        try:
            vhdl_text = generate_vhdl(entity_name, mw.blocks, mw.pins, mw.wires)
        except Exception as exc:
            self._show_error("VHDL generation failed", str(exc))
            return

        # ── Save file dialog ─────────────────────────────────────────────────
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

            # ── Preview dialog ───────────────────────────────────────────────
            preview = Gtk.Dialog(
                title=f"Generated VHDL — {os.path.basename(path)}",
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
            preview.show_all()
            preview.run()
            preview.destroy()
        else:
            save_dialog.destroy()

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
            save_dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
            save_dialog.add_button("Save", Gtk.ResponseType.YES)
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
        self.main_window.pins = []
        self.main_window.wires = []
        self.main_window.current_file_path = None
        self.main_window.undo_stack = []
        self.main_window.redo_stack = []
        self.main_window.selected_block = None
        self.main_window.selected_pin = None
        self.main_window.selected_wire = None
        self.main_window.update_undo_redo_buttons()
        self.main_window.drawing_area.queue_draw()
        self.main_window.set_dirty(False)
        self.main_window.update_status_bar()

    def on_menu_file_load_generic_svcg(self, widget):
        print("A SVCG File|Load menu item was selected.")
        confirm_dialog = Gtk.MessageDialog(
            transient_for=self.main_window,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Replace working SVCG JSON/Project?",
        )
        confirm_dialog.format_secondary_text(f"This operation will replace the existing SVCG JSON file contents/Project. Do you want to proceed?")
        confirm_response = confirm_dialog.run()
        confirm_dialog.destroy()

        if confirm_response != Gtk.ResponseType.YES:
            return
        self.on_load_json_file(widget)



    def on_menu_file_new_generic_json(self, widget):
        print("A JSON wire diagram File|New menu item was selected.")
        self.on_save_as_json_file(widget)

    def on_menu_file_load_generic_json(self, widget):
        print("A JSON wire diagram File|Load menu item was selected.")
        confirm_dialog = Gtk.MessageDialog(
            transient_for=self.main_window,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Replace working SVCG JSON/Project?",
        )
        confirm_dialog.format_secondary_text(f"This operation will replace the existing SVCG JSON file contents/Project. Do you want to proceed?")
        confirm_response = confirm_dialog.run()
        confirm_dialog.destroy()

        if confirm_response != Gtk.ResponseType.YES:
            return
        self.on_load_json_file(widget)


    def on_menu_file_quit(self, widget):
        Gtk.main_quit()

    def on_menu_others(self, widget):
        print("Menu item " + widget.get_name() + " was selected")

    def on_menu_choices_changed(self, widget, current):
        print(current.get_name() + " was selected.")

    def on_menu_choices_toggled(self, widget):
        if widget.get_active():
            print(widget.get_name() + " activated")
        else:
            print(widget.get_name() + " deactivated")

    def on_button_press_event(self, widget, event):
        # Check if right mouse button was pressed
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.popup.popup(None, None, None, None, event.button, event.time)
            return True  # event has been handled

    def on_load_json_file(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Load File",
            parent=self.main_window,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT
        )

        # Add a filter to only show JSON files
        filter_json = Gtk.FileFilter()
        filter_json.set_name("JSON files")
        filter_json.add_mime_type("application/json")
        filter_json.add_pattern("*.json")
        dialog.add_filter(filter_json)

        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            file_path = dialog.get_filename()
            self.main_window.load_from_json(file_path)
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
            action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT
        )
    
        # Add a filter to only show JSON files
        filter_json = Gtk.FileFilter()
        filter_json.set_name("JSON files")
        filter_json.add_mime_type("application/json")
        filter_json.add_pattern("*.json")
        dialog.add_filter(filter_json)
    
        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            file_path = dialog.get_filename()
            # Ensure the file path ends with .json
            if not file_path.lower().endswith('.json'):
                file_path += '.json'
    
            # Check if the file already exists
            if os.path.exists(file_path):
                confirm_dialog = Gtk.MessageDialog(
                    transient_for=self.main_window,
                    flags=0,
                    message_type=Gtk.MessageType.WARNING,
                    buttons=Gtk.ButtonsType.YES_NO,
                    text="File already exists",
                )
                confirm_dialog.format_secondary_text(f"Do you want to replace the existing file '{file_path}'?")
                confirm_response = confirm_dialog.run()
                confirm_dialog.destroy()
    
                if confirm_response != Gtk.ResponseType.YES:
                    dialog.destroy()
                    return
    
            self.main_window.save_to_json(file_path)
            self.main_window.current_file_path = file_path
        dialog.destroy()
    
