#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from blocks import Block
import numpy as np

class DrawingArea(Gtk.DrawingArea):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.grid = None
        self.connect("draw", self.on_draw)
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK |
                        Gdk.EventMask.KEY_PRESS_MASK)
        self.connect("button-press-event", self.on_button_press)
        self.connect("button-release-event", self.on_button_release)
        self.connect("motion-notify-event", self.on_motion_notify)
        self.connect("key-press-event", self.on_key_press)
        self.set_can_focus(True)  # Allow the widget to receive focus

    def on_draw(self, widget, cr):
        width, height = self.get_allocated_width(), self.get_allocated_height()
        self.create_grid(width, height, self.parent_window.grid_size)
        self.parent_window.on_draw(widget, cr)

    def create_grid(self, width, height, grid_size):
        self.grid = np.zeros((height // grid_size, width // grid_size), dtype=int)
        for block in self.parent_window.blocks:
            self.mark_block_on_grid(block, grid_size)
        for pin in self.parent_window.pins:
            self.mark_pin_on_grid(pin, grid_size)
        #print(f"Grid created: {self.grid}")

    def mark_block_on_grid(self, block, grid_size):
        x1, y1 = int(block.x // grid_size), int(block.y // grid_size)
        x2, y2 = int((block.x + block.width) // grid_size), int((block.y + block.height) // grid_size)
        self.grid[y1:y2, x1:x2] = 1

    def mark_pin_on_grid(self, pin, grid_size):
        x1, y1 = int(pin.x // grid_size), int(pin.y // grid_size)
        x2, y2 = int((pin.x + pin.width) // grid_size), int((pin.y + pin.height) // grid_size)
        self.grid[y1:y2, x1:x2] = 1

    def on_button_press(self, widget, event):
        self.parent_window.on_button_press(widget, event)

    def on_button_release(self, widget, event):
        self.parent_window.on_button_release(widget, event)

    def on_motion_notify(self, widget, event):
        self.parent_window.on_motion_notify(widget, event)

    def on_key_press(self, widget, event):
        self.parent_window.on_key_press(widget, event)

