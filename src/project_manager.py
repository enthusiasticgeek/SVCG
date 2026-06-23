#!/usr/bin/env python3
"""
project_manager.py -- mixin for save/load/undo/redo operations
"""
import json
from blocks import Block
from pins import Pin
from wire import Wire


class ProjectManagerMixin:

    def elements_to_json(self):
        try:
            elements = []
            if self.blocks:
                elements.extend([block.to_dict() for block in self.blocks])
            if self.pins:
                elements.extend([pin.to_dict() for pin in self.pins])
            if self.wires:
                elements.extend([wire.to_dict() for wire in self.wires])
            return json.dumps(elements, indent=4)
        except Exception as e:
            print(f"Error in elements_to_json: {e}")
            return "[]"

    def update_json(self):
        try:
            if self.current_file_path:
                with open(self.current_file_path, "w") as file:
                    file.write(self.elements_to_json())
        except IOError as e:
            print(f"IOError in update_json: {e}")
        except Exception as e:
            print(f"Error in update_json: {e}")

    def push_undo(self):
        try:
            self.undo_stack.append(self.elements_to_json())
            self.redo_stack = []
            self.update_undo_redo_buttons()
            self.set_dirty(True)
        except Exception as e:
            print(f"Error in push_undo: {e}")

    def undo(self):
        try:
            if self.undo_stack:
                self.redo_stack.append(self.elements_to_json())
                data = json.loads(self.undo_stack.pop())
                self.blocks = [Block.from_dict(d, self) for d in data if d.get("block_type")]
                self.pins   = [Pin.from_dict(d, self)   for d in data if d.get("pin_type")]
                self.wires  = [Wire.from_dict(d, self)  for d in data if d.get("start_point") is not None]
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
                self.blocks = [Block.from_dict(d, self) for d in data if d.get("block_type")]
                self.pins   = [Pin.from_dict(d, self)   for d in data if d.get("pin_type")]
                self.wires  = [Wire.from_dict(d, self)  for d in data if d.get("start_point") is not None]
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

    def save_to_json(self, file_path):
        try:
            elements = self.elements_to_json()
            if elements != "[]":
                with open(file_path, "w") as file:
                    file.write(elements)
                self.current_file_path = file_path
                self.set_dirty(False)
                self.update_status_bar()
            else:
                print("No data to save. The elements list is empty.")
        except IOError as e:
            print(f"IOError in save_to_json: {e}")
        except Exception as e:
            print(f"Error in save_to_json: {e}")

    def load_from_json(self, file_path):
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
            if data:
                self.blocks = [Block.from_dict(d, self) for d in data if d.get("block_type")]
                self.pins   = [Pin.from_dict(d, self)   for d in data if d.get("pin_type")]
                self.wires  = [Wire.from_dict(d, self)  for d in data if d.get("start_point") is not None]
                self.drawing_area.queue_draw()
                self.current_file_path = file_path
                self.set_dirty(False)
                self.update_status_bar()
            else:
                print("The file is empty or contains no valid data.")
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError in load_from_json: {e}")
        except IOError as e:
            print(f"IOError in load_from_json: {e}")
        except Exception as e:
            print(f"Error in load_from_json: {e}")
