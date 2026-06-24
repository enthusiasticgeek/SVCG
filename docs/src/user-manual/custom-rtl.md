# Custom RTL Blocks & AI Generation

Custom RTL blocks let you define behavioral or RTL logic that goes beyond the standard gate library. The block appears on the canvas and connects to other blocks exactly like a built-in gate.

## Adding a Custom RTL Block

1. Open the **Custom RTL** expander in the left panel → click **Add Custom RTL Block**.
2. Enter the entity/module name, comma-separated input port names, and output port names.
3. Optionally describe the desired behavior and click **"Generate with AI"** — the AI writes the HDL body.
4. Edit the generated code as needed in the editor pane.
5. Click **OK**. The block appears on the canvas.

The entity/module *declaration* (port list) is auto-generated from the names you entered; you provide only the architecture body (VHDL) or module body (Verilog).

## Language awareness

The dialog matches the active HDL language. Code written in VHDL mode is stored separately from Verilog mode, so switching languages and re-editing does not overwrite your work.

## AI Backend

The dialog has an **AI Backend** dropdown:

| Backend | Model picker | Needs |
|---|---|---|
| Auto-detect | Ollama models (live list) | nothing — falls back automatically |
| Ollama (local, free) | all pulled Ollama models | `ollama serve` running |
| Anthropic (cloud) | haiku / sonnet | `ANTHROPIC_API_KEY` env var |
| OpenAI (cloud) | gpt-4o-mini / gpt-4o / … | `OPENAI_API_KEY` env var |
| Cursor / Custom (OpenAI-compatible) | configurable + endpoint URL | `CURSOR_API_KEY` or `OPENAI_API_KEY` |

## Viewing the generated HDL

Right-click the Custom RTL block on canvas → **"View VHDL/Verilog Code"** shows the complete auto-generated entity/module declaration wrapped around your architecture body.

## Export behavior

- In the structural VHDL netlist, custom blocks appear as `component` declarations with sanitized port names. Their full VHDL source is compiled alongside the top-level entity.
- In the structural Verilog netlist, custom blocks appear as module instantiations. The Verilog body is compiled with iverilog if available.
