#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from blocks import Block
from context_menu import ContextMenu
from context_menu import PinContextMenu
from context_menu import WireContextMenu
from drawing_area import DrawingArea
from datetime import datetime
from pins import Pin  # Import the Pin class
from wire import Wire
import json
import random

class BlocksWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Simple VHDL Code Generator (SVCG)")
        self.set_default_size(1000, 600)

        self.mouse_x = 0
        self.mouse_y = 0

        self.clipboard_block = None
        self.clipboard_pin = None

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(self.box)

        self.left_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.box.pack_start(self.left_pane, False, False, 0)

        # Add a label to display mouse coordinates
        self.mouse_label = Gtk.Label()
        self.mouse_label.set_markup(f"<span color='green'>Cursor: (0,0)</span>")
        self.left_pane.pack_start(self.mouse_label, False, False, 0)

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

        for label, block_type in buttons:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_button_clicked, block_type)
            self.gate_box.pack_start(button, False, False, 0)

        # Create an expander_ops for the operations menu
        self.expander_ops = Gtk.Expander(label="Edit Operations")
        self.left_pane.pack_start(self.expander_ops, False, False, 0)

        self.ops_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.expander_ops.add(self.ops_box)

        # Add undo/redo buttons
        self.undo_button = Gtk.Button(label="Undo [CTRL+z]")
        self.undo_button.connect("clicked", self.on_undo)
        self.ops_box.pack_start(self.undo_button, False, False, 0)

        self.redo_button = Gtk.Button(label="Redo [CTRL+r]")
        self.redo_button.connect("clicked", self.on_redo)
        self.ops_box.pack_start(self.redo_button, False, False, 0)

        #self.drawing_area = DrawingArea(self)
        #self.box.pack_start(self.drawing_area, True, True, 0)

        # Wrap the DrawingArea in a ScrolledWindow
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.drawing_area = DrawingArea(self)
        self.drawing_area.set_size_request(5000, 5000)  # Set a large size to trigger scroll bars
        self.scrolled_window.add(self.drawing_area)
        self.box.pack_start(self.scrolled_window, True, True, 0)

        self.blocks = []
        self.pins = []  # List to store pins
        self.grid_size = 20

        self.wires = []
        self.dragging_wire = False
        self.wire_start_point = None

        # Create context menu
        self.context_menu = ContextMenu(self)
        self.pin_context_menu = PinContextMenu(self)
        self.wire_context_menu = WireContextMenu(self)

        self.selected_block = None
        self.selected_pin = None  # Variable to store the selected pin
        self.selected_wire = None  # Variable to store the selected wire

        # Initialize undo/redo stacks
        self.undo_stack = []
        self.redo_stack = []

        self.update_undo_redo_buttons()  # Initialize the sensitivity of the buttons
        self.drawing_area.grab_focus()  # Ensure the DrawingArea has keyboard focus

        #self.connect("key-press-event", self.on_key_press)

    def on_button_clicked(self, widget, block_type):
        self.push_undo()
        # Ensure the initial position and size are multiples of the grid size
        initial_x = round(random.randint(40, 240) / self.grid_size) * self.grid_size
        initial_y = round(random.randint(40, 240) / self.grid_size) * self.grid_size
        initial_width = round(40 / self.grid_size) * self.grid_size  # Half of the current width
        initial_height = round(40 / self.grid_size) * self.grid_size
        timestamp = datetime.now().isoformat(' ', 'seconds')
        new_block = Block(initial_x, initial_y, initial_width, initial_height, f"{block_type} {timestamp}", block_type, self.grid_size)
        self.blocks.append(new_block)
        self.drawing_area.queue_draw()
        self.update_json()
        #self.push_undo()

    def on_pin_button_clicked(self, widget, pin_type):
        self.push_undo()
        # Ensure the initial position and size are multiples of the grid size
        initial_x = round(random.randint(40, 240) / self.grid_size) * self.grid_size
        initial_y = round(random.randint(40, 240) / self.grid_size) * self.grid_size
        initial_width = round(40 / self.grid_size) * self.grid_size  # Half of the current width
        initial_height = round(40 / self.grid_size) * self.grid_size
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
                # Adjust the height based on the number of pins
                #initial_height = round((40 * num_pins) / self.grid_size) * self.grid_size
                initial_height = round((40 * 1) / self.grid_size) * self.grid_size
                new_pin = Pin(initial_x, initial_y, initial_width, initial_height, f"{pin_type} {timestamp}", pin_type, self.grid_size, num_pins)
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

        # Draw wires
        for wire in self.wires:
            wire.draw(cr)

        # Draw temporary wire while dragging
        if self.dragging_wire:
            cr.set_source_rgb(1, 0, 0)  # Red color for wires
            cr.set_line_width(2)
            cr.move_to(self.wire_start_point[0], self.wire_start_point[1])
            cr.line_to(self.mouse_x, self.wire_start_point[1])
            cr.line_to(self.mouse_x, self.mouse_y)
            cr.stroke()

        # for CTRL+z or CTRL+r not loosing drawing area focus
        self.drawing_area.grab_focus()

    def get_column_label(self, index):
        label = ""
        while index >= 0:
            label = chr(index % 26 + ord('A')) + label
            index = index // 26 - 1
        return label

    def on_button_press(self, widget, event):
            if event.button == 1:  # Left click
                self.selected_block = None
                self.selected_pin = None
                self.selected_wire = None
                #######################
                # dragging wire only
                #######################
                for block in self.blocks:
                    if block.contains_pin(int(event.x), int(event.y)):
                       self.wire_start_point = block.contains_pin(int(event.x), int(event.y))
                       self.dragging_wire = True
                       break
                for pin in self.pins:
                    if pin.contains_pin(int(event.x), int(event.y)):
                       self.wire_start_point = pin.contains_pin(int(event.x), int(event.y))
                       self.dragging_wire = True
                       break
                #######################
                # not dragging wire?
                # then move the block
                #######################
                if not self.dragging_wire:
                        for block in self.blocks:
                            if block.contains_point(int(event.x), int(event.y)):
                                self.selected_block = block
                                block.start_drag(int(event.x), int(event.y))
                                break
                        for pin in self.pins:
                            if pin.contains_point(int(event.x), int(event.y)):
                                self.selected_pin = pin
                                pin.start_drag(int(event.x), int(event.y))
                                break
                        for wire in self.wires:
                            if wire.contains_point(int(event.x), int(event.y)):
                                self.selected_wire = wire
                                break
            elif event.button == 3:  # Right click
                for block in self.blocks:
                    if block.contains_point(int(event.x), int(event.y)):
                        self.selected_block = block
                        if block.contains_pin(int(event.x), int(event.y)):
                            self.pin_context_menu.popup(event)
                        else:
                            self.context_menu.popup(event)
                        break
                for pin in self.pins:
                    if pin.contains_point(int(event.x), int(event.y)):
                        self.selected_pin = pin
                        connection_point = pin.contains_pin(int(event.x), int(event.y))
                        if connection_point:
                            self.pin_context_menu.popup(event)
                        else:
                            self.context_menu.popup(event)
                        break
                for wire in self.wires:
                    if wire.contains_point(int(event.x), int(event.y)):
                       self.selected_wire = wire
                       #self.wire_context_menu.popup(event)
                       self.wire_context_menu.popup(None, None, None, None, event.button, event.time)
                       break
            self.drawing_area.grab_focus()  # Ensure the DrawingArea has keyboard focus:

    def on_key_press(self, widget, event):
        self.drawing_area.grab_focus()
        key = Gdk.keyval_name(event.keyval)
        if key == "z" and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.undo()
        elif key == "r" and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.redo()
        elif key == "c" and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.on_copy_block(widget)
        elif key == "x" and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.on_cut_block(widget)
        elif key == "v" and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.on_paste_block(widget)
        elif key == "d" and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.on_delete_block(widget)
        elif key == "p" and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.on_rotate_90(widget)
        #print(f"Key pressed: {key}")  # Debug print statement

    def on_button_release(self, widget, event):
        for block in self.blocks:
            block.end_drag()
            block.update_wire_connections()
        for pin in self.pins:
            pin.end_drag()
            pin.update_wire_connections()
    
        if self.dragging_wire:
            end_point = None
            start_block = None
            end_block = None
            start_pin = None
            end_pin = None
    
            # Find the end point
            for block in self.blocks:
                if block.contains_pin(int(event.x), int(event.y)):
                    end_point = block.contains_pin(int(event.x), int(event.y))
                    end_block = block
                    break
            for pin in self.pins:
                if pin.contains_pin(int(event.x), int(event.y)):
                    end_point = pin.contains_pin(int(event.x), int(event.y))
                    end_pin = pin
                    break
    
            if end_point and end_point != self.wire_start_point:
                duplicate_wire = any(
                    wire.start_point == self.wire_start_point and wire.end_point == end_point or
                    wire.start_point == end_point and wire.end_point == self.wire_start_point
                    for wire in self.wires
                )
                if not duplicate_wire:
                    timestamp = datetime.now().isoformat(' ', 'seconds')
                    new_wire = Wire(f"wire {timestamp}", self.wire_start_point, end_point, "wire", self.grid_size, self)
                    self.wires.append(new_wire)
    
                    # Find the start block or pin
                    for block in self.blocks:
                        if block.contains_pin(int(self.wire_start_point[0]), int(self.wire_start_point[1])):
                            start_block = block
                            break
                    for pin in self.pins:
                        if pin.contains_pin(int(self.wire_start_point[0]), int(self.wire_start_point[1])):
                            start_pin = pin
                            break
    
                    # Connect the wire to the blocks or pins
                    if start_block:
                        start_block.connect_wire(self.wire_start_point, new_wire)
                    if end_block:
                        end_block.connect_wire(end_point, new_wire)
                    if start_pin:
                        start_pin.connect_wire(self.wire_start_point, new_wire)
                    if end_pin:
                        end_pin.connect_wire(end_point, new_wire)
    
                    self.update_json()
                else:
                    print("Duplicate wire connection detected and ignored.")
            else:
                print("Invalid wire connection: both ends must be on valid connection points.")
    
            self.dragging_wire = False
    
        self.update_wires()
        self.drawing_area.queue_draw()
        self.update_json()
        self.push_undo()
        self.drawing_area.grab_focus()
   

    def on_motion_notify(self, widget, event):
        self.mouse_x, self.mouse_y = event.x, event.y
        width, height = self.drawing_area.get_allocated_width(), self.drawing_area.get_allocated_height()
        #print(f"motion notify: {self.mouse_x} {self.mouse_y}, {width}, {height}")
        for block in self.blocks:
            block.drag(event.x, event.y, width, height)
            #print(f"motion notify: {event.x} {event.y}, {width}, {height}")
        for pin in self.pins:
            pin.drag(event.x, event.y, width, height)
            #print(f"motion notify: {event.x} {event.y}, {width}, {height}")
        if self.dragging_wire:
            self.drawing_area.queue_draw()
        self.drawing_area.queue_draw()
        self.update_json()
        self.drawing_area.grab_focus()  # Ensure the DrawingArea has keyboard focus
        #self.push_undo()
        # Update the label with the current mouse coordinates
        self.mouse_label.set_markup(f"<span color='green'>Cursor: ({int(self.mouse_x)}, {int(self.mouse_y)})</span>")

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
        #print('copy block')
        if self.selected_block:
            self.clipboard_block = self.selected_block
            self.clipboard_pin = None  # Clear the pin clipboard
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
            self.clipboard_pin = self.selected_pin
            self.clipboard_block = None  # Clear the block clipboard
            # Create a copy of the selected pin
            new_pin = Pin(
                self.selected_pin.x + self.grid_size,
                self.selected_pin.y + self.grid_size,
                self.selected_pin.width,
                self.selected_pin.height,
                self.selected_pin.text,
                self.selected_pin.pin_type,
                self.grid_size,
                self.selected_pin.num_pins  # Include number of pins for buses
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

    def on_cut_block(self, widget):
        if self.selected_block:
            self.push_undo()
            self.clipboard_block = self.selected_block
            self.clipboard_pin = None  # Clear the pin clipboard
            self.blocks.remove(self.selected_block)
            self.selected_block = None
            self.drawing_area.queue_draw()
            self.update_json()
        elif self.selected_pin:
            self.push_undo()
            self.clipboard_pin = self.selected_pin
            self.clipboard_block = None  # Clear the block clipboard
            self.pins.remove(self.selected_pin)
            self.selected_pin = None
            self.drawing_area.queue_draw()
            self.update_json()

    def on_paste_block(self, widget):
        if self.clipboard_block:
            self.push_undo()
            new_block = Block(
                self.mouse_x,
                self.mouse_y,
                self.clipboard_block.width,
                self.clipboard_block.height,
                self.clipboard_block.text,
                self.clipboard_block.block_type,
                self.grid_size
            )
            new_block.border_color = self.clipboard_block.border_color
            new_block.fill_color = self.clipboard_block.fill_color
            new_block.text_color = self.clipboard_block.text_color
            new_block.rotation = self.clipboard_block.rotation
            self.blocks.append(new_block)
            self.drawing_area.queue_draw()
            self.update_json()
        elif self.clipboard_pin:
            self.push_undo()
            new_pin = Pin(
                self.mouse_x,
                self.mouse_y,
                self.clipboard_pin.width,
                self.clipboard_pin.height,
                self.clipboard_pin.text,
                self.clipboard_pin.pin_type,
                self.grid_size,
                self.clipboard_pin.num_pins  # Include number of pins for buses
            )
            new_pin.border_color = self.clipboard_pin.border_color
            new_pin.fill_color = self.clipboard_pin.fill_color
            new_pin.text_color = self.clipboard_pin.text_color
            new_pin.rotation = self.clipboard_pin.rotation
            self.pins.append(new_pin)
            self.drawing_area.queue_draw()
            self.update_json()
 
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

    def update_wires(self):
        for wire in self.wires:
            #print('recalculate path')
            wire.path = wire.calculate_path()
            if not wire.path:
                #print(f"Removing wire from {wire.start_point} to {wire.end_point} due to no path found")
                self.wires.remove(wire)
        self.drawing_area.queue_draw()

    def blocks_to_json(self):
        blocks_dict = [block.to_dict() for block in self.blocks]
        pins_dict = [pin.to_dict() for pin in self.pins]
        wires_dict = [wire.to_dict() for wire in self.wires]
        #print(blocks_dict)
        #print(pins_dict)
        #print(wires_dict)
        return json.dumps(blocks_dict + pins_dict + wires_dict, indent=4)

    def update_json(self):
        with open("blocks.json", "w") as file:
            file.write(self.blocks_to_json())

    def push_undo(self):
        #print("push undo")
        self.undo_stack.append(self.blocks_to_json())
        self.redo_stack = []
        self.update_undo_redo_buttons()  # Update the sensitivity of the buttons

    def undo(self):
        if self.undo_stack:
           #print("undo")
           self.redo_stack.append(self.blocks_to_json())
           data = json.loads(self.undo_stack.pop())
           self.blocks = [Block.from_dict(block_dict, self) for block_dict in data if block_dict.get("block_type")]
           self.pins = [Pin.from_dict(pin_dict, self) for pin_dict in data if pin_dict.get("pin_type")]
           self.wires = [Wire.from_dict(wire_dict, self) for wire_dict in data if wire_dict.get("start_point")]
           self.drawing_area.queue_draw()
           self.update_json()
           self.update_undo_redo_buttons()  # Update the sensitivity of the buttons

    def redo(self):
        if self.redo_stack:
           #print("redo")
           self.undo_stack.append(self.blocks_to_json())
           data = json.loads(self.redo_stack.pop())
           self.blocks = [Block.from_dict(block_dict, self) for block_dict in data if block_dict.get("block_type")]
           self.pins = [Pin.from_dict(pin_dict, self) for pin_dict in data if pin_dict.get("pin_type")]
           self.wires = [Wire.from_dict(wire_dict, self) for wire_dict in data if wire_dict.get("start_point")]
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

