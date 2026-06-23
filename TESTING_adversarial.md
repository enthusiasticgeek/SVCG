# SVCG Adversarial Test Report (Student Scenarios)

**Date:** 2026-06-23 12:05  
**Platform:** Windows 11 / MSYS2 MinGW64  
**Result: 60/60 passed, 0 skipped**

| # | ID | Test | Result | Notes |
|---|-----|------|--------|-------|
| 1 | TC-01 | TC-01 Half adder canvas counts | PASS |  |
| 2 | TC-01 | TC-01 Half adder VHDL entity ports | PASS |  |
| 3 | TC-01 | TC-01 Half adder VHDL components declared | PASS |  |
| 4 | TC-01 | TC-01 Half adder VHDL port maps fully connected | PASS |  |
| 5 | TC-02 | TC-02 Full adder canvas layout | PASS |  |
| 6 | TC-02 | TC-02 Full adder internal signals in VHDL | PASS |  |
| 7 | TC-02 | TC-02 Full adder no open port maps | PASS |  |
| 8 | TC-02 | TC-02 Full adder round-trip wire IDs | PASS |  |
| 9 | TC-03 | TC-03 MUX_2X1 component in VHDL | PASS |  |
| 10 |  | TC-04 AND chain -- internal net as signal | PASS |  |
| 11 |  | TC-05 NOT chain -- two internal signals | PASS |  |
| 12 | TC-06 | TC-06 DFF VHDL port names | PASS |  |
| 13 | TC-06 | TC-06 DFF testbench clock process | PASS |  |
| 14 | TC-06 | TC-06 DFF testbench D stimulus | PASS |  |
| 15 | TC-06 | TC-06 DFF VHDL GHDL syntax check | PASS |  |
| 16 | TC-07 | TC-07 JKFF Q_bar rename in VHDL | PASS |  |
| 17 | TC-08 | TC-08 SRFF VHDL generation no crash | PASS |  |
| 18 | TC-09 | TC-09 Port names match pin text exactly | PASS |  |
| 19 | TC-10 | TC-10 Net name appears as signal declaration | PASS |  |
| 20 | TC-11 | TC-11 Wire name with space sanitized | PASS |  |
| 21 | TC-12 | TC-12 Unconnected pin maps to open | PASS |  |
| 22 | TC-13 | TC-13 All three port directions in VHDL entity | PASS |  |
| 23 | TC-14 | TC-14 Digit-start pin name sanitized | PASS |  |
| 24 | TC-14 | TC-14 Special-char pin name sanitized | PASS |  |
| 25 | TC-14 | TC-14 Unicode net name sanitized | PASS |  |
| 26 | TC-15 | TC-15 Half adder round-trip counts | PASS |  |
| 27 | TC-16 | TC-16 Wire IDs preserved after save/load | PASS |  |
| 28 | TC-17 | TC-17 Block fill color preserved after save/load | PASS |  |
| 29 | TC-18 | TC-18 Wire net name preserved after save/load | PASS |  |
| 30 | TC-19 | TC-19 Origin-point wire survives reload | PASS |  |
| 31 | TC-20 | TC-20 Block at (0,0) serializes correctly | PASS |  |
| 32 | TC-21 | TC-21 Input-to-input wire no crash | PASS |  |
| 33 | TC-22 | TC-22 Duplicate wire detection logic | PASS |  |
| 34 | TC-23 | TC-23 Overlapping blocks no crash | PASS |  |
| 35 | TC-24 | TC-24 Pin name >200 chars sanitized | PASS |  |
| 36 | TC-25 | TC-25 All-digit pin name gets sig_ prefix | PASS |  |
| 37 | TC-26 | TC-26 Unicode net name sanitized in VHDL | PASS |  |
| 38 | TC-27 | TC-27 Undo on empty stack no crash | PASS |  |
| 39 | TC-28 | TC-28 30 undo push/pop cycles consistent | PASS |  |
| 40 | TC-29 | TC-29 Component save creates JSON file | PASS |  |
| 41 | TC-30 | TC-30 Instantiated component has fresh IDs | PASS |  |
| 42 |  | TC-31 Double instantiation -- no ID collisions | PASS |  |
| 43 | TC-32 | TC-32 Malformed component JSON no crash | PASS |  |
| 44 | TC-33 | TC-33 Testbench UUT port map has all signal names | PASS |  |
| 45 | TC-34 | TC-34 Testbench clock half-period is 5 ns | PASS |  |
| 46 | TC-35 | TC-35 Testbench stimulus covers all non-CLK inputs | PASS |  |
| 47 | TC-36 | TC-36 Bus pin expands to individual bits | PASS |  |
| 48 | TC-37 | TC-37 SVG file has valid XML/SVG header | PASS |  |
| 49 | TC-38 | TC-38 PNG file has valid magic bytes | PASS |  |
| 50 | TC-39 | TC-39 Export empty canvas returns early | PASS |  |
| 51 | TC-40 | TC-40 Bounding box padding is exactly 40px | PASS |  |
| 52 | TC-41 | TC-41 Long diagonal wire has non-empty path | PASS |  |
| 53 | TC-42 | TC-42 A* full-grid fallback on blocked sub-grid | PASS |  |
| 54 | TC-43 | TC-43 Manhattan path geometry correct | PASS |  |
| 55 | TC-44 | TC-44 Wire path has no duplicate consecutive points | PASS |  |
| 56 | TC-45 | TC-45 20-wire bus pattern all non-empty | PASS |  |
| 57 | TC-46 | TC-46 Yosys AND+OR import cell count | PASS |  |
| 58 | TC-47 | TC-47 Yosys unsupported cell warning no crash | PASS |  |
| 59 | TC-48 | TC-48 Yosys empty JSON returns gracefully | PASS |  |
| 60 | TC-49 | TC-49 Yosys multi-driver net no crash | PASS |  |

_60/60 passed, 0 skipped._
