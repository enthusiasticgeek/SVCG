#!/usr/bin/env python3
from main_window import BlocksWindow
import signal
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def signal_handler(sig, frame):
    print("CTRL+C detected. Exiting gracefully...")
    Gtk.main_quit()
    sys.exit(0)

if __name__ == "__main__":
    # Set up the signal handler for SIGINT (CTRL+C)
    signal.signal(signal.SIGINT, signal_handler)

    win = BlocksWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

