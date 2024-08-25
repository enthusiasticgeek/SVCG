#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from blocks import Block
from context_menu import ContextMenu
from drawing_area import DrawingArea

class BlocksWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Simple VHDL Code Generator (SVCG)")
        self.set_default_size(1000, 600)

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(self.box)

        self.left_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.box.pack_start(self.left_pane, False, False, 0)

        # Create an expander for the digital gates menu
        self.expander = Gtk.Expander(label="Digital Gates")
        self.left_pane.pack_start(self.expander, False, False, 0)

        self.gate_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.expander.add(self.gate_box)

        buttons = [
            ("AND Gate", "AND"),
            ("OR Gate", "OR"),
            ("NOT Gate", "NOT"),
            ("NAND Gate", "NAND"),
            ("NOR Gate", "NOR"),
            ("XOR Gate", "XOR"),
            ("XNOR Gate", "XNOR")
        ]

        for label, block_type in buttons:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_button_clicked, block_type)
            self.gate_box.pack_start(button, False, False, 0)

        self.drawing_area = DrawingArea(self)
        self.box.pack_start(self.drawing_area, True, True, 0)

        self.blocks = []
        self.grid_size = 20

        # Create context menu
        self.context_menu = ContextMenu(self)

        self.selected_block = None

    def on_button_clicked(self, widget, block_type):
        # Ensure the initial position and size are multiples of the grid size
        initial_x = round(50 / self.grid_size) * self.grid_size
        initial_y = round(50 / self.grid_size) * self.grid_size
        initial_width = round(50 / self.grid_size) * self.grid_size  # Half of the current width
        initial_height = round(50 / self.grid_size) * self.grid_size
        new_block = Block(initial_x, initial_y, initial_width, initial_height, block_type, block_type, self.grid_size)
        self.blocks.append(new_block)
        self.drawing_area.queue_draw()

    def on_draw(self, widget, cr):
        # Draw grid
        cr.set_source_rgb(0, 1, 0)  # Green color for grid points
        width, height = self.drawing_area.get_allocated_width(), self.drawing_area.get_allocated_height()
        for x in range(0, width, self.grid_size):
            for y in range(0, height, self.grid_size):
                cr.rectangle(x, y, 2, 2)
                cr.fill()

        # Draw row labels (A, B, ..., Z, AA, ..., ZZ)
        cr.set_source_rgb(0, 0, 0)  # Black color for labels
        cr.set_font_size(12)
        for i, x in enumerate(range(0, width, self.grid_size)):
            label = self.get_column_label(i)
            cr.move_to(x + 5, 15)
            cr.show_text(label)

        # Draw column labels (1, 2, 3, ...)
        for i, y in enumerate(range(0, height, self.grid_size)):
            label = str(i + 1)
            cr.move_to(5, y + 15)
            cr.show_text(label)

        # Draw blocks
        for block in self.blocks:
            block.draw(cr)

    def get_column_label(self, index):
        label = ""
        while index >= 0:
            label = chr(index % 26 + ord('A')) + label
            index = index // 26 - 1
        return label

    def on_button_press(self, widget, event):
        if event.button == 1:  # Left click
            for block in self.blocks:
                if block.contains_point(event.x, event.y):
                    block.start_drag(event.x, event.y)
                    break
        elif event.button == 3:  # Right click
            for block in self.blocks:
                if block.contains_point(event.x, event.y):
                    self.selected_block = block
                    self.context_menu.popup(event)
                    break

    def on_button_release(self, widget, event):
        for block in self.blocks:
            block.end_drag()
        self.drawing_area.queue_draw()

    def on_motion_notify(self, widget, event):
        width, height = self.drawing_area.get_allocated_width(), self.drawing_area.get_allocated_height()
        for block in self.blocks:
            block.drag(event.x, event.y, width, height)
        self.drawing_area.queue_draw()

    def on_change_border_color(self, widget):
        if self.selected_block:
            dialog = Gtk.ColorChooserDialog(title="Choose Border Color", transient_for=self)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                color = dialog.get_rgba()
                self.selected_block.border_color = (color.red, color.green, color.blue)
                self.drawing_area.queue_draw()
            dialog.destroy()

    def on_change_fill_color(self, widget):
        if self.selected_block:
            dialog = Gtk.ColorChooserDialog(title="Choose Fill Color", transient_for=self)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                color = dialog.get_rgba()
                self.selected_block.fill_color = (color.red, color.green, color.blue)
                self.drawing_area.queue_draw()
            dialog.destroy()

    def on_change_text(self, widget):
        if self.selected_block:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text="Change Text",
            )
            dialog.format_secondary_text("Enter new text for the block:")
            entry = Gtk.Entry()
            entry.set_text(self.selected_block.text)
            dialog.get_content_area().add(entry)
            dialog.show_all()
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.selected_block.text = entry.get_text()
                self.drawing_area.queue_draw()
            dialog.destroy()

    def on_change_text_color(self, widget):
        if self.selected_block:
            dialog = Gtk.ColorChooserDialog(title="Choose Text Color", transient_for=self)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                color = dialog.get_rgba()
                self.selected_block.text_color = (color.red, color.green, color.blue)
                self.drawing_area.queue_draw()
            dialog.destroy()

    def on_rotate_90(self, widget):
        if self.selected_block:
            self.selected_block.rotate(90)
            self.drawing_area.queue_draw()

    def on_rotate_180(self, widget):
        if self.selected_block:
            self.selected_block.rotate(180)
            self.drawing_area.queue_draw()

    def on_rotate_270(self, widget):
        if self.selected_block:
            self.selected_block.rotate(270)
            self.drawing_area.queue_draw()

    def on_copy_block(self, widget):
        if self.selected_block:
            # Create a copy of the selected block
            new_block = Block(
                self.selected_block.x + self.grid_size,
                self.selected_block.y + self.grid_size,
                self.selected_block.width,
                self.selected_block.height,
                self.selected_block.text,
                self.selected_block.block_type,
                self.grid_size
            )
            new_block.border_color = self.selected_block.border_color
            new_block.fill_color = self.selected_block.fill_color
            new_block.text_color = self.selected_block.text_color
            new_block.rotation = self.selected_block.rotation
            self.blocks.append(new_block)
            self.drawing_area.queue_draw()

    def on_delete_block(self, widget):
        if self.selected_block:
            self.blocks.remove(self.selected_block)
            self.selected_block = None
            self.drawing_area.queue_draw()

if __name__ == "__main__":
    win = BlocksWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

