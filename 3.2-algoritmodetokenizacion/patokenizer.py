# -*- coding: utf-8 -*-
"""
Tokenizer para el lenguaje Little Duck
Basado en el algoritmo de tokenizacion visto en clase.
"""

import re
import sys


class Tokenizer:
    tokens = []
    regex_table = {}
    keyword_list = {}

    def __init__(self, regex_table, keyword_list):
        self.regex_table = regex_table
        self.keyword_list = keyword_list
        self.tokens = []
        self.errors = []

    def longest_match(self, input_string):
        matches = []

        for label, regex in self.regex_table.items():
            match = re.match(regex, input_string)
            if match:
                token_label = label
                token_value = match.group()

                # Si es un identificador, revisar si es keyword
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

        while line:
            # Remover espacios al inicio
            stripped = line.lstrip()
            if len(stripped) < len(line):
                line = stripped

            if not line:
                break

            # Si empieza con #, es comentario -> ignorar el resto de la linea
            if line[0] == "#":
                break

            token = self.longest_match(line)

            if token:
                line_tokens.append(tuple(token))
                line = line[len(token[1]) :]
            else:
                # Error: simbolo no reconocido
                self.errors.append(
                    f"Error lexico en linea {line_number}: simbolo no reconocido '{line[0]}'"
                )
                # Avanzar un caracter y continuar
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

# Expresiones regulares ordenadas por prioridad
# Las mas especificas primero para longest match
regex_table = {
    "cte_float": r"^[0-9]+\.[0-9]+",
    "cte_int": r"^[0-9]+",
    "cte_string": r'^"[^"]*"',
    "id": r"^[a-zA-Z][a-zA-Z0-9_]*",
    "!=": r"^!=",
    "==": r"^==",
    ">=": r"^>=",
    "<=": r"^<=",
    ">": r"^>",
    "<": r"^<",
    "=": r"^=",
    "+": r"^\+",
    "-": r"^\-",
    "*": r"^\*",
    "/": r"^/",
    "(": r"^\(",
    ")": r"^\)",
    "{": r"^\{",
    "}": r"^\}",
    "[": r"^\[",
    "]": r"^\]",
    ";": r"^;",
    ",": r"^,",
    ":": r"^:",
}

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


def main():
    if len(sys.argv) < 2:
        print("Uso: python patokenizer_2026_502.py <archivo>")
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

    # Imprimir token stream formateado
    print("=" * 60)
    print("TOKEN STREAM")
    print("=" * 60)

    for line_num, line_text, line_tokens in results:
        if not line_tokens and not line_text:
            continue
        if not line_tokens and line_text.startswith("#"):
            # Linea de comentario
            print(f"\nLinea {line_num}:    {line_text}")
            print("  (comentario)")
            continue
        if not line_tokens:
            continue

        print(f"\nLinea {line_num}:    {line_text}")

        # Token stream como lista
        token_list_str = ", ".join(f"('{t[0]}', '{t[1]}')" for t in line_tokens)
        print(f"Token stream:  [ {token_list_str} ]")

        # Tabla detallada
        max_val_len = max(len(t[1]) for t in line_tokens)
        for token in line_tokens:
            print(f"  {token[1]:<{max_val_len + 2}} {token[0]}")

    # Imprimir errores
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


if __name__ == "__main__":
    main()
