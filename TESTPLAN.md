# SVCG — Adversarial Test Plan (Student-Scenario Edition)

> **Status: DRAFT — awaiting review before implementation.**
>
> This document describes *what* will be tested and *why*.
> No code is written until this plan is approved.

---

## How to read this plan

Each test case has:
- **ID** — referenced from `test_gui.py` and `TESTING.md`
- **Scenario** — the real-world student activity being simulated
- **Setup** — what the test builds on the canvas
- **Assertions** — what pass/fail means
- **Why it matters** — the real failure mode being guarded against

Test groups are ordered from "student first week" to "advanced/adversarial".

---

## TG-01 — Combinational Circuits (Week 1 coursework)

These are the first circuits a student builds.

### TC-01 · Half Adder
**Scenario:** Student places XOR (sum) and AND (carry), wires two input pins (A, B) to each gate, adds output pins (SUM, CARRY), exports VHDL.

**Setup:**
```
input_pin "A" ─┬─ XOR ─ output_pin "SUM"
               │
input_pin "B" ─┴─ AND ─ output_pin "CARRY"
```

**Assertions:**
- Canvas has 2 blocks, 4 pins, 4 wires after construction
- VHDL entity port list contains `A : in STD_LOGIC`, `B : in STD_LOGIC`, `SUM : out STD_LOGIC`, `CARRY : out STD_LOGIC`
- VHDL architecture contains `component XOR_GATE` and `component AND_GATE`
- Port map entries reference the correct signal names (not `open`)

---

### TC-02 · Full Adder (two Half Adders + OR gate)
**Scenario:** Student builds a 1-bit full adder from primitives — the standard Week 1–2 lab.

**Setup:**
```
input_pin "A" ──┐
input_pin "B" ──┤ HA_1 ─[SUM1]─ HA_2 ─ output_pin "SUM"
input_pin "CIN"─┘       [CO1]──────────┐
                                        OR ─ output_pin "COUT"
                         [CO2]──────────┘
```

**Assertions:**
- 3 blocks (HA, HA, OR), 5 pins (A, B, CIN, SUM, COUT)
- Internal wires named "sum1", "co1", "co2" appear as `signal` declarations in VHDL
- No `open` in the port maps (all pins connected)
- JSON save/reload preserves all 3 wire IDs exactly

---

### TC-03 · 2-to-1 Multiplexer
**Scenario:** Student places a MUX_2X1, connects D0, D1, SEL inputs and Y output.

**Assertions:**
- VHDL port map for MUX2x1 has `A`, `B`, `S`, `Y` mapped (not open)
- `component MUX2x1` appears in the architecture declarations

---

### TC-04 · AND Reduction Chain (3-input AND)
**Scenario:** Student chains two AND gates to implement a 3-input AND: `(A AND B) AND C`.

**Setup:** AND_1 output → AND_2 input A; input pins A, B, C; output pin Y.

**Assertions:**
- Internal net between the two AND gates appears as a `signal` in VHDL
- `AND_1_0` and `AND_2_1` instance names appear in port maps
- Round-trip save/load preserves the two-gate chain

---

### TC-05 · NOT Chain (odd/even inversion sanity check)
**Scenario:** Chain 3 NOT gates. Net at gate 1 output should be inverted; net at gate 3 output should also be inverted.

**Assertions:**
- 3 NOT blocks, 1 input pin, 1 output pin created without error
- VHDL has 3 `component NOT_GATE` usages (one `component` declaration, three port maps)
- 2 internal signals declared

---

## TG-02 — Sequential Circuits (Week 3–4 coursework)

### TC-06 · D Flip-Flop with Clock
**Scenario:** Simplest clocked circuit — DFF with CLK pin, D input, Q output.

**Assertions:**
- VHDL entity port list: `D : in STD_LOGIC`, `clk : in STD_LOGIC`, `Q : out STD_LOGIC`
- Port map `D => D`, `C => clk`, `Q => Q` (using PORT_MAP mapping)
- Testbench generation for this circuit includes a clock process with 10 ns half-period
- Testbench has stimulus for D (toggle high/low)

---

### TC-07 · JK Flip-Flop
**Scenario:** Student uses JKFF block with J, K, CLK inputs and Q, Q_bar outputs.

**Assertions:**
- VHDL contains `component JKFF`
- `Q_bar` port name appears (not `Q'` — the rename must apply)
- No crash when output pin named "Q'" is processed by `_vhdl_port_name`

---

### TC-08 · SR Flip-Flop
**Scenario:** SRFF with S, R, CLK inputs.

