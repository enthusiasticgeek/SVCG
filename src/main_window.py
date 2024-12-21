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

        # Create an expander_basic_ios for the basic_ios menu
        self.expander_basic_ios = Gtk.Expander(label="Clk/Vdd/Gnd")
        self.left_pane.pack_start(self.expander_basic_ios, False, False, 0)

        self.basic_ios_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.expander_basic_ios.add(self.basic_ios_box)

        self.connections = []
        # Add buttons for creating basic_ios and buses
        basic_io_buttons = [
            ("CLK", "CLK"),
            ("GND", "GND"),
            ("VDD 5V", "VDD_5V"),
            ("VDD 3.3V", "VDD_3V3"),
            ("VDD 1.8V", "VDD_1V8"),
            ("VDD 1.2V", "VDD_1V2")
        ]

        for label, basic_io_type in basic_io_buttons:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_pin_button_clicked, basic_io_type)
            self.basic_ios_box.pack_start(button, False, False, 0)

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
        self.expander_gates = Gtk.Expander(label="Digital Gates")
        self.left_pane.pack_start(self.expander_gates, False, False, 0)

        self.gate_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.expander_gates.add(self.gate_box)

        gates_buttons = [
            ("AND Gate", "AND"),
            ("OR Gate", "OR"),
            ("NOT Gate", "NOT"),
            ("NAND Gate", "NAND"),
            ("NOR Gate", "NOR"),
            ("XOR Gate", "XOR"),
            ("XNOR Gate", "XNOR")
        ]

        for label, block_type in gates_buttons:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_button_clicked, block_type)
            self.gate_box.pack_start(button, False, False, 0)

        # Create an expander for the flip-flops menu
        self.expander_flipflops = Gtk.Expander(label="Flip-Flops")
        self.left_pane.pack_start(self.expander_flipflops, False, False, 0)

        self.flipflop_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.expander_flipflops.add(self.flipflop_box)

        flipflop_buttons = [
            ("J-K Flip Flop", "JKFF"),
            ("S-R Flip Flop", "SRFF"),
            ("D Flip Flop", "DFF"),
            ("T Flip Flop", "TFF")
        ]

        for label, block_type in flipflop_buttons:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_button_clicked, block_type)
            self.flipflop_box.pack_start(button, False, False, 0)

        # Create an expander for the flip-flops menu
        self.expander_muxes = Gtk.Expander(label="Muxes")
        self.left_pane.pack_start(self.expander_muxes, False, False, 0)

        self.muxes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.expander_muxes.add(self.muxes_box)

        muxe_buttons = [
            ("2X1 MUX", "MUX_2X1"),
            ("4X1 MUX", "MUX_4X1"),
            ("8X1 MUX", "MUX_8X1")
        ]

        for label, block_type in muxe_buttons:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_button_clicked, block_type)
            self.muxes_box.pack_start(button, False, False, 0)

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
        self.drag_started = False
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

    def on_button_clicked(self, widget, block_type):
        try:
            self.push_undo()
            # Ensure the initial position and size are multiples of the grid size
            initial_x = round(random.randint(40, 400) // self.grid_size) * self.grid_size
            initial_y = round(random.randint(40, 400) // self.grid_size) * self.grid_size
            initial_width = round(40 // self.grid_size) * self.grid_size  # Half of the current width
            initial_height = round(40 // self.grid_size) * self.grid_size
            timestamp = datetime.now().isoformat(' ', 'seconds')
            new_block = Block(initial_x, initial_y, initial_width, initial_height, f"{block_type} {timestamp}", block_type, self.grid_size, self)
            self.blocks.append(new_block)
            self.drawing_area.queue_draw()
            self.update_json()
        except Exception as e:
            print(f"Error in on_button_clicked: {e}")

    def on_pin_button_clicked(self, widget, pin_type):
        try:
            self.push_undo()
            # Ensure the initial position and size are multiples of the grid size
            initial_x = round(random.randint(40, 400) // self.grid_size) * self.grid_size
            initial_y = round(random.randint(40, 400) // self.grid_size) * self.grid_size
            initial_width = round(40 // self.grid_size) * self.grid_size  # Half of the current width
            initial_height = round(40 // self.grid_size) * self.grid_size
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
                    initial_height = round((40 * 1) // self.grid_size) * self.grid_size
                    new_pin = Pin(initial_x, initial_y, initial_width, initial_height, f"{pin_type} {timestamp}", pin_type, self.grid_size, num_pins, self)
                    self.pins.append(new_pin)
                    self.drawing_area.queue_draw()
                    self.update_json()
                dialog.destroy()
            else:
                new_pin = Pin(initial_x, initial_y, initial_width, initial_height, f"{pin_type} {timestamp}", pin_type, self.grid_size, 1, self)
                self.pins.append(new_pin)
                self.drawing_area.queue_draw()
                self.update_json()
        except ValueError as e:
            print(f"ValueError in on_pin_button_clicked: {e}")
        except Exception as e:
            print(f"Error in on_pin_button_clicked: {e}")

    def on_draw(self, widget, cr):
        try:
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
        except Exception as e:
            print(f"Error in on_draw: {e}")

    def get_column_label(self, index):
        label = ""
        while index >= 0:
            label = chr(index % 26 + ord('A')) + label
            index = index // 26 - 1
        return label

    def on_key_press(self, widget, event):
        try:
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
                #print("rotate 90 deg CW")
                self.on_rotate_90(widget)
            return True
        except Exception as e:
            print(f"Error in on_key_press: {e}")

    def on_button_press(self, widget, event):
       if not self.drag_started:
        if event.x < 0 or event.y < 0:
            return False
        if event.button == 1 and event.button == 2 or event.button == 1 and event.button == 3 or event.button == 2 and event.button == 3:
            #print("Multiple buttons pressed")
            return False
        try:
            self.push_undo()  # Push the current state to the undo stack
            if event.button == 1:  # Left click
                #print("Left button pressed")
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
                            block.set_selected(True)
                            block.start_drag(int(event.x), int(event.y))
                            break
                    for pin in self.pins:
                        if pin.contains_point(int(event.x), int(event.y)):
                            self.selected_pin = pin
                            pin.set_selected(True)
                            pin.start_drag(int(event.x), int(event.y))
                            break
                    for wire in self.wires:
                        if wire.contains_point(int(event.x), int(event.y)):
                            self.selected_wire = wire
                            wire.set_selected(True)
                            break
            elif event.button == 2:  # middle click
                #print("Middle button pressed")
                pass
            elif event.button == 3:  # Right click
                #print("Right button pressed")
                for block in self.blocks:
                    if block.contains_point(int(event.x), int(event.y)):
                        self.selected_block = block
                        block.set_selected(True)
                        if block.contains_pin(int(event.x), int(event.y)):
                            self.pin_context_menu.popup(event)
                        else:
                            self.context_menu.popup(event)
                        break
                for pin in self.pins:
                    if pin.contains_point(int(event.x), int(event.y)):
                        self.selected_pin = pin
                        pin.set_selected(True)
                        connection_point = pin.contains_pin(int(event.x), int(event.y))
                        if connection_point:
                            self.pin_context_menu.popup(event)
                        else:
                            self.context_menu.popup(event)
                        break
                for wire in self.wires:
                    if wire.contains_point(int(event.x), int(event.y)):
                        self.selected_wire = wire
                        wire.set_selected(True)
                        self.wire_context_menu.popup(None, None, None, None, event.button, event.time)
                        break
    
            self.drawing_area.queue_draw()
            self.update_json()
            self.push_undo()
            self.drawing_area.grab_focus()  # Ensure the DrawingArea has keyboard focus
            self.drag_started = True
        except Exception as e:
            print(f"Error in on_button_press: {e}")
    
    def on_button_release(self, widget, event):
        #if not self.drag_started:
        #   return True
        if event.x < 0 or event.y < 0:
            return False
        if event.button == 1 and event.button == 2 or event.button == 1 and event.button == 3 or event.button == 2 and event.button == 3:
            #print("Multiple buttons released")
            return False
    
        if event.button == 1:  # left click
            #print("Left button released")
            pass
        elif event.button == 2:  # middle click
            #print("Middle button released")
            pass
        elif event.button == 3:  # Right click
            #print("Right button released")
            pass
    
        try:
            self.push_undo()
            for block in self.blocks:
                block.end_drag()
                block.set_selected(False)
                block.update_points()
            for pin in self.pins:
                pin.end_drag()
                pin.set_selected(False)
                pin.update_points()
    
            # dragging pins/block complete
            if not self.dragging_wire:
                #print("dragging block/pins")
                for block in self.blocks:
                    #print("block....")
                    if block.contains_point(int(event.x), int(event.y)):
                        #print(f"block {block.block_type.lower()} drag complete")
                        block_dict = block.to_dict()
                        for widx, wire in enumerate(self.wires):
                            for idx, input_wires in enumerate(block_dict['input_wires']):
                                if input_wires is not None and wire.id in input_wires:
                                    #print(f"{wire.start_point} {wire.end_point} and {block.prev_input_connections()}")
                                    if self.convert_to_tuple(wire.start_point) in block.prev_input_connections():
                                        wire.update_start_point(block_dict['input_points'][idx])
                                    elif self.convert_to_tuple(wire.end_point) in block.prev_input_connections():
                                        wire.update_end_point(block_dict['input_points'][idx])
                            for idx, output_wires in enumerate(block_dict['output_wires']):
                                if output_wires is not None and wire.id in output_wires:
                                    #print(f"{wire.start_point} {wire.end_point} and {block.prev_input_connections()}")
                                    if self.convert_to_tuple(wire.start_point) in block.prev_output_connections():
                                        wire.update_start_point(block_dict['output_points'][idx])
                                    elif self.convert_to_tuple(wire.end_point) in block.prev_output_connections():
                                        wire.update_end_point(block_dict['output_points'][idx])
                        block.update_points()
                        break
                for pin in self.pins:
                    #print("pin....")
                    if pin.contains_point(int(event.x), int(event.y)):
                        #print(f"pin {pin.pin_type.lower()} drag complete")
                        pin_dict = pin.to_dict()
                        for widx, wire in enumerate(self.wires):
                            for idx, wires in enumerate(pin_dict['wires']):
                                if wires is not None and wire.id in wires:
                                    #print(f"{wire.start_point} {wire.end_point} and {pin.prev_connections()}")
                                    if self.convert_to_tuple(wire.start_point) in pin.prev_connections():
                                        wire.update_start_point(pin_dict['connection_points'][idx])
                                    elif self.convert_to_tuple(wire.end_point) in pin.prev_connections():
                                        wire.update_end_point(pin_dict['connection_points'][idx])
                        pin.update_points()
                        break
    
                self.update_json()
    
            # dragging wire complete
            elif self.dragging_wire:
                #print("wire dragged")
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
                    # Check for duplicate wire
                    duplicate_wire = any(
                        (wire.start_point == self.wire_start_point and wire.end_point == end_point) or
                        (wire.start_point == end_point and wire.end_point == self.wire_start_point)
                        for wire in self.wires
                    )
                    if not duplicate_wire:
                        timestamp = datetime.now().isoformat(' ', 'seconds')
                        new_wire = Wire(f"wire {timestamp}", self.wire_start_point, end_point, "wire", self.grid_size, self)
                        print(f"{new_wire.id} new wire created with name {new_wire.text}")
    
                        # Find the start block or pin
                        for block in self.blocks:
                            if block.contains_pin(int(self.wire_start_point[0]), int(self.wire_start_point[1])):
                                start_block = block
                                break
                        for pin in self.pins:
                            if pin.contains_pin(int(self.wire_start_point[0]), int(self.wire_start_point[1])):
                                start_pin = pin
                                break
    
                        self.wires.append(new_wire)
                        self.update_json()
    
                        # Update the wires list in the connected blocks and pins
                        if start_block:
                            index = self.find_closest_point(start_block.input_points + start_block.output_points, self.wire_start_point)
                            if index is not None:
                                if self.wire_start_point in start_block.input_points:
                                    if start_block.input_wires[start_block.input_points.index(self.wire_start_point)] is None:
                                        start_block.input_wires[start_block.input_points.index(self.wire_start_point)] = []
                                    start_block.input_wires[start_block.input_points.index(self.wire_start_point)].append(new_wire.id)
                                else:
                                    if start_block.output_wires[start_block.output_points.index(self.wire_start_point)] is None:
                                        start_block.output_wires[start_block.output_points.index(self.wire_start_point)] = []
                                    start_block.output_wires[start_block.output_points.index(self.wire_start_point)].append(new_wire.id)
                        if end_block:
                            index = self.find_closest_point(end_block.input_points + end_block.output_points, end_point)
                            if index is not None:
                                if end_point in end_block.input_points:
                                    if end_block.input_wires[end_block.input_points.index(end_point)] is None:
                                        end_block.input_wires[end_block.input_points.index(end_point)] = []
                                    end_block.input_wires[end_block.input_points.index(end_point)].append(new_wire.id)
                                else:
                                    if end_block.output_wires[end_block.output_points.index(end_point)] is None:
                                        end_block.output_wires[end_block.output_points.index(end_point)] = []
                                    end_block.output_wires[end_block.output_points.index(end_point)].append(new_wire.id)
                        if start_pin:
                            index = self.find_closest_point(start_pin.connection_points, self.wire_start_point)
                            if index is not None:
                                if start_pin.wires[index] is None:
                                    start_pin.wires[index] = []
                                start_pin.wires[index].append(new_wire.id)
                        if end_pin:
                            index = self.find_closest_point(end_pin.connection_points, end_point)
                            if index is not None:
                                if end_pin.wires[index] is None:
                                    end_pin.wires[index] = []
                                end_pin.wires[index].append(new_wire.id)
                        self.dragging_wire = False
    
                    else:
                        print("Duplicate wire connection detected and ignored.")
                else:
                    print("Invalid wire connection: both ends must be on valid connection points.")
                    self.dragging_wire = False
    
            self.drawing_area.queue_draw()
            self.update_json()
            self.push_undo()
            self.drawing_area.grab_focus()
            self.drag_started = False
    
        except Exception as e:
            print(f"Error in on_button_release: {e}")

    def on_motion_notify(self, widget, event):
        #print("MOUSE BUTTON MOTION")
        try:
            self.mouse_x, self.mouse_y = max(0,int(event.x)), max(0,int(event.y))
            width, height = self.drawing_area.get_allocated_width(), self.drawing_area.get_allocated_height()
            for block in self.blocks:
                block.drag(self.mouse_x, self.mouse_y, width, height)
            for pin in self.pins:
                pin.drag(self.mouse_x, self.mouse_y, width, height)
            if self.dragging_wire:
                self.drawing_area.queue_draw()
            self.drawing_area.queue_draw()
            self.update_json()
            self.drawing_area.grab_focus()  # Ensure the DrawingArea has keyboard focus
            # Update the label with the current mouse coordinates
            self.mouse_label.set_markup(f"<span color='green'>Cursor: ({int(self.mouse_x)}, {int(self.mouse_y)})</span>")
        except Exception as e:
            print(f"Error in on_motion_notify: {e}")

    def find_closest_point(self, points, target, tolerance=10):
        for i, point in enumerate(points):
            if abs(point[0] - target[0]) <= tolerance and abs(point[1] - target[1]) <= tolerance:
                return i
        return None

    def on_change_border_color(self, widget):
        try:
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
        except Exception as e:
            print(f"Error in on_change_border_color: {e}")

    def on_change_fill_color(self, widget):
        try:
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
        except Exception as e:
            print(f"Error in on_change_fill_color: {e}")

    def on_change_text(self, widget):
        try:
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
        except Exception as e:
            print(f"Error in on_change_text: {e}")

    def on_change_text_color(self, widget):
        try:
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
        except Exception as e:
            print(f"Error in on_change_text_color: {e}")

    def on_rotate_90(self, widget):
        try:
            if self.selected_block and self.block_has_no_wires_connected(self.selected_block):
                self.selected_block.rotate(90)
                self.update_points()
                self.drawing_area.queue_draw()
                self.update_json()  # Update the JSON file
                self.push_undo()
            elif self.selected_pin and self.pin_has_no_wires_connected(self.selected_pin):
                self.selected_pin.rotate(90)
                self.update_points()
                self.drawing_area.queue_draw()
                self.update_json()  # Update the JSON file
                self.push_undo()
            elif not self.block_has_no_wires_connected(self.selected_block) or not self.pin_has_no_wires_connected(self.selected_pin):
                self.show_error_message("Cannot rotate block/pin", "The block/pin has wires connected. Disconnect wires and try again!")
        except Exception as e:
            print(f"Error in on_rotate_90: {e}")

    def on_rotate_180(self, widget):
        try:
            if self.selected_block and self.block_has_no_wires_connected(self.selected_block):
                self.selected_block.rotate(180)
                self.update_points()
                self.drawing_area.queue_draw()
                self.update_json()  # Update the JSON file
                self.push_undo()
            elif self.selected_pin and self.pin_has_no_wires_connected(self.selected_pin):
                self.selected_pin.rotate(180)
                self.update_points()
                self.drawing_area.queue_draw()
                self.update_json()  # Update the JSON file
                self.push_undo()
            elif not self.block_has_no_wires_connected(self.selected_block) or not self.pin_has_no_wires_connected(self.selected_pin):
                self.show_error_message("Cannot rotate block/pin", "The block/pin has wires connected. Disconnect wires and try again!")
        except Exception as e:
            print(f"Error in on_rotate_180: {e}")

    def on_rotate_270(self, widget):
        try:
            if self.selected_block and self.block_has_no_wires_connected(self.selected_block):
                self.selected_block.rotate(270)
                self.update_points()
                self.drawing_area.queue_draw()
                self.update_json()  # Update the JSON file
                self.push_undo()
            elif self.selected_pin and self.pin_has_no_wires_connected(self.selected_pin):
                self.selected_pin.rotate(270)
                self.update_points()
                self.drawing_area.queue_draw()
                self.update_json()  # Update the JSON file
                self.push_undo()
            elif not self.block_has_no_wires_connected(self.selected_block) or not self.pin_has_no_wires_connected(self.selected_pin):
                self.show_error_message("Cannot rotate block/pin", "The block/pin has wires connected. Disconnect wires and try again!")
        except Exception as e:
            print(f"Error in on_rotate_270: {e}")

    def on_copy_block(self, widget):
        try:
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
                    self.grid_size,
                    self
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
                    self.selected_pin.num_pins,  # Include number of pins for buses
                    self
                )
                new_pin.border_color = self.selected_pin.border_color
                new_pin.fill_color = self.selected_pin.fill_color
                new_pin.text_color = self.selected_pin.text_color
                new_pin.rotation = self.selected_pin.rotation
                self.pins.append(new_pin)
                self.drawing_area.queue_draw()
                self.update_json()
                self.push_undo()
        except Exception as e:
            print(f"Error in on_copy_block: {e}")


    def delete_block_wire_connections(self):
        try:
            self.selected_block.print_wires()
            wires_to_remove = []

            for wire in self.wires:
                print(f"{wire.id}")
                for idx, i_wire in enumerate(self.selected_block.get_input_wires()):
                    for widx, w_wire in enumerate(i_wire):
                        if isinstance(w_wire, str) and wire.id in w_wire:
                            print(f"deleting {w_wire}")
                            wires_to_remove.append(wire)
                for idx, o_wire in enumerate(self.selected_block.get_output_wires()):
                    for widx, w_wire in enumerate(o_wire):
                        if isinstance(w_wire, str) and wire.id in w_wire:
                            print(f"deleting {w_wire}")
                            wires_to_remove.append(wire)

            # Remove wires outside the loop
            for wire in wires_to_remove:
                self.wires.remove(wire)

            self.selected_block.clear_wires()
            self.selected_block.print_wires()

            # Update the JSON file
            self.update_json()
            self.push_undo()
            self.drawing_area.queue_draw()

        except Exception as e:
            print(f"Error in delete_block_wire_connections: {e}")


    def delete_pin_wire_connections(self):
        try:
            self.selected_pin.print_wires()
            wires_to_remove = []
    
            for wire in self.wires:
                print(f"{wire.id}")
                for idx, i_wire in enumerate(self.selected_pin.get_wires()):
                    print(f"GET WIRE {i_wire}")
                    for widx, w_wire in enumerate(i_wire):
                        if isinstance(w_wire, str) and wire.id in w_wire:
                            print(f"deleting {w_wire}")
                            wires_to_remove.append(wire)
    
            # Remove wires outside the loop
            for wire in wires_to_remove:
                self.wires.remove(wire)
    
            self.selected_pin.clear_wires()
            self.selected_pin.print_wires()
    
            # Update the JSON file
            self.update_json()
            self.push_undo()
            self.drawing_area.queue_draw()
        except Exception as e:
            print(f"An error occurred: {e}")
    

    def on_delete_block(self, widget):
        try:
            if self.selected_block:
                self.push_undo()
                self.delete_block_wire_connections()
                self.blocks.remove(self.selected_block)
                self.selected_block = None
                self.drawing_area.queue_draw()
                self.update_json()
            elif self.selected_pin:
                self.push_undo()
                self.delete_pin_wire_connections()
                self.pins.remove(self.selected_pin)
                self.selected_pin = None
                self.drawing_area.queue_draw()
                self.update_json()
        except Exception as e:
            print(f"Error in on_delete_block: {e}")

    def on_cut_block(self, widget):
        try:
            if self.selected_block:
                self.push_undo()
                self.delete_block_wire_connections()
                self.clipboard_block = self.selected_block
                self.clipboard_pin = None  # Clear the pin clipboard
                self.blocks.remove(self.selected_block)
                self.selected_block = None
                self.drawing_area.queue_draw()
                self.update_json()
            elif self.selected_pin:
                self.push_undo()
                self.delete_pin_wire_connections()
                self.clipboard_pin = self.selected_pin
                self.clipboard_block = None  # Clear the block clipboard
                self.pins.remove(self.selected_pin)
                self.selected_pin = None
                self.drawing_area.queue_draw()
                self.update_json()
        except Exception as e:
            print(f"Error in on_cut_block: {e}")

    def on_paste_block(self, widget):
        try:
            if self.clipboard_block:
                self.push_undo()
                new_block = Block(
                    self.mouse_x,
                    self.mouse_y,
                    self.clipboard_block.width,
                    self.clipboard_block.height,
                    self.clipboard_block.text,
                    self.clipboard_block.block_type,
                    self.grid_size,
                    self
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
                    self.clipboard_pin.num_pins,  # Include number of pins for buses
                    self
                )
                new_pin.border_color = self.clipboard_pin.border_color
                new_pin.fill_color = self.clipboard_pin.fill_color
                new_pin.text_color = self.clipboard_pin.text_color
                new_pin.rotation = self.clipboard_pin.rotation
                self.pins.append(new_pin)
                self.drawing_area.queue_draw()
                self.update_json()
        except Exception as e:
            print(f"Error in on_paste_block: {e}")

    def on_connect_pin(self, widget):
        try:
            if self.selected_block:
               print("Connect pin")  # Placeholder for connect action
            elif self.selected_pin:
               print("Connect pin")  # Placeholder for connect action
        except Exception as e:
            print(f"Error in on_connect_pin: {e}")

    def on_disconnect_pin(self, widget):
        try:
            if self.selected_block:
               print("Disconnect pin")  # Placeholder for disconnect action
            elif self.selected_pin:
               print("Disconnect pin")  # Placeholder for connect action
        except Exception as e:
            print(f"Error in on_disconnect_pin: {e}")

    def update_wires(self):
        try:
            for wire in self.wires:
                wire.path = wire.calculate_path()
                if not wire.path:
                    self.delete_wire(wire)
            self.drawing_area.queue_draw()
        except Exception as e:
            print(f"Error in update_wires: {e}")

    def delete_wire(self, wire):
        try:
            # Remove the wire from the wires list
            self.wires.remove(wire)

            for block in self.blocks:
                block_dict = block.to_dict()
                if wire.start_point in block.input_connections():
                   print("Found wire start point in input connections!")
                   self.reset_wire_by_index(wire, block_dict['input_wires'])
                if wire.start_point in block.output_connections():
                   print("Found wire start point in output connections!")
                   self.reset_wire_by_index(wire, block_dict['output_wires'])
                if wire.end_point in block.input_connections():
                   print("Found wire end point in input connections!")
                   self.reset_wire_by_index(wire, block_dict['input_wires'])
                if wire.end_point in block.output_connections():
                   print("Found wire end point in output connections!")
                   self.reset_wire_by_index(wire, block_dict['output_wires'])

            for pin in self.pins:
                pin_dict = pin.to_dict()
                if wire.start_point in pin.connections():
                   print("Found wire start point in connections!")
                   self.reset_wire_by_index(wire, pin_dict['wires'])
                if wire.end_point in pin.connections():
                   print("Found wire end point in connections!")
                   self.reset_wire_by_index(wire, pin_dict['wires'])

            # Update the JSON file
            self.update_json()
            self.push_undo()
            self.drawing_area.queue_draw()
        except Exception as e:
            print(f"Error in delete_wire: {e}")

    def reset_wire_by_index(self, wire, wires):
        try:
            for idx, w in enumerate(wires):
                if w is not None and wire.id in w:
                   print(f"Found {wire.id} at index {idx}")
                   wires[idx] = []
        except Exception as e:
            print(f"Error in reset_wire_by_index: {e}")

    def elements_to_json(self):
        try:
            blocks_dict = [block.to_dict() for block in self.blocks]
            pins_dict = [pin.to_dict() for pin in self.pins]
            wires_dict = [wire.to_dict() for wire in self.wires]
            return json.dumps(blocks_dict + pins_dict + wires_dict, indent=4)
        except Exception as e:
            print(f"Error in elements_to_json: {e}")

    def update_json(self):
        try:
            with open("blocks.json", "w") as file:
                file.write(self.elements_to_json())
        except IOError as e:
            print(f"IOError in update_json: {e}")
        except Exception as e:
            print(f"Error in update_json: {e}")

    def push_undo(self):
        try:
            self.undo_stack.append(self.elements_to_json())
            self.redo_stack = []
            self.update_undo_redo_buttons()  # Update the sensitivity of the buttons
        except Exception as e:
            print(f"Error in push_undo: {e}")

    def undo(self):
        try:
            if self.undo_stack:
                self.redo_stack.append(self.elements_to_json())
                data = json.loads(self.undo_stack.pop())
                self.blocks = [Block.from_dict(block_dict, self) for block_dict in data if block_dict.get("block_type")]
                self.pins = [Pin.from_dict(pin_dict, self) for pin_dict in data if pin_dict.get("pin_type")]
                self.wires = [Wire.from_dict(wire_dict, self) for wire_dict in data if wire_dict.get("start_point") or wire_dict.get("end_point")]
                self.drawing_area.queue_draw()
                self.update_json()
                self.update_undo_redo_buttons()
        except Exception as e:
            print(f"Error in undo: {e}")

    def redo(self):
        try:
            if self.redo_stack:
                self.undo_stack.append(self.elements_to_json())
                data = json.loads(self.redo_stack.pop())
                self.blocks = [Block.from_dict(block_dict, self) for block_dict in data if block_dict.get("block_type")]
                self.pins = [Pin.from_dict(pin_dict, self) for pin_dict in data if pin_dict.get("pin_type")]
                self.wires = [Wire.from_dict(wire_dict, self) for wire_dict in data if wire_dict.get("start_point") or wire_dict.get("end_point")]
                self.drawing_area.queue_draw()
                self.update_json()
                self.update_undo_redo_buttons()
        except Exception as e:
            print(f"Error in redo: {e}")

    def on_undo(self, widget):
        try:
            self.undo()
        except Exception as e:
            print(f"Error in on_undo: {e}")

    def on_redo(self, widget):
        try:
            self.redo()
        except Exception as e:
            print(f"Error in on_redo: {e}")

    def update_undo_redo_buttons(self):
        try:
            self.undo_button.set_sensitive(len(self.undo_stack) > 0)
            self.redo_button.set_sensitive(len(self.redo_stack) > 0)
        except Exception as e:
            print(f"Error in update_undo_redo_buttons: {e}")

    def update_points(self):
        for block in self.blocks:
            #print("block....")
            #if block.contains_point(int(event.x), int(event.y)):
                #print(f"block {block.block_type.lower()} drag complete")
                block_dict = block.to_dict()
                for widx, wire in enumerate(self.wires):
                    for idx, input_wires in enumerate(block_dict['input_wires']):
                        if input_wires is not None and wire.id in input_wires:
                            #print(f"{wire.start_point} {wire.end_point} and {block.prev_input_connections()}")
                            if self.convert_to_tuple(wire.start_point) in block.prev_input_connections():
                                wire.update_start_point(block_dict['input_points'][idx])
                            elif self.convert_to_tuple(wire.end_point) in block.prev_input_connections():
                                wire.update_end_point(block_dict['input_points'][idx])
                    for idx, output_wires in enumerate(block_dict['output_wires']):
                        if output_wires is not None and wire.id in output_wires:
                            #print(f"{wire.start_point} {wire.end_point} and {block.prev_input_connections()}")
                            if self.convert_to_tuple(wire.start_point) in block.prev_output_connections():
                                wire.update_start_point(block_dict['output_points'][idx])
                            elif self.convert_to_tuple(wire.end_point) in block.prev_output_connections():
                                wire.update_end_point(block_dict['output_points'][idx])
                block.update_points()
                break
        for pin in self.pins:
            #print("pin....")
            #if pin.contains_point(int(event.x), int(event.y)):
                #print(f"pin {pin.pin_type.lower()} drag complete")
                pin_dict = pin.to_dict()
                for widx, wire in enumerate(self.wires):
                    for idx, wires in enumerate(pin_dict['wires']):
                        if wires is not None and wire.id in wires:
                            #print(f"{wire.start_point} {wire.end_point} and {pin.prev_connections()}")
                            if self.convert_to_tuple(wire.start_point) in pin.prev_connections():
                                wire.update_start_point(pin_dict['connection_points'][idx])
                            elif self.convert_to_tuple(wire.end_point) in pin.prev_connections():
                                wire.update_end_point(pin_dict['connection_points'][idx])
                pin.update_points()
                break

    def pin_has_no_wires_connected(self, pin):
        # Check if all input_wires lists are empty
        if all(not wires for wires in pin.wires):
            return True
        return False


    def block_has_no_wires_connected(self, block):
        # Check if all input_wires lists are empty
        if all(not wires for wires in block.input_wires):
            # Check if all output_wires lists are empty
            if all(not wires for wires in block.output_wires):
                return True
        return False

    def print_wires(self):
        try:
            print("[main_window] Wires:")
            for wire in self.wires:
                print(f"Wire ID: {wire.id}")
                print(f"Wire Text: {wire.text}")
                print(f"Start Point: {wire.start_point}")
                print(f"End Point: {wire.end_point}")
                print(f"Grid Size: {wire.grid_size}")
                print(f"Path: {wire.path}")
                print(f"Wire Type: {wire.wire_type}")
                print("---------------------------")
        except Exception as e:
            print(f"Error in print_wires: {e}")

    def convert_to_tuple(self, input_data):
        if isinstance(input_data, list):
            return tuple(input_data)
        elif isinstance(input_data, tuple):
            return input_data
        else:
            raise ValueError("Input must be a list or a tuple")


    def show_error_message(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
    
if __name__ == "__main__":
    win = BlocksWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

