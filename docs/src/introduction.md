# SVCG — Simple VHDL/Verilog Code Generator

A GTK3-based Python desktop application for visually designing digital circuits and generating **VHDL or Verilog**. Place logic blocks on a schematic canvas, wire them together, and export a complete structural HDL file in your chosen language.

![SVCG — JK flip-flop schematic](../../SVCG1.png)

*JK flip-flop with J, K, CLK inputs, PRE (preset), CLR (reset), Q and Q̄ outputs. Selected wire shown in orange; drag the mid-point handle to reroute.*

## Feature Overview

| Category | Highlights |
|---|---|
| **Schematic editor** | Drag-and-drop on a 5000×5000 scrollable canvas; zoom; multi-select |
| **Logic gates** | AND, OR, NOT, NAND, NOR, XOR, XNOR |
| **Flip-flops** | JK, SR, D (pipeline variant), T |
| **Multiplexers** | 2×1, 4×1, 8×1 MUX |
| **Tristate buffers** | 2, 4, 8 channel |
| **Arithmetic** | Full Adder (standard, Gray Cell, White Cell), Half Adder |
| **I/O primitives** | Input/Output/Bidirectional pins and buses, CLK, VDD, GND |
| **HDL export** | Structural VHDL entity + architecture; structural Verilog module |
| **Custom RTL** | Behavioral blocks with AI-generated VHDL or Verilog body |
| **Simulation** | GHDL testbench auto-generation + GTKWave waveform viewer |
| **Import** | Yosys synthesis JSON → canvas |
| **EDIF export** | Experimental netlist export |
