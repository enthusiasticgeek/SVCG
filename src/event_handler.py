#!/usr/bin/env python3
"""
event_handler.py -- mixin for mouse/keyboard events, drawing, and wire management
"""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from datetime import datetime
from drawing_area import DrawingArea
from wire import Wire


class EventHandlerMixin:

    def on_draw(self, widget, cr):
        try:
            dark = getattr(self, 'dark_mode', False)
            width, height = DrawingArea.CANVAS_SIZE, DrawingArea.CANVAS_SIZE

            # Canvas background
            if dark:
                cr.set_source_rgb(0.12, 0.12, 0.12)
            else:
                cr.set_source_rgb(1.0, 1.0, 1.0)
            cr.rectangle(0, 0, width, height)
            cr.fill()

            # Grid dots
            cr.set_source_rgb(0, 0.55, 0) if dark else cr.set_source_rgb(0, 1, 0)
            for x in range(0, width, self.grid_size):
                for y in range(0, height, self.grid_size):
                    cr.rectangle(x, y, 2, 2)
                    cr.fill()

            # Axis labels
            cr.set_source_rgb(0.75, 0.75, 0.75) if dark else cr.set_source_rgb(0, 0, 0)
            cr.set_font_size(12)
            for i, x in enumerate(range(0, width, self.grid_size)):
                label = self.get_column_label(i)
                cr.move_to(x + 5, 15)
                cr.show_text(label)

            for i, y in enumerate(range(0, height, self.grid_size)):
                label = str(i + 1)
                cr.move_to(5, y + 15)
                cr.show_text(label)

            for block in self.blocks:
                block.draw(cr)
            for pin in self.pins:
                pin.draw(cr)
            for wire in self.wires:
                wire.draw(cr)

            if self.dragging_wire:
                cr.set_source_rgb(1, 0, 0)
                cr.set_line_width(2)
                cr.move_to(self.wire_start_point[0], self.wire_start_point[1])
                cr.line_to(self.mouse_x, self.wire_start_point[1])
                cr.line_to(self.mouse_x, self.mouse_y)
                cr.stroke()

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
                self.on_rotate_90(widget)
            elif key == "Escape":
                self._clear_multi_select()
                self.drawing_area.queue_draw()
                self.update_status_bar()
            return True
        except Exception as e:
            print(f"Error in on_key_press: {e}")

    def _clear_multi_select(self):
        for b in self.selected_blocks:
            b.set_selected(False)
        for p in self.selected_pins:
            p.set_selected(False)
        for w in self.selected_wires:
            w.set_selected(False)
        self.selected_blocks = []
        self.selected_pins = []
        self.selected_wires = []

    def on_button_press(self, widget, event):
        if not self.drag_started:
            if event.x < 0 or event.y < 0:
                return False
            if (event.button == 1 and event.button == 2 or
                    event.button == 1 and event.button == 3 or
                    event.button == 2 and event.button == 3):
                return False
            try:
                self.push_undo()
                if event.button == 1:
                    shift_held = bool(event.state & Gdk.ModifierType.SHIFT_MASK)
                    cx = int(event.x / self.drawing_area.zoom)
                    cy = int(event.y / self.drawing_area.zoom)

                    if shift_held:
                        clicked = False
                        for block in self.blocks:
                            if block.contains_point(cx, cy):
                                if block in self.selected_blocks:
                                    self.selected_blocks.remove(block)
                                    block.set_selected(False)
                                else:
                                    self.selected_blocks.append(block)
                                    block.set_selected(True)
                                    self.selected_block = block
                                clicked = True
                                break
                        if not clicked:
                            for pin in self.pins:
                                if pin.contains_point(cx, cy):
                                    if pin in self.selected_pins:
                                        self.selected_pins.remove(pin)
                                        pin.set_selected(False)
                                    else:
                                        self.selected_pins.append(pin)
                                        pin.set_selected(True)
                                        self.selected_pin = pin
                                    clicked = True
                                    break
                        if not clicked:
                            for wire in self.wires:
                                if wire.contains_point(cx, cy):
                                    if wire in self.selected_wires:
                                        self.selected_wires.remove(wire)
                                        wire.set_selected(False)
                                    else:
                                        self.selected_wires.append(wire)
                                        wire.set_selected(True)
                                        self.selected_wire = wire
                                    break
                        for b in self.selected_blocks:
                            b.start_drag(cx, cy)
                        for p in self.selected_pins:
                            p.start_drag(cx, cy)
                    else:
                        self._clear_multi_select()
                        self.selected_block = None
                        self.selected_pin = None
                        self.selected_wire = None
                        for block in self.blocks:
                            if block.contains_pin(cx, cy):
                                self.wire_start_point = block.contains_pin(cx, cy)
                                self.dragging_wire = True
                                break
                        for pin in self.pins:
                            if pin.contains_pin(cx, cy):
                                self.wire_start_point = pin.contains_pin(cx, cy)
                                self.dragging_wire = True
                                break
                        if not self.dragging_wire:
                            for block in self.blocks:
                                if block.contains_point(cx, cy):
                                    self.selected_block = block
                                    block.set_selected(True)
                                    block.start_drag(cx, cy)
                                    break
                            for pin in self.pins:
                                if pin.contains_point(cx, cy):
                                    self.selected_pin = pin
                                    pin.set_selected(True)
                                    pin.start_drag(cx, cy)
                                    break
                            for wire in self.wires:
                                if wire.contains_point(cx, cy):
                                    self.selected_wire = wire
                                    wire.set_selected(True)
                                    break
                elif event.button == 3:
                    for block in self.blocks:
                        if block.contains_point(int(event.x / self.drawing_area.zoom), int(event.y / self.drawing_area.zoom)):
                            self.selected_block = block
                            block.set_selected(True)
                            self.context_menu.set_view_vhdl_code_sensitive(True)
                            if block.contains_pin(int(event.x / self.drawing_area.zoom), int(event.y / self.drawing_area.zoom)):
                                self.pin_context_menu.popup(event)
                            else:
                                self.context_menu.popup(event)
                            break
                    for pin in self.pins:
                        if pin.contains_point(int(event.x / self.drawing_area.zoom), int(event.y / self.drawing_area.zoom)):
                            self.selected_pin = pin
                            pin.set_selected(True)
                            self.context_menu.set_view_vhdl_code_sensitive(False)
                            connection_point = pin.contains_pin(int(event.x / self.drawing_area.zoom), int(event.y / self.drawing_area.zoom))
                            if connection_point:
                                self.pin_context_menu.popup(event)
                            else:
                                self.context_menu.popup(event)
                            break
                    for wire in self.wires:
                        if wire.contains_point(int(event.x / self.drawing_area.zoom), int(event.y / self.drawing_area.zoom)):
                            self.selected_wire = wire
                            wire.set_selected(True)
                            self.wire_context_menu.popup(None, None, None, None, event.button, event.time)
                            break

                self.drawing_area.queue_draw()
                self.update_json()
                self.push_undo()
                self.drawing_area.grab_focus()
                self.drag_started = True
                self.update_status_bar()
            except Exception as e:
                print(f"Error in on_button_press: {e}")

    def on_button_release(self, widget, event):
        if event.x < 0 or event.y < 0:
            return False
        if (event.button == 1 and event.button == 2 or
                event.button == 1 and event.button == 3 or
                event.button == 2 and event.button == 3):
            return False

        try:
            self.push_undo()
            for block in self.blocks:
                block.end_drag()
                if block not in self.selected_blocks:
                    block.set_selected(False)
                block.update_points()
            for pin in self.pins:
                pin.end_drag()
                if pin not in self.selected_pins:
                    pin.set_selected(False)
                pin.update_points()

            if not self.dragging_wire:
                for block in self.blocks:
                    if block.contains_point(int(event.x / self.drawing_area.zoom), int(event.y / self.drawing_area.zoom)):
                        block_dict = block.to_dict()
                        for widx, wire in enumerate(self.wires):
                            for idx, input_wires in enumerate(block_dict['input_wires']):
                                if input_wires is not None and wire.id in input_wires:
                                    if self.convert_to_tuple(wire.start_point) in block.prev_input_connections():
                                        wire.update_start_point(block_dict['input_points'][idx])
                                    elif self.convert_to_tuple(wire.end_point) in block.prev_input_connections():
                                        wire.update_end_point(block_dict['input_points'][idx])
                            for idx, output_wires in enumerate(block_dict['output_wires']):
                                if output_wires is not None and wire.id in output_wires:
                                    if self.convert_to_tuple(wire.start_point) in block.prev_output_connections():
                                        wire.update_start_point(block_dict['output_points'][idx])
                                    elif self.convert_to_tuple(wire.end_point) in block.prev_output_connections():
                                        wire.update_end_point(block_dict['output_points'][idx])
                        block.update_points()
                        break
                for pin in self.pins:
                    if pin.contains_point(int(event.x / self.drawing_area.zoom), int(event.y / self.drawing_area.zoom)):
                        pin_dict = pin.to_dict()
                        for widx, wire in enumerate(self.wires):
                            for idx, wires in enumerate(pin_dict['wires']):
                                if wires is not None and wire.id in wires:
                                    if self.convert_to_tuple(wire.start_point) in pin.prev_connections():
                                        wire.update_start_point(pin_dict['connection_points'][idx])
                                    elif self.convert_to_tuple(wire.end_point) in pin.prev_connections():
                                        wire.update_end_point(pin_dict['connection_points'][idx])
                        pin.update_points()
                        break
                self.update_json()

            elif self.dragging_wire:
                end_point = None
                start_block = None
                end_block = None
                start_pin = None
                end_pin = None

                for block in self.blocks:
                    if block.contains_pin(int(event.x / self.drawing_area.zoom), int(event.y / self.drawing_area.zoom)):
                        end_point = block.contains_pin(int(event.x / self.drawing_area.zoom), int(event.y / self.drawing_area.zoom))
                        end_block = block
                        break
                for pin in self.pins:
                    if pin.contains_pin(int(event.x / self.drawing_area.zoom), int(event.y / self.drawing_area.zoom)):
                        end_point = pin.contains_pin(int(event.x / self.drawing_area.zoom), int(event.y / self.drawing_area.zoom))
                        end_pin = pin
                        break

                if end_point and end_point != self.wire_start_point:
                    duplicate_wire = any(
                        (wire.start_point == self.wire_start_point and wire.end_point == end_point) or
                        (wire.start_point == end_point and wire.end_point == self.wire_start_point)
                        for wire in self.wires
                    )
                    if not duplicate_wire:
                        timestamp = datetime.now().isoformat(' ', 'seconds')
                        new_wire = Wire(f"wire {timestamp}", self.wire_start_point, end_point, "wire", self.grid_size, self)
                        print(f"{new_wire.id} new wire created with name {new_wire.text}")

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
            self.update_status_bar()
        except Exception as e:
            print(f"Error in on_button_release: {e}")

    def on_motion_notify(self, widget, event):
        try:
            self.mouse_x = max(0, int(event.x / self.drawing_area.zoom))
            self.mouse_y = max(0, int(event.y / self.drawing_area.zoom))
            width, height = self.drawing_area.get_allocated_width(), self.drawing_area.get_allocated_height()
            for block in self.blocks:
                block.drag(self.mouse_x, self.mouse_y, width, height)
            for pin in self.pins:
                pin.drag(self.mouse_x, self.mouse_y, width, height)
            self.drawing_area.queue_draw()
            self.update_json()
            self.drawing_area.grab_focus()
            self.mouse_label.set_markup(f"<span color='green'>Cursor: ({int(self.mouse_x)}, {int(self.mouse_y)})</span>")
        except Exception as e:
            print(f"Error in on_motion_notify: {e}")

    def find_closest_point(self, points, target, tolerance=10):
        for i, point in enumerate(points):
            if abs(point[0] - target[0]) <= tolerance and abs(point[1] - target[1]) <= tolerance:
                return i
        return None

    def update_points(self):
        for block in self.blocks:
            block_dict = block.to_dict()
            for widx, wire in enumerate(self.wires):
                for idx, input_wires in enumerate(block_dict['input_wires']):
                    if input_wires is not None and wire.id in input_wires:
                        if self.convert_to_tuple(wire.start_point) in block.prev_input_connections():
                            wire.update_start_point(block_dict['input_points'][idx])
                        elif self.convert_to_tuple(wire.end_point) in block.prev_input_connections():
                            wire.update_end_point(block_dict['input_points'][idx])
                for idx, output_wires in enumerate(block_dict['output_wires']):
                    if output_wires is not None and wire.id in output_wires:
                        if self.convert_to_tuple(wire.start_point) in block.prev_output_connections():
                            wire.update_start_point(block_dict['output_points'][idx])
                        elif self.convert_to_tuple(wire.end_point) in block.prev_output_connections():
                            wire.update_end_point(block_dict['output_points'][idx])
            block.update_points()
        for pin in self.pins:
            pin_dict = pin.to_dict()
            for widx, wire in enumerate(self.wires):
                for idx, wires in enumerate(pin_dict['wires']):
                    if wires is not None and wire.id in wires:
                        if self.convert_to_tuple(wire.start_point) in pin.prev_connections():
                            wire.update_start_point(pin_dict['connection_points'][idx])
                        elif self.convert_to_tuple(wire.end_point) in pin.prev_connections():
                            wire.update_end_point(pin_dict['connection_points'][idx])
            pin.update_points()

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
            self.wires.remove(wire)
            for block in self.blocks:
                block_dict = block.to_dict()
                if wire.start_point in block.input_connections():
                    self.reset_wire_by_index(wire, block_dict['input_wires'])
                if wire.start_point in block.output_connections():
                    self.reset_wire_by_index(wire, block_dict['output_wires'])
                if wire.end_point in block.input_connections():
                    self.reset_wire_by_index(wire, block_dict['input_wires'])
                if wire.end_point in block.output_connections():
                    self.reset_wire_by_index(wire, block_dict['output_wires'])
            for pin in self.pins:
                pin_dict = pin.to_dict()
                if wire.start_point in pin.connections():
                    self.reset_wire_by_index(wire, pin_dict['wires'])
                if wire.end_point in pin.connections():
                    self.reset_wire_by_index(wire, pin_dict['wires'])
            self.update_json()
            self.push_undo()
            self.drawing_area.queue_draw()
        except Exception as e:
            print(f"Error in delete_wire: {e}")

    def reset_wire_by_index(self, wire, wires):
        try:
            for idx, w in enumerate(wires):
                if w is not None and wire.id in w:
                    wires[idx] = []
        except Exception as e:
            print(f"Error in reset_wire_by_index: {e}")

    def pin_has_no_wires_connected(self, pin):
        if pin:
            if all(not wires for wires in pin.wires):
                return True
        return False

    def block_has_no_wires_connected(self, block):
        if block:
            if all(not wires for wires in block.input_wires):
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
