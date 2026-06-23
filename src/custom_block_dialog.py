#!/usr/bin/env python3
"""
custom_block_dialog.py -- GTK dialog for defining a Custom RTL Block.

The user fills in:
  - Entity name (used as component name in generated VHDL)
  - Input port names (comma-separated)
  - Output port names (comma-separated)
  - Architecture body VHDL (the entity declaration is auto-generated)
  - (optional) "Generate with AI" button calls Anthropic API via ANTHROPIC_API_KEY env var
"""
import json
import os
import threading
import urllib.request
import urllib.error

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

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

_API_URL = "https://api.anthropic.com/v1/messages"
_MODEL   = "claude-haiku-4-5-20251001"   # fast + cheap for code generation


def _call_claude(entity, in_names, out_names, description, callback):
    """
    Call the Anthropic Messages API in a background thread.
    Invokes callback(arch_text, error_str) on the GTK main thread when done.
    Requires ANTHROPIC_API_KEY environment variable.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        GLib.idle_add(callback, None,
            "ANTHROPIC_API_KEY environment variable is not set.\n"
            "Set it before launching SVCG:\n\n"
            "  export ANTHROPIC_API_KEY=sk-ant-...")
        return

    ports_desc = ""
    if in_names:
        ports_desc += "Inputs:  " + ", ".join(in_names) + " (all STD_LOGIC)\n"
    if out_names:
        ports_desc += "Outputs: " + ", ".join(out_names) + " (all STD_LOGIC)\n"

    user_msg = (
        f"Write a VHDL architecture body for the following entity.\n\n"
        f"Entity name: {entity}\n"
        f"{ports_desc}"
        f"Description: {description or 'Not provided — infer from port names.'}\n\n"
        "Requirements:\n"
        "- Output ONLY the architecture block (starting with 'architecture ...' and ending with 'end architecture ...;')\n"
        "- Use STD_LOGIC_1164 only (no NUMERIC_STD unless essential)\n"
        "- Include a complete, synthesisable behavioral implementation\n"
        "- Add brief comments explaining key steps\n"
        "- Do NOT include the entity declaration or library/use clauses"
    )

    payload = json.dumps({
        "model": _MODEL,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": user_msg}],
    }).encode()

    req = urllib.request.Request(
        _API_URL,
        data=payload,
        headers={
            "x-api-key":         api_key,
            "anthropic-version": "2023-06-01",
            "content-type":      "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read())
        arch_text = body["content"][0]["text"].strip()
        GLib.idle_add(callback, arch_text, None)
    except urllib.error.HTTPError as e:
        err = f"API error {e.code}: {e.read().decode()[:300]}"
        GLib.idle_add(callback, None, err)
    except Exception as e:
        GLib.idle_add(callback, None, str(e))


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
        self.set_default_size(660, 560)
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

        # AI description + button row
        grid.attach(Gtk.Label(label="AI Description:", halign=Gtk.Align.END), 0, 3, 1, 1)
        ai_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        ai_row.set_hexpand(True)
        self._ai_desc_entry = Gtk.Entry()
        self._ai_desc_entry.set_placeholder_text(
            "Optional: describe behavior, e.g. '4-bit up counter, sync reset'")
        self._ai_desc_entry.set_hexpand(True)
        ai_row.pack_start(self._ai_desc_entry, True, True, 0)
        self._ai_btn = Gtk.Button(label="Generate with AI")
        self._ai_btn.set_tooltip_text(
            "Call Claude AI to write the architecture body.\n"
            "Requires ANTHROPIC_API_KEY environment variable.")
        self._ai_btn.connect("clicked", self._on_generate_ai)
        ai_row.pack_start(self._ai_btn, False, False, 0)
        grid.attach(ai_row, 1, 3, 1, 1)

        # Hint
        hint = Gtk.Label(
            label="The entity declaration is auto-generated. Write only the architecture body below.",
            halign=Gtk.Align.START,
        )
        hint.set_line_wrap(True)
        grid.attach(hint, 0, 4, 2, 1)

        # VHDL architecture editor
        grid.attach(Gtk.Label(label="Architecture:", halign=Gtk.Align.END,
                               valign=Gtk.Align.START), 0, 5, 1, 1)
        self._vhdl_view = Gtk.TextView()
        self._vhdl_view.set_monospace(True)
        self._vhdl_view.set_wrap_mode(Gtk.WrapMode.NONE)
        sw = Gtk.ScrolledWindow()
        sw.set_size_request(-1, 240)
        sw.set_hexpand(True)
        sw.set_vexpand(True)
        sw.add(self._vhdl_view)
        grid.attach(sw, 1, 5, 1, 1)

        if existing:
            self._entity_entry.set_text(existing.get("entity_name", ""))
            self._inputs_entry.set_text(", ".join(existing.get("input_names", [])))
            self._outputs_entry.set_text(", ".join(existing.get("output_names", [])))
            self._vhdl_view.get_buffer().set_text(existing.get("vhdl", ""))
        else:
            self._vhdl_view.get_buffer().set_text(_ARCH_TEMPLATE)

        self.show_all()

    # ------------------------------------------------------------------
    # AI generation
    # ------------------------------------------------------------------

    def _on_generate_ai(self, widget):
        entity    = self._entity_entry.get_text().strip() or "MY_BLOCK"
        in_names  = [s.strip() for s in self._inputs_entry.get_text().split(",") if s.strip()]
        out_names = [s.strip() for s in self._outputs_entry.get_text().split(",") if s.strip()]
        desc      = self._ai_desc_entry.get_text().strip()

        self._ai_btn.set_label("Generating…")
        self._ai_btn.set_sensitive(False)

        thread = threading.Thread(
            target=_call_claude,
            args=(entity, in_names, out_names, desc, self._on_ai_result),
            daemon=True,
        )
        thread.start()

    def _on_ai_result(self, arch_text, error):
        self._ai_btn.set_label("Generate with AI")
        self._ai_btn.set_sensitive(True)
        if error:
            dlg = Gtk.MessageDialog(
                transient_for=self, flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="AI generation failed",
            )
            dlg.format_secondary_text(error)
            dlg.run()
            dlg.destroy()
        else:
            self._vhdl_view.get_buffer().set_text(arch_text)

    # ------------------------------------------------------------------

    def get_data(self):
        """Return a custom_data dict with entity_name, input_names, output_names, vhdl."""
        entity    = self._entity_entry.get_text().strip() or "MY_BLOCK"
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
