#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run all test files in `casos-prueba` through the `patokenizer` Tokenizer.

Usage:
  python run_casos.py            # runs files in ./casos-prueba
  python run_casos.py <folder>   # run files in specified folder
"""

import sys
from pathlib import Path

from patokenizer import Tokenizer, keyword_list, regex_table


def run_file(path: Path):
    text = path.read_text(encoding="utf-8")
    tokenizer = Tokenizer(regex_table, keyword_list)
    results = tokenizer.tokenize(text)

    print("=" * 80)
    print(f"FILE: {path}")
    print("=" * 80)

    for line_num, line_text, line_tokens in results:
        if not line_tokens and not line_text:
            continue
        if not line_tokens and line_text.startswith("#"):
            print(f"\nLinea {line_num}:    {line_text}")
            print("  (comentario)")
            continue
        if not line_tokens:
            continue

        print(f"\nLinea {line_num}:    {line_text}")

        token_list_str = ", ".join(f"('{t[0]}', '{t[1]}')" for t in line_tokens)
        print(f"Token stream:  [ {token_list_str} ]")

        max_val_len = max(len(t[1]) for t in line_tokens)
        for token in line_tokens:
            print(f"  {token[1]:<{max_val_len + 2}} {token[0]}")

    if tokenizer.errors:
        print("\n" + "=" * 60)
        print("ERRORES LEXICOS")
        print("=" * 60)
        for error in tokenizer.errors:
            print(f"  {error}")
    else:
        print("\n" + "=" * 60)
        print("No se encontraron errores lexicos.")
        print("=" * 60)


def main():
    base = Path(__file__).parent
    casos_dir = base / "casos-prueba"
    if len(sys.argv) > 1:
        casos_dir = Path(sys.argv[1])

    if not casos_dir.exists():
        print(f"Casos directory not found: {casos_dir}")
        sys.exit(1)

    files = sorted(p for p in casos_dir.iterdir() if p.is_file())
    if not files:
        print(f"No test files found in {casos_dir}")
        sys.exit(1)

    for f in files:
        run_file(f)


if __name__ == "__main__":
    main()
