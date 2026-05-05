"""Pruebas unitarias para el parser predictivo de Little Duck."""

from __future__ import annotations

import unittest

from parser_predictivo_little_duck import PARSE_TABLE, Tokenizer, analizar


VALID_CASES = [
    "a = 7 + 4 + 5 ;",
    "b = 12 / (3.0 + 3) ;",
    'c = "hola " + "mundo";',
    "d = 7 / 2 >= 12 - 20 + 1;",
    "e = 2 * 2 * -2;",
    'f = "hola" != "bye";',
    "g = (x1 - x2) + (y1 - y2) ;",
    "h = waa * waa - waa / -waa;",
]

INVALID_CASES = [
    "i = waa + ;",
    "i = -x  y;",
    "i = 18.31416",
    "i = 56 * ( 7 - 1  ;",
]


class PredictiveParserTests(unittest.TestCase):
    def test_valid_cases_parse_without_errors(self) -> None:
        for source in VALID_CASES:
            with self.subTest(source=source):
                _, lexical_errors, syntax_errors, _ = analizar(source)
                self.assertEqual([], lexical_errors)
                self.assertEqual([], syntax_errors)

    def test_invalid_cases_report_syntax_errors(self) -> None:
        for source in INVALID_CASES:
            with self.subTest(source=source):
                _, lexical_errors, syntax_errors, _ = analizar(source)
                self.assertEqual([], lexical_errors)
                self.assertGreater(len(syntax_errors), 0)

    def test_parse_table_contains_relational_entries(self) -> None:
        for token_type in ("GT", "LT", "GE", "LE", "NE", "EQ"):
            with self.subTest(token_type=token_type):
                self.assertIn(token_type, PARSE_TABLE["<OP_REL>"])

    def test_string_tokens_stop_at_closing_quote(self) -> None:
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize('c = "hola " + "mundo";')
        token_types = [token.type for token in tokens]
        self.assertEqual(
            [
                "ID",
                "ASSIGN",
                "CTE_STR",
                "PLUS",
                "CTE_STR",
                "SEMICOLON",
                "EOF",
            ],
            token_types,
        )


if __name__ == "__main__":
    unittest.main()
