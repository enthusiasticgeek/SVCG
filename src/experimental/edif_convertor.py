#!/usr/bin/env python3

#experimental!

import json
import sys

def generate_edif_netlist(json_file_path, edif_file_path):
    try:
        # Read the JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        # Initialize the EDIF netlist
        edif_netlist = []

        # Extract blocks, pins, and wires
        blocks = [item for item in data if item.get("block_type")]
        pins = [item for item in data if item.get("pin_type")]
        wires = [item for item in data if item.get("start_point") or item.get("end_point")]

        # Add EDIF header
        edif_netlist.append("(edif netlist_name (edifVersion 2 0 0) (edifLevel 0) (keywordMap (keywordLevel 0))")
        edif_netlist.append("  (library library_name (edifLevel 0) (technology (numberDefinition 16)))")
        edif_netlist.append("    (cell cell_name (view netlist_view (interface))")

        # Add blocks to the EDIF netlist
        for block in blocks:
            block_info = f"""
            (cell {block["id"]} (view netlist_view (interface))
              (cellType GENERIC)
              (viewType NETLIST)
              (interface
                {generate_edif_ports(block)}
              )
            )"""
            edif_netlist.append(block_info)

        # Add pins to the EDIF netlist
        for pin in pins:
            pin_info = f"""
            (cell {pin["id"]} (view netlist_view (interface))
              (cellType GENERIC)
              (viewType NETLIST)
              (interface
                {generate_edif_ports(pin)}
              )
            )"""
            edif_netlist.append(pin_info)

        # Add wires to the EDIF netlist
        for wire in wires:
            wire_info = f"""
            (net {wire["id"]} (joined
              {generate_edif_net_connections(wire, blocks, pins)}
            ))"""
            edif_netlist.append(wire_info)

        # Add EDIF footer
        edif_netlist.append("    )")
        edif_netlist.append("  )")
        edif_netlist.append(")")

        # Write the EDIF netlist to a file
        with open(edif_file_path, 'w') as file:
            file.write("\n".join(edif_netlist))

        print(f"EDIF netlist successfully generated and saved to {edif_file_path}")

    except FileNotFoundError:
        print(f"Error: The file {json_file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {json_file_path} is not a valid JSON file.")
    except IOError as e:
        print(f"Error: An I/O error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def generate_edif_ports(component):
    ports = []
    if "input_points" in component:
        for i, point in enumerate(component["input_points"]):
            ports.append(f"(port {component['input_names'][i]} (direction INPUT))")
    if "output_points" in component:
        for i, point in enumerate(component["output_points"]):
            ports.append(f"(port {component['output_names'][i]} (direction OUTPUT))")
    if "connection_points" in component:
        for i, point in enumerate(component["connection_points"]):
            ports.append(f"(port {component['name']} (direction INOUT))")
    return "\n          ".join(ports)

def generate_edif_net_connections(wire, blocks, pins):
    connections = []
    for block in blocks:
        if wire["id"] in [item for sublist in block["input_wires"] for item in sublist]:
            index = [item for sublist in block["input_wires"] for item in sublist].index(wire["id"])
            connections.append(f"(portRef {block['input_names'][index]} (instanceRef {block['id']}))")
        if wire["id"] in [item for sublist in block["output_wires"] for item in sublist]:
            index = [item for sublist in block["output_wires"] for item in sublist].index(wire["id"])
            connections.append(f"(portRef {block['output_names'][index]} (instanceRef {block['id']}))")
    for pin in pins:
        if wire["id"] in [item for sublist in pin["wires"] for item in sublist]:
            connections.append(f"(portRef {pin['name']} (instanceRef {pin['id']}))")
    return "\n          ".join(connections)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python edif_convertor.py <json_file_path_with_extension.json> <generated_output_edif_file_path_with_extension.edf>")
        sys.exit(1)

    json_file_path = sys.argv[1]
    edif_file_path = sys.argv[2]
    generate_edif_netlist(json_file_path, edif_file_path)
