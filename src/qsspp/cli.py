#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 SCHARTIER Isaac
# SPDX-License-Identifier: MIT

# src/qsspp/cli.py

import argparse
import sys
from pathlib import Path

from .core import compile_qss


def compile_one(src: Path, dst: Path) -> bool:
    """Compile a single .qsspp -> .qss. Returns True on success."""
    try:
        css = compile_qss(src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(css, encoding="utf-8")
        print(f"[OK] {src} -> {dst} ({len(css)} bytes)")
        return True
    except Exception as e:
        print(f"[ERROR] {src}: {e}", file=sys.stderr)
        return False


def resolve_inputs(patterns: list[str]) -> list[Path]:
    """Resolve glob patterns to .qsspp files."""
    files: list[Path] = []
    for pat in patterns:
        # support recursive globs like assets/**/*.qsspp
        matches = list(Path().glob(pat))
        if not matches:
            print(f"[WARN] no files matched: {pat}", file=sys.stderr)
        files.extend(matches)
    # keep only .qsspp files
    files = [p for p in files if p.is_file() and p.suffix.lower() == ".qsspp"]
    # de-duplicate while preserving order
    seen = set()
    uniq: list[Path] = []
    for f in files:
        if f not in seen:
            uniq.append(f)
            seen.add(f)
    return uniq


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="ss-qssppc",
        description="Compile .qsspp files to .qss (no watcher).",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="Input .qsspp files (supports glob patterns like assets/**/*.qsspp)",
    )
    parser.add_argument(
        "-o",
        "--out",
        help=(
            "If a single input is provided: path to the output .qss file "
            "(or a directory). If multiple inputs are provided: output directory."
        ),
    )
    args = parser.parse_args()

    sources = resolve_inputs(args.inputs)
    if not sources:
        print("[ERROR] no valid .qsspp inputs found.", file=sys.stderr)
        return 2

    out_arg = Path(args.out) if args.out else None

    # With multiple inputs, --out must be a directory (or omitted)
    if len(sources) > 1 and out_arg and out_arg.suffix.lower() == ".qss":
        print("[ERROR] with multiple inputs, --out must be a directory (not a .qss file).",
              file=sys.stderr)
        return 2

    success = True
    if len(sources) == 1:
        src = sources[0]
        if out_arg:
            dst = out_arg if out_arg.suffix.lower() == ".qss" else (out_arg / (src.stem + ".qss"))
        else:
            dst = src.with_suffix(".qss")
        success &= compile_one(src, dst)
    else:
        # multiple inputs
        if out_arg:
            out_arg.mkdir(parents=True, exist_ok=True)
        for src in sources:
            dst = (out_arg / (src.stem + ".qss")) if out_arg else src.with_suffix(".qss")
            success &= compile_one(src, dst)

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
