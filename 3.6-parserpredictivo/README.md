# Actividad 3.6 - Parser predictivo y parse tables

Implementacion de un parser predictivo LL(1) para asignaciones de Little Duck.
El proyecto incluye un tokenizer reducido, una parse table explicita, casos de
prueba y pruebas unitarias. No se genera PDF en este directorio.

## Archivos

- `parser_predictivo_little_duck.py`: tokenizer, gramatica, conjuntos FIRST/FOLLOW, parse table y parser LL(1).
- `casos_prueba.txt`: casos solicitados en la actividad.
- `run_pruebas.py`: script que compara cada caso contra el resultado esperado.
- `test_parser_predictivo.py`: pruebas unitarias con `unittest`.
- `resultados_pruebas.txt`: salida capturada de `run_pruebas.py`.
- `requirements.txt`: documenta que no hay dependencias externas.

## Entorno virtual

```bash
cd /Users/ramiro/Desktop/code/class-acts/compi-acts/3.6-parserpredictivo
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Uso

Ejecutar los casos de la actividad:

```bash
.venv/bin/python parser_predictivo_little_duck.py casos_prueba.txt
```

Ver tambien los pasos de la pila predictiva:

```bash
.venv/bin/python parser_predictivo_little_duck.py casos_prueba.txt --steps
```

Ver salida de pruebas con resultado esperado:

```bash
.venv/bin/python run_pruebas.py
```

Ejecutar pruebas unitarias:

```bash
.venv/bin/python -m unittest -v
```

## Gramatica implementada

```text
<ASSIGN>          ::= id = <EXPRESION> ;
<EXPRESION>       ::= <EXP> <EXPRESION_PRIME>
<EXPRESION_PRIME> ::= <OP_REL> <EXP> | epsilon
<OP_REL>          ::= > | < | >= | <= | != | ==
<EXP>             ::= <TERMINO> <EXP_PRIME>
<EXP_PRIME>       ::= + <TERMINO> <EXP_PRIME>
                    | - <TERMINO> <EXP_PRIME>
                    | epsilon
<TERMINO>         ::= <FACTOR> <TERMINO_PRIME>
<TERMINO_PRIME>   ::= * <FACTOR> <TERMINO_PRIME>
                    | / <FACTOR> <TERMINO_PRIME>
                    | epsilon
<FACTOR>          ::= ( <EXPRESION> )
                    | <SIGN> <VAR_CTE>
                    | <VAR_CTE>
<SIGN>            ::= + | -
<VAR_CTE>         ::= id | cte_int | cte_float | cte_str
```

## FIRST

| No terminal | FIRST |
|---|---|
| `<ASSIGN>` | `{ id }` |
| `<EXPRESION>` | `{ (, +, -, id, cte_int, cte_float, cte_str }` |
| `<EXPRESION_PRIME>` | `{ >, <, >=, <=, !=, ==, epsilon }` |
| `<OP_REL>` | `{ >, <, >=, <=, !=, == }` |
| `<EXP>` | `{ (, +, -, id, cte_int, cte_float, cte_str }` |
| `<EXP_PRIME>` | `{ +, -, epsilon }` |
| `<TERMINO>` | `{ (, +, -, id, cte_int, cte_float, cte_str }` |
| `<TERMINO_PRIME>` | `{ *, /, epsilon }` |
| `<FACTOR>` | `{ (, +, -, id, cte_int, cte_float, cte_str }` |
| `<SIGN>` | `{ +, - }` |
| `<VAR_CTE>` | `{ id, cte_int, cte_float, cte_str }` |

## FOLLOW

| No terminal | FOLLOW |
|---|---|
| `<ASSIGN>` | `{ EOF }` |
| `<EXPRESION>` | `{ ;, ) }` |
| `<EXPRESION_PRIME>` | `{ ;, ) }` |
| `<OP_REL>` | `{ (, +, -, id, cte_int, cte_float, cte_str }` |
| `<EXP>` | `{ >, <, >=, <=, !=, ==, ;, ) }` |
| `<EXP_PRIME>` | `{ >, <, >=, <=, !=, ==, ;, ) }` |
| `<TERMINO>` | `{ +, -, >, <, >=, <=, !=, ==, ;, ) }` |
| `<TERMINO_PRIME>` | `{ +, -, >, <, >=, <=, !=, ==, ;, ) }` |
| `<FACTOR>` | `{ *, /, +, -, >, <, >=, <=, !=, ==, ;, ) }` |
| `<SIGN>` | `{ id, cte_int, cte_float, cte_str }` |
| `<VAR_CTE>` | `{ *, /, +, -, >, <, >=, <=, !=, ==, ;, ) }` |

## Parse table resultante

Solo se listan las entradas no vacias. Las entradas no listadas son errores.

| No terminal | Lookahead | Produccion |
|---|---|---|
| `<ASSIGN>` | `id` | `id = <EXPRESION> ;` |
| `<EXPRESION>` | `(, +, -, id, cte_int, cte_float, cte_str` | `<EXP> <EXPRESION_PRIME>` |
| `<EXPRESION_PRIME>` | `>, <, >=, <=, !=, ==` | `<OP_REL> <EXP>` |
| `<EXPRESION_PRIME>` | `;, )` | `epsilon` |
| `<OP_REL>` | `>` | `>` |
| `<OP_REL>` | `<` | `<` |
| `<OP_REL>` | `>=` | `>=` |
| `<OP_REL>` | `<=` | `<=` |
| `<OP_REL>` | `!=` | `!=` |
| `<OP_REL>` | `==` | `==` |
| `<EXP>` | `(, +, -, id, cte_int, cte_float, cte_str` | `<TERMINO> <EXP_PRIME>` |
| `<EXP_PRIME>` | `+` | `+ <TERMINO> <EXP_PRIME>` |
| `<EXP_PRIME>` | `-` | `- <TERMINO> <EXP_PRIME>` |
| `<EXP_PRIME>` | `>, <, >=, <=, !=, ==, ;, )` | `epsilon` |
| `<TERMINO>` | `(, +, -, id, cte_int, cte_float, cte_str` | `<FACTOR> <TERMINO_PRIME>` |
| `<TERMINO_PRIME>` | `*` | `* <FACTOR> <TERMINO_PRIME>` |
| `<TERMINO_PRIME>` | `/` | `/ <FACTOR> <TERMINO_PRIME>` |
| `<TERMINO_PRIME>` | `+, -, >, <, >=, <=, !=, ==, ;, )` | `epsilon` |
| `<FACTOR>` | `(` | `( <EXPRESION> )` |
| `<FACTOR>` | `+, -` | `<SIGN> <VAR_CTE>` |
| `<FACTOR>` | `id, cte_int, cte_float, cte_str` | `<VAR_CTE>` |
| `<SIGN>` | `+` | `+` |
| `<SIGN>` | `-` | `-` |
| `<VAR_CTE>` | `id` | `id` |
| `<VAR_CTE>` | `cte_int` | `cte_int` |
| `<VAR_CTE>` | `cte_float` | `cte_float` |
| `<VAR_CTE>` | `cte_str` | `cte_str` |

## Notas para el PDF

Incluye la gramatica, las tablas FIRST/FOLLOW, la parse table anterior y una
explicacion breve del codigo. Para resultados, usa la salida de:

```bash
.venv/bin/python run_pruebas.py
```
