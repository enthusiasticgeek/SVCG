#!/usr/bin/env python3
import cairo
import math
import numpy as np
import random
import uuid
from astar import AStar

class Wire:
    def __init__(self, text, start_point, end_point, wire_type, grid_size, parent_window, start_block=None, end_block=None, start_pin=None, end_pin=None):
        self.id = f"wire_{str(uuid.uuid4().int)[:10]}"  # Generate a unique 10-digit ID
        self.text = text
        self.text_pos_x = round(random.randint(20,40))
        self.text_pos_y = round(random.randint(20,40))
        self.start_point = start_point
        self.end_point = end_point
        self.grid_size = grid_size
        self.parent_window = parent_window
        self.start_block = start_block
        self.end_block = end_block
        self.start_pin = start_pin
        self.end_pin = end_pin
        self.wire_type = wire_type
        self.path = self.calculate_path()
        self.selected = False  # Attribute to track selection state

    def set_selected(self, selected):
        self.selected = selected

    def update_start_point(self, new_start_point):
        self.start_point = new_start_point
        self.path = self.calculate_path()

    def update_end_point(self, new_end_point):
        self.end_point = new_end_point
        self.path = self.calculate_path()

    def update_connections(self):
        #print(f"Updating connections for wire {self.text}")
        #print(f"Before update - Start Point: {self.start_point}, End Point: {self.end_point}")
        if self.start_block:
            self.start_point = self.start_block.contains_pin(int(self.start_point[0]), int(self.start_point[1]))
        if self.end_block:
            self.end_point = self.end_block.contains_pin(int(self.end_point[0]), int(self.end_point[1]))
        if self.start_pin:
            self.start_point = self.start_pin.contains_pin(int(self.start_point[0]), int(self.start_point[1]))
        if self.end_pin:
            self.end_point = self.end_pin.contains_pin(int(self.end_point[0]), int(self.end_point[1]))
        #print(f"After update - Start Point: {self.start_point}, End Point: {self.end_point}")
        self.path = self.calculate_path()

    def calculate_path(self):
        if self.start_point is None or self.end_point is None:
            print("Start or end point is None. Cannot calculate path.")
            return []
        self.path = self.calculate_path_astar()
        return self.path
 
    ############## MANHATTAN ROUTING ###############
    def calculate_path_manhattan(self):
        x1, y1 = self.start_point
        x2, y2 = self.end_point

        x1, y1 = int(x1), int(y1)
        x2, y2 = int(x2), int(y2)

        path = []
        if x1 != x2:
            path.extend([(x, y1) for x in range(x1, x2 + 1)])
        if y1 != y2:
            path.extend([(x2, y) for y in range(y1, y2 + 1)])
        return path

    def draw_manhattan(self, cr):
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(2)
        for segment in self.path:
            x1, y1, x2, y2 = segment
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
        cr.stroke()

    ############## ASTAR ROUTING ###############
    def calculate_path_astar(self):
        if self.start_point is None or self.end_point is None:
            print("Start or end point is None. Cannot calculate path.")
            return []
        grid = self.parent_window.drawing_area.grid
        astar = AStar(grid)
        start_point = (int(self.start_point[0] / self.grid_size), int(self.start_point[1] / self.grid_size))
        end_point = (int(self.end_point[0] / self.grid_size), int(self.end_point[1] / self.grid_size))
        came_from, cost_so_far = astar.astar(start_point, end_point)
        path = astar.reconstruct_path(came_from, start_point, end_point)
        if not path:
            print(f"No path found from {start_point} to {end_point}")
        return path
    

    def draw(self, cr):
        cr.set_source_rgb(0, 0, 1)
        cr.set_line_width(2)

        if self.path:
            cr.move_to(self.path[0][0] * self.grid_size, self.path[0][1] * self.grid_size)
            for x, y in self.path[1:]:
                cr.line_to(x * self.grid_size, y * self.grid_size)
            cr.stroke()

            fill_color = (0, 0, 1)
            cr.set_source_rgb(*fill_color)
            cr.set_font_size(8)
            cr.move_to(self.path[0][0] * self.grid_size + self.text_pos_x, self.path[0][1] * self.grid_size + self.text_pos_y)
            cr.show_text(self.text)

    def contains_point(self, x, y, tolerance=10):
        def point_on_line(px, py, x1, y1, x2, y2, tolerance):
            dx = x2 - x1
            dy = y2 - y1
            length = (dx * dx + dy * dy) ** 0.5
            if length == 0:
                return False
            u = ((px - x1) * dx + (py - y1) * dy) / (length * length)
            if u < 0 or u > 1:
                return False
            xx = x1 + u * dx
            yy = y1 + u * dy
            distance = ((px - xx) ** 2 + (py - yy) ** 2) ** 0.5
            return distance <= tolerance

        if self.path:
            for i in range(len(self.path) - 1):
                x1, y1 = self.path[i]
                x2, y2 = self.path[i + 1]
                if point_on_line(x, y, x1 * self.grid_size, y1 * self.grid_size, x2 * self.grid_size, y2 * self.grid_size, tolerance):
                    return True
        return False

    """
    def to_dict1(self):
        return {
            "name": self.text,
            "start_point": self.start_point,
            "end_point": self.end_point,
            "wire_type": self.wire_type,
            "grid_size": self.grid_size,
            "start_block": self.start_block.to_dict() if self.start_block else None,
            "end_block": self.end_block.to_dict() if self.end_block else None,
            "start_pin": self.start_pin.to_dict() if self.start_pin else None,
            "end_pin": self.end_pin.to_dict() if self.end_pin else None,
        }

    @staticmethod
    def from_dict1(wire_dict, Block, Pin, parent_window):
        start_block = Block.from_dict(wire_dict["start_block"], parent_window) if wire_dict["start_block"] else None
        end_block = Block.from_dict(wire_dict["end_block"], parent_window) if wire_dict["end_block"] else None
        start_pin = Pin.from_dict(wire_dict["start_pin"], parent_window) if wire_dict["start_pin"] else None
        end_pin = Pin.from_dict(wire_dict["end_pin"], parent_window) if wire_dict["end_pin"] else None
        return Wire(wire_dict["name"], wire_dict["start_point"], wire_dict["end_point"], wire_dict["wire_type"], wire_dict["grid_size"], parent_window, start_block, end_block, start_pin, end_pin)
    """


    
    def to_dict(self):
        return {
            "id": self.id,  # Include the ID in the JSON
            "name": self.text,
            "start_point": self.start_point,
            "end_point": self.end_point,
            "wire_type": self.wire_type,
            "grid_size": self.grid_size,
        }

    @staticmethod
    def from_dict(wire_dict, parent_window):
        wire = Wire(
            wire_dict["name"],
            wire_dict["start_point"],
            wire_dict["end_point"],
            wire_dict["wire_type"],
            wire_dict["grid_size"],
            parent_window
        )
        wire.id = wire_dict.get("id", f"wire_{str(uuid.uuid4().int)[:10]}")  # Ensure the ID is set
        return wire
