#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from blocks import Block
from context_menu import ContextMenu
from context_menu import PinContextMenu
from context_menu import WireContextMenu
from drawing_area import DrawingArea
from menu import MenuBar
from datetime import datetime
from pins import Pin
from wire import Wire
from project_manager import ProjectManagerMixin
from event_handler import EventHandlerMixin
from vhdl_viewer import VhdlViewerMixin
from component_library import ComponentLibraryMixin
import random
import os


class BlocksWindow(ProjectManagerMixin, EventHandlerMixin, VhdlViewerMixin, ComponentLibraryMixin, Gtk.Window):
    def __init__(self):
        super().__init__(title="Simple VHDL Code Generator (SVCG)")
        self.set_default_size(1000, 600)

        self.current_file_path = None

        self.mouse_x = 0
        self.mouse_y = 0

        self.clipboard_block = None
        self.clipboard_pin = None

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.vbox)

        self.menu_bar = MenuBar(self)
        menubar = self.menu_bar.menubar
        self.vbox.pack_start(menubar, False, False, 0)

        expander_tb = Gtk.Expander(label="ToolBar")
        self.vbox.pack_start(expander_tb, False, False, 0)
        toolbar = self.menu_bar.toolbar
        expander_tb.add(toolbar)

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.vbox.pack_start(self.box, True, True, 0)

        self.left_scrolled_window = Gtk.ScrolledWindow()
        self.left_scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.box.pack_start(self.left_scrolled_window, False, False, 0)

        self.left_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.left_scrolled_window.add(self.left_pane)

        self.mouse_label = Gtk.Label()
        self.mouse_label.set_markup(f"<span color='green'>Cursor: (0,0)</span>")
        self.left_pane.pack_start(self.mouse_label, False, False, 0)

        self.expander_basic_ios = Gtk.Expander(label="Clk/Vdd/Gnd")
        self.left_pane.pack_start(self.expander_basic_ios, False, False, 0)

        self.basic_ios_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.expander_basic_ios.add(self.basic_ios_box)

        self.connections = []
        basic_io_buttons = [
            ("CLK", "CLK"),
            ("GND", "GND"),
            ("VDD 5V", "VDD_5V"),
            ("VDD 3.3V", "VDD_3V3"),
            ("VDD 1.8V", "VDD_1V8"),
            ("VDD 1.2V", "VDD_1V2"),
        ]
        for label, basic_io_type in basic_io_buttons:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_pin_button_clicked, basic_io_type)
            self.basic_ios_box.pack_start(button, False, False, 0)

        self.expander_pins = Gtk.Expander(label="IO Pins/Buses")
        self.left_pane.pack_start(self.expander_pins, False, False, 0)

        self.pins_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.expander_pins.add(self.pins_box)

        pin_buttons = [
            ("Input Pin", "input_pin"),
            ("Output Pin", "output_pin"),
            ("Input/Output Pin", "input_output_pin"),
            ("Input Bus", "input_bus"),
            ("Output Bus", "output_bus"),
            ("Input/Output Bus", "input_output_bus"),
        ]
        for label, pin_type in pin_buttons:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_pin_button_clicked, pin_type)
            button.set_tooltip_text("Right click top left area of the generated pin for more options!")
            self.pins_box.pack_start(button, False, False, 0)

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
            ("XNOR Gate", "XNOR"),
        ]
        for label, block_type in gates_buttons:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_button_clicked, block_type)
            button.set_tooltip_text("Right click top left area of the generated block for more options!")
            self.gate_box.pack_start(button, False, False, 0)

        self.expander_flipflops = Gtk.Expander(label="Flip-Flops")
        self.left_pane.pack_start(self.expander_flipflops, False, False, 0)

        self.flipflop_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.expander_flipflops.add(self.flipflop_box)

        flipflop_buttons = [
            ("J-K Flip Flop", "JKFF"),
            ("S-R Flip Flop", "SRFF"),
            ("D Flip Flop Pipeline", "DFF_PIPELINE"),
            ("D Flip Flop", "DFF"),
            ("T Flip Flop", "TFF"),
        ]
        for label, block_type in flipflop_buttons:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_button_clicked, block_type)
            button.set_tooltip_text("Right click top left area of the generated block for more options!")
            self.flipflop_box.pack_start(button, False, False, 0)

        self.expander_muxes = Gtk.Expander(label="Muxes/Buffers")
        self.left_pane.pack_start(self.expander_muxes, False, False, 0)

        self.muxes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.expander_muxes.add(self.muxes_box)

        muxe_buttons = [
            ("2X1 MUX", "MUX_2X1"),
            ("4X1 MUX", "MUX_4X1"),
            ("8X1 MUX", "MUX_8X1"),
            ("Tristate Buf 2", "TRISTATEBUF_2"),
            ("Tristate Buf 4", "TRISTATEBUF_4"),
            ("Tristate Buf 8", "TRISTATEBUF_8"),
        ]
        for label, block_type in muxe_buttons:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_button_clicked, block_type)
            button.set_tooltip_text("Right click top left area of the generated block for more options!")
            self.muxes_box.pack_start(button, False, False, 0)

        self.expander_arithmetic = Gtk.Expander(label="Arithmetic")
        self.left_pane.pack_start(self.expander_arithmetic, False, False, 0)

        self.arithmetic_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.expander_arithmetic.add(self.arithmetic_box)

        arithmetic_buttons = [
            ("Full Adder", "FA"),
            ("Half Adder", "HA"),
            ("Full Adder Gray Cell", "FA_GC"),
            ("Full Adder White Cell", "FA_WC"),
        ]
        for label, block_type in arithmetic_buttons:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_button_clicked, block_type)
            button.set_tooltip_text("Right click top left area of the generated block for more options!")
            self.arithmetic_box.pack_start(button, False, False, 0)

        # Custom RTL blocks panel
        self.expander_custom_rtl = Gtk.Expander(label="Custom RTL")
        self.left_pane.pack_start(self.expander_custom_rtl, False, False, 0)

        self.custom_rtl_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.expander_custom_rtl.add(self.custom_rtl_box)

        add_custom_btn = Gtk.Button(label="Add Custom RTL Block")
        add_custom_btn.set_tooltip_text("Define a behavioral RTL block with custom VHDL")
        add_custom_btn.connect("clicked", self.on_add_custom_rtl_block)
        self.custom_rtl_box.pack_start(add_custom_btn, False, False, 0)

        # Components library panel
        self.expander_components = Gtk.Expander(label="Components")
        self.left_pane.pack_start(self.expander_components, False, False, 0)

        comp_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.expander_components.add(comp_outer)

        refresh_btn = Gtk.Button(label="Refresh")
        refresh_btn.connect("clicked", lambda w: self.refresh_component_panel())
        comp_outer.pack_start(refresh_btn, False, False, 0)

        self.comp_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        comp_outer.pack_start(self.comp_box, False, False, 0)

        self.expander_ops = Gtk.Expander(label="Edit Operations")
        self.left_pane.pack_start(self.expander_ops, False, False, 0)

        self.ops_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.expander_ops.add(self.ops_box)

        self.undo_button = Gtk.Button(label="Undo [CTRL+z]")
        self.undo_button.connect("clicked", self.on_undo)
        self.ops_box.pack_start(self.undo_button, False, False, 0)

        self.redo_button = Gtk.Button(label="Redo [CTRL+r]")
        self.redo_button.connect("clicked", self.on_redo)
        self.ops_box.pack_start(self.redo_button, False, False, 0)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.drawing_area = DrawingArea(self)
        self.drawing_area.set_size_request(DrawingArea.CANVAS_SIZE, DrawingArea.CANVAS_SIZE)
        self.scrolled_window.add(self.drawing_area)
        self.box.pack_start(self.scrolled_window, True, True, 0)

        self.blocks = []
        self.pins = []
        self.grid_size = 20

        self.wires = []
        self.dragging_wire = False
        self.drag_started = False
        self.wire_start_point = None

        self.context_menu = ContextMenu(self)
        self.pin_context_menu = PinContextMenu(self)
        self.wire_context_menu = WireContextMenu(self)

        self.selected_block = None
        self.selected_pin = None
        self.selected_wire = None

        self.selected_blocks = []
        self.selected_pins = []
        self.selected_wires = []

        self.undo_stack = []
        self.redo_stack = []

        self.update_undo_redo_buttons()
        self.refresh_component_panel()
        self.drawing_area.grab_focus()

        self.dirty = False
        self.dark_mode = False

        self.status_bar = Gtk.Label()
        self.status_bar.set_markup("<span color='#555555'>Ready</span>")
        self.status_bar.set_halign(Gtk.Align.START)
        self.status_bar.set_margin_start(6)
        self.status_bar.set_margin_bottom(2)
        self.vbox.pack_end(self.status_bar, False, False, 0)

        self.connect("delete-event", self.on_delete_event)

    # ------------------------------------------------------------------
    # Window-level state
    # ------------------------------------------------------------------

    def set_dirty(self, dirty):
        self.dirty = dirty
        title = "Simple VHDL Code Generator (SVCG)"
        if self.current_file_path:
            title += f" — {os.path.basename(self.current_file_path)}"
        if dirty:
            title = "* " + title
        self.set_title(title)

    def update_status_bar(self):
        parts = []
        total_sel = len(self.selected_blocks) + len(self.selected_pins) + len(self.selected_wires)
        if total_sel > 1:
            parts.append(f"Selected: {total_sel} items (Blocks:{len(self.selected_blocks)} Pins:{len(self.selected_pins)} Wires:{len(self.selected_wires)})")
        elif self.selected_block:
            parts.append(f"Block: {self.selected_block.text} [{self.selected_block.block_type}]")
        elif self.selected_pin:
            parts.append(f"Pin: {self.selected_pin.text} [{self.selected_pin.pin_type}]")
        elif self.selected_wire:
            parts.append(f"Wire: {self.selected_wire.text}")
        else:
            parts.append("Ready")
        parts.append(f"Blocks: {len(self.blocks)}  Pins: {len(self.pins)}  Wires: {len(self.wires)}")
        if self.current_file_path:
            parts.append(os.path.basename(self.current_file_path))
        self.status_bar.set_markup(
            "<span color='#555555'>" + " | ".join(parts) + "</span>"
        )

    def on_delete_event(self, widget, event):
        if not self.dirty:
            return False
        dialog = Gtk.MessageDialog(
            transient_for=self, flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.NONE,
            text="You have unsaved changes.",
        )
        dialog.format_secondary_text("Save before closing?")
        dialog.add_button("Discard", Gtk.ResponseType.NO)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Save", Gtk.ResponseType.YES)
        dialog.set_default_response(Gtk.ResponseType.YES)
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            if self.current_file_path:
                self.save_to_json(self.current_file_path)
            else:
                self.menu_bar.on_save_as_json_file(None)
            return self.dirty
        elif response == Gtk.ResponseType.NO:
            return False
        else:
            return True

    # ------------------------------------------------------------------
    # Element creation
    # ------------------------------------------------------------------

    def on_button_clicked(self, widget, block_type):
        try:
            self.push_undo()
            initial_x = round(random.randint(40, 400) // self.grid_size) * self.grid_size
            initial_y = round(random.randint(40, 400) // self.grid_size) * self.grid_size
            initial_width = round(40 // self.grid_size) * self.grid_size
            initial_height = round(40 // self.grid_size) * self.grid_size
            timestamp = datetime.now().isoformat(' ', 'seconds')
            new_block = Block(initial_x, initial_y, initial_width, initial_height,
                              f"{block_type} {timestamp}", block_type, self.grid_size, self)
            self.blocks.append(new_block)
            self.drawing_area.queue_draw()
            self.update_json()
        except Exception as e:
            print(f"Error in on_button_clicked: {e}")

    def on_pin_button_clicked(self, widget, pin_type):
        try:
            self.push_undo()
            initial_x = round(random.randint(40, 400) // self.grid_size) * self.grid_size
            initial_y = round(random.randint(40, 400) // self.grid_size) * self.grid_size
            initial_width = round(40 // self.grid_size) * self.grid_size
            initial_height = round(40 // self.grid_size) * self.grid_size
            timestamp = datetime.now().isoformat(' ', 'seconds')

            if "bus" in pin_type:
                dialog = Gtk.MessageDialog(
                    transient_for=self, flags=0,
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
                    initial_height = round((40 * 1) // self.grid_size) * self.grid_size
                    new_pin = Pin(initial_x, initial_y, initial_width, initial_height,
                                  f"{pin_type} {timestamp}", pin_type, self.grid_size, num_pins, self)
                    self.pins.append(new_pin)
                    self.drawing_area.queue_draw()
                    self.update_json()
                dialog.destroy()
            else:
                new_pin = Pin(initial_x, initial_y, initial_width, initial_height,
                              f"{pin_type} {timestamp}", pin_type, self.grid_size, 1, self)
                self.pins.append(new_pin)
                self.drawing_area.queue_draw()
                self.update_json()
        except ValueError as e:
            print(f"ValueError in on_pin_button_clicked: {e}")
        except Exception as e:
            print(f"Error in on_pin_button_clicked: {e}")

    # ------------------------------------------------------------------
    # Element operations (context menu handlers)
    # ------------------------------------------------------------------

    def on_change_border_color(self, widget):
        try:
            target = self.selected_block or self.selected_pin
            if target:
                dialog = Gtk.ColorChooserDialog(title="Choose Border Color", transient_for=self)
                response = dialog.run()
                if response == Gtk.ResponseType.OK:
                    color = dialog.get_rgba()
                    target.border_color = (color.red, color.green, color.blue)
                    self.drawing_area.queue_draw()
                    self.update_json()
                    self.push_undo()
                dialog.destroy()
        except Exception as e:
            print(f"Error in on_change_border_color: {e}")

    def on_change_fill_color(self, widget):
        try:
            target = self.selected_block or self.selected_pin
            if target:
                dialog = Gtk.ColorChooserDialog(title="Choose Fill Color", transient_for=self)
                response = dialog.run()
                if response == Gtk.ResponseType.OK:
                    color = dialog.get_rgba()
                    target.fill_color = (color.red, color.green, color.blue)
                    self.drawing_area.queue_draw()
                    self.update_json()
                    self.push_undo()
                dialog.destroy()
        except Exception as e:
            print(f"Error in on_change_fill_color: {e}")

    def on_change_text(self, widget):
        try:
            if self.selected_block:
                self._text_dialog("Change Text", "Enter new text for the block:", self.selected_block)
            elif self.selected_pin:
                self._text_dialog("Change Text", "Enter new text for the pin:", self.selected_pin)
        except Exception as e:
            print(f"Error in on_change_text: {e}")

    def _text_dialog(self, title, prompt, target):
        dialog = Gtk.MessageDialog(
            transient_for=self, flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=title,
        )
        dialog.format_secondary_text(prompt)
        entry = Gtk.Entry()
        entry.set_text(target.text)
        dialog.get_content_area().add(entry)
        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            target.text = entry.get_text()
            self.drawing_area.queue_draw()
            self.update_json()
            self.push_undo()
        dialog.destroy()

    def on_change_text_color(self, widget):
        try:
            target = self.selected_block or self.selected_pin
            if target:
                dialog = Gtk.ColorChooserDialog(title="Choose Text Color", transient_for=self)
                response = dialog.run()
                if response == Gtk.ResponseType.OK:
                    color = dialog.get_rgba()
                    target.text_color = (color.red, color.green, color.blue)
                    self.drawing_area.queue_draw()
                    self.update_json()
                    self.push_undo()
                dialog.destroy()
        except Exception as e:
            print(f"Error in on_change_text_color: {e}")

    def _do_rotate(self, angle):
        """Rotate the selected block or pin by angle degrees, rewiring attached wires."""
        if self.selected_block:
            self.selected_block.rotate(angle)
        elif self.selected_pin:
            self.selected_pin.rotate(angle)
        else:
            return
        self.update_points()
        self.drawing_area.queue_draw()
        self.update_json()
        self.push_undo()

    def on_rotate_90(self, widget):
        try:
            self._do_rotate(90)
        except Exception as e:
            print(f"Error in on_rotate_90: {e}")

    def on_rotate_180(self, widget):
        try:
            self._do_rotate(180)
        except Exception as e:
            print(f"Error in on_rotate_180: {e}")

    def on_rotate_270(self, widget):
        try:
            self._do_rotate(270)
        except Exception as e:
            print(f"Error in on_rotate_270: {e}")

    def on_copy_block(self, widget):
        try:
            if self.selected_blocks or self.selected_pins:
                self.push_undo()
                offset = self.grid_size * 2
                new_blocks = []
                new_pins = []
                for block in list(self.selected_blocks):
                    nb = Block(block.x + offset, block.y + offset, block.width, block.height,
                               block.text, block.block_type, self.grid_size, self)
                    nb.border_color = block.border_color
                    nb.fill_color = block.fill_color
                    nb.text_color = block.text_color
                    nb.rotation = block.rotation
                    if block.block_type == "CUSTOM":
                        nb.custom_data = block.custom_data
                        nb.update_points()
                        nb.init_wires()
                    self.blocks.append(nb)
                    new_blocks.append(nb)
                for pin in list(self.selected_pins):
                    np_ = Pin(pin.x + offset, pin.y + offset, pin.width, pin.height,
                              pin.text, pin.pin_type, self.grid_size, pin.num_pins, self)
                    np_.border_color = pin.border_color
                    np_.fill_color = pin.fill_color
                    np_.text_color = pin.text_color
                    np_.rotation = pin.rotation
                    self.pins.append(np_)
                    new_pins.append(np_)
                self._clear_multi_select()
                for nb in new_blocks:
                    nb.set_selected(True)
                    self.selected_blocks.append(nb)
                for np_ in new_pins:
                    np_.set_selected(True)
                    self.selected_pins.append(np_)
                self.drawing_area.queue_draw()
                self.update_json()
            elif self.selected_block:
                self.clipboard_block = self.selected_block
                self.clipboard_pin = None
                new_block = Block(
                    self.selected_block.x + self.grid_size,
                    self.selected_block.y + self.grid_size,
                    self.selected_block.width, self.selected_block.height,
                    self.selected_block.text, self.selected_block.block_type,
                    self.grid_size, self,
                )
                new_block.border_color = self.selected_block.border_color
                new_block.fill_color = self.selected_block.fill_color
                new_block.text_color = self.selected_block.text_color
                new_block.rotation = self.selected_block.rotation
                if self.selected_block.block_type == "CUSTOM":
                    new_block.custom_data = self.selected_block.custom_data
                    new_block.update_points()
                    new_block.init_wires()
                self.blocks.append(new_block)
                self.drawing_area.queue_draw()
                self.update_json()
                self.push_undo()
            elif self.selected_pin:
                self.clipboard_pin = self.selected_pin
                self.clipboard_block = None
                new_pin = Pin(
                    self.selected_pin.x + self.grid_size,
                    self.selected_pin.y + self.grid_size,
                    self.selected_pin.width, self.selected_pin.height,
                    self.selected_pin.text, self.selected_pin.pin_type,
                    self.grid_size, self.selected_pin.num_pins, self,
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
                for idx, i_wire in enumerate(self.selected_block.get_input_wires()):
                    for widx, w_wire in enumerate(i_wire):
                        if isinstance(w_wire, str) and wire.id in w_wire:
                            wires_to_remove.append(wire)
                for idx, o_wire in enumerate(self.selected_block.get_output_wires()):
                    for widx, w_wire in enumerate(o_wire):
                        if isinstance(w_wire, str) and wire.id in w_wire:
                            wires_to_remove.append(wire)
            for wire in wires_to_remove:
                self.wires.remove(wire)
            self.selected_block.clear_wires()
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
                for idx, i_wire in enumerate(self.selected_pin.get_wires()):
                    for widx, w_wire in enumerate(i_wire):
                        if isinstance(w_wire, str) and wire.id in w_wire:
                            wires_to_remove.append(wire)
            for wire in wires_to_remove:
                self.wires.remove(wire)
            self.selected_pin.clear_wires()
            self.update_json()
            self.push_undo()
            self.drawing_area.queue_draw()
        except Exception as e:
            print(f"An error occurred: {e}")

    def on_delete_block(self, widget):
        try:
            if self.selected_blocks or self.selected_pins:
                self.push_undo()
                for block in list(self.selected_blocks):
                    self.selected_block = block
                    self.delete_block_wire_connections()
                    if block in self.blocks:
                        self.blocks.remove(block)
                for pin in list(self.selected_pins):
                    self.selected_pin = pin
                    self.delete_pin_wire_connections()
                    if pin in self.pins:
                        self.pins.remove(pin)
                self.selected_blocks = []
                self.selected_pins = []
                self.selected_block = None
                self.selected_pin = None
                self.drawing_area.queue_draw()
                self.update_json()
            elif self.selected_block:
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
            if self.selected_blocks or self.selected_pins:
                self.push_undo()
                for block in list(self.selected_blocks):
                    self.selected_block = block
                    self.delete_block_wire_connections()
                    if block in self.blocks:
                        self.blocks.remove(block)
                for pin in list(self.selected_pins):
                    self.selected_pin = pin
                    self.delete_pin_wire_connections()
                    if pin in self.pins:
                        self.pins.remove(pin)
                self.selected_blocks = []
                self.selected_pins = []
                self.selected_block = None
                self.selected_pin = None
                self.drawing_area.queue_draw()
                self.update_json()
            elif self.selected_block:
                self.push_undo()
                self.delete_block_wire_connections()
                self.clipboard_block = self.selected_block
                self.clipboard_pin = None
                self.blocks.remove(self.selected_block)
                self.selected_block = None
                self.drawing_area.queue_draw()
                self.update_json()
            elif self.selected_pin:
                self.push_undo()
                self.delete_pin_wire_connections()
                self.clipboard_pin = self.selected_pin
                self.clipboard_block = None
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
                    self.mouse_x, self.mouse_y,
                    self.clipboard_block.width, self.clipboard_block.height,
                    self.clipboard_block.text, self.clipboard_block.block_type,
                    self.grid_size, self,
                )
                new_block.border_color = self.clipboard_block.border_color
                new_block.fill_color = self.clipboard_block.fill_color
                new_block.text_color = self.clipboard_block.text_color
                new_block.rotation = self.clipboard_block.rotation
                if self.clipboard_block.block_type == "CUSTOM":
                    new_block.custom_data = self.clipboard_block.custom_data
                    new_block.update_points()
                    new_block.init_wires()
                self.blocks.append(new_block)
                self.drawing_area.queue_draw()
                self.update_json()
            elif self.clipboard_pin:
                self.push_undo()
                new_pin = Pin(
                    self.mouse_x, self.mouse_y,
                    self.clipboard_pin.width, self.clipboard_pin.height,
                    self.clipboard_pin.text, self.clipboard_pin.pin_type,
                    self.grid_size, self.clipboard_pin.num_pins, self,
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

    def on_add_custom_rtl_block(self, widget):
        from custom_block_dialog import CustomBlockDialog
        dialog = CustomBlockDialog(self)
        response = dialog.run()
        if response != Gtk.ResponseType.OK:
            dialog.destroy()
            return
        cd = dialog.get_data()
        dialog.destroy()
        self.push_undo()
        n_ports = max(len(cd["input_names"]), len(cd["output_names"]), 1)
        w = self.grid_size * 6
        h = self.grid_size * max(n_ports + 2, 4)
        x = round(random.randint(40, 400) // self.grid_size) * self.grid_size
        y = round(random.randint(40, 400) // self.grid_size) * self.grid_size
        new_block = Block(x, y, w, h, cd["entity_name"], "CUSTOM", self.grid_size, self)
        new_block.custom_data = cd
        new_block.update_points()
        new_block.init_wires()
        self.blocks.append(new_block)
        self.drawing_area.queue_draw()
        self.update_json()

    def on_edit_custom_rtl_block(self, widget):
        if not self.selected_block or self.selected_block.block_type != "CUSTOM":
            return
        from custom_block_dialog import CustomBlockDialog
        block = self.selected_block
        dialog = CustomBlockDialog(self, existing=block.custom_data)
        response = dialog.run()
        if response != Gtk.ResponseType.OK:
            dialog.destroy()
            return
        cd = dialog.get_data()
        dialog.destroy()
        self.push_undo()
        block.custom_data = cd
        block.text = cd["entity_name"]
        n_ports = max(len(cd["input_names"]), len(cd["output_names"]), 1)
        block.height = self.grid_size * max(n_ports + 2, 4)
        block.update_points()
        block.init_wires()
        self.drawing_area.queue_draw()
        self.update_json()

    def on_connect_pin(self, widget):
        try:
            if self.selected_block or self.selected_pin:
                print("Connect pin")
        except Exception as e:
            print(f"Error in on_connect_pin: {e}")

    def on_disconnect_pin(self, widget):
        try:
            if self.selected_block or self.selected_pin:
                print("Disconnect pin")
        except Exception as e:
            print(f"Error in on_disconnect_pin: {e}")

    # ------------------------------------------------------------------
    # Canvas export (SVG / PNG)
    # ------------------------------------------------------------------

    def _compute_bbox(self, padding=40):
        xs, ys = [], []
        for b in self.blocks:
            xs += [b.x, b.x + b.width]
            ys += [b.y, b.y + b.height]
        for p in self.pins:
            xs += [p.x, p.x + p.width]
            ys += [p.y, p.y + p.height]
        for w in self.wires:
            for gx, gy in (w.path or []):
                xs.append(gx * self.grid_size)
                ys.append(gy * self.grid_size)
        if not xs:
            return 0, 0, 400, 300
        return (max(0, min(xs) - padding), max(0, min(ys) - padding),
                max(xs) + padding, max(ys) + padding)

    def _render_schematic(self, cr):
        for block in self.blocks:
            block.draw(cr)
        for pin in self.pins:
            pin.draw(cr)
        for wire in self.wires:
            wire.draw(cr)

    def on_export_svg(self, widget):
        try:
            import cairo as _cairo
            if not self.blocks and not self.pins:
                self.show_error_message("Nothing to export", "Add blocks and pins to the canvas first.")
                return
            dialog = Gtk.FileChooserDialog(
                title="Export as SVG", parent=self,
                action=Gtk.FileChooserAction.SAVE,
            )
            dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                Gtk.STOCK_SAVE,   Gtk.ResponseType.ACCEPT)
            flt = Gtk.FileFilter()
            flt.set_name("SVG files (*.svg)")
            flt.add_pattern("*.svg")
            dialog.add_filter(flt)
            base = os.path.splitext(os.path.basename(self.current_file_path))[0] if self.current_file_path else "schematic"
            dialog.set_current_name(f"{base}.svg")
            resp = dialog.run()
            if resp == Gtk.ResponseType.ACCEPT:
                path = dialog.get_filename()
                if not path.lower().endswith(".svg"):
                    path += ".svg"
                dialog.destroy()
                x0, y0, x1, y1 = self._compute_bbox()
                w, h = max(1.0, x1 - x0), max(1.0, y1 - y0)
                surface = _cairo.SVGSurface(path, w, h)
                cr = _cairo.Context(surface)
                cr.set_source_rgb(1, 1, 1)
                cr.paint()
                cr.translate(-x0, -y0)
                self._render_schematic(cr)
                surface.finish()
            else:
                dialog.destroy()
        except Exception as e:
            self.show_error_message("SVG export failed", str(e))
            print(f"Error in on_export_svg: {e}")

    def on_export_png(self, widget):
        try:
            import cairo as _cairo
            if not self.blocks and not self.pins:
                self.show_error_message("Nothing to export", "Add blocks and pins to the canvas first.")
                return
            dialog = Gtk.FileChooserDialog(
                title="Export as PNG", parent=self,
                action=Gtk.FileChooserAction.SAVE,
            )
            dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                Gtk.STOCK_SAVE,   Gtk.ResponseType.ACCEPT)
            flt = Gtk.FileFilter()
            flt.set_name("PNG files (*.png)")
            flt.add_pattern("*.png")
            dialog.add_filter(flt)
            base = os.path.splitext(os.path.basename(self.current_file_path))[0] if self.current_file_path else "schematic"
            dialog.set_current_name(f"{base}.png")
            resp = dialog.run()
            if resp == Gtk.ResponseType.ACCEPT:
                path = dialog.get_filename()
                if not path.lower().endswith(".png"):
                    path += ".png"
                dialog.destroy()
                x0, y0, x1, y1 = self._compute_bbox()
                w, h = max(1, int(x1 - x0)), max(1, int(y1 - y0))
                surface = _cairo.ImageSurface(_cairo.FORMAT_ARGB32, w, h)
                cr = _cairo.Context(surface)
                cr.set_source_rgb(1, 1, 1)
                cr.paint()
                cr.translate(-x0, -y0)
                self._render_schematic(cr)
                surface.write_to_png(path)
            else:
                dialog.destroy()
        except Exception as e:
            self.show_error_message("PNG export failed", str(e))
            print(f"Error in on_export_png: {e}")


if __name__ == "__main__":
    win = BlocksWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
