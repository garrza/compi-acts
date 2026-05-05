"""Ejecuta los casos solicitados para la actividad 3.6."""

from __future__ import annotations

from parser_predictivo_little_duck import analizar


CASOS = [
    ("a = 7 + 4 + 5 ;", True),
    ("b = 12 / (3.0 + 3) ;", True),
    ('c = "hola " + "mundo";', True),
    ("d = 7 / 2 >= 12 - 20 + 1;", True),
    ("e = 2 * 2 * -2;", True),
    ('f = "hola" != "bye";', True),
    ("g = (x1 - x2) + (y1 - y2) ;", True),
    ("h = waa * waa - waa / -waa;", True),
    ("i = waa + ;", False),
    ("i = -x  y;", False),
    ("i = 18.31416", False),
    ("i = 56 * ( 7 - 1  ;", False),
]


def main() -> int:
    failed = 0

    for index, (source, expected_valid) in enumerate(CASOS, start=1):
        _, lexical_errors, syntax_errors, _ = analizar(source)
        is_valid = not lexical_errors and not syntax_errors

        expected_label = "valida" if expected_valid else "invalida"
        result_label = "valida" if is_valid else "invalida"
        status = "OK" if is_valid == expected_valid else "FALLO"

        print("=" * 72)
        print(f"Caso {index}: {source}")
        print(f"Esperado: {expected_label}")
        print(f"Resultado: {result_label}")
        print(f"Estado: {status}")

        for error in lexical_errors:
            print(
                f"Error lexico: linea {error.line}, columna {error.column}, "
                f"simbolo {error.symbol!r}"
            )

        for error in syntax_errors:
            print(
                f"Error sintactico: linea {error.line}, columna {error.column}, "
                f"esperaba {error.expected}, recibio {error.received}"
            )

        if status != "OK":
            failed += 1

    print("=" * 72)
    print(f"Resumen: {len(CASOS) - failed}/{len(CASOS)} casos con resultado esperado")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
