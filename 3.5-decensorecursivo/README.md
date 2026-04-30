# Actividad 3.5 - Descenso recursivo

Parser de descenso recursivo para validar asignaciones de Little Duck.

## Gramatica implementada

```text
<ASSIGN>         ::= id = <EXPRESION> ;
<EXPRESION>      ::= <EXP> [ <OP_REL> <EXP> ]
<OP_REL>         ::= > | < | >= | <= | != | ==
<EXP>            ::= <TERMINO> <EXP_PRIME>
<EXP_PRIME>      ::= (+ | -) <TERMINO> <EXP_PRIME> | epsilon
<TERMINO>        ::= <FACTOR> <TERMINO_PRIME>
<TERMINO_PRIME>  ::= (* | /) <FACTOR> <TERMINO_PRIME> | epsilon
<FACTOR>         ::= ( <EXPRESION> ) | (+ | -) <VAR_CTE> | <VAR_CTE>
<VAR_CTE>        ::= id | cte_int | cte_float
```

## Tokenizer integrado

El archivo `parser_little_duck.py` incluye un tokenizer reducido inspirado en
las actividades 3.2 y 3.3. Reconoce los tokens necesarios para esta actividad:

- `ID`
- `CTE_INT`
- `CTE_FLOAT`
- `ASSIGN`
- `PLUS`, `MINUS`, `TIMES`, `DIVIDE`
- `GT`, `LT`, `GE`, `LE`, `NE`, `EQ`
- `LPAREN`, `RPAREN`, `SEMICOLON`

## Uso

```bash
cd /Users/ramiro/Desktop/code/class-acts/compi-acts/3.5-decensorecursivo
.venv/bin/python parser_little_duck.py
.venv/bin/python parser_little_duck.py ejemplos_assign.txt
```

Sin argumentos corre una lista de ejemplos validos e invalidos. Con un archivo
como argumento analiza su contenido y muestra el token stream junto con el
resultado sintactico.

## Verificacion

```bash
.venv/bin/python -m py_compile parser_little_duck.py
.venv/bin/python parser_little_duck.py ejemplos_assign.txt
```
