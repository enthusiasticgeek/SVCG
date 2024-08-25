#!/usr/bin/env python3
from main_window import BlocksWindow
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

if __name__ == "__main__":
    win = BlocksWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

