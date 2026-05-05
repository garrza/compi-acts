# Actividad 3.6 - Parser predictivo y parse tables

Parser predictivo LL(1) para validar asignaciones de Little Duck. El directorio
incluye solo el codigo fuente, los casos de prueba y estas notas para documentar
la implementacion en el PDF.

## Archivos

- `parser_predictivo_little_duck.py`: tokenizer reducido, FIRST/FOLLOW, parse table y parser predictivo.
- `casos_prueba.txt`: casos solicitados por la actividad.

## Como correrlo

```bash
cd /Users/ramiro/Desktop/code/class-acts/compi-acts/3.6-parserpredictivo
.venv/bin/python parser_predictivo_little_duck.py casos_prueba.txt
```

Tambien funciona sin argumento porque toma `casos_prueba.txt` por defecto:

```bash
.venv/bin/python parser_predictivo_little_duck.py
```

## Gramatica

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

## Parse table

Solo se listan entradas no vacias. Las entradas faltantes son errores.

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

## Explicacion breve para el PDF

El tokenizer recorre cada linea, ignora espacios y comentarios, y aplica la
coincidencia mas larga para reconocer constantes, identificadores, operadores,
parentesis y `;`. Si no reconoce un simbolo, agrega un error lexico con linea y
columna.

El parser usa una pila inicial `EOF, <ASSIGN>`. Si el tope es terminal, debe
coincidir con el token actual. Si el tope es no terminal, consulta la parse
table con el lookahead y empuja la produccion encontrada en orden inverso. Una
celda vacia de la tabla produce un error sintactico con los tokens esperados.
