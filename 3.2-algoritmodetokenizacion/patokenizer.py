# -*- coding: utf-8 -*-
"""
Tokenizer para el lenguaje Little Duck.

Lee un archivo de entrada, reconoce lexemas con expresiones regulares y
genera un token stream dividido por lineas.
"""

import re
import sys


class Tokenizer:
    def __init__(self, regex_table, keyword_list):
        if isinstance(regex_table, dict):
            self.regex_table = list(regex_table.items())
        else:
            self.regex_table = list(regex_table)
        self.keyword_list = keyword_list
        self.tokens = []
        self.errors = []

    def longest_match(self, input_string):
        matches = []

        for label, regex in self.regex_table:
            match = re.match(regex, input_string)
            if match:
                token_label = label
                token_value = match.group()

                if label == "id" and token_value in self.keyword_list:
                    token_label = self.keyword_list[token_value]

                matches.append([token_label, token_value])

        if matches:
            best_match = max(matches, key=lambda x: len(x[1]))
            return best_match
        else:
            return None

    def tokenize_line(self, line, line_number):
        line_tokens = []
        column = 1

        while line:
            stripped = line.lstrip()
            if len(stripped) < len(line):
                column += len(line) - len(stripped)
                line = stripped

            if not line:
                break

            if line[0] == "#":
                line_tokens.append(("comment", line))
                break

            token = self.longest_match(line)

            if token:
                line_tokens.append(tuple(token))
                column += len(token[1])
                line = line[len(token[1]) :]
            else:
                self.errors.append(
                    "Error lexico en linea "
                    f"{line_number}, columna {column}: "
                    f"simbolo no reconocido {line[0]!r}"
                )
                column += 1
                line = line[1:]

        return line_tokens

    def tokenize(self, input_text):
        self.tokens = []
        self.errors = []
        lines = input_text.split("\n")

        for i, line in enumerate(lines, start=1):
            line_tokens = self.tokenize_line(line, i)
            self.tokens.append((i, line.strip(), line_tokens))

        return self.tokens


# === Definicion del lexico de Little Duck ===

# Expresiones regulares ordenadas por prioridad.
# Las variantes de dos caracteres van antes que las de un caracter.
regex_table = [
    ("cte_float", r"^[0-9]+\.[0-9]+"),
    ("cte_int", r"^[0-9]+"),
    ("cte_str", r'^"[^"\n]*"'),
    ("op_ne", r"^!="),
    ("op_eq", r"^=="),
    ("op_ge", r"^>="),
    ("op_le", r"^<="),
    ("op_gt", r"^>"),
    ("op_lt", r"^<"),
    ("op_assign", r"^="),
    ("op_plus", r"^\+"),
    ("op_minus", r"^-"),
    ("op_times", r"^\*"),
    ("op_divide", r"^/"),
    ("l_paren", r"^\("),
    ("r_paren", r"^\)"),
    ("l_brace", r"^\{"),
    ("r_brace", r"^\}"),
    ("l_bracket", r"^\["),
    ("r_bracket", r"^\]"),
    ("semicolon", r"^;"),
    ("comma", r"^,"),
    ("colon", r"^:"),
    ("id", r"^[A-Za-z][A-Za-z0-9_]*"),
]

# Palabras reservadas -> label unico para cada una
keyword_list = {
    "program": "kw_program",
    "main": "kw_main",
    "var": "kw_var",
    "end": "kw_end",
    "void": "kw_void",
    "int": "kw_int",
    "float": "kw_float",
    "string": "kw_string",
    "if": "kw_if",
    "else": "kw_else",
    "do": "kw_do",
    "while": "kw_while",
    "print": "kw_print",
}


def format_token_stream(line_tokens):
    token_list_str = ", ".join(f"({label}, {value!r})" for label, value in line_tokens)
    return f"[ {token_list_str} ]"


def print_token_results(results, errors):
    print("=" * 60)
    print("TOKEN STREAM")
    print("=" * 60)

    for line_num, line_text, line_tokens in results:
        if not line_tokens and not line_text:
            continue
        if not line_tokens:
            continue

        print(f"\nLinea {line_num}:    {line_text}")
        print(f"Token stream:  {format_token_stream(line_tokens)}")

        max_val_len = max(len(value) for _, value in line_tokens)
        for label, value in line_tokens:
            print(f"  {value:<{max_val_len + 2}} {label}")

    if errors:
        print("\n" + "=" * 60)
        print("ERRORES LEXICOS")
        print("=" * 60)
        for error in errors:
            print(f"  {error}")
    else:
        print("\n" + "=" * 60)
        print("No se encontraron errores lexicos.")
        print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Uso: python patokenizer.py <archivo>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, "r", encoding="utf-8") as f:
            input_text = f.read()
    except FileNotFoundError:
        print(f"Error: No se encontro el archivo '{filename}'")
        sys.exit(1)

    tokenizer = Tokenizer(regex_table, keyword_list)
    results = tokenizer.tokenize(input_text)
    print_token_results(results, tokenizer.errors)


if __name__ == "__main__":
    main()
