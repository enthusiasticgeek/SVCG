# Getting Started

## Prerequisites

### Required — Python + GTK3

#### Windows (MSYS2 MinGW64) *(recommended)*

1. Install [MSYS2](https://www.msys2.org/).
2. Open the **MSYS2 MinGW64** shell and run:

```bash
pacman -S mingw-w64-x86_64-python-gobject \
          mingw-w64-x86_64-gtk3 \
          mingw-w64-x86_64-python-cairo \
          mingw-w64-x86_64-python-numpy
```

> **Note:** Always launch SVCG from the **MSYS2 MinGW64** terminal.
> Standard Windows PowerShell/CMD does not have GTK3 Python bindings.

#### Linux (Debian/Ubuntu)

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-numpy
```

#### Linux (Fedora/RHEL)

```bash
sudo dnf install python3-gobject gtk3 python3-cairo python3-numpy
```

---

### Optional — VHDL simulation (GHDL)

Required for `File > Generate Testbench + Simulate...` and the in-preview VHDL syntax check.

#### Windows (MSYS2 MinGW64)

```bash
pacman -S mingw-w64-x86_64-ghdl-llvm
```

#### Linux

```bash
sudo apt install ghdl      # Debian/Ubuntu
sudo dnf install ghdl      # Fedora/RHEL
```

---

### Optional — Verilog syntax check (Icarus Verilog)

Used by `Generate HDL…` preview to syntax-check Verilog output. Without it the preview still works — syntax checking is simply skipped.

#### Windows (MSYS2 MinGW64)

```bash
pacman -S mingw-w64-x86_64-iverilog
```

#### Linux

```bash
sudo apt install iverilog   # Debian/Ubuntu
sudo dnf install iverilog   # Fedora/RHEL
```

---

### Optional — AI code generation (Ollama)

Used by **"Generate with AI"** in the Custom RTL Block dialog. Runs entirely locally — no API key needed.

#### Windows

```powershell
winget install Ollama.Ollama
```

Then pull the default model (Microsoft Phi-3 Mini, ~2.2 GB):

```bash
ollama pull phi3:mini
```

#### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull phi3:mini
```

Other AI backends (all optional):

| Backend | Needs |
|---|---|
| Anthropic (cloud) | `ANTHROPIC_API_KEY` env var |
| OpenAI (cloud) | `OPENAI_API_KEY` env var |
| Cursor / any OpenAI-compatible server | endpoint URL in dialog |

---

## Running SVCG

```bash
cd src
python3 main.py
```
