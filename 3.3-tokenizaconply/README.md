# Actividad 3.3 - Lexer de Little Duck con PLY

Lexer de Little Duck implementado con `ply.lex`. Lee un archivo fuente, genera un token stream unico y lo imprime agrupado por linea solo para facilitar la lectura.

## PLY

`PLY` (`Python Lex-Yacc`) implementa herramientas tipo `lex` y `yacc` en Python. Para construir un lexer se define:

- `tokens`: lista de nombres de tokens validos.
- `t_TOKEN = r"..."`: reglas simples por expresion regular.
- `def t_TOKEN(t): ...`: reglas con logica adicional.
- `t_ignore`, `t_newline`, `t_error`: reglas especiales para espacios, saltos de linea y errores.

Al ejecutar `lex.lex()`, PLY valida que `tokens` exista, que no haya reglas para tokens no declarados, que las regex compilen, que ninguna acepte cadena vacia y que las funciones tengan una firma valida. Las reglas por funcion se prueban en orden de aparicion; las reglas por string se ordenan por longitud de regex, lo que ayuda a reconocer `==` antes que `=`.

Las palabras reservadas se reconocen con la regla de identificadores y una tabla:

```python
def t_ID(t):
    r"[A-Za-z][A-Za-z0-9_]*"
    t.type = reserved.get(t.value, "ID")
    return t
```

Esto evita que lexemas como `printed` se partan incorrectamente como `print` + `ed`.

## Cambios desde 3.2

- Lexer reimplementado con `ply.lex`.
- Labels normalizados en mayusculas.
- Palabras reservadas identificadas de forma unica con `reserved`.
- Soporte para `[` y `]`, usados por los casos de prueba.
- Identificadores con `_` despues del primer caracter.
- Errores lexicos con linea, columna y `lexpos`.
- Salida detallada por token, agrupada por linea.

## Lexemas

Automatas usados:

- `A_ID`: `q0 --letra--> q1; q1 --(letra|digito|_)--> q1`
- `A_INT`: `q0 --digito--> q1; q1 --digito--> q1`
- `A_FLOAT`: `A_INT --.--> q2; q2 --digito--> q3; q3 --digito--> q3`
- `A_STRING`: `q0 --"--> q1; q1 --char/escape--> q1; q1 --"--> qf`
- `A_SYMBOL`: `q0 --simbolo--> qf`
- `A_COMMENT`: `q0 --#--> q1; q1 --no salto de linea--> q1`

### Palabras reservadas

Todas usan `A_ID` y despues se validan contra `reserved`.

| Lexema | Label | Regex |
|---|---|---|
| `program` | `PROGRAM` | `[A-Za-z][A-Za-z0-9_]*` + lookup |
| `var` | `VAR` | `[A-Za-z][A-Za-z0-9_]*` + lookup |
| `int` | `INT` | `[A-Za-z][A-Za-z0-9_]*` + lookup |
| `float` | `FLOAT` | `[A-Za-z][A-Za-z0-9_]*` + lookup |
| `string` | `STRING` | `[A-Za-z][A-Za-z0-9_]*` + lookup |
| `void` | `VOID` | `[A-Za-z][A-Za-z0-9_]*` + lookup |
| `main` | `MAIN` | `[A-Za-z][A-Za-z0-9_]*` + lookup |
| `end` | `END` | `[A-Za-z][A-Za-z0-9_]*` + lookup |
| `print` | `PRINT` | `[A-Za-z][A-Za-z0-9_]*` + lookup |
| `if` | `IF` | `[A-Za-z][A-Za-z0-9_]*` + lookup |
| `else` | `ELSE` | `[A-Za-z][A-Za-z0-9_]*` + lookup |
| `do` | `DO` | `[A-Za-z][A-Za-z0-9_]*` + lookup |
| `while` | `WHILE` | `[A-Za-z][A-Za-z0-9_]*` + lookup |

### Otros tokens

| Lexema | Label | Automata | Regex |
|---|---|---|---|
| identificador | `ID` | `A_ID` | `[A-Za-z][A-Za-z0-9_]*` |
| entero | `CTE_INT` | `A_INT` | `\d+` |
| flotante | `CTE_FLOAT` | `A_FLOAT` | `\d+\.\d+` |
| string | `CTE_STRING` | `A_STRING` | `"([^\\\n]|(\\.))*?"` |
| `==` | `EQ` | `A_SYMBOL` | `==` |
| `!=` | `NE` | `A_SYMBOL` | `!=` |
| `>=` | `GE` | `A_SYMBOL` | `>=` |
| `<=` | `LE` | `A_SYMBOL` | `<=` |
| `>` | `GT` | `A_SYMBOL` | `>` |
| `<` | `LT` | `A_SYMBOL` | `<` |
| `=` | `ASSIGN` | `A_SYMBOL` | `=` |
| `+` | `PLUS` | `A_SYMBOL` | `\+` |
| `-` | `MINUS` | `A_SYMBOL` | `-` |
| `*` | `TIMES` | `A_SYMBOL` | `\*` |
| `/` | `DIVIDE` | `A_SYMBOL` | `/` |
| `(` | `LPAREN` | `A_SYMBOL` | `\(` |
| `)` | `RPAREN` | `A_SYMBOL` | `\)` |
| `{` | `LBRACE` | `A_SYMBOL` | `\{` |
| `}` | `RBRACE` | `A_SYMBOL` | `\}` |
| `[` | `LBRACKET` | `A_SYMBOL` | `\[` |
| `]` | `RBRACKET` | `A_SYMBOL` | `\]` |
| `,` | `COMMA` | `A_SYMBOL` | `,` |
| `;` | `SEMICOLON` | `A_SYMBOL` | `;` |
| `:` | `COLON` | `A_SYMBOL` | `:` |
| `#...` | `COMMENT` ignorado | `A_COMMENT` | `\#.*` |

## Uso

```bash
cd 3.3-tokenizaconply
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python lexer_little_duck.py casos-prueba/patoprograma.txt
```

El lexer depende de `ply==3.11`, instalado desde `requirements.txt` dentro del entorno virtual local.

## Salida

```text
Linea 1:    program ejemplo;
PROGRAM        value: program            lexpos: 0     column: 1
ID             value: ejemplo            lexpos: 8     column: 9
SEMICOLON      value: ;                  lexpos: 15    column: 16
```

Los errores se reportan al final con linea, columna y `lexpos`.

## Verificacion 

```bash
.venv/bin/python -m py_compile lexer_little_duck.py
.venv/bin/python lexer_little_duck.py casos-prueba/patoprograma.txt
.venv/bin/python lexer_little_duck.py casos-prueba/errores_test.txt
```

## Fuentes

- https://www.dabeaz.com/ply/ply.html
- https://ply.readthedocs.io/en/latest/ply.html
- https://github.com/dabeaz/ply
