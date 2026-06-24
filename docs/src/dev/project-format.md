# Project File Format

Designs are stored as JSON arrays in `.json` files. Each element is one of three types distinguished by a unique key:

## Block

Identified by the `block_type` key.

```json
{
  "id": "block_1234567890",
  "name": "XOR_1",
  "block_type": "XOR",
  "x": 100, "y": 100,
  "width": 60, "height": 60,
  "rotation": 0,
  "input_points": [[100, 110], [100, 130]],
  "output_points": [[160, 120]],
  "input_names": ["A", "B"],
  "output_names": ["Y"],
  "input_wires":  [["wire_abc"], ["wire_def"]],
  "output_wires": [["wire_ghi"]],
  "border_color": [0, 0, 0, 1],
  "fill_color":   [1, 1, 1, 1],
  "text_color":   [0, 0, 0, 1],
  "grid_size": 10,
  "timestamp": 1718000000.0
}
```

Custom RTL blocks additionally carry a `custom_data` object:

```json
"custom_data": {
  "entity_name": "MY_BLOCK",
  "input_names": ["A", "B"],
  "output_names": ["Y"],
  "vhdl":      "...",
  "vhdl_body": "...",
  "verilog_body": "..."
}
```

The `"vhdl"` key is always present for backward compatibility with older project files. Language-specific keys (`vhdl_body`, `verilog_body`) hold the code for each respective language.

## Pin

Identified by the `pin_type` key.

```json
{
  "id": "pin_9876543210",
  "name": "A",
  "pin_type": "input_pin",
  "x": 20, "y": 100,
  "width": 40, "height": 30,
  "rotation": 0,
  "connection_points": [[60, 115]],
  "wires": [["wire_abc"]],
  "num_pins": 1,
  "border_color": [0, 0, 0, 1],
  "fill_color":   [0.8, 0.9, 1, 1],
  "text_color":   [0, 0, 0, 1],
  "grid_size": 10,
  "timestamp": 1718000000.0
}
```

`pin_type` is one of: `input_pin`, `output_pin`, `bidirectional_pin`, `input_bus`, `output_bus`, `bidirectional_bus`, `CLK`, `VDD_5V`, `VDD_3V3`, `VDD_1V8`, `VDD_1V2`, `GND`.

## Wire

Identified by a non-`null` `start_point` key.

```json
{
  "id": "wire_abc",
  "name": "A_xor",
  "text": "A_xor",
  "start_point": [60, 115],
  "end_point":   [100, 110],
  "wire_type": "wire",
  "path": [[60,115], [80,115], [80,110], [100,110]],
  "waypoint": null,
  "grid_size": 10
}
```

`text` is the user-visible net name displayed on the canvas and used as the `signal` / `wire` name in the generated HDL.
