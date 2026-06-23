#!/usr/bin/env python3
"""
custom_block_dialog.py -- GTK dialog for defining a Custom RTL Block.

Supported AI backends (selectable from a dropdown in the dialog):
  - Auto-detect          tries Ollama first, then Anthropic
  - Ollama  (local)      http://localhost:11434  — free, no key needed
  - Anthropic (cloud)    https://api.anthropic.com — needs ANTHROPIC_API_KEY
  - OpenAI  (cloud)      https://api.openai.com   — needs OPENAI_API_KEY
  - Custom / Cursor      any OpenAI-compatible endpoint (user supplies URL)
                         needs OPENAI_API_KEY or CURSOR_API_KEY env var
"""
import json
import os
import re
import threading
import urllib.request
import urllib.error

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

_ARCH_TEMPLATE_VHDL = """\
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

_ARCH_TEMPLATE_VERILOG = """\
// Write your module body here.
// The module header (port list) is generated automatically from the ports above.
// Do NOT add 'module ...' or 'endmodule' — they are added automatically.
//
// Example (D flip-flop with async reset):
//
// reg q_reg;
// always @(posedge clk or posedge rst) begin
//     if (rst) q_reg <= 1'b0;
//     else     q_reg <= d;
// end
// assign q = q_reg;
"""

# Ollama
_OLLAMA_BASE          = "http://localhost:11434"
_OLLAMA_CHAT          = _OLLAMA_BASE + "/api/chat"
_OLLAMA_TAGS          = _OLLAMA_BASE + "/api/tags"
_OLLAMA_DEFAULT_MODEL = "phi3:mini"

# Anthropic
_ANTHROPIC_URL    = "https://api.anthropic.com/v1/messages"
_ANTHROPIC_MODELS = ["claude-haiku-4-5-20251001", "claude-sonnet-4-6"]

# OpenAI
_OPENAI_URL    = "https://api.openai.com/v1/chat/completions"
_OPENAI_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]

# Backend IDs
_BACKEND_AUTO      = "auto"
_BACKEND_OLLAMA    = "ollama"
_BACKEND_ANTHROPIC = "anthropic"
_BACKEND_OPENAI    = "openai"
_BACKEND_CUSTOM    = "custom"   # OpenAI-compatible: Cursor, LM Studio, Jan.ai, …

_BACKEND_LABELS = [
    (_BACKEND_AUTO,      "Auto-detect"),
    (_BACKEND_OLLAMA,    "Ollama  (local, free)"),
    (_BACKEND_ANTHROPIC, "Anthropic  (cloud)"),
    (_BACKEND_OPENAI,    "OpenAI  (cloud)"),
    (_BACKEND_CUSTOM,    "Cursor / Custom  (OpenAI-compatible)"),
]

# Default URL hint shown in the custom URL field per backend
_CUSTOM_URL_HINTS = {
    _BACKEND_CUSTOM: "https://api.cursor.sh/v1/chat/completions",
}


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _build_prompt(entity, in_names, out_names, description, language="vhdl"):
    ports_desc = ""
    if in_names:
        ports_desc += "Inputs:  " + ", ".join(in_names) + "\n"
    if out_names:
        ports_desc += "Outputs: " + ", ".join(out_names) + "\n"

    if language == "verilog":
        return (
            f"Write a Verilog module body for the following module.\n\n"
            f"Module name: {entity}\n"
            f"{ports_desc}"
            f"Description: {description or 'Not provided — infer from port names.'}\n\n"
            "Requirements:\n"
            "- Output ONLY the module body (signal/reg declarations and logic)\n"
            "- Do NOT include the 'module' header line or 'endmodule'\n"
            "- All ports are 1-bit (wire for inputs, reg for outputs unless combinational)\n"
            "- Use synthesisable Verilog-2001 or SystemVerilog\n"
            "- Add brief comments explaining key steps"
        )
    else:
        return (
            f"Write a VHDL architecture body for the following entity.\n\n"
            f"Entity name: {entity}\n"
            f"{ports_desc}"
            f"Description: {description or 'Not provided — infer from port names.'}\n\n"
            "Requirements:\n"
            "- Output ONLY the architecture block (starting with 'architecture ...' "
            "and ending with 'end architecture ...;')\n"
            "- Use STD_LOGIC_1164 only (no NUMERIC_STD unless essential)\n"
            "- Include a complete, synthesisable behavioral implementation\n"
            "- Add brief comments explaining key steps\n"
            "- Do NOT include the entity declaration or library/use clauses"
        )


def _strip_fences(text):
    """Remove markdown ```vhdl...``` wrappers if the model added them."""
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    return text.strip()


def _fetch_ollama_models():
    """Return list of model name strings from the local Ollama instance, or []."""
    try:
        req = urllib.request.Request(_OLLAMA_TAGS, method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
        return [m.get("name", "") for m in data.get("models", []) if m.get("name")]
    except Exception:
        return []


def _ollama_available():
    return bool(_fetch_ollama_models())


# ---------------------------------------------------------------------------
# Per-backend call functions — all run in a background thread and deliver
# results via GLib.idle_add(callback, arch_text_or_None, error_or_None).
# ---------------------------------------------------------------------------

def _call_ollama(model, prompt, callback):
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }).encode()
    req = urllib.request.Request(
        _OLLAMA_CHAT, data=payload,
        headers={"content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read())
        GLib.idle_add(callback, _strip_fences(body["message"]["content"]), None)
    except Exception as e:
        GLib.idle_add(callback, None, f"Ollama error: {e}")


def _call_anthropic(model, prompt, callback):
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        GLib.idle_add(callback, None,
            "ANTHROPIC_API_KEY environment variable is not set.\n\n"
            "Set it before launching SVCG, or choose a different backend.")
        return
    payload = json.dumps({
        "model": model,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        _ANTHROPIC_URL, data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read())
        GLib.idle_add(callback, _strip_fences(body["content"][0]["text"]), None)
    except urllib.error.HTTPError as e:
        GLib.idle_add(callback, None,
            f"Anthropic API error {e.code}: {e.read().decode()[:300]}")
    except Exception as e:
        GLib.idle_add(callback, None, str(e))


def _call_openai_compat(url, model, api_key, prompt, callback):
    """
    Generic OpenAI-compatible chat completions call.
    Used for both the 'openai' backend and 'custom' (Cursor, LM Studio, …).
    """
    if not api_key:
        GLib.idle_add(callback, None,
            "No API key found.\n\n"
            "For OpenAI:  set OPENAI_API_KEY\n"
            "For Cursor:  set CURSOR_API_KEY  (or OPENAI_API_KEY)\n"
            "For local servers (LM Studio etc.): key can be any non-empty string.")
        return
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
    }).encode()
    req = urllib.request.Request(
        url, data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "content-type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read())
        text = body["choices"][0]["message"]["content"]
        GLib.idle_add(callback, _strip_fences(text), None)
    except urllib.error.HTTPError as e:
        GLib.idle_add(callback, None,
            f"API error {e.code}: {e.read().decode()[:300]}")
    except Exception as e:
        GLib.idle_add(callback, None, str(e))


def _openai_api_key():
    return os.environ.get("OPENAI_API_KEY", "")


def _cursor_api_key():
    return (os.environ.get("CURSOR_API_KEY") or
            os.environ.get("OPENAI_API_KEY") or "")


# ---------------------------------------------------------------------------
# Dialog
# ---------------------------------------------------------------------------

class CustomBlockDialog(Gtk.Dialog):
    """
    Dialog to create or edit a Custom RTL block.

    Pass `existing` (a custom_data dict) to pre-populate fields for editing.
    Call `get_data()` after the dialog is accepted to retrieve the new data.
    """

    def __init__(self, parent, existing=None, language="vhdl"):
        self._language = language.lower()
        lang_label = "VHDL" if self._language == "vhdl" else "Verilog"
        super().__init__(title=f"Custom RTL Block ({lang_label})", transient_for=parent, flags=0)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK,     Gtk.ResponseType.OK,
        )
        self.set_default_size(700, 640)
        self.set_default_response(Gtk.ResponseType.OK)

        content = self.get_content_area()
        grid = Gtk.Grid(row_spacing=8, column_spacing=10, margin=10)
        content.pack_start(grid, True, True, 0)

        row = 0

        # --- Entity name ---
        grid.attach(Gtk.Label(label="Entity Name:", halign=Gtk.Align.END), 0, row, 1, 1)
        self._entity_entry = Gtk.Entry()
        self._entity_entry.set_hexpand(True)
        self._entity_entry.set_activates_default(True)
        self._entity_entry.set_placeholder_text("e.g. MY_COUNTER")
        grid.attach(self._entity_entry, 1, row, 1, 1)
        row += 1

        # --- Input ports ---
        grid.attach(Gtk.Label(label="Input Ports:", halign=Gtk.Align.END), 0, row, 1, 1)
        self._inputs_entry = Gtk.Entry()
        self._inputs_entry.set_placeholder_text("comma-separated, e.g.  clk, rst, d")
        self._inputs_entry.set_hexpand(True)
        grid.attach(self._inputs_entry, 1, row, 1, 1)
        row += 1

        # --- Output ports ---
        grid.attach(Gtk.Label(label="Output Ports:", halign=Gtk.Align.END), 0, row, 1, 1)
        self._outputs_entry = Gtk.Entry()
        self._outputs_entry.set_placeholder_text("comma-separated, e.g.  q, q_bar")
        self._outputs_entry.set_hexpand(True)
        grid.attach(self._outputs_entry, 1, row, 1, 1)
        row += 1

        # --- AI Backend + Model selector ---
        grid.attach(Gtk.Label(label="AI Backend:", halign=Gtk.Align.END), 0, row, 1, 1)
        backend_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        backend_box.set_hexpand(True)

        self._backend_combo = Gtk.ComboBoxText()
        for bid, blabel in _BACKEND_LABELS:
            self._backend_combo.append(bid, blabel)
        self._backend_combo.set_active_id(_BACKEND_AUTO)
        self._backend_combo.connect("changed", self._on_backend_changed)
        backend_box.pack_start(self._backend_combo, False, False, 0)

        self._model_combo = Gtk.ComboBoxText()
        self._model_combo.set_hexpand(True)
        self._model_combo.append_text(_OLLAMA_DEFAULT_MODEL)
        self._model_combo.set_active(0)
        backend_box.pack_start(self._model_combo, True, True, 0)

        grid.attach(backend_box, 1, row, 1, 1)
        row += 1

        # --- Custom URL row (shown only for CUSTOM backend) ---
        self._url_label = Gtk.Label(label="Endpoint URL:", halign=Gtk.Align.END)
        grid.attach(self._url_label, 0, row, 1, 1)
        self._url_entry = Gtk.Entry()
        self._url_entry.set_hexpand(True)
        self._url_entry.set_placeholder_text(
            "e.g. https://api.cursor.sh/v1/chat/completions  or  http://localhost:1234/v1/chat/completions")
        grid.attach(self._url_entry, 1, row, 1, 1)
        self._url_label.set_no_show_all(True)
        self._url_entry.set_no_show_all(True)
        row += 1

        # --- AI Description + Generate button ---
        grid.attach(Gtk.Label(label="AI Description:", halign=Gtk.Align.END), 0, row, 1, 1)
        ai_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        ai_row.set_hexpand(True)
        self._ai_desc_entry = Gtk.Entry()
        self._ai_desc_entry.set_placeholder_text(
            "Optional: describe behavior, e.g. '4-bit up counter, sync reset'")
        self._ai_desc_entry.set_hexpand(True)
        ai_row.pack_start(self._ai_desc_entry, True, True, 0)
        self._ai_btn = Gtk.Button(label="Generate with AI")
        self._ai_btn.connect("clicked", self._on_generate_ai)
        ai_row.pack_start(self._ai_btn, False, False, 0)
        grid.attach(ai_row, 1, row, 1, 1)
        row += 1

        # --- Status label ---
        self._status_label = Gtk.Label(halign=Gtk.Align.START)
        self._status_label.set_markup("<small><i>Checking AI backend…</i></small>")
        grid.attach(self._status_label, 1, row, 1, 1)
        row += 1

        # --- Hint ---
        if self._language == "verilog":
            hint_text = ("The module header (port list) is auto-generated. "
                         "Write only the module body below (no 'module'/'endmodule').")
        else:
            hint_text = "The entity declaration is auto-generated. Write only the architecture body below."
        hint = Gtk.Label(label=hint_text, halign=Gtk.Align.START)
        hint.set_line_wrap(True)
        grid.attach(hint, 0, row, 2, 1)
        row += 1

        # --- HDL code editor ---
        body_label = "Module Body:" if self._language == "verilog" else "Architecture:"
        grid.attach(Gtk.Label(label=body_label, halign=Gtk.Align.END,
                               valign=Gtk.Align.START), 0, row, 1, 1)
        self._vhdl_view = Gtk.TextView()
        self._vhdl_view.set_monospace(True)
        self._vhdl_view.set_wrap_mode(Gtk.WrapMode.NONE)
        sw = Gtk.ScrolledWindow()
        sw.set_size_request(-1, 200)
        sw.set_hexpand(True)
        sw.set_vexpand(True)
        sw.add(self._vhdl_view)
        grid.attach(sw, 1, row, 1, 1)

        # Pre-populate if editing existing block
        if existing:
            self._entity_entry.set_text(existing.get("entity_name", ""))
            self._inputs_entry.set_text(", ".join(existing.get("input_names", [])))
            self._outputs_entry.set_text(", ".join(existing.get("output_names", [])))
            if self._language == "verilog":
                code = existing.get("verilog_body", existing.get("vhdl", ""))
            else:
                code = existing.get("vhdl_body", existing.get("vhdl", ""))
            self._vhdl_view.get_buffer().set_text(code)
        else:
            tmpl = _ARCH_TEMPLATE_VERILOG if self._language == "verilog" else _ARCH_TEMPLATE_VHDL
            self._vhdl_view.get_buffer().set_text(tmpl)

        self.show_all()

        # Populate Ollama models and refresh status asynchronously
        threading.Thread(target=self._refresh_ollama_models, daemon=True).start()

    # ------------------------------------------------------------------
    # Backend / model management
    # ------------------------------------------------------------------

    def _refresh_ollama_models(self):
        models = _fetch_ollama_models()
        GLib.idle_add(self._apply_ollama_models, models)

    def _apply_ollama_models(self, models):
        """Rebuild the model combo with Ollama models (called on GTK thread)."""
        current = self._model_combo.get_active_text() or _OLLAMA_DEFAULT_MODEL
        while len(self._model_combo.get_model()):
            self._model_combo.remove(0)

        if models:
            for m in models:
                self._model_combo.append_text(m)
            restored = False
            for i, m in enumerate(models):
                if m == current:
                    self._model_combo.set_active(i)
                    restored = True
                    break
            if not restored:
                self._model_combo.set_active(0)
        else:
            self._model_combo.append_text(_OLLAMA_DEFAULT_MODEL + "  (not pulled)")
            self._model_combo.set_active(0)

        self._update_status(ollama_models=models)

    def _set_model_list(self, models):
        """Replace model combo contents with a fixed list."""
        while len(self._model_combo.get_model()):
            self._model_combo.remove(0)
        for m in models:
            self._model_combo.append_text(m)
        self._model_combo.set_active(0)

    def _on_backend_changed(self, combo):
        backend = combo.get_active_id()

        # Show/hide custom URL row
        show_url = (backend == _BACKEND_CUSTOM)
        self._url_label.set_visible(show_url)
        self._url_entry.set_visible(show_url)

        if backend == _BACKEND_ANTHROPIC:
            self._set_model_list(_ANTHROPIC_MODELS)
            self._update_status()

        elif backend == _BACKEND_OPENAI:
            self._set_model_list(_OPENAI_MODELS)
            self._update_status()

        elif backend == _BACKEND_CUSTOM:
            # Generic model name — user types what their server expects
            self._set_model_list(["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo",
                                   "cursor-fast", "cursor-small"])
            if not self._url_entry.get_text():
                self._url_entry.set_text(_CUSTOM_URL_HINTS.get(_BACKEND_CUSTOM, ""))
            self._update_status()

        else:
            # ollama or auto → refresh live model list
            threading.Thread(target=self._refresh_ollama_models, daemon=True).start()

    def _update_status(self, ollama_models=None):
        backend = self._backend_combo.get_active_id() or _BACKEND_AUTO

        if backend == _BACKEND_ANTHROPIC:
            key_ok = bool(os.environ.get("ANTHROPIC_API_KEY"))
            self._status_label.set_markup(
                "<small><i>Anthropic cloud — "
                + ("API key found ✓" if key_ok else "set ANTHROPIC_API_KEY")
                + "</i></small>")

        elif backend == _BACKEND_OPENAI:
            key_ok = bool(_openai_api_key())
            self._status_label.set_markup(
                "<small><i>OpenAI cloud — "
                + ("API key found ✓" if key_ok else "set OPENAI_API_KEY")
                + "</i></small>")

        elif backend == _BACKEND_CUSTOM:
            key_ok = bool(_cursor_api_key())
            url = self._url_entry.get_text().strip() or "(no URL entered)"
            self._status_label.set_markup(
                f"<small><i>Custom endpoint: {url} — "
                + ("key found ✓" if key_ok else "set CURSOR_API_KEY or OPENAI_API_KEY")
                + "</i></small>")

        else:
            if ollama_models is None:
                ollama_models = _fetch_ollama_models()
            if backend == _BACKEND_OLLAMA:
                self._status_label.set_markup(
                    "<small><i>Ollama local — "
                    + ("ready ✓" if ollama_models else "not reachable (run: ollama serve)")
                    + "</i></small>")
            else:  # auto
                if ollama_models:
                    msg = "Auto → Ollama local (preferred) ✓"
                elif os.environ.get("ANTHROPIC_API_KEY"):
                    msg = "Auto → Anthropic cloud (Ollama unavailable)"
                else:
                    msg = "Auto → no backend available"
                self._status_label.set_markup(f"<small><i>{msg}</i></small>")

    # ------------------------------------------------------------------
    # Resolve which backend + model to actually call
    # ------------------------------------------------------------------

    def _resolve_backend_model(self):
        """
        Return (backend_id, model, extra) where extra is the custom URL for
        _BACKEND_CUSTOM, or None for all others.
        Resolves _BACKEND_AUTO to a concrete backend.
        """
        backend = self._backend_combo.get_active_id() or _BACKEND_AUTO
        # strip "(not pulled)" or similar suffixes added for display
        model = (self._model_combo.get_active_text() or "").split("  ")[0].strip()
        url   = self._url_entry.get_text().strip()

        if backend == _BACKEND_AUTO:
            if _ollama_available():
                backend = _BACKEND_OLLAMA
                if not model:
                    model = _OLLAMA_DEFAULT_MODEL
            else:
                backend = _BACKEND_ANTHROPIC
                if not model or model not in _ANTHROPIC_MODELS:
                    model = _ANTHROPIC_MODELS[0]

        return backend, model, url

    # ------------------------------------------------------------------
    # AI generation
    # ------------------------------------------------------------------

    def _on_generate_ai(self, widget):
        entity    = self._entity_entry.get_text().strip() or "MY_BLOCK"
        in_names  = [s.strip() for s in self._inputs_entry.get_text().split(",") if s.strip()]
        out_names = [s.strip() for s in self._outputs_entry.get_text().split(",") if s.strip()]
        desc      = self._ai_desc_entry.get_text().strip()

        backend, model, url = self._resolve_backend_model()

        self._ai_btn.set_label("Generating…")
        self._ai_btn.set_sensitive(False)
        self._status_label.set_markup(
            f"<small><i>Generating via {backend} / {model}…</i></small>")

        prompt = _build_prompt(entity, in_names, out_names, desc, self._language)

        if backend == _BACKEND_OLLAMA:
            args = (_call_ollama, model, prompt, self._on_ai_result)
        elif backend == _BACKEND_ANTHROPIC:
            args = (_call_anthropic, model, prompt, self._on_ai_result)
        elif backend == _BACKEND_OPENAI:
            args = (_call_openai_compat, _OPENAI_URL, model,
                    _openai_api_key(), prompt, self._on_ai_result)
        else:  # custom / cursor
            api_key = _cursor_api_key()
            if not url:
                url = _CUSTOM_URL_HINTS.get(_BACKEND_CUSTOM, "")
            args = (_call_openai_compat, url, model, api_key, prompt, self._on_ai_result)

        threading.Thread(target=args[0], args=args[1:], daemon=True).start()

    def _on_ai_result(self, arch_text, error):
        self._ai_btn.set_label("Generate with AI")
        self._ai_btn.set_sensitive(True)
        if error:
            self._status_label.set_markup("<small><i>Generation failed.</i></small>")
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
            threading.Thread(target=self._refresh_ollama_models, daemon=True).start()

    # ------------------------------------------------------------------

    def get_data(self):
        """Return a custom_data dict with entity_name, input_names, output_names, and code bodies."""
        entity    = self._entity_entry.get_text().strip() or "MY_BLOCK"
        in_names  = [s.strip() for s in self._inputs_entry.get_text().split(",")  if s.strip()]
        out_names = [s.strip() for s in self._outputs_entry.get_text().split(",") if s.strip()]
        buf = self._vhdl_view.get_buffer()
        code = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), True)
        data = {
            "entity_name":  entity,
            "input_names":  in_names,
            "output_names": out_names,
            "vhdl":         code,   # backward-compat key — always present
        }
        if self._language == "verilog":
            data["verilog_body"] = code
        else:
            data["vhdl_body"]    = code
        return data
