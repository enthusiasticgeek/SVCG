#!/usr/bin/env python3
import cairo
import math
import pprint
from datetime import datetime
from wire import Wire

class Pin:
    def __init__(self, x, y, width, height, text, pin_type, grid_size, num_pins=1, parent_window=None):
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
        self.connections = []  # List of dictionaries to track connections
        self.parent_window = parent_window  # Add the parent_window attribute
        self.update_points()
        self.x_orig = x
        self.y_orig = y
        self.x_new = x
        self.y_new = y

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

    def contains_point(self, x, y):
        if "bus" in self.pin_type.lower():
            # For buses, consider the entire area covered by the connection points
            for point in self.connection_points:
                if (point[0] - 10 <= x <= point[0] + 10 and
                    point[1] - 10 <= y <= point[1] + 10):
                    return True
            return (self.x <= x <= self.x + self.width*self.num_pins and
                    self.y <= y <= self.y + self.height)
        else:
            # For single pins, use the original bounds check
            return (self.x <= x <= self.x + self.width and
                    self.y <= y <= self.y + self.height)

    def contains_pin(self, x, y):
        self.update_points()
        for point in self.connection_points:
            if (point[0] - 10 <= int(x) <= point[0] + 10 and
               point[1] - 10 <= int(y) <= point[1] + 10):
               #print(f'=================== contains pin {x},{y},{point[0]},{point[1]} =================')
               return point  # Return the connection point
        #print(f'**DOES NOT contain pin {x},{y}**')
        return None

    def start_drag(self, x, y):
        self.dragging = True
        self.offset_x = x - self.x
        self.offset_y = y - self.y
        self.x_orig = self.offset_x
        self.y_orig = self.offset_y
        #print(f"start_drag {self.offset_x} and {self.offset_y}")

    def drag(self, x, y, max_x, max_y):
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

    def end_drag(self):
        self.dragging = False
        self.x = round(self.x / self.grid_size) * self.grid_size
        self.y = round(self.y / self.grid_size) * self.grid_size
        self.width = round(self.width / self.grid_size) * self.grid_size
        self.height = round(self.height / self.grid_size) * self.grid_size
        self.update_points()
        #self.update_wire_connections()
        ## Update start and end block coordinates in wire connections
        self.update_start_pin_coordinates(self.connections, self.text, self.x, self.y)
        #self.update_end_pin_coordinates(self.connections, self.text, self.x, self.y)

        #print(f"Pin {self.text} end drag at ({self.x}, {self.y})")
        self.x_orig = self.x_new
        self.y_orig = self.y_new
        self.x_new = self.x
        self.y_new = self.y
        print(f"Pin {self.text} end drag at ({self.x_new}, {self.y_new}) from ({self.x_orig}, {self.y_orig})")

    def update_start_pin_coordinates(self, connections, text, new_x, new_y):
        for connection in connections:
            pprint.pprint(f"{connection}")
            if connection['wire'] and connection['wire'].start_pin and connection['wire'].start_pin.text == text:
                print("here1")
                connection['wire'].start_pin.x = new_x
                connection['wire'].start_pin.y = new_y
                pprint.pprint(f"===={connection}")

    def update_end_pin_coordinates(self, connections, text, new_x, new_y):
        for connection in connections:
            if connection['wire'] and connection['wire'].end_pin and connection['wire'].end_pin.text == text:
                print("here2")
                connection['wire'].end_pin.x = new_x
                connection['wire'].end_pin.y = new_y

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

    def update_wire_connections(self):
        for connection in self.connections:
            if connection['wire'] is not None:
                if connection['wire'].start_point == connection['point']:
                    connection['wire'].start_pin = self
                    connection['wire'].update_start_point(connection['point'])
                if connection['wire'].end_point == connection['point']:
                    connection['wire'].end_pin = self
                    connection['wire'].update_end_point(connection['point'])

        updated_connections = {k: self.extract_wire_details(v['wire']) for k, v in enumerate(self.connections) if v['wire'] is not None}
        #pprint.pprint(f"current connections: {updated_connections}")
        # Return the updated connections if needed
        return updated_connections

    def rotate(self, angle):
        self.rotation = (self.rotation + angle) % 360
        self.update_points()

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

    def to_dict(self):
        #connections_dict = {str(k): v for k, v in self.connections.items()}
        connections_dict = {str(k): (v['wire'].to_dict() if v['wire'] is not None else None) for k, v in enumerate(self.connections)}
        return {
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
            "connections": connections_dict,  # Include connections in the JSON
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
        pin.border_color = tuple(data.get("border_color", (0, 0, 0)))
        pin.fill_color = tuple(data.get("fill_color", (0.8, 0.8, 0.8)))
        pin.text_color = tuple(data.get("text_color", (0, 0, 0)))
        pin.rotation = data.get("rotation", 0)
        #pin.connections = {eval(k): v for k, v in data.get("connections", {}).items()}
        pin.connections = [{'point': eval(k), 'wire': (Wire.from_dict(v, pin.parent_window) if v is not None else None)} for k, v in data.get("connections", {}).items()]
        return pin

