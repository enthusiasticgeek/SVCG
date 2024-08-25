#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class ContextMenu:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.context_menu = Gtk.Menu()

        change_border_color_item = Gtk.MenuItem(label="Change Border Color")
        change_fill_color_item = Gtk.MenuItem(label="Change Fill Color")
        change_text_item = Gtk.MenuItem(label="Change Text")
        change_text_color_item = Gtk.MenuItem(label="Change Text Color")
        rotate_90_item = Gtk.MenuItem(label="Rotate 90°")
        rotate_180_item = Gtk.MenuItem(label="Rotate 180°")
        rotate_270_item = Gtk.MenuItem(label="Rotate 270°")
        copy_item = Gtk.MenuItem(label="Copy")
        delete_item = Gtk.MenuItem(label="Delete")

        change_border_color_item.connect("activate", self.on_change_border_color)
        change_fill_color_item.connect("activate", self.on_change_fill_color)
        change_text_item.connect("activate", self.on_change_text)
        change_text_color_item.connect("activate", self.on_change_text_color)
        rotate_90_item.connect("activate", self.on_rotate_90)
        rotate_180_item.connect("activate", self.on_rotate_180)
        rotate_270_item.connect("activate", self.on_rotate_270)
        copy_item.connect("activate", self.on_copy_block)
        delete_item.connect("activate", self.on_delete_block)

        self.context_menu.append(change_border_color_item)
        self.context_menu.append(change_fill_color_item)
        self.context_menu.append(change_text_item)
        self.context_menu.append(change_text_color_item)
        self.context_menu.append(rotate_90_item)
        self.context_menu.append(rotate_180_item)
        self.context_menu.append(rotate_270_item)
        self.context_menu.append(copy_item)
        self.context_menu.append(delete_item)
        self.context_menu.show_all()

    def popup(self, event):
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

