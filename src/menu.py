#!/usr/bin/env python3
import gi
import os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

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

    def on_menu_file_new_generic_svcg(self, widget):
        print("A SVCG File|New menu item was selected.")

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
            dialog.destroy()
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
            dialog.destroy()
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
            self.on_save_as_file(widget)

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
    
