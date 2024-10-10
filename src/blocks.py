#!/usr/bin/env python3
import cairo
import math
from datetime import datetime
from wire import Wire

class Block:
    def __init__(self, x, y, width, height, text, block_type, grid_size, parent_window=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.block_type = block_type
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.grid_size = grid_size
        self.border_color = (0, 0, 0)  # Default border color (black)
        self.fill_color = (0.8, 0.8, 0.8)  # Default fill color (light gray)
        self.text_color = (0, 0, 0)  # Default text color (black)
        self.rotation = 0  # Initial rotation angle in degrees
        self.selected = False  # Attribute to track selection state
        self.input_points = []
        self.output_points = []
        self.timestamp = datetime.now().isoformat(' ', 'seconds')
        self.input_connections = {}  # Dictionary to track input connections
        self.output_connections = {}  # Dictionary to track output connections
        self.selected = False  # Attribute to track selection state
        self.input_names = []
        self.output_names = []
        self.parent_window = parent_window  # Add the parent_window attribute
        self.update_points()

    def update_points(self):
        if self.block_type == "NOT":
            self.input_points = [self.rotate_point(self.x + self.width/2, self.y)]
            self.output_points = [self.rotate_point(self.x + self.width/2, self.y + self.height)]
            self.input_names = ["IN1"]
            self.output_names = ["OUT1"]
        elif self.block_type in ["AND", "NAND", "OR", "NOR", "XOR", "XNOR"]:
            self.input_points = [self.rotate_point(self.x, self.y), self.rotate_point(self.x + self.width, self.y)]
            self.output_points = [self.rotate_point(self.x + self.width/2, self.y + self.height)]
            self.input_names = ["IN1", "IN2"]
            self.output_names = ["OUT1"]
        # Initialize connections for new points
        #self.input_connections = {point: None for point in self.input_points}
        #self.output_connections = {point: None for point in self.output_points}

        # Print all points in input and output connections
        print(f"Input Points: {self.input_points}")
        print(f"Output Points: {self.output_points}")
        #print(f"Input Connections: {self.input_connections}")
        #print(f"Output Connections: {self.output_connections}")
    
    def rotate_point(self, x, y):
        # Rotate the point around the center of the block
        cx, cy = self.x + self.width / 2, self.y + self.height / 2
        angle = math.radians(self.rotation)
        dx, dy = x - cx, y - cy
        new_x = cx + dx * math.cos(angle) - dy * math.sin(angle)
        new_y = cy + dx * math.sin(angle) + dy * math.cos(angle)
        return (new_x, new_y)

    def draw(self, cr):
        cr.save()
        cr.translate(self.x + self.width / 2, self.y + self.height / 2)
        cr.rotate(math.radians(self.rotation))
        cr.translate(-self.width / 2, -self.height / 2)
        if self.block_type == "NOT":
            self.draw_not_block(cr)
        elif self.block_type == "AND":
            self.draw_and_block(cr)
        elif self.block_type == "NAND":
            self.draw_nand_block(cr)
        elif self.block_type == "OR":
            self.draw_or_block(cr)
        elif self.block_type == "NOR":
            self.draw_nor_block(cr)
        elif self.block_type == "XOR":
            self.draw_xor_block(cr)
        elif self.block_type == "XNOR":
            self.draw_xnor_block(cr)
        else:
            self.draw_default_block(cr)
        cr.stroke()

        # Draw input and output points
        cr.set_source_rgb(0, 0.6, 0)  # Green color for points
        for point in self.input_points + self.output_points:
            cr.arc(point[0], point[1], 4, 0, 2 * math.pi)
            #cr.stroke()
            cr.fill()

        # Draw input and output points
        cr.set_source_rgb(0, 0.6, 0)  # Green color for points
        for point in self.input_points:
          for name in self.input_names:
            cr.set_source_rgb(*self.text_color)
            cr.set_font_size(8)
            cr.move_to(point[0]+5, point[1] - 10)
            cr.show_text(name)
            cr.stroke()

        # Draw input and output points
        cr.set_source_rgb(0, 0.6, 0)  # Green color for points
        for point in self.output_points:
          for name in self.output_names:
            cr.set_source_rgb(*self.text_color)
            cr.set_font_size(8)
            cr.move_to(point[0]+5, point[1] + 10)
            cr.show_text(name)
            cr.stroke()

        cr.restore()

    def draw_default_block(self, cr):
        # Set fill color based on selection state
        fill_color = (1, 1, 0) if self.selected else self.fill_color

        cr.set_source_rgb(*fill_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()

        cr.set_source_rgb(*self.border_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

        cr.set_source_rgb(*self.text_color)
        cr.set_font_size(10)  # Reduced font size
        cr.move_to(10, 20)
        cr.show_text(self.text)

    def draw_not_gate(self, cr, x_offset, y_offset, scale):
        # Set line width and color
        cr.set_line_width(2)
        cr.set_source_rgb(*self.border_color)

        # Define the vertices of the isosceles triangle
        base_length = 40 * scale
        height = 30 * scale

        # Calculate the coordinates of the vertices
        x1 = x_offset
        y1 = y_offset
        x2 = x_offset + base_length
        y2 = y_offset
        x3 = x_offset + base_length / 2
        y3 = y_offset + height

        # Draw the triangle
        cr.move_to(x1, y1)
        cr.line_to(x2, y2)
        cr.line_to(x3, y3)
        cr.close_path()
        cr.stroke()

        # Fill the triangle
        cr.set_source_rgb(*self.fill_color)
        cr.move_to(x1, y1)
        cr.line_to(x2, y2)
        cr.line_to(x3, y3)
        cr.close_path()
        cr.fill()

        # Draw the small circle for NOT
        cr.set_source_rgb(*self.border_color)
        cr.arc(x_offset + 20 * scale, y_offset + 35 * scale, 5 * scale, 0, 2 * 3.14159)
        cr.stroke()

        # Add input and output points
        self.input_points = [(20, -0)]
        self.output_points = [(20, self.height+0)]

    def draw_not_block(self, cr):
        # Set fill color based on selection state
        fill_color = (1, 1, 0) if self.selected else self.fill_color

        cr.set_source_rgb(*fill_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()

        cr.set_source_rgb(*self.border_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

        self.draw_not_gate(cr, 15, 13, 0.3)
        cr.set_source_rgb(*self.text_color)
        cr.set_font_size(8)  # Reduced font size
        cr.move_to(10, 10)
        cr.show_text(self.text)

    def draw_and_gate(self, cr, x_offset, y_offset, scale):
        # Set line width and color
        cr.set_line_width(2)
        cr.set_source_rgb(*self.border_color)

        # Draw the image
        cr.move_to(x_offset, y_offset)
        cr.curve_to(
        1 * scale + x_offset,
        50 * scale + y_offset,
        39 * scale + x_offset,
        50 * scale + y_offset,
        40 * scale + x_offset,
        0 * scale + y_offset
        )
        cr.line_to(0 * scale + x_offset, 0 * scale + y_offset)
        cr.stroke()

        # Fill the NAND gate shape
        cr.set_source_rgb(*self.fill_color)
        cr.move_to(x_offset, y_offset)
        cr.curve_to(
        1 * scale + x_offset,
        50 * scale + y_offset,
        39 * scale + x_offset,
        50 * scale + y_offset,
        40 * scale + x_offset,
        0 * scale + y_offset
        )
        cr.line_to(0 * scale + x_offset, 0 * scale + y_offset)
        cr.fill()

        # Draw the text
        #cr.set_source_rgb(*self.text_color)
        #cr.set_font_size(10 * scale)  # Reduced font size
        #cr.move_to(8 * scale + x_offset, 20 * scale + y_offset)
        #cr.show_text(self.text)
        #cr.stroke()

        # Add input and output points
        self.input_points = [(0, 0),(self.width,0)]
        self.output_points = [(self.width/2, self.height)]

    def draw_and_block(self, cr):
        # Set fill color based on selection state
        fill_color = (1, 1, 0) if self.selected else self.fill_color

        cr.set_source_rgb(*fill_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()

        cr.set_source_rgb(*self.border_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

        self.draw_and_gate(cr, 15, 15, 0.3)
        cr.set_source_rgb(*self.text_color)
        cr.set_font_size(8)  # Reduced font size
        cr.move_to(10, 10)
        cr.show_text(self.text)

    def draw_nand_gate(self, cr, x_offset, y_offset, scale):
        # Set line width and color
        cr.set_line_width(2)
        cr.set_source_rgb(*self.border_color)

        # Draw the image
        cr.move_to(x_offset, y_offset)
        cr.curve_to(
        1 * scale + x_offset,
        50 * scale + y_offset,
        39 * scale + x_offset,
        50 * scale + y_offset,
        40 * scale + x_offset,
        0 * scale + y_offset
        )
        cr.line_to(0 * scale + x_offset, 0 * scale + y_offset)
        cr.stroke()

        # Draw the small circle for NOT
        cr.set_source_rgb(*self.border_color)
        cr.arc(x_offset + 20 * scale, y_offset + 45 * scale, 5 * scale, 0, 2 * 3.14159)
        cr.stroke()

        # Fill the NAND gate shape
        cr.set_source_rgb(*self.fill_color)
        cr.move_to(x_offset, y_offset)
        cr.curve_to(
        1 * scale + x_offset,
        50 * scale + y_offset,
        39 * scale + x_offset,
        50 * scale + y_offset,
        40 * scale + x_offset,
        0 * scale + y_offset
        )
        cr.line_to(0 * scale + x_offset, 0 * scale + y_offset)
        cr.fill()

        # Add input and output points
        self.input_points = [(0, 0),(self.width,0)]
        self.output_points = [(self.width/2, self.height)]

        # Draw the text
        #cr.set_source_rgb(*self.text_color)
        #cr.set_font_size(10 * scale)  # Reduced font size
        #cr.move_to(8 * scale + x_offset, 20 * scale + y_offset)
        #cr.show_text(self.text)
        #cr.stroke()

    def draw_nand_block(self, cr):
        # Set fill color based on selection state
        fill_color = (1, 1, 0) if self.selected else self.fill_color

        cr.set_source_rgb(*fill_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()

        cr.set_source_rgb(*self.border_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

        self.draw_nand_gate(cr, 15, 15, 0.3)
        cr.set_source_rgb(*self.text_color)
        cr.set_font_size(8)  # Reduced font size
        cr.move_to(10, 10)
        cr.show_text(self.text)

    def draw_or_gate(self, cr, x_offset, y_offset, scale):
        # Set line width and color
        cr.set_line_width(1)
        cr.set_source_rgb(*self.fill_color)

        # Draw the first curve
        cr.move_to(x_offset, y_offset)
        cr.curve_to(
        10 * scale + x_offset,
        50 * scale + y_offset,
        30 * scale + x_offset,
        50 * scale + y_offset,
        40 * scale + x_offset,
        0 * scale + y_offset
        )

        # Draw the second curve parallel to the first curve
        cr.curve_to(
        30 * scale + x_offset,
        20 * scale + y_offset,
        10 * scale + x_offset,
        20 * scale + y_offset,
        x_offset,
        y_offset
        )

        # Close the path to create a filled area
        cr.close_path()

        # Fill the area between the two curves
        cr.fill()

        # Draw the border of the XNOR gate
        cr.set_source_rgb(*self.border_color)
        cr.move_to(x_offset, y_offset)
        cr.curve_to(
        10 * scale + x_offset,
        50 * scale + y_offset,
        30 * scale + x_offset,
        50 * scale + y_offset,
        40 * scale + x_offset,
        0 * scale + y_offset
        )
        cr.curve_to(
        30 * scale + x_offset,
        20 * scale + y_offset,
        10 * scale + x_offset,
        20 * scale + y_offset,
        x_offset,
        y_offset
        )
        cr.close_path()
        cr.stroke()

        # Add input and output points
        self.input_points = [(0, 0),(self.width,0)]
        self.output_points = [(self.width/2, self.height)]

        # Draw the text
        #cr.set_source_rgb(*self.text_color)
        #cr.set_font_size(8 * scale)  # Reduced font size
        #cr.move_to(x_offset + 8 * scale, y_offset + 25 * scale)
        #cr.show_text(self.text)
        #cr.stroke()

    def draw_or_block(self, cr):
        # Set fill color based on selection state
        fill_color = (1, 1, 0) if self.selected else self.fill_color

        cr.set_source_rgb(*fill_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()

        cr.set_source_rgb(*self.border_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

        self.draw_or_gate(cr, 15, 15, 0.3)
        cr.set_source_rgb(*self.text_color)
        cr.set_font_size(8)  # Reduced font size
        cr.move_to(10, 10)
        cr.show_text(self.text)

    def draw_nor_gate(self, cr, x_offset, y_offset, scale):
        # Set line width and color
        cr.set_line_width(1)
        cr.set_source_rgb(*self.fill_color)

        # Draw the first curve
        cr.move_to(x_offset, y_offset)
        cr.curve_to(
        10 * scale + x_offset,
        50 * scale + y_offset,
        30 * scale + x_offset,
        50 * scale + y_offset,
        40 * scale + x_offset,
        0 * scale + y_offset
        )

        # Draw the second curve parallel to the first curve
        cr.curve_to(
        30 * scale + x_offset,
        20 * scale + y_offset,
        10 * scale + x_offset,
        20 * scale + y_offset,
        x_offset,
        y_offset
        )

        # Close the path to create a filled area
        cr.close_path()

        # Fill the area between the two curves
        cr.fill()

        # Draw the border of the XNOR gate
        cr.set_source_rgb(*self.border_color)
        cr.move_to(x_offset, y_offset)
        cr.curve_to(
        10 * scale + x_offset,
        50 * scale + y_offset,
        30 * scale + x_offset,
        50 * scale + y_offset,
        40 * scale + x_offset,
        0 * scale + y_offset
        )
        cr.curve_to(
        30 * scale + x_offset,
        20 * scale + y_offset,
        10 * scale + x_offset,
        20 * scale + y_offset,
        x_offset,
        y_offset
        )
        cr.close_path()
        cr.stroke()

       # Draw the small circle for NOT
        cr.set_source_rgb(*self.border_color)
        cr.arc(x_offset + 20 * scale, y_offset + 43 * scale, 5 * scale, 0, 2 * 3.14159)
        cr.stroke()

        # Add input and output points
        self.input_points = [(0, 0),(self.width,0)]
        self.output_points = [(self.width/2, self.height)]

        # Draw the text
        #cr.set_source_rgb(*self.text_color)
        #cr.set_font_size(8 * scale)  # Reduced font size
        #cr.move_to(x_offset + 8 * scale, y_offset + 25 * scale)
        #cr.show_text(self.text)
        #cr.stroke()

    def draw_nor_block(self, cr):
        # Set fill color based on selection state
        fill_color = (1, 1, 0) if self.selected else self.fill_color

        cr.set_source_rgb(*fill_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()

        cr.set_source_rgb(*self.border_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

        self.draw_nor_gate(cr, 15, 15, 0.3)
        cr.set_source_rgb(*self.text_color)
        cr.set_font_size(8)  # Reduced font size
        cr.move_to(10, 10)
        cr.show_text(self.text)

    def draw_xor_gate(self, cr, x_offset, y_offset, scale):
        # Set line width and color
        cr.set_line_width(1)
        cr.set_source_rgb(*self.fill_color)

        # Draw the first curve
        cr.move_to(x_offset, y_offset)
        cr.curve_to(
        10 * scale + x_offset,
        50 * scale + y_offset,
        30 * scale + x_offset,
        50 * scale + y_offset,
        40 * scale + x_offset,
        0 * scale + y_offset
        )

        # Draw the second curve parallel to the first curve
        cr.curve_to(
        30 * scale + x_offset,
        20 * scale + y_offset,
        10 * scale + x_offset,
        20 * scale + y_offset,
        x_offset,
        y_offset
        )

        # Close the path to create a filled area
        cr.close_path()

        # Fill the area between the two curves
        cr.fill()

        # Draw the border of the XOR gate
        cr.set_source_rgb(*self.border_color)
        cr.move_to(x_offset, y_offset)
        cr.curve_to(
        10 * scale + x_offset,
        50 * scale + y_offset,
        30 * scale + x_offset,
        50 * scale + y_offset,
        40 * scale + x_offset,
        0 * scale + y_offset
        )
        cr.curve_to(
        30 * scale + x_offset,
        20 * scale + y_offset,
        10 * scale + x_offset,
        20 * scale + y_offset,
        x_offset,
        y_offset
        )
        cr.close_path()
        cr.stroke()

        # Draw the second curve for the border
        cr.set_source_rgb(*self.border_color)
        cr.move_to(x_offset, y_offset - 10 * scale)
        cr.curve_to(
        10 * scale + x_offset,
        18 * scale + y_offset,
        30 * scale + x_offset,
        18 * scale + y_offset,
        40 * scale + x_offset,
        -10 * scale + y_offset
        )
        cr.stroke()

        # Add input and output points
        self.input_points = [(0,0),(self.width,0)]
        self.output_points = [(self.width/2, self.height)]

        # Draw the text
        #cr.set_source_rgb(*self.text_color)
        #cr.set_font_size(8 * scale)  # Reduced font size
        #cr.move_to(x_offset + 8 * scale, y_offset + 25 * scale)
        #cr.show_text(self.text)
        #cr.stroke()

    def draw_xor_block(self, cr):
        # Set fill color based on selection state
        fill_color = (1, 1, 0) if self.selected else self.fill_color

        cr.set_source_rgb(*fill_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()

        cr.set_source_rgb(*self.border_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

        self.draw_xor_gate(cr, 15, 15, 0.3)
        cr.set_source_rgb(*self.text_color)
        cr.set_font_size(8)  # Reduced font size
        cr.move_to(10, 10)
        cr.show_text(self.text)

    def draw_xnor_gate(self, cr, x_offset, y_offset, scale):
        # Set line width and color
        cr.set_line_width(1)
        cr.set_source_rgb(*self.fill_color)

        # Draw the first curve
        cr.move_to(x_offset, y_offset)
        cr.curve_to(
        10 * scale + x_offset,
        50 * scale + y_offset,
        30 * scale + x_offset,
        50 * scale + y_offset,
        40 * scale + x_offset,
        0 * scale + y_offset
        )

        # Draw the second curve parallel to the first curve
        cr.curve_to(
        30 * scale + x_offset,
        20 * scale + y_offset,
        10 * scale + x_offset,
        20 * scale + y_offset,
        x_offset,
        y_offset
        )

        # Close the path to create a filled area
        cr.close_path()

        # Fill the area between the two curves
        cr.fill()

        # Draw the border of the XNOR gate
        cr.set_source_rgb(*self.border_color)
        cr.move_to(x_offset, y_offset)
        cr.curve_to(
        10 * scale + x_offset,
        50 * scale + y_offset,
        30 * scale + x_offset,
        50 * scale + y_offset,
        40 * scale + x_offset,
        0 * scale + y_offset
        )
        cr.curve_to(
        30 * scale + x_offset,
        20 * scale + y_offset,
        10 * scale + x_offset,
        20 * scale + y_offset,
        x_offset,
        y_offset
        )
        cr.close_path()
        cr.stroke()

        # Draw the second curve for the border
        cr.set_source_rgb(*self.border_color)
        cr.move_to(x_offset, y_offset - 10 * scale)
        cr.curve_to(
        10 * scale + x_offset,
        18 * scale + y_offset,
        30 * scale + x_offset,
        18 * scale + y_offset,
        40 * scale + x_offset,
        -10 * scale + y_offset
        )
        cr.stroke()

        # Draw the small circle for NOT
        cr.set_source_rgb(*self.border_color)
        cr.arc(x_offset + 20 * scale, y_offset + 43 * scale, 5 * scale, 0, 2 * 3.14159)
        cr.stroke()

        # Add input and output points
        self.input_points = [(0,0),(self.width,0)]
        self.output_points = [(self.width/2, self.height)]

        # Draw the text
        #cr.set_source_rgb(*self.text_color)
        #cr.set_font_size(8 * scale)  # Reduced font size
        #cr.move_to(x_offset + 8 * scale, y_offset + 25 * scale)
        #cr.show_text(self.text)
        #cr.stroke()

    def draw_xnor_block(self, cr):
        # Set fill color based on selection state
        fill_color = (1, 1, 0) if self.selected else self.fill_color

        cr.set_source_rgb(*fill_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()

        cr.set_source_rgb(*self.border_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

        self.draw_xnor_gate(cr, 15, 15, 0.3)
        cr.set_source_rgb(*self.text_color)
        cr.set_font_size(8)  # Reduced font size
        cr.move_to(10, 10)
        cr.show_text(self.text)

    def draw_text(self, cr, text, x, y):
        cr.set_source_rgb(*self.text_color)
        cr.set_font_size(8)  # Reduced font size
        cr.move_to(x, y)
        cr.show_text(text)

    def contains_point(self, x, y):
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)

    def contains_pin(self, x, y):
        self.update_points()
        for point in self.input_points + self.output_points:
            if (point[0] - 10 <= int(x) <= point[0] + 10 and
               point[1] - 10 <= int(y) <= point[1] + 10):
               #print(f'=================== block contains pin {x},{y},{point[0]},{point[1]} =================')
               return point
        #print(f'**DOES NOT contains pin {x},{y},{point[0]},{point[1]}**')
        return None


    def start_drag(self, x, y):
        self.dragging = True
        self.offset_x = x - self.x
        self.offset_y = y - self.y

    def drag(self, x, y, max_x, max_y):
        if self.dragging:
            new_x = x - self.offset_x
            new_y = y - self.offset_y
            if new_x >= 0 and new_x + self.width <= max_x:
                self.x = new_x
            if new_y >= 0 and new_y + self.height <= max_y:
                self.y = new_y
            self.update_points()

    def end_drag(self):
        self.dragging = False
        self.x = round(self.x / self.grid_size) * self.grid_size
        self.y = round(self.y / self.grid_size) * self.grid_size
        self.width = round(self.width / self.grid_size) * self.grid_size
        self.height = round(self.height / self.grid_size) * self.grid_size
        self.update_points()
        self.update_wire_connections()
        print(f"Block {self.text} end drag at ({self.x}, {self.y})")

    def update_start_block_coordinates(connections, text, new_x, new_y):
        for point, wire_details in connections.items():
            if wire_details['start_block']['text'] == text:
                wire_details['start_block']['x'] = new_x
                wire_details['start_block']['y'] = new_y
    
    def update_end_block_coordinates(connections, text, new_x, new_y):
        for point, wire_details in connections.items():
            if wire_details['end_block']['text'] == text:
                wire_details['end_block']['x'] = new_x
                wire_details['end_block']['y'] = new_y

    def extract_wire_details(self,wire):
        return {
            'text': wire.text,
            'start_point': wire.start_point,
            'end_point': wire.end_point,
            'grid_size': wire.grid_size,
            'parent_window': wire.parent_window,
            'path': wire.path,
            'start_block': {
                'x': wire.start_block.x if wire.start_block else None,
                'y': wire.start_block.y if wire.start_block else None,
                'width': wire.start_block.width if wire.start_block else None,
                'height': wire.start_block.height if wire.start_block else None,
                'text': wire.start_block.text if wire.start_block else None,
                'block_type': wire.start_block.block_type if wire.start_block else None,
                # Add other relevant attributes as needed
            },
            'end_block': {
                'x': wire.end_block.x if wire.end_block else None,
                'y': wire.end_block.y if wire.end_block else None,
                'width': wire.end_block.width if wire.end_block else None,
                'height': wire.end_block.height if wire.end_block else None,
                'text': wire.end_block.text if wire.end_block else None,
                'block_type': wire.end_block.block_type if wire.end_block else None,
                # Add other relevant attributes as needed
            },
            'start_pin': {
                'x': wire.start_pin.x if wire.start_pin else None,
                'y': wire.start_pin.y if wire.start_pin else None,
                'width': wire.start_pin.width if wire.start_pin else None,
                'height': wire.start_pin.height if wire.start_pin else None,
                'text': wire.start_pin.text if wire.start_pin else None,
                'pin_type': wire.start_pin.pin_type if wire.start_pin else None,
                # Add other relevant attributes as needed
            },
            'end_pin': {
                'x': wire.end_pin.x if wire.end_pin else None,
                'y': wire.end_pin.y if wire.end_pin else None,
                'width': wire.end_pin.width if wire.end_pin else None,
                'height': wire.end_pin.height if wire.end_pin else None,
                'text': wire.end_pin.text if wire.end_pin else None,
                'pin_type': wire.end_pin.pin_type if wire.end_pin else None,
                # Add other relevant attributes as needed
            }
        }



    def update_wire_connections(self):
        for point, wire in self.output_connections.items():
            if wire is not None:
                wire.start_block = self
                wire.update_start_point(point)
        for point, wire in self.input_connections.items():
            if wire is not None:
                wire.end_block = self
                wire.update_end_point(point)

    def rotate(self, angle):
        self.rotation = (self.rotation + angle) % 360
        self.update_points()

    def connect_wire(self, start_point, end_point):
        print(f"Connecting wire from {start_point} to {end_point}")
        if start_point in self.input_points:
            self.input_connections[start_point] = end_point
        if start_point in self.output_points:
            self.output_connections[start_point] = end_point
        if end_point in self.input_points:
            self.input_connections[end_point] = start_point
        if end_point in self.output_points:
            self.output_connections[end_point] = start_point
        #print(f"Updated connections: {self.input_connections}, {self.output_connections}")
        updated_output_connections = {k: (v.text, v.start_point, v.end_point, v.grid_size) for k, v in self.output_connections.items()}
        updated_input_connections = {k: (v.text, v.start_point, v.end_point, v.grid_size) for k, v in self.input_connections.items()}
        #print(f"Updated output connections: {updated_output_connections}")
        #print(f"Updated input connections: {updated_input_connections}")

    def to_dict(self):
        #input_connections_dict = {str(k): v for k, v in self.input_connections.items()}
        #output_connections_dict = {str(k): v for k, v in self.output_connections.items()}
        input_connections_dict = {str(k): (v.to_dict() if v is not None else None) for k, v in self.input_connections.items()}
        output_connections_dict = {str(k): (v.to_dict() if v is not None else None) for k, v in self.output_connections.items()}
        return {
        "name": self.text,
        "block_type": self.block_type,
        "x": self.x,
        "y": self.y,
        "width": self.width,
        "height": self.height,
        "rotation": self.rotation,
        "input_points": self.input_points,
        "output_points": self.output_points,
        "border_color": self.border_color,
        "fill_color": self.fill_color,
        "text_color": self.text_color,
        "timestamp": self.timestamp,
        "input_connections": input_connections_dict,  # Include connections in the JSON
        "output_connections": output_connections_dict,  # Include connections in the JSON
        "input_names": self.input_names,
        "output_names": self.output_names,
        "grid_size": self.grid_size  # Include grid_size in the JSON
        }

    @classmethod
    def from_dict(cls, data, parent_window):
        block = cls(
        data["x"],
        data["y"],
        data["width"],
        data["height"],
        data["name"],
        data["block_type"],
        data["grid_size"],
        parent_window  # Pass the parent_window attribute
        )
        block.border_color = tuple(data["border_color"])
        block.fill_color = tuple(data["fill_color"])
        block.text_color = tuple(data["text_color"])
        block.rotation = data["rotation"]
        #block.input_connections = {eval(k): v for k, v in data["input_connections"].items()}
        #block.output_connections = {eval(k): v for k, v in data["output_connections"].items()}
        block.input_connections = {eval(k): (Wire.from_dict(v, block.parent_window) if v is not None else None) for k, v in data["input_connections"].items()}
        block.output_connections = {eval(k): (Wire.from_dict(v, block.parent_window) if v is not None else None) for k, v in data["output_connections"].items()}
        block.input_names = data["input_names"]
        block.output_names = data["output_names"]
        return block

