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

from patokenizer import Tokenizer, keyword_list, print_token_results, regex_table


def run_file(path: Path):
    text = path.read_text(encoding="utf-8")
    tokenizer = Tokenizer(regex_table, keyword_list)
    results = tokenizer.tokenize(text)

    print("=" * 80)
    print(f"FILE: {path}")
    print("=" * 80)
    print_token_results(results, tokenizer.errors)


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
