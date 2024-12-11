#!/usr/bin/env python3
import cairo
import math
import pprint
import uuid
from datetime import datetime
from wire import Wire

class Pin:
    def __init__(self, x, y, width, height, text, pin_type, grid_size, num_pins=1, parent_window=None):
        self.id = f"pin_{str(uuid.uuid4().int)[:10]}"  # Generate a unique 10-digit ID
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.pin_type = pin_type
        self.num_pins = num_pins
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.grid_size = grid_size
        self.border_color = (0, 0, 0)  # Default border color (black)
        self.fill_color = (0.8, 0.8, 0.8)  # Default fill color (light gray)
        self.text_color = (0, 0, 0)  # Default text color (black)
        self.rotation = 0  # Initial rotation angle in degrees
        self.selected = False  # Attribute to track selection state
        self.timestamp = datetime.now().isoformat(' ', 'seconds')
        self.connection_points = []  # List of dictionaries to track connections
        self.prev_connection_points = []  # List of dictionaries to track connections
        #self.wires = [None] * num_pins  # List to store wire IDs for each connection point
        self.wires = [[] for _ in range(num_pins)]  # List to store wire IDs for each connection point
        self.parent_window = parent_window  # Add the parent_window attribute
        self.update_points()

    def set_selected(self, selected):
        self.selected = selected

    def update_points(self):
        # Define points for pins (similar to blocks)
        if "bus" in self.pin_type.lower():
            # For buses, create multiple connection points based on num_pins
            self.connection_points = [
                self.rotate_point(int(self.x + (i * self.width) + self.width/2), int(self.y + self.height))
                for i in range(self.num_pins)
            ]
        else:
            # For single pins, create a single connection point
            self.connection_points = [self.rotate_point(int(self.x + self.width / 2), int(self.y + self.height))]

        # Print the connection points for debugging
        #print(f"Updated connection points for pin {self.text}: {self.connection_points}")

        #self.connections = {point: None for point in self.connection_points}

        # Print all points in input and output connections
        #print(f"Connection Points: {self.connection_points}")
        #print(f"Connections: {self.connections}")

    def prev_connections(self):
        return self.prev_connection_points

    def connections(self):
        return self.connection_points

    def rotate_point(self, x, y):
        # Rotate the point around the center of the pin
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

        # Draw arrows based on pin type
        if "input_pin" in self.pin_type.lower():
            self.draw_pin(cr)
            self.draw_input_arrow(cr)
        if "output_pin" in self.pin_type.lower():
            self.draw_pin(cr)
            self.draw_output_arrow(cr)
        if "input_output_pin" in self.pin_type.lower():
            self.draw_pin(cr)
            self.draw_input_arrow(cr)
            self.draw_output_arrow(cr)
        if "input_bus" in self.pin_type.lower():
            self.draw_bus(cr)
        if "output_bus" in self.pin_type.lower():
            self.draw_bus(cr)
        if "input_output_bus" in self.pin_type.lower():
            self.draw_bus(cr)
        if "CLK" or "GND" or "VDD_5V" or "VDD_3V3" or "VDD_1V8" or "VDD_1V2" in self.pin_type:
            self.draw_vdd_clk_gnd(cr,self.pin_type)
            self.draw_input_arrow(cr)
        self.update_points()

        cr.restore()

    def draw_pin(self, cr):
        cr.set_line_width(1)

        # Set fill color based on selection state
        fill_color = (1, 1, 0) if self.selected else self.fill_color

        cr.set_source_rgb(*self.text_color)
        cr.set_font_size(8)  # Reduced font size
        cr.move_to(0,-5)
        cr.show_text(self.text)

        # Draw the pin shape
        cr.set_source_rgb(*fill_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()

        cr.set_source_rgb(*self.border_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

    def draw_vdd_clk_gnd(self, cr, pin_type_text):
        cr.set_line_width(1)

        # Set fill color based on selection state
        fill_color = (1, 1, 0) if self.selected else self.fill_color

        cr.set_source_rgb(*self.text_color)
        cr.set_font_size(8)  # Reduced font size
        cr.move_to(0,-5)
        cr.show_text(self.text)

        # Draw the pin shape
        cr.set_source_rgb(*fill_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()

        cr.set_source_rgb(*self.border_color)
        cr.rectangle(0, 0, self.width, self.height)
        cr.stroke()

        # Draw pin type text
        cr.move_to(self.width/2,self.height/2)
        cr.show_text(pin_type_text)

    def draw_bus(self, cr):
            cr.set_line_width(1)

            # Set fill color based on selection state
            fill_color = (1, 1, 0) if self.selected else self.fill_color

            pin_width = self.width  # Width of each pin

            # Draw the pin shape
            #cr.set_source_rgb(*fill_color)
            #cr.rectangle(0, 0, self.height, self.height/self.num_pins)
            #cr.fill()

            cr.set_source_rgb(*self.border_color)
            cr.rectangle(0, 0, self.width, self.height)
            cr.stroke()

            cr.set_source_rgb(*self.text_color)
            cr.set_font_size(8)  # Reduced font size
            cr.move_to(0,-5)
            cr.show_text(self.text)

            # Draw the individual pins within the large rectangle
            for i in range(self.num_pins):
                # Draw the pin shape
                cr.set_source_rgb(*self.fill_color)
                cr.rectangle(i * pin_width, 0, pin_width, self.height)
                cr.fill()

                cr.set_source_rgb(*self.border_color)
                cr.rectangle(i * pin_width, 0, pin_width, self.height)
                cr.stroke()

                cr.set_source_rgb(*self.text_color)
                cr.set_font_size(8)  # Reduced font size
                cr.move_to(i*self.width + 20, self.height - 20)
                cr.show_text(str(self.num_pins - i - 1))

                if "input_bus" in self.pin_type.lower():

                   cr.set_source_rgb(*self.border_color)
                   cr.move_to(i*self.width + 20 , self.height)
                   cr.line_to(i*self.width + 20 - 10, self.height - 10)
                   cr.line_to(i*self.width + 20 + 10, self.height - 10)
                   cr.close_path()
                   cr.fill()

                if "output_bus" in self.pin_type.lower():

                   cr.set_source_rgb(*self.border_color)
                   cr.move_to(i*self.width + 20,  0)
                   cr.line_to(i*self.width + 20 - 10, 10)
                   cr.line_to(i*self.width + 20 + 10, 10)
                   cr.close_path()
                   cr.fill()

                if "input_output_bus" in self.pin_type.lower():

                   cr.set_source_rgb(*self.border_color)
                   cr.move_to(i*self.width + 20,  0)
                   cr.line_to(i*self.width + 20 - 10, 10)
                   cr.line_to(i*self.width + 20 + 10, 10)
                   cr.close_path()
                   cr.fill()

                   cr.set_source_rgb(*self.border_color)
                   cr.move_to(i*self.width + 20 , self.height)
                   cr.line_to(i*self.width + 20 - 10, self.height - 10)
                   cr.line_to(i*self.width + 20 + 10, self.height - 10)
                   cr.close_path()
                   cr.fill()

                # show green connection pin
                cr.set_source_rgb(0, 0.6, 0)  # Green color for points
                cr.arc(i*self.width+20, self.height, 4, 0, 2 * math.pi)
                cr.fill()

    def draw_output_arrow(self, cr):
        cr.set_line_width(1)
        cr.set_source_rgb(*self.border_color)
        cr.move_to(self.width / 2, 0)
        cr.line_to(self.width / 2 - 10, 10)
        cr.line_to(self.width / 2 + 10, 10)
        cr.close_path()
        cr.fill()

        # show green connection pin
        cr.set_source_rgb(0, 0.6, 0)  # Green color for points
        cr.arc(self.width / 2, self.height, 4, 0, 2 * math.pi)
        cr.fill()

    def draw_input_arrow(self, cr):
        cr.set_line_width(1)
        cr.set_source_rgb(*self.border_color)
        cr.move_to(self.width / 2, self.height)
        cr.line_to(self.width / 2 - 10, self.height - 10)
        cr.line_to(self.width / 2 + 10, self.height - 10)
        cr.close_path()
        cr.fill()

        # show green connection pin
        cr.set_source_rgb(0, 0.6, 0)  # Green color for points
        cr.arc(self.width / 2, self.height, 4, 0, 2 * math.pi)
        cr.fill()

    def contains_point(self, x, y, tolerance = 10):
        if "bus" in self.pin_type.lower():
            # For buses, consider the entire area covered by the connection points
            for point in self.connection_points:
                if (point[0] - tolerance <= int(x) <= point[0] + tolerance and
                    point[1] - tolerance <= int(y) <= point[1] + tolerance):
                    return True
            print(f"X: {self.x - tolerance} <= {int(x)} <=  {self.x + self.width*self.num_pins + tolerance}")
            print(f"Y: {self.y - tolerance} <= {int(y)} <=  {self.y + self.height + tolerance}")
            return (self.x - tolerance <= int(x) <= self.x + self.width*self.num_pins + tolerance and
                    self.y - tolerance <= int(y) <= self.y + self.height + tolerance)
        else:
            # For single pins, use the original bounds check
            print(f"X: {self.x - tolerance} <= {int(x)} <=  {self.x + self.width + tolerance}")
            print(f"Y: {self.y - tolerance} <= {int(y)} <=  {self.y + self.height + tolerance}")
            return (self.x - tolerance <= int(x) <= self.x + self.width + tolerance and
                    self.y - tolerance <= int(y) <= self.y + self.height + tolerance)

    def contains_pin(self, x, y, tolerance = 5):
        self.update_points()
        for point in self.connection_points:
            if (point[0] - tolerance <= int(x) <= point[0] + tolerance and
               point[1] - tolerance <= int(y) <= point[1] + tolerance):
               print(f'=================== contains pin {x},{y},{point[0]},{point[1]} =================')
               return point  # Return the connection point
        #print(f'**DOES NOT contain pin {x},{y}**')
        return None

    def start_drag(self, x, y):
        self.dragging = True
        self.offset_x = x - self.x
        self.offset_y = y - self.y
        #print(f"start_drag {self.offset_x} and {self.offset_y}")
        self.prev_connection_points = self.connection_points.copy()

    def drag_old(self, x, y, max_x, max_y):
        if self.dragging:
            new_x = x - self.offset_x
            new_y = y - self.offset_y
            if new_x >= 0 and new_x + self.width*self.num_pins <= max_x:
                self.x = new_x
                #print(f"drag {self.x}")
            if new_y >= 0 and new_y + self.height <= max_y:
                self.y = new_y
                #print(f"drag {self.y}")
            self.update_points()

    def drag(self, x, y, max_x, max_y):
        if self.dragging:
            new_x = max(0, min(x - self.offset_x, max_x - self.width * self.num_pins))
            new_y = max(0, min(y - self.offset_y, max_y - self.height))
            self.x = new_x
            self.y = new_y
            self.update_points()
 

    def end_drag(self):
        self.dragging = False
        self.x = round(self.x / self.grid_size) * self.grid_size
        self.y = round(self.y / self.grid_size) * self.grid_size
        self.width = round(self.width / self.grid_size) * self.grid_size
        self.height = round(self.height / self.grid_size) * self.grid_size
        # Update wire connections
        #self.parent_window.update_wires()
        #self.update_wire_connections()
        ## Update start and end block coordinates in wire connections
        #self.update_start_pin_coordinates(self.connections, self.text, self.x, self.y)
        #self.update_end_pin_coordinates(self.connections, self.text, self.x, self.y)

        #print(f"Pin {self.text} end drag at ({self.x}, {self.y})")
        self.update_points()

        #for connection in self.connections:
        #    connection['wire'].path = connection['wire'].calculate_path()  # Recalculate the path
        #    connection['wire'].parent_window.update_wires()


    """
    def update_start_pin_coordinates(self, connections, text, new_x, new_y):
        for connection in connections:
            pprint.pprint(f"{connection}")
            if connection['wire'] and connection['wire'].start_pin and connection['wire'].start_pin.text == text:
                connection['wire'].start_pin.x = new_x
                connection['wire'].start_pin.y = new_y

    def update_end_pin_coordinates(self, connections, text, new_x, new_y):
        for connection in connections:
            if connection['wire'] and connection['wire'].end_pin and connection['wire'].end_pin.text == text:
                print("here2")
                connection['wire'].end_pin.x = new_x
                connection['wire'].end_pin.y = new_y

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
        print("Pins ============")
        if start_point in self.connection_points:
            self.connections.append({'point': start_point, 'wire': end_point})
        if end_point in self.connection_points:
            self.connections.append({'point': end_point, 'wire': start_point})
        #print(f"Updated connections: {self.connections}")
        updated_connections = {k: (v['wire'].to_dict() if v['wire'] is not None else None) for k, v in enumerate(self.connections)}
        #print(f"Updated connections: {updated_connections}")
    """

    def to_dict(self):
        return {
            "id": self.id,  # Include the ID in the JSON
            "name": self.text,
            "pin_type": self.pin_type,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "rotation": self.rotation,
            "border_color": self.border_color,
            "fill_color": self.fill_color,
            "text_color": self.text_color,
            "timestamp": self.timestamp,
            "connection_points": self.connection_points,  # Include connection points in the JSON
            "wires": self.wires,  # Include wires in the JSON
            "grid_size": self.grid_size,  # Include grid_size in the JSON
            "num_pins": self.num_pins  # Include number of pins for buses
        }
    
    
    @classmethod
    def from_dict(cls, data, parent_window):
        pin = cls(
            data.get("x", 0),
            data.get("y", 0),
            data.get("width", 50),
            data.get("height", 50),
            data.get("name", ""),
            data.get("pin_type", ""),
            data.get("grid_size", 20),
            data.get("num_pins", 1),
            parent_window
        )
        pin.id = data.get("id", f"pin_{str(uuid.uuid4().int)[:10]}")  # Ensure the ID is set
        pin.border_color = tuple(data.get("border_color", (0, 0, 0)))
        pin.fill_color = tuple(data.get("fill_color", (0.8, 0.8, 0.8)))
        pin.text_color = tuple(data.get("text_color", (0, 0, 0)))
        pin.rotation = data.get("rotation", 0)
        pin.connection_points = data.get("connection_points", [])
        #pin.wires = data.get("wires", [None] * pin.num_pins)  # Set the wires list
        pin.wires = data.get("wires", [[] for _ in range(pin.num_pins)])  # Set the wires list
        return pin
    
    """
    @staticmethod
    def from_dict(pin_dict, parent):
        pin = Pin(
            pin_dict["x"],
            pin_dict["y"],
            pin_dict["width"],
            pin_dict["height"],
            pin_dict["text"],
            pin_dict["pin_type"],
            parent.grid_size,
            pin_dict["num_pins"],
            parent
        )
        pin.id = pin_dict["id"]
        pin.border_color = pin_dict["border_color"]
        pin.fill_color = pin_dict["fill_color"]
        pin.text_color = pin_dict["text_color"]
        pin.rotation = pin_dict["rotation"]
        pin.connection_points = pin_dict["connection_points"]
        pin.wires = pin_dict["wires"]
        return pin

    """
