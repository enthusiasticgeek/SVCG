#!/usr/bin/env python3
import cairo
import math
from datetime import datetime
from wire import Wire

class Pin:
    def __init__(self, x, y, width, height, text, pin_type, grid_size, num_pins=1):
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
        self.connections = {}  # Dictionary to track connections
        self.update_points()

    def update_points(self):
        # Define points for pins (similar to blocks)
        if "bus" in self.pin_type.lower():
            # For buses, create multiple connection points based on num_pins
            self.connection_points = [
                self.rotate_point(self.x + (i * self.width) + 20, self.y + self.height / self.num_pins)
                for i in range(self.num_pins)
            ]
        else:
            # For single pins, create a single connection point
            self.connection_points = [self.rotate_point(self.x + self.width / 2, self.y + self.height)]

        # Print the connection points for debugging
        #print(f"Updated connection points for pin {self.text}: {self.connection_points}")
    
        self.connections = {point: None for point in self.connection_points}
    
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
            cr.rectangle(0, 0, self.width, self.height/self.num_pins)
            cr.stroke()

            cr.set_source_rgb(*self.text_color)
            cr.set_font_size(8)  # Reduced font size
            cr.move_to(0,-5)
            cr.show_text(self.text)

            # Draw the individual pins within the large rectangle
            for i in range(self.num_pins):
                # Draw the pin shape
                cr.set_source_rgb(*self.fill_color)
                cr.rectangle(i * pin_width, 0, pin_width, self.height/self.num_pins)
                cr.fill()

                cr.set_source_rgb(*self.border_color)
                cr.rectangle(i * pin_width, 0, pin_width, self.height/self.num_pins)
                cr.stroke()

                cr.set_source_rgb(*self.text_color)
                cr.set_font_size(8)  # Reduced font size
                cr.move_to(i*self.width + 20, self.height/self.num_pins - 20)
                cr.show_text(str(self.num_pins - i - 1))

                if "input_bus" in self.pin_type.lower():

                   cr.set_source_rgb(*self.border_color)
                   cr.move_to(i*self.width + 20 , self.height/self.num_pins)
                   cr.line_to(i*self.width + 20 - 10, self.height/self.num_pins - 10)
                   cr.line_to(i*self.width + 20 + 10, self.height/self.num_pins - 10)
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
                   cr.move_to(i*self.width + 20 , self.height/self.num_pins)
                   cr.line_to(i*self.width + 20 - 10, self.height/self.num_pins - 10)
                   cr.line_to(i*self.width + 20 + 10, self.height/self.num_pins - 10)
                   cr.close_path()
                   cr.fill()
          
                # show green connection pin
                cr.set_source_rgb(0, 0.6, 0)  # Green color for points
                cr.arc(i*self.width+20, self.height/self.num_pins, 4, 0, 2 * math.pi)
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
        cr.arc(self.width / 2, self.height/self.num_pins, 4, 0, 2 * math.pi)
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
        cr.arc(self.width / 2, self.height/self.num_pins, 4, 0, 2 * math.pi)
        cr.fill()

    def contains_point_old(self, x, y):
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)


    def contains_point(self, x, y):
        if "bus" in self.pin_type.lower():
            # For buses, consider the entire area covered by the connection points
            for point in self.connection_points:
                if (point[0] - 10 <= x <= point[0] + 10 and
                    point[1] - 10 <= y <= point[1] + 10):
                    return True
            return (self.x <= x <= self.x + self.width and
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
               print(f'contains pin {x},{y},{point[0]},{point[1]}')
               return point  # Return the connection point
        print(f'**DOES NOT contain pin {x},{y}**')
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
        print(f"Pin {self.text} end drag at ({self.x}, {self.y})")

    def update_wire_connections(self):
        for point, wire in self.connections.items():
            if wire is not None:
                if wire.start_point == point:
                    wire.update_start_point(point)
                elif wire.end_point == point:
                    wire.update_end_point(point)
    
    def rotate(self, angle):
        self.rotation = (self.rotation + angle) % 360
        self.update_points()

    def connect_wire(self, start_point, end_point):
        self.connections[start_point] = end_point

    def to_dict(self):
        connections_dict = {str(k): v for k, v in self.connections.items()}
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
    def from_dict(cls, data):
        pin = cls(
            data.get("x", 0),
            data.get("y", 0),
            data.get("width", 50),
            data.get("height", 50),
            data.get("name", ""),
            data.get("pin_type", ""),
            data.get("grid_size", 20),
            data.get("num_pins", 1)
        )
        pin.border_color = tuple(data.get("border_color", (0, 0, 0)))
        pin.fill_color = tuple(data.get("fill_color", (0.8, 0.8, 0.8)))
        pin.text_color = tuple(data.get("text_color", (0, 0, 0)))
        pin.rotation = data.get("rotation", 0)
        pin.connections = {eval(k): v for k, v in data.get("connections", {}).items()}
        return pin
