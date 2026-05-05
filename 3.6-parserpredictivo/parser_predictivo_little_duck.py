"""Parser predictivo LL(1) para asignaciones de Little Duck."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Token:
    type: str
    value: str
    line: int
    column: int


@dataclass(frozen=True)
class LexicalError:
    line: int
    column: int
    symbol: str


@dataclass(frozen=True)
class SyntaxErrorInfo:
    expected: str
    received: str
    line: int
    column: int


class Tokenizer:
    """Tokenizer reducido para los tokens usados por ASSIGN."""

    token_specs = [
        ("CTE_FLOAT", r"\d+\.\d+"),
        ("CTE_INT", r"\d+"),
        ("CTE_STR", r'"([^"\\\n]|\\.)*"'),
        ("NE", r"!="),
        ("EQ", r"=="),
        ("GE", r">="),
        ("LE", r"<="),
        ("GT", r">"),
        ("LT", r"<"),
        ("ASSIGN", r"="),
        ("PLUS", r"\+"),
        ("MINUS", r"-"),
        ("TIMES", r"\*"),
        ("DIVIDE", r"/"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("SEMICOLON", r";"),
        ("ID", r"[A-Za-z][A-Za-z0-9_]*"),
    ]

    def __init__(self) -> None:
        self.patterns = [
            (token_type, re.compile(pattern))
            for token_type, pattern in self.token_specs
        ]
        self.errors: list[LexicalError] = []

    def tokenize(self, source: str) -> list[Token]:
        tokens: list[Token] = []
        self.errors = []
        lines = source.splitlines()

        for line_number, line in enumerate(lines, start=1):
            index = 0
            while index < len(line):
                char = line[index]

                if char in " \t\r":
                    index += 1
                    continue

                if char == "#":
                    break

                match = self._longest_match(line[index:])
                if match is None:
                    self.errors.append(
                        LexicalError(
                            line=line_number,
                            column=index + 1,
                            symbol=char,
                        )
                    )
                    index += 1
                    continue

                token_type, value = match
                tokens.append(
                    Token(
                        type=token_type,
                        value=value,
                        line=line_number,
                        column=index + 1,
                    )
                )
                index += len(value)

        eof_line, eof_column = self._eof_position(source, lines)
        tokens.append(Token("EOF", "", eof_line, eof_column))
        return tokens

    def _longest_match(self, text: str) -> tuple[str, str] | None:
        matches: list[tuple[str, str]] = []

        for token_type, pattern in self.patterns:
            match = pattern.match(text)
            if match:
                matches.append((token_type, match.group(0)))

        if not matches:
            return None

        return max(matches, key=lambda item: len(item[1]))

    def _eof_position(self, source: str, lines: list[str]) -> tuple[int, int]:
        if not source:
            return 1, 1
        if source.endswith("\n"):
            return len(lines) + 1, 1
        return len(lines), len(lines[-1]) + 1


EPSILON = "epsilon"

N_ASSIGN = "<ASSIGN>"
N_EXPRESION = "<EXPRESION>"
N_EXPRESION_PRIME = "<EXPRESION_PRIME>"
N_OP_REL = "<OP_REL>"
N_EXP = "<EXP>"
N_EXP_PRIME = "<EXP_PRIME>"
N_TERMINO = "<TERMINO>"
N_TERMINO_PRIME = "<TERMINO_PRIME>"
N_FACTOR = "<FACTOR>"
N_SIGN = "<SIGN>"
N_VAR_CTE = "<VAR_CTE>"

NON_TERMINALS = {
    N_ASSIGN,
    N_EXPRESION,
    N_EXPRESION_PRIME,
    N_OP_REL,
    N_EXP,
    N_EXP_PRIME,
    N_TERMINO,
    N_TERMINO_PRIME,
    N_FACTOR,
    N_SIGN,
    N_VAR_CTE,
}

TERMINALS = {
    "ID",
    "CTE_INT",
    "CTE_FLOAT",
    "CTE_STR",
    "ASSIGN",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "GT",
    "LT",
    "GE",
    "LE",
    "NE",
    "EQ",
    "LPAREN",
    "RPAREN",
    "SEMICOLON",
    "EOF",
}

FIRST_EXPRESION = {"LPAREN", "PLUS", "MINUS", "ID", "CTE_INT", "CTE_FLOAT", "CTE_STR"}
REL_OPS = {"GT", "LT", "GE", "LE", "NE", "EQ"}
ADD_OPS = {"PLUS", "MINUS"}
MULT_OPS = {"TIMES", "DIVIDE"}
VAR_CTE_STARTS = {"ID", "CTE_INT", "CTE_FLOAT", "CTE_STR"}

FIRST = {
    N_ASSIGN: {"ID"},
    N_EXPRESION: FIRST_EXPRESION,
    N_EXPRESION_PRIME: REL_OPS | {EPSILON},
    N_OP_REL: REL_OPS,
    N_EXP: FIRST_EXPRESION,
    N_EXP_PRIME: ADD_OPS | {EPSILON},
    N_TERMINO: FIRST_EXPRESION,
    N_TERMINO_PRIME: MULT_OPS | {EPSILON},
    N_FACTOR: FIRST_EXPRESION,
    N_SIGN: ADD_OPS,
    N_VAR_CTE: VAR_CTE_STARTS,
}

FOLLOW = {
    N_ASSIGN: {"EOF"},
    N_EXPRESION: {"SEMICOLON", "RPAREN"},
    N_EXPRESION_PRIME: {"SEMICOLON", "RPAREN"},
    N_OP_REL: FIRST_EXPRESION,
    N_EXP: REL_OPS | {"SEMICOLON", "RPAREN"},
    N_EXP_PRIME: REL_OPS | {"SEMICOLON", "RPAREN"},
    N_TERMINO: ADD_OPS | REL_OPS | {"SEMICOLON", "RPAREN"},
    N_TERMINO_PRIME: ADD_OPS | REL_OPS | {"SEMICOLON", "RPAREN"},
    N_FACTOR: MULT_OPS | ADD_OPS | REL_OPS | {"SEMICOLON", "RPAREN"},
    N_SIGN: VAR_CTE_STARTS,
    N_VAR_CTE: MULT_OPS | ADD_OPS | REL_OPS | {"SEMICOLON", "RPAREN"},
}


def build_parse_table() -> dict[str, dict[str, tuple[str, ...]]]:
    table: dict[str, dict[str, tuple[str, ...]]] = {
        non_terminal: {} for non_terminal in NON_TERMINALS
    }

    table[N_ASSIGN]["ID"] = ("ID", "ASSIGN", N_EXPRESION, "SEMICOLON")

    for token_type in FIRST_EXPRESION:
        table[N_EXPRESION][token_type] = (N_EXP, N_EXPRESION_PRIME)
        table[N_EXP][token_type] = (N_TERMINO, N_EXP_PRIME)
        table[N_TERMINO][token_type] = (N_FACTOR, N_TERMINO_PRIME)

    for token_type in REL_OPS:
        table[N_EXPRESION_PRIME][token_type] = (N_OP_REL, N_EXP)
        table[N_EXP_PRIME][token_type] = ()
        table[N_TERMINO_PRIME][token_type] = ()
        table[N_OP_REL][token_type] = (token_type,)

    for token_type in {"SEMICOLON", "RPAREN"}:
        table[N_EXPRESION_PRIME][token_type] = ()
        table[N_EXP_PRIME][token_type] = ()
        table[N_TERMINO_PRIME][token_type] = ()

    for token_type in ADD_OPS:
        table[N_EXP_PRIME][token_type] = (token_type, N_TERMINO, N_EXP_PRIME)
        table[N_SIGN][token_type] = (token_type,)
        table[N_TERMINO_PRIME][token_type] = ()
        table[N_FACTOR][token_type] = (N_SIGN, N_VAR_CTE)

    for token_type in MULT_OPS:
        table[N_TERMINO_PRIME][token_type] = (
            token_type,
            N_FACTOR,
            N_TERMINO_PRIME,
        )

    table[N_FACTOR]["LPAREN"] = ("LPAREN", N_EXPRESION, "RPAREN")

    for token_type in VAR_CTE_STARTS:
        table[N_FACTOR][token_type] = (N_VAR_CTE,)
        table[N_VAR_CTE][token_type] = (token_type,)

    return table


PARSE_TABLE = build_parse_table()

TOKEN_DISPLAY = {
    "ID": "id",
    "CTE_INT": "cte_int",
    "CTE_FLOAT": "cte_float",
    "CTE_STR": "cte_str",
    "ASSIGN": "=",
    "PLUS": "+",
    "MINUS": "-",
    "TIMES": "*",
    "DIVIDE": "/",
    "GT": ">",
    "LT": "<",
    "GE": ">=",
    "LE": "<=",
    "NE": "!=",
    "EQ": "==",
    "LPAREN": "(",
    "RPAREN": ")",
    "SEMICOLON": ";",
    "EOF": "fin de entrada",
}


class PredictiveParser:
    """Parser de pila que consulta explicitamente la parse table LL(1)."""

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.position = 0
        self.errors: list[SyntaxErrorInfo] = []

    def parse(self) -> bool:
        stack = ["EOF", N_ASSIGN]

        while stack:
            top = stack.pop()
            current = self.current()

            if top in TERMINALS:
                if top == current.type:
                    self.advance()
                else:
                    self.add_error([top], current)
                    self.recover_terminal(top)
                continue

            if top in NON_TERMINALS:
                production = PARSE_TABLE[top].get(current.type)
                if production is None and current.type == "EOF" and EPSILON in FIRST[top]:
                    continue

                if production is None:
                    self.add_error(self.expected_for(top), current)
                    self.recover_non_terminal(top, stack)
                    continue

                for symbol in reversed(production):
                    stack.append(symbol)
                continue

            raise ValueError(f"Simbolo desconocido en la pila: {top}")

        return not self.errors

    def current(self) -> Token:
        return self.tokens[self.position]

    def advance(self) -> None:
        if self.position < len(self.tokens) - 1:
            self.position += 1

    def add_error(self, expected_tokens: list[str] | set[str], received: Token) -> None:
        self.errors.append(
            SyntaxErrorInfo(
                expected=format_expected(expected_tokens),
                received=display_token(received.type),
                line=received.line,
                column=received.column,
            )
        )

    def expected_for(self, non_terminal: str) -> set[str]:
        expected = set(FIRST[non_terminal])
        expected.discard(EPSILON)
        if EPSILON in FIRST[non_terminal]:
            expected |= FOLLOW[non_terminal]
        return expected

    def recover_terminal(self, expected: str) -> None:
        current = self.current()

        if expected == "SEMICOLON":
            while self.current().type not in {"SEMICOLON", "EOF"}:
                self.advance()
            if self.current().type == "SEMICOLON":
                self.advance()
            return

        if expected == "RPAREN":
            return

        if expected == "EOF":
            while self.current().type != "EOF":
                self.advance()
            return

        if current.type != "EOF":
            self.advance()

    def recover_non_terminal(self, non_terminal: str, stack: list[str]) -> None:
        current = self.current()

        if current.type == "EOF":
            return

        if current.type in FOLLOW[non_terminal]:
            return

        self.advance()
        stack.append(non_terminal)


def display_token(token_type: str) -> str:
    return TOKEN_DISPLAY.get(token_type, token_type)


def format_expected(expected_tokens: list[str] | set[str]) -> str:
    ordered = sorted(expected_tokens, key=lambda token: TOKEN_DISPLAY.get(token, token))
    return ", ".join(display_token(token) for token in ordered)


def format_tokens(tokens: list[Token]) -> str:
    visible_tokens = [token for token in tokens if token.type != "EOF"]
    return "[ " + ", ".join(f"({t.type}, {t.value!r})" for t in visible_tokens) + " ]"


def analizar(
    source: str,
) -> tuple[list[Token], list[LexicalError], list[SyntaxErrorInfo]]:
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize(source)

    parser = PredictiveParser(tokens)
    if not tokenizer.errors:
        parser.parse()

    return tokens, tokenizer.errors, parser.errors


def print_report(source: str) -> int:
    tokens, lexical_errors, syntax_errors = analizar(source)

    print("TOKEN STREAM")
    print(format_tokens(tokens))

    if lexical_errors:
        print("\nERRORES LEXICOS")
        for error in lexical_errors:
            print(
                f"Linea {error.line}, columna {error.column}: "
                f"simbolo no reconocido {error.symbol!r}"
            )
        return 1

    if syntax_errors:
        print("\nERRORES SINTACTICOS")
        for error in syntax_errors:
            print(
                f"Linea {error.line}, columna {error.column}: "
                f"esperaba {error.expected}, recibio {error.received}"
            )
        return 1

    print("\nOK: asignacion valida")
    return 0


def load_cases(path: Path) -> list[str]:
    return [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print(
            "Uso: python parser_predictivo_little_duck.py [archivo]",
            file=sys.stderr,
        )
        return 2

    source_path = (
        Path(argv[1])
        if len(argv) == 2
        else Path(__file__).with_name("casos_prueba.txt")
    )
    if not source_path.is_file():
        print(f"Error: no se encontro el archivo {source_path}", file=sys.stderr)
        return 2

    cases = load_cases(source_path)
    for index, case in enumerate(cases, start=1):
        print("=" * 72)
        print(f"Caso {index}: {case}")
        print_report(case)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