**Assertions:**
- VHDL generates without error
- Port map contains `S =>`, `R =>`, `Q =>`

---

## TG-03 — VHDL Output Correctness

These tests check the *content* of generated VHDL, not just that it runs.

### TC-09 · Port names match pin text labels exactly
**Scenario:** Student names pins "my_input", "my_output" — these must appear verbatim in the VHDL entity (no UUID, no timestamp).

**Assertions:**
- `my_input : in STD_LOGIC` appears in entity port list
- `my_output : out STD_LOGIC` appears in entity port list

---

### TC-10 · Internal wire net name → signal declaration
**Scenario:** Student right-clicks a wire and sets net name to "internal_carry". The VHDL must declare `signal internal_carry : STD_LOGIC;`.

**Assertions:**
- `signal internal_carry : STD_LOGIC;` appears in architecture declarations
- The net name is used (not the wire UUID) in the port maps that reference it

---

### TC-11 · Wire net name with spaces → sanitized
**Scenario:** Student accidentally names a wire "sum out" (with a space).

**Assertions:**
- VHDL signal name becomes `sum_out` (space replaced with underscore)
- No VHDL syntax error (no raw space in identifier)

---

### TC-12 · Unconnected block pin → "open" in port map
**Scenario:** Student adds a 2-input AND gate but only connects one input. The unconnected input should map to `open` in VHDL.

**Assertions:**
- Port map for the unconnected input contains `=> open`
- No crash, no KeyError, no empty string port name

---

### TC-13 · All port directions correct
**Scenario:** Entity with `input_pin`, `output_pin`, and `input_output_pin` — all three directions must appear.

**Assertions:**
- `in STD_LOGIC` appears for input pin
- `out STD_LOGIC` appears for output pin
- `inout STD_LOGIC` appears for bidirectional pin

---

### TC-14 · Pin with illegal VHDL identifier → sanitized
**Scenario:** Student names pins "3V_power", "signal!out", "my-net" (digit start, exclamation mark, hyphen).

**Assertions:**
- "3V_power" → `sig_3V_power` (digit prefix handled)
- "signal!out" → `signal_out` (! removed)
- "my-net" → `my_net` (hyphen → underscore)
- Generated VHDL does not contain the raw illegal identifier

---

## TG-04 — Save / Load Round-Trip (Data Fidelity)

### TC-15 · Half adder round-trip — counts preserved
**Assertions:** After save + reload, block/pin/wire counts are identical to before save.

### TC-16 · Wire IDs preserved after save/load
**Scenario:** Wire ID links blocks together; if IDs change on reload, port maps break.

**Assertions:** Each wire loaded from JSON has the same `.id` as the wire that was saved.

### TC-17 · Block colors preserved
**Scenario:** Student customises a block's fill color — it must survive save/reload.

**Assertions:** `block.fill_color` after reload equals the original tuple.

### TC-18 · Wire net names preserved
**Assertions:** `wire.text` after reload equals the name set before save.

### TC-19 · Wire at canvas origin survives reload (regression for fixed bug)
**Scenario:** Any wire where `start_point = [0, 0]` was silently dropped before the fix.

**Assertions:** Wire count after reload equals wire count before save when origin-point wire is present.

---

## TG-05 — Adversarial / Student-Mistake Edge Cases

### TC-20 · Block placed at extreme position (x=0, y=0)
**Assertions:** Block created, `elements_to_json` succeeds, save/load round-trip works.

### TC-21 · Wire from input pin to another input pin (student wiring mistake)
**Scenario:** Student accidentally draws a wire from one input pin's connection point to another input pin's connection point.

**Assertions:** Wire is created without crash; VHDL export does not crash; the wire appears in the JSON.

### TC-22 · Duplicate wire detection
**Scenario:** Student draws the exact same wire twice (same start and end points).

**Assertions:** Second wire is NOT added (`on_button_release` duplicate check fires); `len(wires)` stays the same.

### TC-23 · Overlapping blocks (two blocks at identical x, y)
**Assertions:** Both blocks exist on canvas; `elements_to_json` includes both; no crash.

### TC-24 · Pin name >200 characters long
**Assertions:** `_sanitize()` returns a string; VHDL generation does not crash; output is valid Python string.

### TC-25 · Pin named with only digits ("123")
**Assertions:** `_sanitize("123")` returns `"sig_123"` (digit-start fix applied).

### TC-26 · Wire net name with Unicode characters ("Σout", "clk→Q")
**Assertions:** `_sanitize()` returns ASCII-only string; VHDL generation does not crash.

