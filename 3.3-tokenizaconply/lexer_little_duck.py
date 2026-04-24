"""Lexer de Little Duck implementado con PLY."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from typing import Protocol, TypedDict, cast

import ply.lex as lex


class TokenInfo(TypedDict):
    type: str
    value: object
    line: int
    column: int
    lexpos: int


class LexicalError(TypedDict):
    line: int
    column: int
    lexpos: int
    symbol: str


class PlyLexer(Protocol):
    lineno: int

    def input(self, s: str) -> None: ...
    def token(self) -> PlyToken | None: ...
    def skip(self, n: int) -> None: ...


class PlyToken(Protocol):
    type: str
    value: str
    lineno: int
    lexpos: int
    lexer: PlyLexer


class LittleDuckLexer:
    reserved = {
        "program": "PROGRAM",
        "var": "VAR",
        "int": "INT",
        "float": "FLOAT",
        "string": "STRING",
        "void": "VOID",
        "main": "MAIN",
        "end": "END",
        "print": "PRINT",
        "if": "IF",
        "else": "ELSE",
        "do": "DO",
        "while": "WHILE",
    }

    tokens = [
        "ID",
        "CTE_INT",
        "CTE_FLOAT",
        "CTE_STRING",
        "EQ",
        "NE",
        "GE",
        "LE",
        "GT",
        "LT",
        "ASSIGN",
        "PLUS",
        "MINUS",
        "TIMES",
        "DIVIDE",
        "LPAREN",
        "RPAREN",
        "LBRACE",
        "RBRACE",
        "LBRACKET",
        "RBRACKET",
        "COMMA",
        "SEMICOLON",
        "COLON",
    ] + list(reserved.values())

    t_EQ = r"=="
    t_NE = r"!="
    t_GE = r">="
    t_LE = r"<="
    t_GT = r">"
    t_LT = r"<"
    t_ASSIGN = r"="
    t_PLUS = r"\+"
    t_MINUS = r"-"
    t_TIMES = r"\*"
    t_DIVIDE = r"/"
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LBRACE = r"\{"
    t_RBRACE = r"\}"
    t_LBRACKET = r"\["
    t_RBRACKET = r"\]"
    t_COMMA = r","
    t_SEMICOLON = r";"
    t_COLON = r":"

    t_ignore = " \t\r"

    def __init__(self) -> None:
        self.lexer: PlyLexer = cast(PlyLexer, lex.lex(module=self))
        self.source = ""
        self.errors: list[LexicalError] = []

    def reset(self) -> None:
        self.lexer.lineno = 1
        self.errors = []

    def find_column(self, lexpos: int) -> int:
        line_start = self.source.rfind("\n", 0, lexpos) + 1
        return (lexpos - line_start) + 1

    def t_COMMENT(self, t: PlyToken) -> None:
        r"\#.*"
        pass

    def t_newline(self, t: PlyToken) -> None:
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_CTE_FLOAT(self, t: PlyToken) -> PlyToken:
        r"\d+\.\d+"
        return t

    def t_CTE_INT(self, t: PlyToken) -> PlyToken:
        r"\d+"
        return t

    def t_CTE_STRING(self, t: PlyToken) -> PlyToken:
        r'"([^\\\n]|(\\.))*?"'
        return t

    def t_ID(self, t: PlyToken) -> PlyToken:
        r"[A-Za-z][A-Za-z0-9_]*"
        t.type = self.reserved.get(t.value, "ID")
        return t

    def t_error(self, t: PlyToken) -> None:
        column = self.find_column(t.lexpos)
        self.errors.append(
            {
                "line": t.lineno,
                "column": column,
                "lexpos": t.lexpos,
                "symbol": t.value[0],
            }
        )
        t.lexer.skip(1)

    def tokenize_text(
        self, source: str
    ) -> tuple[list[TokenInfo], dict[int, list[TokenInfo]]]:
        self.source = source
        self.reset()
        self.lexer.input(source)

        stream: list[TokenInfo] = []
        tokens_by_line: dict[int, list[TokenInfo]] = defaultdict(list)

        while True:
            token = self.lexer.token()
            if token is None:
                break

            token_info: TokenInfo = {
                "type": token.type,
                "value": token.value,
                "line": token.lineno,
                "column": self.find_column(token.lexpos),
                "lexpos": token.lexpos,
            }
            stream.append(token_info)
            tokens_by_line[token.lineno].append(token_info)

        return stream, dict(tokens_by_line)

    def tokenize_file(
        self, file_path: str
    ) -> tuple[list[str], list[TokenInfo], dict[int, list[TokenInfo]]]:
        source = Path(file_path).read_text(encoding="utf-8")
        lines = source.splitlines()
        stream, tokens_by_line = self.tokenize_text(source)
        return lines, stream, tokens_by_line


def format_token_row(token: TokenInfo) -> str:
    return (
        f"{token['type']:<14} "
        f"value: {str(token['value']):<18} "
        f"lexpos: {token['lexpos']:<5} "
        f"column: {token['column']}"
    )


def print_report(
    lines: list[str],
    tokens_by_line: dict[int, list[TokenInfo]],
    errors: list[LexicalError],
) -> None:
    print("=" * 72)
    print("TOKEN STREAM DE LITTLE DUCK")
    print("=" * 72)

    for index, line in enumerate(lines, start=1):
        line_tokens = tokens_by_line.get(index, [])
        print(f"\nLinea {index}:    {line}")
        for token in line_tokens:
            print(format_token_row(token))

    print("\n" + "=" * 72)
    if errors:
        print("ERRORES LEXICOS")
        print("=" * 72)
        for error in errors:
            print(
                f"Linea {error['line']}, columna {error['column']}, "
                f"lexpos {error['lexpos']}: "
                f"simbolo no reconocido {error['symbol']!r}"
            )
    else:
        print("Sin errores lexicos.")
        print("=" * 72)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(
            "Uso: python3 lexer_little_duck.py <archivo_fuente>",
            file=sys.stderr,
        )
        return 1

    source_path = Path(argv[1])
    if not source_path.is_file():
        print(
            f"Error: no se encontro el archivo {str(source_path)!r}.", file=sys.stderr
        )
        return 1

    lexer = LittleDuckLexer()
    lines, _, tokens_by_line = lexer.tokenize_file(str(source_path))
    print_report(lines, tokens_by_line, lexer.errors)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
