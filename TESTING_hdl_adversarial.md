# SVCG HDL Adversarial Test Report (VHDL + Verilog)

**Date:** 2026-06-23 13:41  
**Platform:** Windows 11 / MSYS2 MinGW64  
**Result: 92/92 passed, 0 skipped**

| # | ID | Test | Result | Notes |
|---|-----|------|--------|-------|
| 1 | T01 | T01 VHDL empty canvas skeleton | PASS |  |
| 2 | T02 | T02 VHDL half adder port directions | PASS |  |
| 3 | T03 | T03 VHDL component declarations | PASS |  |
| 4 | T04 | T04 VHDL no unconnected ports in half adder | PASS |  |
| 5 | T05 | T05 VHDL has signal declarations for internal nets | PASS |  |
| 6 | T06 | T06 VHDL port maps use named association (=>) | PASS |  |
| 7 | T07 | T07 VHDL has library IEEE and use clause | PASS |  |
| 8 | T08 | T08 VHDL all standard block types exported | PASS |  |
| 9 | T09 | T09 VHDL reserved word 'signal' in port name sanitized | PASS |  |
| 10 | T10 | T10 VHDL inout port direction preserved | PASS |  |
| 11 | T11 | T11 Verilog empty canvas skeleton | PASS |  |
| 12 | T12 | T12 Verilog half adder port directions | PASS |  |
| 13 | T13 | T13 Verilog has no VHDL component keywords | PASS |  |
| 14 | T14 | T14 Verilog port maps use dot-notation (.port(signal)) | PASS |  |
| 15 | T15 | T15 Verilog internal signals declared as wire | PASS |  |
| 16 | T16 | T16 Verilog ends with endmodule | PASS |  |
| 17 | T17 | T17 Verilog output contains no VHDL keywords | PASS |  |
| 18 | T18 | T18 Verilog all standard block types exported | PASS |  |
| 19 | T19 | T19 Verilog unconnected port uses 1'bz not VHDL open | PASS |  |
| 20 | T20 | T20 Verilog inout port direction preserved | PASS |  |
| 21 | T21 | T21 Custom VHDL entity declaration auto-generated | PASS |  |
| 22 | T22 | T22 Custom VHDL user architecture body included verbatim | PASS |  |
| 23 | T23 | T23 Custom VHDL empty body generates stub architecture | PASS |  |
| 24 | T24 | T24 Custom VHDL always includes library/use clauses | PASS |  |
| 25 | T25 | T25 Custom VHDL with no ports is valid (port-less entity) | PASS |  |
| 26 | T26 | T26 Custom VHDL input default := '0', output has none | PASS |  |
| 27 | T27 | T27 Custom Verilog module header auto-generated | PASS |  |
| 28 | T28 | T28 Custom Verilog user body placed before endmodule | PASS |  |
| 29 | T29 | T29 Custom Verilog empty body generates stub comment | PASS |  |
| 30 | T30 | T30 Custom Verilog exactly one endmodule in output | PASS |  |
| 31 | T31 | T31 Custom Verilog output contains no VHDL keywords | PASS |  |
| 32 | T32 | T32 Custom Verilog outputs declared as 'output reg' | PASS |  |
| 33 | T33 | T33 Default HDL language is VHDL | PASS |  |
| 34 | T34 | T34 HDL combo switching updates hdl_language | PASS |  |
| 35 | T35 | T35 Window title shows active HDL language | PASS |  |
| 36 | T36 | T36 CustomBlockDialog stores language parameter | PASS |  |
| 37 | T37 | T37 VHDL AI prompt asks for architecture block | PASS |  |
| 38 | T38 | T38 Verilog AI prompt asks for module body (no header) | PASS |  |
| 39 | T39 | T39 All port names appear in both VHDL and Verilog prompts | PASS |  |
| 40 | T40 | T40 Description included in prompt; empty description gets fallback | PASS |  |
| 41 | T41 | T41 VHDL reserved words as port names are sanitized | PASS |  |
| 42 | T42 | T42 _sanitize() handles Verilog-relevant reserved words | PASS |  |
| 43 | T43 | T43 Digit-leading port names prefixed sig_ in both languages | PASS |  |
| 44 | T44 | T44 200-char port name does not crash either HDL generator | PASS |  |
| 45 | T45 | T45 GHDL syntax check on VHDL half adder | PASS |  |
| 46 | T46 | T46 iverilog syntax check on Verilog half adder | PASS |  |
| 47 | T47 | T47 GHDL syntax check on custom VHDL DFF | PASS |  |
| 48 | T48 | T48 iverilog syntax check on custom Verilog DFF | PASS |  |
| 49 | T49 | T49 Same port names appear in VHDL and Verilog outputs | PASS |  |
| 50 | T50 | T50 Top-level name consistent between VHDL entity and Verilog module | PASS |  |
| 51 | T51 | T51 Instantiation count consistent between VHDL and Verilog | PASS |  |
| 52 | T52 | T52 Switching back to VHDL generates correct VHDL output | PASS |  |
| 53 | T53 | T53 Net name with spaces sanitized in VHDL signal declaration | PASS |  |
| 54 | T54 | T54 Net name with hyphens sanitized in Verilog wire declaration | PASS |  |
| 55 | T55 | T55 Net name 'signal' (VHDL reserved) becomes sig_signal in VHDL | PASS |  |
| 56 | T56 | T56 Net name 'wire' (Verilog reserved) becomes sig_wire in Verilog | PASS |  |
| 57 | T57 | T57 All-special-char net name produces valid identifier in both HDLs | PASS |  |
| 58 | T58 | T58 Digit-only net name becomes sig_42 in both VHDL and Verilog | PASS |  |
| 59 | T59 | T59 Three AND gates yield three distinct VHDL port map instances | PASS |  |
| 60 | T60 | T60 Three AND gates yield three distinct Verilog instance identifiers | PASS |  |
| 61 | T61 | T61 Block label with spaces sanitized in VHDL instance label | PASS |  |
| 62 | T62 | T62 Block label with spaces sanitized in Verilog instance identifier | PASS |  |
| 63 | T63 | T63 Identical block labels get unique instance names via index suffix | PASS |  |
| 64 | T64 | T64 VHDL entity port count equals number of IO pins | PASS |  |
| 65 | T65 | T65 Verilog module port count equals number of IO pins | PASS |  |
| 66 | T66 | T66 Duplicate IO pin names: deduplication keeps exactly one port entry | PASS |  |
| 67 | T67 | T67 CLK pin type exported with 'in' direction in both HDLs | PASS |  |
| 68 | T68 | T68 Custom VHDL: VHDL reserved port name 'signal' sanitized to sig_signal | PASS |  |
| 69 | T69 | T69 Custom Verilog: Verilog reserved port name 'wire' sanitized to sig_wire | PASS |  |
| 70 | T70 | T70 Custom block with 16 inputs + 8 outputs does not crash | PASS |  |
| 71 | T71 | T71 Custom VHDL: digit-leading port name sanitized to sig_3bit | PASS |  |
| 72 | T72 | T72 Custom Verilog: Verilog reserved port name 'module' sanitized to sig_module | PASS |  |
| 73 | T73 | T73 GHDL: custom VHDL with formerly-reserved port name passes syntax check | PASS |  |
| 74 | T74 | T74 iverilog: custom Verilog with formerly-reserved port name passes syntax check | PASS |  |
| 75 | T75 | T75 Testbench entity name is entity_name_tb | PASS |  |
| 76 | T76 | T76 CLK port generates 100 MHz clock process | PASS |  |
| 77 | T77 | T77 Active-low signal 'nrst' initialised to '1' in testbench | PASS |  |
| 78 | T78 | T78 Active-low signal pulsed LOW then HIGH in stimulus | PASS |  |
| 79 | T79 | T79 Regular input pulsed HIGH then LOW in stimulus | PASS |  |
| 80 | T80 | T80 Port-less entity produces valid testbench skeleton | PASS |  |
| 81 | T81 | T81 Output ports not driven in testbench stimulus process | PASS |  |
| 82 | T82 | T82 Multiple CLK ports each generate their own clock process | PASS |  |
| 83 | T83 | T83 Clock port detection is case-insensitive (sys_CLK, Clk_in) | PASS |  |
| 84 | T84 | T84 Active-low suffix patterns _n / _b / _bar all detected | PASS |  |
| 85 | T85 | T85 Active-low prefix patterns n_ / nrst / nreset all detected | PASS |  |
| 86 | T86 | T86 UUT instantiation label is 'uut' | PASS |  |
| 87 | T87 | T87 Every VHDL port map uses named association (=>) | PASS |  |
| 88 | T88 | T88 Every Verilog instance uses .portname(signal) dot notation | PASS |  |
| 89 | T89 | T89 Two AND instances → one VHDL component decl + two port maps | PASS |  |
| 90 | T90 | T90 VHDL architecture has one 'begin' and ends with 'end Structural;' | PASS |  |
| 91 | T91 | T91 Canvas with no IO pins yields empty port list in both HDLs | PASS |  |
| 92 | T92 | T92 Testbench contains 'Simulation complete' report statement | PASS |  |

_92/92 passed, 0 skipped._
