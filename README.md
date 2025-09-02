# ss-qsspp — Minimal QSS Preprocessor for Qt / PySide

A compact, predictable preprocessor for **Qt Style Sheets (QSS)** inspired by SCSS: variables, imports, color functions, and theme layering.  
Goal: generate clean `.qss` from source `.qsspp` files with minimal magic.

---

## Features

- **Variables** (`$primary: #1f1f1f;`) with `$var` usage
- **Relative imports**: `@import "partials/buttons.qsspp";`
- **Color functions**: `lighten(#rrggbb, 10%)`, `darken(#rrggbb, 8%)`, `alpha(#rrggbb, 0.5)`
- **Import cycle detection**
- **Safe replacement** (word-boundary) and **removal of var declarations** from the final output
- UTF-8 I/O, Windows/macOS/Linux

_Not supported by design:_ selector nesting, mixins, conditionals, loops.

---

## Installation

Local (development) install:

```bash
# optional: create a venv
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -e .
```

The CLI is installed as `ss-qssppc`.

---

## Quick Start (CLI)

Compile a single file:

```bash
ss-qssppc assets/style.qsspp -o assets/style.qss
```

Compile multiple files to a directory:

```bash
ss-qssppc "assets/themes/*.qsspp" -o build/styles
```

> PowerShell users: quote globs, e.g. `"assets/**/*.qsspp"`.

Help:

```bash
ss-qssppc --help
```

---

## Python API

Compile at runtime:

```python
from qsspp import compile_qss

css = compile_qss("assets/style.qsspp")
app.setStyleSheet(css)
```

Load a precompiled `.qss`:

```python
with open("assets/style.qss", "r", encoding="utf-8") as f:
    app.setStyleSheet(f.read())
```

---

## QSSPP Syntax

### Variables

```scss
$radius: 8px;
$text:   #EAEAEA;

QPushButton {
  border-radius: $radius;
  color: $text;
}
```

### Imports

```scss
@import "partials/forms.qsspp";
@import "../shared/colors.qsspp";
```

### Color functions

```scss
QPushButton:hover   { background: lighten(#1f1f1f, 8%); }
QPushButton:pressed { background: darken(#1f1f1f, 6%); }
QFrame { background: alpha(#000000, 0.08); }  /* outputs rgba(...) */
```

---

## Theming

Organize themes under `assets/themes/` and import common styles at the end of each theme file.

```text
assets/
├─ themes/
│  ├─ dark-theme.qsspp
│  └─ light-theme.qsspp
└─ style.qsspp
```

**Example: `assets/themes/dark-theme.qsspp`**

```scss
/* Theme variables (dark) */
$text_foreground: #8a95aa;
$form_radius: 8px;
$form_bg_color: #1b1e23;
$form_bg_color_hover: #21252d;
$form_bg_color_pressed: #272c36;

@import "../style.qsspp";
```

**Example: `assets/themes/light-theme.qsspp`**

```scss
/* Theme variables (light) */
$text_foreground: #2b2f36;
$form_radius: 8px;
$form_bg_color: #f5f7fb;
$form_bg_color_hover: #eceff5;
$form_bg_color_pressed: #e2e8f0;

@import "../style.qsspp";
```

**Common styles: `assets/style.qsspp`**

```scss
QPushButton {
  border: none;
  border-radius: $form_radius;
  color: $text_foreground;
  background: $form_bg_color;
}
QPushButton:hover   { background: $form_bg_color_hover; }
QPushButton:pressed { background: $form_bg_color_pressed; }
```

Build themed outputs:

```bash
ss-qssppc assets/themes/dark-theme.qsspp  -o assets/style-dark.qss
ss-qssppc assets/themes/light-theme.qsspp -o assets/style-light.qss
```

---

## Project layout

```text
ss_qsspp/
├─ src/
│  └─ qsspp/
│     ├─ __init__.py       # exports compile_qss
│     ├─ core.py           # preprocessor logic
│     └─ cli.py            # ss-qssppc entry point
├─ pyproject.toml
├─ README.md
└─ LICENSE
```

---

## Troubleshooting

- **Unresolved variables in output**: ensure the theme defines them *before* importing common styles; check import paths.
- **PowerShell globbing**: always quote patterns (`"assets/**/*.qsspp"`).
- **Encoding**: files are read/written in UTF-8.
- **Comments**: variable declarations are removed from output; general comments can be kept or stripped depending on configuration.

---

## License & headers

Project distributed under MIT (see `LICENSE`). Recommended SPDX headers at the top of source files:

```text
SPDX-FileCopyrightText: 2025 SCHARTIER Isaac
SPDX-License-Identifier: MIT
```

---

## Versioning & support

- Semantic Versioning: `MAJOR.MINOR.PATCH`.
- Open issues with: OS, Python version, minimal \*.qsspp snippet, expected vs. actual output, CLI command, and stack trace if any.
