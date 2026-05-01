# Parser de descenso recursivo para asignaciones de Little Duck.

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
    """Tokenizer reducido para la sintaxis usada por ASSIGN."""

    token_specs = [
        ("CTE_FLOAT", r"\d+\.\d+"),
        ("CTE_INT", r"\d+"),
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

        for line_number, line in enumerate(source.splitlines(), start=1):
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

        tokens.append(Token("EOF", "", len(source.splitlines()) + 1, 1))
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


class TokenStream:
    """Manejo basico del token actual, como en el ejemplo de clase."""

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token:
        return self.tokens[self.pos]

    def avanza(self) -> Token:
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return self.current()


class Parser:
    relational_ops = {"GT", "LT", "GE", "LE", "NE", "EQ"}
    add_ops = {"PLUS", "MINUS"}
    mult_ops = {"TIMES", "DIVIDE"}
    var_cte = {"ID", "CTE_INT", "CTE_FLOAT"}

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = TokenStream(tokens)
        self.errors: list[SyntaxErrorInfo] = []

    def parse(self) -> bool:
        if self.current().type == "EOF":
            self.add_error("id")
            return False

        while self.current().type != "EOF":
            start_pos = self.tokens.pos
            self.assign()

            if self.tokens.pos == start_pos:
                self.tokens.avanza()

        return not self.errors

    # <ASSIGN> ::= id = <EXPRESION> ;
    def assign(self) -> None:
        self.expect("ID", "id")
        self.expect("ASSIGN", "=")
        self.expresion()
        if not self.expect("SEMICOLON", ";"):
            self.synchronize()

    # <EXPRESION> ::= <EXP> [ <OP_REL> <EXP> ]
    def expresion(self) -> None:
        self.exp()

        if self.current().type in self.relational_ops:
            self.tokens.avanza()
            self.exp()

    # <EXP> ::= <TERMINO> <EXP_PRIME>
    def exp(self) -> None:
        self.termino()
        self.exp_prime()

    # <EXP_PRIME> ::= (+ | -) <TERMINO> <EXP_PRIME> | epsilon
    def exp_prime(self) -> None:
        if self.current().type in self.add_ops:
            self.tokens.avanza()
            self.termino()
            self.exp_prime()

    # <TERMINO> ::= <FACTOR> <TERMINO_PRIME>
    def termino(self) -> None:
        self.factor()
        self.termino_prime()

    # <TERMINO_PRIME> ::= (* | /) <FACTOR> <TERMINO_PRIME> | epsilon
    def termino_prime(self) -> None:
        if self.current().type in self.mult_ops:
            self.tokens.avanza()
            self.factor()
            self.termino_prime()

    # <FACTOR> ::= ( <EXPRESION> ) | (+ | -) <VAR_CTE> | <VAR_CTE>
    def factor(self) -> None:
        token = self.current()

        if token.type == "LPAREN":
            self.tokens.avanza()
            self.expresion()
            self.expect("RPAREN", ")")
            return

        if token.type in self.add_ops:
            self.tokens.avanza()
            self.var_cte_rule()
            return

        self.var_cte_rule()

    # <VAR_CTE> ::= id | cte_int | cte_float
    def var_cte_rule(self) -> None:
        if self.current().type in self.var_cte:
            self.tokens.avanza()
            return

        self.add_error("id, cte_int o cte_float")
        self.recover_from_factor_error()

    def expect(self, token_type: str, expected: str) -> bool:
        if self.current().type == token_type:
            self.tokens.avanza()
            return True

        self.add_error(expected)
        return False

    def add_error(self, expected: str) -> None:
        token = self.current()
        self.errors.append(
            SyntaxErrorInfo(
                expected=expected,
                received=token.type if token.type != "EOF" else "EOF",
                line=token.line,
                column=token.column,
            )
        )

    def recover_from_factor_error(self) -> None:
        if self.current().type not in {"EOF", "SEMICOLON", "RPAREN"}:
            self.tokens.avanza()

    def synchronize(self) -> None:
        while self.current().type not in {"EOF", "SEMICOLON"}:
            self.tokens.avanza()
        if self.current().type == "SEMICOLON":
            self.tokens.avanza()

    def current(self) -> Token:
        return self.tokens.current()


def format_tokens(tokens: list[Token]) -> str:
    visible_tokens = [token for token in tokens if token.type != "EOF"]
    return "[ " + ", ".join(f"({t.type}, {t.value!r})" for t in visible_tokens) + " ]"


def analizar(
    source: str,
) -> tuple[list[Token], list[LexicalError], list[SyntaxErrorInfo]]:
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize(source)

    parser = Parser(tokens)
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


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Uso: python parser_little_duck.py [archivo_fuente]", file=sys.stderr)
        return 2

    source_path = Path(argv[1])
    if not source_path.is_file():
        print(f"Error: no se encontro el archivo {source_path}", file=sys.stderr)
        return 2

    return print_report(source_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
