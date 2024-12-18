#!/usr/bin/env python3
import cairo
import math
import pprint
import uuid
from datetime import datetime
from wire import Wire

class Block:
    def __init__(self, x, y, width, height, text, block_type, grid_size, parent_window=None):
        self.id = f"block_{str(uuid.uuid4().int)[:10]}"  # Generate a unique 10-digit ID
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
        self.prev_input_points = []
        self.prev_output_points = []
        self.timestamp = datetime.now().isoformat(' ', 'seconds')
        #self.input_connections = []  # List of dictionaries to track input connections
        #self.output_connections = []  # List of dictionaries to track output connections
        self.input_names = []
        self.output_names = []
        #self.input_wires = []  # List to store wire IDs for input points
        #self.output_wires = []  # List to store wire IDs for output points
        self.input_wires = [[] for _ in self.input_points]  # List to store wire IDs for input points
        self.output_wires = [[] for _ in self.output_points]  # List to store wire IDs for output points
        self.parent_window = parent_window  # Add the parent_window attribute
        self.update_points()
        self.init_wires()

    def print_wires(self):
        self.print_input_wires()
        self.print_output_wires()

    def print_input_wires(self):
        for index, wire_list in enumerate(self.input_wires):
            print(f"Wires at pin {index}: {wire_list}")

    def print_output_wires(self):
        for index, wire_list in enumerate(self.output_wires):
            print(f"Wires at pin {index}: {wire_list}")

    def get_wires(self):
        return self.input_wires + self.output_wires

    def get_input_wires(self):
        return self.input_wires

    def get_output_wires(self):
        return self.output_wires

    def clear_wires(self):
        self.input_wires = [[] for _ in self.input_points]
        self.output_wires = [[] for _ in self.output_points]


    def prev_connections(self):
        return self.prev_input_points + self.prev_output_points

    def prev_input_connections(self):
        return self.prev_input_points

    def prev_output_connections(self):
        return self.prev_output_points

    def connections(self):
        return self.input_points + self.output_points

    def input_connections(self):
        return self.input_points

    def output_connections(self):
        return self.output_points

    def init_wires(self):
        if self.block_type == "NOT":
            self.input_wires = [[]]  # Initialize wires list for input points
            self.output_wires = [[]]  # Initialize wires list for output points
        elif self.block_type in ["AND", "NAND", "OR", "NOR", "XOR", "XNOR"]:
            self.input_wires = [[], []]  # Initialize wires list for input points
            self.output_wires = [[]]  # Initialize wires list for output points
        elif self.block_type in ["JKFF", "SRFF"]:
            self.input_wires = [[], [], [], [], []]  # Initialize wires list for input points
            self.output_wires = [[], []]  # Initialize wires list for output points
        elif self.block_type in ["DFF", "TFF"]:
            self.input_wires = [[], [], [], []]  # Initialize wires list for input points
            self.output_wires = [[], []]  # Initialize wires list for output points
        elif self.block_type in ["MUX_2X1"]:
            self.input_wires = [[], [], []]  # Initialize wires list for input points
            self.output_wires = [[]]  # Initialize wires list for output points
        elif self.block_type in ["MUX_4X1"]:
            self.input_wires = [[], [], [], [], [], []]  # Initialize wires list for input points
            self.output_wires = [[]]  # Initialize wires list for output points



    def set_selected(self, selected):
        self.selected = selected

    def update_points(self):
        if self.block_type == "NOT":
            self.input_points = [self.rotate_point(int(self.x + self.width/2), int(self.y))]
            self.output_points = [self.rotate_point(int(self.x + self.width/2), int(self.y + self.height))]
            self.input_names = ["IN1"]
            self.output_names = ["OUT1"]
        elif self.block_type in ["AND", "NAND", "OR", "NOR", "XOR", "XNOR"]:
            self.input_points = [self.rotate_point(int(self.x), int(self.y)), self.rotate_point(int(self.x + self.width), int(self.y))]
            self.output_points = [self.rotate_point(int(self.x + self.width/2), int(self.y + self.height))]
            self.input_names = ["IN1", "IN2"]
            self.output_names = ["OUT1"]
        elif self.block_type in ["JKFF", "SRFF"]:
            self.input_points = [self.rotate_point(int(self.x), int(self.y)), self.rotate_point(int(self.x + self.width/2), int(self.y)), self.rotate_point(int(self.x + self.width), int(self.y)), \
                                 self.rotate_point(int(self.x), int(self.y + self.height/2)), self.rotate_point(int(self.x + self.width), int(self.y + self.height/2))] 
            self.output_points = [self.rotate_point(int(self.x), int(self.y + self.height)), self.rotate_point(int(self.x + self.width), int(self.y + self.height))]
            if self.block_type in ["JKFF"]:
               self.input_names = ["J","CLK","K", "PRE", "CLR"]
               self.output_names = ["Q","Q'"]
            elif self.block_type in ["SRFF"]:
               self.input_names = ["S","CLK","R", "PRE", "CLR"]
               self.output_names = ["Q","Q'"]
        elif self.block_type in ["DFF", "TFF"]:
            self.input_points = [self.rotate_point(int(self.x), int(self.y)), self.rotate_point(int(self.x + self.width), int(self.y)), \
                                 self.rotate_point(int(self.x), int(self.y + self.height/2)), self.rotate_point(int(self.x + self.width), int(self.y + self.height/2))] 
            self.output_points = [self.rotate_point(int(self.x), int(self.y + self.height)), self.rotate_point(int(self.x + self.width), int(self.y + self.height))]
            if self.block_type in ["DFF"]:
               self.input_names = ["D","CLK", "PRE", "CLR"]
               self.output_names = ["Q","Q'"]
            elif self.block_type in ["TFF"]:
               self.input_names = ["T","CLK", "PRE", "CLR"]
               self.output_names = ["Q","Q'"]
        elif self.block_type in ["MUX_2X1"]:
            self.input_points = [self.rotate_point(int(self.x), int(self.y + self.height/2)), self.rotate_point(int(self.x), int(self.y + 3*self.height/2)), self.rotate_point(int(self.x + 1*self.width), int(self.y + 2*self.height))]
            self.output_points = [self.rotate_point(int(self.x + self.width*(1+1)), int(self.y + self.height))]
            self.input_names = ["I0","I1","S0"]
            self.output_names = ["O0"]
        elif self.block_type in ["MUX_4X1"]:
            #print("MUX_4x1")
            self.input_points = [self.rotate_point(int(self.x), int(self.y + self.height/2)), self.rotate_point(int(self.x), int(self.y + 3*self.height/2)), self.rotate_point(int(self.x), int(self.y + 5*self.height/2)), self.rotate_point(int(self.x), int(self.y + 7*self.height/2)), self.rotate_point(int(self.x + 1*self.width), int(self.y + 4*self.height)), self.rotate_point(int(self.x + 2*self.width), int(self.y + 4*self.height)) ]
            self.output_points = [self.rotate_point(int(self.x + self.width*(2+1)), int(self.y + 2*self.height))]
            self.input_names = ["I0","I1","I2","I3","S0","S1"]
            self.output_names = ["O0"]
                 
             
        # Initialize connections for new points
        #self.input_connections = {point: None for point in self.input_points}
        #self.output_connections = {point: None for point in self.output_points}

        # Print all points in input and output connections
        #print(f"Input Points: {self.input_points}")
        #print(f"Output Points: {self.output_points}")
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
        elif self.block_type == "JKFF" or self.block_type == "SRFF":
            self.draw_flipflop_block(cr)
        elif self.block_type == "DFF" or self.block_type == "TFF":
            self.draw_flipflop_block(cr)
        elif self.block_type == "MUX_2X1":
            self.draw_mux(cr, 2)
        elif self.block_type == "MUX_4X1":
            self.draw_mux(cr, 4)
        else:
            self.draw_default_block(cr)
        cr.stroke()
        cr.restore()

        
        cr.save()
        # Draw input and output points
        cr.set_source_rgb(0, 0.6, 0)  # Green color for points
        for point in self.input_points + self.output_points:
            cr.arc(point[0], point[1], 4, 0, 2 * math.pi)
            #cr.stroke()
            cr.fill()

        # Draw names text for input points
        cr.set_source_rgb(0, 0.6, 0)  # Green color for points
        for point, name in zip(self.input_points, self.input_names):
            cr.set_source_rgb(*self.text_color)
            cr.set_font_size(8)
            cr.move_to(point[0] + 5, point[1] - 10)
            cr.show_text(name)
            cr.stroke()
        
        # Draw names text for output points
        cr.set_source_rgb(0, 0.6, 0)  # Green color for points
        for point, name in zip(self.output_points, self.output_names):
            cr.set_source_rgb(*self.text_color)
            cr.set_font_size(8)
            cr.move_to(point[0] + 5, point[1] + 10)
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
        #self.input_points = [(self.width/2, 0)]
        #self.output_points = [(self.width/2, self.height)]

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
        #self.input_points = [(0, 0),(self.width,0)]
        #self.output_points = [(self.width/2, self.height)]

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
        #self.input_points = [(0, 0),(self.width,0)]
        #self.output_points = [(self.width/2, self.height)]

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
        #self.input_points = [(0, 0),(self.width,0)]
        #self.output_points = [(self.width/2, self.height)]

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
        #self.input_points = [(0, 0),(self.width,0)]
        #self.output_points = [(self.width/2, self.height)]

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
        #self.input_points = [(0,0),(self.width,0)]
        #self.output_points = [(self.width/2, self.height)]

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
        #self.input_points = [(0,0),(self.width,0)]
        #self.output_points = [(self.width/2, self.height)]

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

    def draw_flipflop_block(self, cr):
        # Set fill color based on selection state
        fill_color = (1, 1, 0) if self.selected else self.fill_color

        cr.set_source_rgb(*fill_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()

        cr.set_source_rgb(*self.border_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

        cr.set_source_rgb(*self.text_color)
        cr.set_font_size(8)  # Reduced font size
        cr.move_to(10, 10)
        cr.show_text(self.text)

    def draw_mux(self, cr, sel):
        mux = 2**sel
        # Set fill color based on selection state
        fill_color = (1, 1, 0) if self.selected else self.fill_color

        cr.set_source_rgb(*fill_color)
        cr.rectangle(0, 0, self.width*sel//2 + self.width, self.height*sel)
        cr.fill()

        cr.set_source_rgb(*self.border_color)
        cr.rectangle(0, 0, self.width*sel//2 + self.width, self.height*sel)
        cr.stroke()

        cr.set_source_rgb(*self.text_color)
        cr.set_font_size(8)  # Reduced font size
        cr.move_to(10, 10)
        cr.show_text(self.text)

        self.draw_trapezoid(cr, (self.width*sel//2 + self.width)//3, (self.height*sel)//3, self.width/2, self.width/40, self.height/4,90)

    def draw_trapezoid(self, cr, x, y, width, height1, height2, rotation_angle):
        # Save the current state
        cr.save()

        # Translate to the center of the trapezoid
        cr.translate(x + width / 2, y + (height1 + height2) / 2)

        # Rotate around the center
        cr.rotate(math.radians(rotation_angle))

        # Define the points of the trapezoid
        points = [
            (-width / 2, -(height1 + height2) / 2),
            (width / 2, -(height1 + height2) / 2),
            (width / 2 + (height2 - height1) / 2, (height2 - height1) / 2),
            (-width / 2 - (height2 - height1) / 2, (height2 - height1) / 2)
        ]

        # Move to the first point
        cr.move_to(*points[0])

        # Draw the lines
        for point in points[1:]:
            cr.line_to(*point)

        # Close the path
        cr.close_path()

        # Fill the trapezoid
        cr.set_source_rgb(*self.fill_color)
        cr.fill_preserve()

        # Stroke the border
        cr.set_source_rgb(*self.border_color)
        cr.stroke()

        # Restore the previous state
        cr.restore()


    def draw_text(self, cr, text, x, y):
        cr.set_source_rgb(*self.text_color)
        cr.set_font_size(8)  # Reduced font size
        cr.move_to(x, y)
        cr.show_text(text)

    def contains_point(self, x, y, tolerance = 10):
        return (self.x - tolerance <= int(x) <= self.x + self.width + tolerance and
                self.y - tolerance <= int(y) <= self.y + self.height + tolerance)

    def contains_pin(self, x, y, tolerance = 10):
        self.update_points()
        for point in self.input_points + self.output_points:
            if (point[0] - tolerance <= int(x) <= point[0] + tolerance and
               point[1] - tolerance <= int(y) <= point[1] + tolerance):
               #print(f'=================== block contains pin {x},{y},{point[0]},{point[1]} =================')
               return point
        #print(f'**DOES NOT contains pin {x},{y},{point[0]},{point[1]}**')
        return None

    def start_drag(self, x, y):
        self.dragging = True
        self.offset_x = x - self.x
        self.offset_y = y - self.y
        #print(f"start_drag {self.offset_x} and {self.offset_y}")
        self.prev_output_points = self.output_points.copy()
        self.prev_input_points = self.input_points.copy()

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
        # Update wire connections
        #self.parent_window.update_wires()
        #self.update_wire_connections()
        ## Update start and end block coordinates in wire connections
        #self.update_start_block_coordinates(self.output_connections, self.text, self.x, self.y)
        #self.update_end_block_coordinates(self.input_connections, self.text, self.x, self.y)


    """
    def update_start_block_coordinates(self, connections, text, new_x, new_y):
        for connection in connections:
            if connection['wire'] and connection['wire'].start_block and connection['wire'].start_block.text == text:
                print("here1")
                connection['wire'].start_block.x = new_x
                connection['wire'].start_block.y = new_y

    def update_end_block_coordinates(self, connections, text, new_x, new_y):
        for connection in connections:
            if connection['wire'] and connection['wire'].end_block and connection['wire'].end_block.text == text:
                print("here2")
                connection['wire'].end_block.x = new_x
                connection['wire'].end_block.y = new_y

    """
    def extract_wire_details(self, wire):
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


    def rotate(self, angle):
        self.rotation = (self.rotation + angle) % 360
        self.update_points()

    """
    def connect_wire(self, start_point, end_point):
        print(f"Connecting wire from {start_point} to {end_point}")
        print("Blocks ============")
        if start_point in self.input_points:
            self.input_connections.append({'point': start_point, 'wire': end_point})
        if start_point in self.output_points:
            self.output_connections.append({'point': start_point, 'wire': end_point})
        if end_point in self.input_points:
            self.input_connections.append({'point': end_point, 'wire': start_point})
        if end_point in self.output_points:
            self.output_connections.append({'point': end_point, 'wire': start_point})
        #print(f"Updated connections: {self.input_connections}, {self.output_connections}")
        updated_output_connections = {k: (v['wire'].text, v['wire'].start_point, v['wire'].end_point, v['wire'].grid_size) for k, v in enumerate(self.output_connections)}
        updated_input_connections = {k: (v['wire'].text, v['wire'].start_point, v['wire'].end_point, v['wire'].grid_size) for k, v in enumerate(self.input_connections)}
        print(f"Updated output connections: {updated_output_connections}")
        print(f"Updated input connections: {updated_input_connections}")

    """

    def to_dict(self):
        return {
            "id": self.id,  # Include the ID in the JSON
            "name": self.text,
            "block_type": self.block_type,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "rotation": self.rotation,
            "input_points": self.input_points,
            "output_points": self.output_points,
            "input_wires": self.input_wires,  # Include input wires in the JSON
            "output_wires": self.output_wires,  # Include output wires in the JSON
            "border_color": self.border_color,
            "fill_color": self.fill_color,
            "text_color": self.text_color,
            "timestamp": self.timestamp,
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
        block.id = data.get("id", f"block_{str(uuid.uuid4().int)[:10]}")  # Ensure the ID is set
        block.border_color = tuple(data["border_color"])
        block.fill_color = tuple(data["fill_color"])
        block.text_color = tuple(data["text_color"])
        block.rotation = data["rotation"]
        block.input_points = data["input_points"]
        block.output_points = data["output_points"]
        block.input_names = data["input_names"]
        block.output_names = data["output_names"]
        #block.input_wires = data.get("input_wires", [None] * len(block.input_points))  # Set the input wires list
        #block.output_wires = data.get("output_wires", [None] * len(block.output_points))  # Set the output wires list
        block.input_wires = data.get("input_wires", [[] for _ in block.input_points])  # Set the input wires list
        block.output_wires = data.get("output_wires", [[] for _ in block.output_points])  # Set the output wires list
        return block
    
  
    """
    @staticmethod
    def from_dict(block_dict, parent):
        block = Block(
            block_dict["x"],
            block_dict["y"],
            block_dict["width"],
            block_dict["height"],
            block_dict["text"],
            block_dict["block_type"],
            parent.grid_size,
            parent
        )
        block.id = block_dict["id"]
        block.border_color = block_dict["border_color"]
        block.fill_color = block_dict["fill_color"]
        block.text_color = block_dict["text_color"]
        block.rotation = block_dict["rotation"]
        block.input_points = block_dict["input_points"]
        block.output_points = block_dict["output_points"]
        block.input_wires = block_dict["input_wires"]
        block.output_wires = block_dict["output_wires"]
        block.input_names = block_dict["input_names"]
        block.output_names = block_dict["output_names"]
        return block
    """
