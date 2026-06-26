#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class ContextMenu:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.context_menu = Gtk.Menu()
        self._edit_rtl_item = None  # set in __init__ body below

        change_border_color_item = Gtk.MenuItem(label="Change Border Color")
        change_fill_color_item = Gtk.MenuItem(label="Change Fill Color")
        change_text_item = Gtk.MenuItem(label="Change Text/Rename")
        change_text_color_item = Gtk.MenuItem(label="Change Text Color")
        rotate_90_item = Gtk.MenuItem(label="Rotate 90° (CTRL + p)")
        rotate_180_item = Gtk.MenuItem(label="Rotate 180°")
        rotate_270_item = Gtk.MenuItem(label="Rotate 270°")
        copy_item = Gtk.MenuItem(label="Copy (CTRL + c)")
        delete_item = Gtk.MenuItem(label="Delete (CTRL + d)")
        view_vhdl_item = Gtk.MenuItem(label="View VHDL Code")
        self._edit_rtl_item = Gtk.MenuItem(label="Edit RTL...")

        change_border_color_item.connect("activate", self.on_change_border_color)
        change_fill_color_item.connect("activate", self.on_change_fill_color)
        change_text_item.connect("activate", self.on_change_text)
        change_text_color_item.connect("activate", self.on_change_text_color)
        rotate_90_item.connect("activate", self.on_rotate_90)
        rotate_180_item.connect("activate", self.on_rotate_180)
        rotate_270_item.connect("activate", self.on_rotate_270)
        copy_item.connect("activate", self.on_copy_block)
        delete_item.connect("activate", self.on_delete_block)
        view_vhdl_item.connect("activate", self.on_view_vhdl_code)
        self._edit_rtl_item.connect("activate", self.on_edit_rtl)

        self.context_menu.append(change_border_color_item)
        self.context_menu.append(change_fill_color_item)
        self.context_menu.append(change_text_item)
        self.context_menu.append(change_text_color_item)
        self.context_menu.append(rotate_90_item)
        self.context_menu.append(rotate_180_item)
        self.context_menu.append(rotate_270_item)
        self.context_menu.append(copy_item)
        self.context_menu.append(delete_item)
        self.context_menu.append(view_vhdl_item)
        self.context_menu.append(self._edit_rtl_item)
        self.context_menu.show_all()

    def popup(self, event):
        blk = self.parent_window.selected_block
        self._edit_rtl_item.set_visible(blk is not None and blk.block_type == "CUSTOM")
        self.context_menu.popup(None, None, None, None, event.button, event.time)

    def on_change_border_color(self, widget):
        self.parent_window.on_change_border_color(widget)

    def on_change_fill_color(self, widget):
        self.parent_window.on_change_fill_color(widget)

    def on_change_text(self, widget):
        self.parent_window.on_change_text(widget)

    def on_change_text_color(self, widget):
        self.parent_window.on_change_text_color(widget)

    def on_rotate_90(self, widget):
        self.parent_window.on_rotate_90(widget)

    def on_rotate_180(self, widget):
        self.parent_window.on_rotate_180(widget)

    def on_rotate_270(self, widget):
        self.parent_window.on_rotate_270(widget)

    def on_copy_block(self, widget):
        self.parent_window.on_copy_block(widget)

    def on_delete_block(self, widget):
        self.parent_window.on_delete_block(widget)

    def on_view_vhdl_code(self, widget):
        self.parent_window.on_view_vhdl_code(widget)

    def on_edit_rtl(self, widget):
        self.parent_window.on_edit_custom_rtl_block(widget)

    def set_view_vhdl_code_sensitive(self, sensitive):
        for item in self.context_menu.get_children():
            if item.get_label() == "View VHDL Code":
                item.set_sensitive(sensitive)
                break

class PinContextMenu:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.context_menu = Gtk.Menu()

        disconnect_item = Gtk.MenuItem(label="Disconnect (remove wires)")
        disconnect_item.connect("activate", self.on_disconnect)
        self.context_menu.append(disconnect_item)
        self.context_menu.show_all()

    def popup(self, event):
        self.context_menu.popup(None, None, None, None, event.button, event.time)

    def on_disconnect(self, widget):
        self.parent_window.on_disconnect_pin(widget)

class WireContextMenu(Gtk.Menu):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        rename_item = Gtk.MenuItem(label="Rename (set net name)")
        rename_item.connect("activate", self.on_rename_wire)
        self.append(rename_item)

        delete_item = Gtk.MenuItem(label="Delete")
        delete_item.connect("activate", self.on_delete_wire)
        self.append(delete_item)

        self.show_all()

    def on_rename_wire(self, widget):
        wire = self.parent.selected_wire
        if not wire:
            return
        dialog = Gtk.MessageDialog(
            transient_for=self.parent, flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Rename Wire / Set Net Name",
        )
        entry = Gtk.Entry()
        entry.set_text(wire.text)
        entry.set_activates_default(True)
        dialog.get_content_area().pack_end(entry, False, False, 6)
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            wire.text = entry.get_text()
            self.parent.update_json()
            self.parent.push_undo()
            self.parent.drawing_area.queue_draw()
            self.parent.update_status_bar()
        dialog.destroy()

    def on_delete_wire(self, widget):
        if self.parent.selected_wire:
            self.parent.delete_wire(self.parent.selected_wire)
            self.parent.selected_wire = None