### TC-27 · Undo past the beginning of history (empty stack)
**Assertions:** `undo()` on empty stack → canvas unchanged, no exception.

### TC-28 · 30 undo push/pop cycles — stack stays consistent
**Scenario:** Push undo 30 times, then undo 30 times, then redo 30 times.

**Assertions:** After all 30 redos, canvas state equals the final pushed state; stack lengths are consistent.

---

## TG-06 — Component Library

### TC-29 · Save half adder selection as component
**Assertions:** File appears in `src/components/` with correct `.json` extension; file is valid JSON with `"blocks"`, `"pins"`, `"wires"` keys.

### TC-30 · Instantiate saved component — fresh IDs
**Assertions:** All blocks/pins/wires in the new instance have IDs different from the original saved component.

### TC-31 · Instantiate same component twice — no ID collisions
**Assertions:** No two objects in `win.blocks + win.pins + win.wires` share the same `.id` after double instantiation.

### TC-32 · Load malformed component JSON
**Assertions:** `instantiate_component()` does not crash; canvas is unchanged.

---

## TG-07 — Testbench Quality

### TC-33 · UUT port map signal names match entity ports
**Scenario:** If entity has port `A`, testbench UUT port map must have `A => A`.

**Assertions:** For each `(pname, _)` in the port list, the string `f"{pname} => {pname}"` appears in the testbench.

### TC-34 · Clock half-period is 5 ns
**Assertions:** Testbench contains `wait for 5 ns;` in the clock process.

### TC-35 · All non-CLK inputs get stimulus
**Scenario:** Entity with ports A, B (inputs) and CLK — A and B must both get `<= '1'; wait for 10 ns; <= '0'; wait for 10 ns;`.

**Assertions:** `A <= '1';` and `B <= '1';` both appear in the `stim_proc` process.

### TC-36 · Bus pin expands to individual bits in testbench
**Scenario:** input_bus with 4 pins → testbench has 4 separate signals.

**Assertions:** Testbench port list has 4 entries named `bus_0`, `bus_1`, `bus_2`, `bus_3`.

---

## TG-08 — Export File Format Integrity

### TC-37 · SVG file has valid SVG header
**Assertions:** File starts with `<?xml` or `<svg`; can be opened by an SVG parser.

### TC-38 · PNG file has valid magic bytes
**Assertions:** First 8 bytes equal `b'\x89PNG\r\n\x1a\n'` (PNG signature).

### TC-39 · Export with empty canvas returns early (no crash, no empty file)
**Assertions:** `on_export_svg` / `on_export_png` return without producing a 0-byte file when canvas is empty.

### TC-40 · Bounding box padding is exactly 40px
**Assertions:** `_compute_bbox(padding=40)` returns `x0 = min_x - 40` and `x1 = max_x + 40`.

---

## TG-09 — Wire Routing Robustness

### TC-41 · Long diagonal wire (top-left → bottom-right, 30+ cells apart)
**Assertions:** `wire.path` is non-empty; path starts near start_point and ends near end_point.

### TC-42 · A* bounding-box fallback triggered (endpoints >25 cells apart on one axis)
**Assertions:** Wire path is computed via full-grid A* fallback and is non-empty.

### TC-43 · Manhattan fallback path is geometrically correct
**Scenario:** Manually call `_manhattan_path((0,0), (5,3))`.

**Assertions:** Path starts at (0,0), ends at (5,3); every consecutive step is exactly 1 cell apart; no duplicates.

### TC-44 · Wire path has no duplicate consecutive points
**Scenario:** Create a wire across a crowded canvas.

**Assertions:** No two adjacent points in `wire.path` are identical.

### TC-45 · 20-wire bus pattern — all paths non-empty
**Scenario:** Create 20 wires from a column of input pins to a column of output pins (standard bus).

**Assertions:** All 20 wires have `path` length > 1.

---

## TG-10 — Yosys Import

### TC-46 · Simple AND+OR Yosys JSON import
**Setup:** Minimal Yosys JSON with one `$_AND_` and one `$_OR_` cell and two module ports.

**Assertions:**
- 2 blocks added to canvas (AND, OR)
- `n_cells_added == 2` returned
- `warnings` list is empty

### TC-47 · Import with unsupported cell type
**Setup:** Yosys JSON containing a `$_TRIBUF_` cell (not in `YOSYS_TO_SVCG`).

**Assertions:** Unsupported cell skipped; warning logged; no crash; supported cells still imported.

### TC-48 · Import empty Yosys JSON `{}`
**Assertions:** Returns `(0, 0, ["No modules found in JSON."])`; canvas unchanged.

