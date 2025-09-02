#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 SCHARTIER Isaac
# SPDX-License-Identifier: MIT

# src/qsspp/core.py

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Set

_VAR_DEF_RE = re.compile(r'^\s*\$([A-Za-z_]\w*)\s*:\s*(.+?);\s*$', re.MULTILINE)
_VAR_USE_RE = re.compile(r'\$([A-Za-z_]\w*)\b')
_IMPORT_RE = re.compile(r'^\s*@import\s+"([^"]+)"\s*;.*$', re.MULTILINE)
_FUNC_RE = re.compile(r'\b(darken|lighten|alpha)\(\s*([^,]+)\s*,\s*([^)]+)\)', re.IGNORECASE)


def _hex_to_rgb(s: str):
    s = s.strip()
    if s.startswith('#'):
        s = s[1:]
    if len(s) == 3:
        s = ''.join(ch * 2 for ch in s)
    if len(s) != 6:
        raise ValueError(f"Invalid color: #{s}")
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)
    return r, g, b


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return "#{:02X}{:02X}{:02X}".format(
        max(0, min(255, r)),
        max(0, min(255, g)),
        max(0, min(255, b)),
    )


def _parse_percent_or_float(s: str) -> float:
    s = s.strip()
    if s.endswith('%'):
        return float(s[:-1]) / 100.0
    return float(s)


def _lighten(hex_color: str, amt: str) -> str:
    r, g, b = _hex_to_rgb(hex_color)
    f = _parse_percent_or_float(amt)
    r = int(r + (255 - r) * f)
    g = int(g + (255 - g) * f)
    b = int(b + (255 - b) * f)
    return _rgb_to_hex(r, g, b)


def _darken(hex_color: str, amt: str) -> str:
    r, g, b = _hex_to_rgb(hex_color)
    f = _parse_percent_or_float(amt)
    r = int(r * (1 - f))
    g = int(g * (1 - f))
    b = int(b * (1 - f))
    return _rgb_to_hex(r, g, b)


def _alpha(hex_color: str, a: str) -> str:
    # Qt rgba(r,g,b,a) support
    r, g, b = _hex_to_rgb(hex_color)
    a_val = _parse_percent_or_float(a)
    if 0 <= a_val <= 1:
        alpha_255 = int(round(a_val * 255))
    else:
        # to 50% for exemple
        alpha_255 = int(round(_parse_percent_or_float(a) * 255))
    return f"rgba({r}, {g}, {b}, {alpha_255})"


def _apply_functions(text: str) -> str:
    def repl(m: re.Match):
        func = m.group(1).lower()
        color = m.group(2).strip()
        amt = m.group(3).strip()
        if func == 'lighten':
            return _lighten(color, amt)
        elif func == 'darken':
            return _darken(color, amt)
        elif func == 'alpha':
            return _alpha(color, amt)
        return m.group(0)

    # Repeat as long as there are functions to resolve (e.g., nested ones)
    last = None
    cur = text
    for _ in range(10):  # avoid infinite loop
        cur2 = _FUNC_RE.sub(repl, cur)
        if cur2 == cur:
            break
        cur = cur2
    return cur


def _collect(source: Path, visited: Set[Path]) -> str:
    source = source.resolve()
    if source in visited:
        raise RuntimeError(f"Import cycle detected with: {source}")
    visited.add(source)

    text = source.read_text(encoding='utf-8')

    # Résoudre les imports *avant* d'extraire les variables, pour permettre
    # d'overrider des variables après import.
    def import_repl(m: re.Match):
        rel = m.group(1)
        child = (source.parent / rel).resolve()
        if not child.exists():
            raise FileNotFoundError(f"@import not found: {child}")
        return _collect(child, visited)

    text = _IMPORT_RE.sub(import_repl, text)
    return text


def _extract_vars(text: str) -> Dict[str, str]:
    vars_: Dict[str, str] = {}
    for m in _VAR_DEF_RE.finditer(text):
        name = m.group(1)
        val = m.group(2).strip()
        vars_[name] = val
    return vars_


def _remove_comments(text: str) -> str:
    return re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)


def _remove_var_declarations(text: str) -> str:
    # remove lines that are variable declarations
    text = _VAR_DEF_RE.sub('', text)

    # remove leftover comment lines that only contain comments around variables
    lines = []
    skip_next = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # skip comments that look like "/* --- Variables --- */"
        if stripped.startswith("/*") and "Variables" in stripped and stripped.endswith("*/"):
            continue
        lines.append(line)
    return "\n".join(lines)


def _expand_vars(text: str, vars_: Dict[str, str]) -> str:
    # multi-pass resolution (if one variable uses another variable)
    resolved = dict(vars_)
    for _ in range(10):  # max depth
        changed = False
        for k, v in list(resolved.items()):
            new_v = _VAR_USE_RE.sub(lambda m: resolved.get(m.group(1), m.group(0)), v)
            if new_v != v:
                resolved[k] = new_v
                changed = True
        if not changed:
            break

    def use_repl(m: re.Match):
        key = m.group(1)
        return resolved.get(key, m.group(0))  # laisse tel quel si inconnue

    return _VAR_USE_RE.sub(use_repl, text)


def compile_qss(input_path: str | Path) -> str:
    """
    Compiles a .qsspp file into pure QSS:
    - @import
    - $var variables
    - Color functions (lighten, darken, alpha)
    """
    root = Path(input_path).resolve()
    raw = _collect(root, set())
    vars_ = _extract_vars(raw)
    without_defs = _remove_var_declarations(raw)
    without_defs = _remove_comments(without_defs)
    expanded = _expand_vars(without_defs, vars_)
    final = _apply_functions(expanded)
    return final


if __name__ == "__main__":
    import argparse, sys

    p = argparse.ArgumentParser(description="Mini QSS preprocessor (variables + functions).")
    p.add_argument("input", help="Source .qsspp file")
    p.add_argument("-o", "--output", help="Output .qss file (otherwise stdout)")
    args = p.parse_args()

    css = compile_qss(args.input)
    if args.output:
        Path(args.output).write_text(css, encoding='utf-8')
    else:
        sys.stdout.write(css)
