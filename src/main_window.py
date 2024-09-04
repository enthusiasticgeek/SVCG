#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from blocks import Block
from context_menu import ContextMenu
from context_menu import PinContextMenu
from drawing_area import DrawingArea
from datetime import datetime
from pins import Pin  # Import the Pin class
import json

class BlocksWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Simple VHDL Code Generator (SVCG)")
        self.set_default_size(1000, 600)

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(self.box)

        self.left_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.box.pack_start(self.left_pane, False, False, 0)

        # Create an expander_pins for the pins menu
        self.expander_pins = Gtk.Expander(label="IO Pins/Buses")
        self.left_pane.pack_start(self.expander_pins, False, False, 0)

        self.pins_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.expander_pins.add(self.pins_box)

        # Add buttons for creating pins and buses
        pin_buttons = [
            ("Input Pin", "input_pin"),
            ("Output Pin", "output_pin"),
            ("Input/Output Pin", "input_output_pin"),
            ("Input Bus", "input_bus"),
            ("Output Bus", "output_bus"),
            ("Input/Output Bus", "input_output_bus")
        ]

        for label, pin_type in pin_buttons:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_pin_button_clicked, pin_type)
            self.pins_box.pack_start(button, False, False, 0)


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

        # Create an expander_ops for the operations menu
        self.expander_ops = Gtk.Expander(label="Edit Operations")
        self.left_pane.pack_start(self.expander_ops, False, False, 0)

        self.ops_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.expander_ops.add(self.ops_box)

        for label, block_type in buttons:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_button_clicked, block_type)
            self.gate_box.pack_start(button, False, False, 0)

        # Add undo/redo buttons
        self.undo_button = Gtk.Button(label="Undo")
        self.undo_button.connect("clicked", self.on_undo)
        self.ops_box.pack_start(self.undo_button, False, False, 0)

        self.redo_button = Gtk.Button(label="Redo")
        self.redo_button.connect("clicked", self.on_redo)
        self.ops_box.pack_start(self.redo_button, False, False, 0)


        #self.drawing_area = DrawingArea(self)
        #self.box.pack_start(self.drawing_area, True, True, 0)


        # Wrap the DrawingArea in a ScrolledWindow
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.drawing_area = DrawingArea(self)
        self.scrolled_window.add(self.drawing_area)
        self.box.pack_start(self.scrolled_window, True, True, 0)

        self.blocks = []
        self.pins = []  # List to store pins
        self.grid_size = 20

        # Create context menu
        self.context_menu = ContextMenu(self)
        self.pin_context_menu = PinContextMenu(self)

        self.selected_block = None
        self.selected_pin = None  # Variable to store the selected pin

        # Initialize undo/redo stacks
        self.undo_stack = []
        self.redo_stack = []

        self.update_undo_redo_buttons()  # Initialize the sensitivity of the buttons

        self.drawing_area.grab_focus()  # Ensure the DrawingArea has keyboard focus


    def on_button_clicked(self, widget, block_type):
        self.push_undo()
        # Ensure the initial position and size are multiples of the grid size
        initial_x = round(50 / self.grid_size) * self.grid_size
        initial_y = round(50 / self.grid_size) * self.grid_size
        initial_width = round(50 / self.grid_size) * self.grid_size  # Half of the current width
        initial_height = round(50 / self.grid_size) * self.grid_size
        timestamp = datetime.now().isoformat(' ', 'seconds')
        new_block = Block(initial_x, initial_y, initial_width, initial_height, f"{block_type} {timestamp}", block_type, self.grid_size)
        self.blocks.append(new_block)
        self.drawing_area.queue_draw()
        self.update_json()
        #self.push_undo()


    def on_pin_button_clicked(self, widget, pin_type):
        self.push_undo()
        # Ensure the initial position and size are multiples of the grid size
        initial_x = round(50 / self.grid_size) * self.grid_size
        initial_y = round(50 / self.grid_size) * self.grid_size
        initial_width = round(50 / self.grid_size) * self.grid_size  # Half of the current width
        initial_height = round(50 / self.grid_size) * self.grid_size
        timestamp = datetime.now().isoformat(' ', 'seconds')

        if "bus" in pin_type:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text="Enter Number of Pins",
            )
            entry = Gtk.Entry()
            dialog.get_content_area().add(entry)
            dialog.show_all()
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                num_pins = int(entry.get_text())
                new_pin = Pin(initial_x, initial_y, initial_width, initial_height * num_pins, f"{pin_type} {timestamp}", pin_type, self.grid_size, num_pins)
                self.pins.append(new_pin)
                self.drawing_area.queue_draw()
                self.update_json()
            dialog.destroy()
        else:
            new_pin = Pin(initial_x, initial_y, initial_width, initial_height, f"{pin_type} {timestamp}", pin_type, self.grid_size)
            self.pins.append(new_pin)
            self.drawing_area.queue_draw()
            self.update_json()

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

        # Draw pins
        for pin in self.pins:
            pin.draw(cr)

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
                for pin in self.pins:
                    if pin.contains_point(event.x, event.y):
                        pin.start_drag(event.x, event.y)
                        break
            elif event.button == 3:  # Right click
                for block in self.blocks:
                    if block.contains_point(event.x, event.y):
                        self.selected_block = block
                        if block.contains_pin(event.x, event.y):
                            self.pin_context_menu.popup(event)
                        else:
                            self.context_menu.popup(event)
                        break
                for pin in self.pins:
                    if pin.contains_point(event.x, event.y):
                        self.selected_pin = pin
                        if pin.contains_pin(event.x, event.y):
                            self.pin_context_menu.popup(event)
                        else:
                            self.context_menu.popup(event)
                        break


    def on_key_press(self, widget, event):
        key = Gdk.keyval_name(event.keyval)
        if key == "z" and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.undo()
        elif key == "r" and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.redo()


    def on_button_release(self, widget, event):
        for block in self.blocks:
            block.end_drag()
        for pin in self.pins:
            pin.end_drag()
        self.drawing_area.queue_draw()
        self.update_json()
        self.push_undo()

    def on_motion_notify(self, widget, event):
        width, height = self.drawing_area.get_allocated_width(), self.drawing_area.get_allocated_height()
        for block in self.blocks:
            block.drag(event.x, event.y, width, height)
        for pin in self.pins:
            pin.drag(event.x, event.y, width, height)
        self.drawing_area.queue_draw()
        self.update_json()
        #self.push_undo()

    def on_change_border_color(self, widget):
        if self.selected_block:
            dialog = Gtk.ColorChooserDialog(title="Choose Border Color", transient_for=self)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                color = dialog.get_rgba()
                self.selected_block.border_color = (color.red, color.green, color.blue)
                self.drawing_area.queue_draw()
                self.update_json()  # Update the JSON file
                self.push_undo()
            dialog.destroy()
        elif self.selected_pin:
            dialog = Gtk.ColorChooserDialog(title="Choose Border Color", transient_for=self)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                color = dialog.get_rgba()
                self.selected_pin.border_color = (color.red, color.green, color.blue)
                self.drawing_area.queue_draw()
                self.update_json()  # Update the JSON file
                self.push_undo()
            dialog.destroy()

    def on_change_fill_color(self, widget):
        if self.selected_block:
            dialog = Gtk.ColorChooserDialog(title="Choose Fill Color", transient_for=self)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                color = dialog.get_rgba()
                self.selected_block.fill_color = (color.red, color.green, color.blue)
                self.drawing_area.queue_draw()
                self.update_json()  # Update the JSON file
                self.push_undo()
            dialog.destroy()
        elif self.selected_pin:
            dialog = Gtk.ColorChooserDialog(title="Choose Fill Color", transient_for=self)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                color = dialog.get_rgba()
                self.selected_pin.fill_color = (color.red, color.green, color.blue)
                self.drawing_area.queue_draw()
                self.update_json()  # Update the JSON file
                self.push_undo()
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
                self.update_json()  # Update the JSON file
                self.push_undo()
            dialog.destroy()
        elif self.selected_pin:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text="Change Text",
            )
            dialog.format_secondary_text("Enter new text for the pin:")
            entry = Gtk.Entry()
            entry.set_text(self.selected_pin.text)
            dialog.get_content_area().add(entry)
            dialog.show_all()
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.selected_pin.text = entry.get_text()
                self.drawing_area.queue_draw()
                self.update_json()  # Update the JSON file
                self.push_undo()
            dialog.destroy()


    def on_change_text_color(self, widget):
        if self.selected_block:
            dialog = Gtk.ColorChooserDialog(title="Choose Text Color", transient_for=self)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                color = dialog.get_rgba()
                self.selected_block.text_color = (color.red, color.green, color.blue)
                self.drawing_area.queue_draw()
                self.update_json()  # Update the JSON file
                self.push_undo()
            dialog.destroy()
        elif self.selected_pin:
            dialog = Gtk.ColorChooserDialog(title="Choose Text Color", transient_for=self)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                color = dialog.get_rgba()
                self.selected_pin.text_color = (color.red, color.green, color.blue)
                self.drawing_area.queue_draw()
                self.update_json()  # Update the JSON file
                self.push_undo()
            dialog.destroy()

    def on_rotate_90(self, widget):
        if self.selected_block:
            self.selected_block.rotate(90)
            self.drawing_area.queue_draw()
            self.update_json()  # Update the JSON file
            self.push_undo()
        elif self.selected_pin:
            self.selected_pin.rotate(90)
            self.drawing_area.queue_draw()
            self.update_json()  # Update the JSON file
            self.push_undo()

    def on_rotate_180(self, widget):
        if self.selected_block:
            self.selected_block.rotate(180)
            self.drawing_area.queue_draw()
            self.update_json()  # Update the JSON file
            self.push_undo()
        elif self.selected_pin:
            self.selected_pin.rotate(180)
            self.drawing_area.queue_draw()
            self.update_json()  # Update the JSON file
            self.push_undo()

    def on_rotate_270(self, widget):
        if self.selected_block:
            self.selected_block.rotate(270)
            self.drawing_area.queue_draw()
            self.update_json()  # Update the JSON file
            self.push_undo()
        elif self.selected_pin:
            self.selected_pin.rotate(270)
            self.drawing_area.queue_draw()
            self.update_json()  # Update the JSON file
            self.push_undo()

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
            self.update_json()
            self.push_undo()
        elif self.selected_pin:
            # Create a copy of the selected pin
            new_pin = Pin(
                self.selected_pin.x + self.grid_size,
                self.selected_pin.y + self.grid_size,
                self.selected_pin.width,
                self.selected_pin.height,
                self.selected_pin.text,
                self.selected_pin.pin_type,
                self.grid_size
            )
            new_pin.border_color = self.selected_pin.border_color
            new_pin.fill_color = self.selected_pin.fill_color
            new_pin.text_color = self.selected_pin.text_color
            new_pin.rotation = self.selected_pin.rotation
            self.pins.append(new_pin)
            self.drawing_area.queue_draw()
            self.update_json()
            self.push_undo()

    def on_delete_block(self, widget):
        if self.selected_block:
            self.push_undo()
            self.blocks.remove(self.selected_block)
            self.selected_block = None
            self.drawing_area.queue_draw()
            self.update_json()
            #self.push_undo()
        elif self.selected_pin:
            self.push_undo()
            self.pins.remove(self.selected_pin)
            self.selected_pin = None
            self.drawing_area.queue_draw()
            self.update_json()
            #self.push_undo()


    def on_connect_pin(self, widget):
        if self.selected_block:
           print("Connect pin")  # Placeholder for connect action
        elif self.selected_pin:
           print("Connect pin")  # Placeholder for connect action

    def on_disconnect_pin(self, widget):
        if self.selected_block:
           print("Disconnect pin")  # Placeholder for disconnect action
        elif self.selected_pin:
           print("Disconnect pin")  # Placeholder for connect action


    def blocks_to_json(self):
        blocks_dict = [block.to_dict() for block in self.blocks]
        pins_dict = [pin.to_dict() for pin in self.pins]
        return json.dumps(blocks_dict + pins_dict, indent=4)

    def update_json(self):
        with open("blocks.json", "w") as file:
            file.write(self.blocks_to_json())

    def push_undo(self):
        print("push undo")
        self.undo_stack.append(self.blocks_to_json())
        self.redo_stack = []
        self.update_undo_redo_buttons()  # Update the sensitivity of the buttons

    """
    def redo(self):
        if self.redo_stack:
           print("redo")
           self.undo_stack.append(self.blocks_to_json())
           self.blocks = [Block.from_dict(block_dict) for block_dict in json.loads(self.redo_stack.pop())]
           self.pins = [Pin.from_dict(pin_dict) for pin_dict in json.loads(self.redo_stack.pop())]
           self.drawing_area.queue_draw()
           self.update_json()
           self.update_undo_redo_buttons()  # Update the sensitivity of the buttons

    def undo(self):
        if self.undo_stack:
           print("undo")
           self.redo_stack.append(self.blocks_to_json())
           self.blocks = [Block.from_dict(block_dict) for block_dict in json.loads(self.undo_stack.pop())]
           self.pins = [Pin.from_dict(pin_dict) for pin_dict in json.loads(self.undo_stack.pop())]
           self.drawing_area.queue_draw()
           self.update_json()
           self.update_undo_redo_buttons()  # Update the sensitivity of the buttons
    """


    def undo(self):
            if self.undo_stack:
                print("undo")
                self.redo_stack.append(self.blocks_to_json())
                data = json.loads(self.undo_stack.pop())
                self.blocks = [Block.from_dict(block_dict) for block_dict in data if block_dict.get("block_type")]
                self.pins = [Pin.from_dict(pin_dict) for pin_dict in data if pin_dict.get("pin_type")]
                self.drawing_area.queue_draw()
                self.update_json()
                self.update_undo_redo_buttons()  # Update the sensitivity of the buttons

    def redo(self):
            if self.redo_stack:
                print("redo")
                self.undo_stack.append(self.blocks_to_json())
                data = json.loads(self.redo_stack.pop())
                self.blocks = [Block.from_dict(block_dict) for block_dict in data if block_dict.get("block_type")]
                self.pins = [Pin.from_dict(pin_dict) for pin_dict in data if pin_dict.get("pin_type")]
                self.drawing_area.queue_draw()
                self.update_json()
                self.update_undo_redo_buttons()  # Update the sensitivity of the buttons


    def on_undo(self, widget):
        self.undo()

    def on_redo(self, widget):
        self.redo()

    def update_undo_redo_buttons(self):
        self.undo_button.set_sensitive(len(self.undo_stack) > 0)
        self.redo_button.set_sensitive(len(self.redo_stack) > 0)


if __name__ == "__main__":
    win = BlocksWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

