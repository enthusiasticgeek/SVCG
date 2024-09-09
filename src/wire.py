#!/usr/bin/env python3
import cairo
import math

class Wire:
    def __init__(self, start_point, end_point, grid_size):
        self.start_point = start_point
        self.end_point = end_point
        self.grid_size = grid_size

    def draw(self, cr):
        #print(f"Drawing wire: start_point={self.start_point}, end_point={self.end_point}")
        cr.set_source_rgb(0, 0, 0)  # Black color for wires
        cr.set_line_width(2)
        cr.move_to(self.start_point[0], self.start_point[1])
        cr.line_to(self.end_point[0], self.start_point[1])
        cr.line_to(self.end_point[0], self.end_point[1])
        cr.stroke()

    def to_dict(self):
        return {
            "start_point": self.start_point,
            "end_point": self.end_point,
            "grid_size": self.grid_size
        }

    @staticmethod
    def from_dict(wire_dict):
        return Wire(wire_dict["start_point"], wire_dict["end_point"], wire_dict["grid_size"])
