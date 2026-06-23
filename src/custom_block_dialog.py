#!/usr/bin/env python3
"""
custom_block_dialog.py -- GTK dialog for defining a Custom RTL Block.

The user fills in:
  - Entity name (used as component name in generated VHDL)
  - Input port names (comma-separated)
  - Output port names (comma-separated)
  - Architecture body VHDL (the entity declaration is auto-generated)
"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

_ARCH_TEMPLATE = """\
-- Write your behavioral or structural architecture here.
-- The entity declaration is generated automatically from the ports above.
--
-- Example (D flip-flop with async reset):
--
-- architecture rtl of MY_BLOCK is
-- begin
--   process(clk, rst)
--   begin
--     if rst = '0' then
--       q <= '0';
--     elsif rising_edge(clk) then
--       q <= d;
--     end if;
--   end process;
-- end architecture rtl;
"""


class CustomBlockDialog(Gtk.Dialog):
    """
    Dialog to create or edit a Custom RTL block.

    Pass `existing` (a custom_data dict) to pre-populate the fields for editing.
    Call `get_data()` after the dialog is accepted to retrieve the new custom_data.
    """

    def __init__(self, parent, existing=None):
        super().__init__(title="Custom RTL Block", transient_for=parent, flags=0)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK,     Gtk.ResponseType.OK,
        )
        self.set_default_size(640, 520)
        self.set_default_response(Gtk.ResponseType.OK)

        content = self.get_content_area()
        grid = Gtk.Grid(row_spacing=8, column_spacing=10, margin=10)
        content.pack_start(grid, True, True, 0)

        # Entity name
        grid.attach(Gtk.Label(label="Entity Name:", halign=Gtk.Align.END), 0, 0, 1, 1)
        self._entity_entry = Gtk.Entry()
        self._entity_entry.set_hexpand(True)
        self._entity_entry.set_activates_default(True)
        self._entity_entry.set_placeholder_text("e.g. MY_COUNTER")
        grid.attach(self._entity_entry, 1, 0, 1, 1)

        # Input ports
        grid.attach(Gtk.Label(label="Input Ports:", halign=Gtk.Align.END), 0, 1, 1, 1)
        self._inputs_entry = Gtk.Entry()
        self._inputs_entry.set_placeholder_text("comma-separated, e.g.  clk, rst, d")
        self._inputs_entry.set_hexpand(True)
        grid.attach(self._inputs_entry, 1, 1, 1, 1)

        # Output ports
        grid.attach(Gtk.Label(label="Output Ports:", halign=Gtk.Align.END), 0, 2, 1, 1)
        self._outputs_entry = Gtk.Entry()
        self._outputs_entry.set_placeholder_text("comma-separated, e.g.  q, q_bar")
        self._outputs_entry.set_hexpand(True)
        grid.attach(self._outputs_entry, 1, 2, 1, 1)

        # Hint
        hint = Gtk.Label(
            label="The entity declaration is auto-generated. Write only the architecture body below.",
            halign=Gtk.Align.START,
            margin_top=4,
        )
        hint.set_line_wrap(True)
        grid.attach(hint, 0, 3, 2, 1)

        # VHDL architecture editor
        grid.attach(Gtk.Label(label="Architecture:", halign=Gtk.Align.END, valign=Gtk.Align.START), 0, 4, 1, 1)
        self._vhdl_view = Gtk.TextView()
        self._vhdl_view.set_monospace(True)
        self._vhdl_view.set_wrap_mode(Gtk.WrapMode.NONE)
        sw = Gtk.ScrolledWindow()
        sw.set_size_request(-1, 260)
        sw.set_hexpand(True)
        sw.set_vexpand(True)
        sw.add(self._vhdl_view)
        grid.attach(sw, 1, 4, 1, 1)

        if existing:
            self._entity_entry.set_text(existing.get("entity_name", ""))
            self._inputs_entry.set_text(", ".join(existing.get("input_names", [])))
            self._outputs_entry.set_text(", ".join(existing.get("output_names", [])))
            self._vhdl_view.get_buffer().set_text(existing.get("vhdl", ""))
        else:
            self._vhdl_view.get_buffer().set_text(_ARCH_TEMPLATE)

        self.show_all()

    def get_data(self):
        """Return a custom_data dict with entity_name, input_names, output_names, vhdl."""
        entity = self._entity_entry.get_text().strip() or "MY_BLOCK"
        in_names  = [s.strip() for s in self._inputs_entry.get_text().split(",")  if s.strip()]
        out_names = [s.strip() for s in self._outputs_entry.get_text().split(",") if s.strip()]
        buf = self._vhdl_view.get_buffer()
        vhdl = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), True)
        return {
            "entity_name":  entity,
            "input_names":  in_names,
            "output_names": out_names,
            "vhdl":         vhdl,
        }
