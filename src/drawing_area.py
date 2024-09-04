#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from blocks import Block

class DrawingArea(Gtk.DrawingArea):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
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
        self.parent_window.on_draw(widget, cr)

    def on_button_press(self, widget, event):
        self.parent_window.on_button_press(widget, event)

    def on_button_release(self, widget, event):
        self.parent_window.on_button_release(widget, event)

    def on_motion_notify(self, widget, event):
        self.parent_window.on_motion_notify(widget, event)

    def on_key_press(self, widget, event):
        self.parent_window.on_key_press(widget, event)