### TC-49 · Import JSON where same net bit appears in two output drivers (multi-driver net)
**Assertions:** Import completes without crash; wires created for at least one driver; no `AttributeError`.

---

## Summary Table

| Group | Tests | Focus |
|-------|-------|-------|
| TG-01 | TC-01 – TC-05 | Combinational circuits a student builds in week 1 |
| TG-02 | TC-06 – TC-08 | Sequential circuits (DFF, JKFF, SRFF) |
| TG-03 | TC-09 – TC-14 | VHDL content correctness |
| TG-04 | TC-15 – TC-19 | JSON save/load fidelity |
| TG-05 | TC-20 – TC-28 | Adversarial / student-mistake edge cases |
| TG-06 | TC-29 – TC-32 | Component library |
| TG-07 | TC-33 – TC-36 | Testbench generation quality |
| TG-08 | TC-37 – TC-40 | Export file format integrity |
| TG-09 | TC-41 – TC-45 | Wire routing robustness |
| TG-10 | TC-46 – TC-49 | Yosys JSON import |
| **Total** | **49 new tests** | |

Combined with the existing 58 tests in `test_gui.py` → **107 tests total** once this plan is implemented.

---

## Implementation caveats

### C-1 · Grid initialisation before wire routing
`wire.calculate_path_astar()` reads `win.drawing_area.grid`.
That grid is normally created inside `DrawingArea.on_draw()` the first time the canvas is painted.
In the headless test runner the window is visible but tests run 600 ms after `show_all()`, so the
first `on_draw` has already fired and `grid` is set.
Any test that creates wires **must** call `win.drawing_area.create_grid(5000, 5000, gs)` first to
ensure the grid reflects the current block/pin layout; otherwise A* may route through a stale
obstacle map.

### C-2 · Wire connection registration
Normally `on_button_release` registers a new wire's ID into `block.input_wires[i]` / `block.output_wires[i]`
and `pin.wires[i]`.  VHDL tests (TC-01 to TC-08) need correct port-map signal resolution, which
depends on those wire lists.
A helper `connect_wire(win, src, src_idx, src_role, dst, dst_idx, dst_role, net)` is used:
it reads the actual canvas coordinates from the object's connection-point lists, creates a `Wire`,
appends its ID to both endpoint objects, and appends the wire to `win.wires`.
`src_role` / `dst_role` is `"input"` or `"output"` for blocks, `"pin"` for Pin objects.

### C-3 · TC-22 (duplicate wire) — no synthetic mouse events
The duplicate-wire guard sits inside `on_button_release`, which is not called in headless tests.
TC-22 replicates the exact guard expression from `event_handler.py` directly and asserts it
evaluates to `True` for an identical wire — confirming the logic is correct without needing mouse input.

### C-4 · TC-42 (A* bounding-box fallback) — forced with a blocked sub-grid
The A* bbox optimisation only falls back to full-grid when the sub-grid path is blocked.
TC-42 places a wall of blocks across the direct path between two points that are ≤ 25 cells apart,
rebuilds the grid, and verifies the wire uses the full-grid fallback (path length > what the
sub-grid could have produced).

### C-5 · TC-43 (Manhattan path geometry) — unit-tested without canvas
`Wire._manhattan_path` is a pure function; TC-43 calls it directly with known inputs and checks
every step, duplicate-free, starts at origin, ends at the given target.

### C-6 · TC-36 (bus pin in testbench) — bit expansion
`testbench_gen.generate_testbench` expands bus pins via `"bus" in ptype.lower()` and `pin.num_pins`.
TC-36 builds a 4-bit `input_bus` Pin (`num_pins=4`) and checks the testbench port list contains
four distinct signal names.

### C-7 · TC-46–TC-49 (Yosys) — synthetic JSON, no Yosys binary
The Yosys tests construct minimal valid Yosys-format dicts in Python and write them to a temp
`.json` file, then call `import_yosys_json(path, win)`.  No real Yosys binary is required.

### C-8 · GHDL syntax check (TC-06, TC-07, TC-08)
If `ghdl` is on PATH the generated VHDL is passed through `check_vhdl_syntax()` and the test
asserts zero errors.  If GHDL is not available the assertion is skipped and a `[SKIP]` note is
recorded in the report.

### C-9 · Test isolation
Each test group resets `win.blocks`, `win.pins`, `win.wires`, `win.undo_stack`, `win.redo_stack`
to `[]` at the start.  Individual tests that create canvas objects clean them up at the end of
the test function to avoid cross-contamination.
