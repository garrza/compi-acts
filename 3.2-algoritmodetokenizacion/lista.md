# Analisis lexico de Little Duck

Actividad 3.2: implementacion del analisis lexico con expresiones regulares para reconocimiento y generacion de tokens.

## Archivos de entrega

- `patokenizer.py`: tokenizer principal.
- `run_casos.py`: ejecuta todos los casos en `casos-prueba/`.
- `casos-prueba/factorial.txt`: caso proporcionado.
- `casos-prueba/patoprograma.txt`: caso proporcionado.
- `casos-prueba/lexico.txt`: caso proporcionado de cobertura lexica y errores.
- `casos-prueba/lexico_extendido.txt`: caso propio con cobertura completa del lexico de Little Duck.
- `casos-prueba/custom_test.txt`: programa propio completo.
- `casos-prueba/errores_test.txt`: recuperacion ante simbolos no reconocidos.
- `patokenizer_colab.ipynb`: notebook para ejecutar el tokenizer en Colab.

## Lexemas y expresiones regulares

| Categoria | Token | Expresion regular | Ejemplos |
| --- | --- | --- | --- |
| Palabra reservada | `kw_program` | `program` | `program` |
| Palabra reservada | `kw_main` | `main` | `main` |
| Palabra reservada | `kw_var` | `var` | `var` |
| Palabra reservada | `kw_end` | `end` | `end` |
| Palabra reservada | `kw_void` | `void` | `void` |
| Palabra reservada | `kw_int` | `int` | `int` |
| Palabra reservada | `kw_float` | `float` | `float` |
| Palabra reservada | `kw_string` | `string` | `string` |
| Palabra reservada | `kw_if` | `if` | `if` |
| Palabra reservada | `kw_else` | `else` | `else` |
| Palabra reservada | `kw_do` | `do` | `do` |
| Palabra reservada | `kw_while` | `while` | `while` |
| Palabra reservada | `kw_print` | `print` | `print` |
| Identificador | `id` | `[A-Za-z][A-Za-z0-9_]*` | `x`, `contador`, `id_7` |
| Constante entera | `cte_int` | `[0-9]+` | `0`, `14`, `7879` |
| Constante flotante | `cte_float` | `[0-9]+\.[0-9]+` | `3.14`, `0.001` |
| Constante string | `cte_str` | `"[^"\n]*"` | `"hola"`, `"cade #"` |
| Comentario | `comment` | `#.*` | `# comentario` |
| Asignacion | `op_assign` | `=` | `=` |
| Relacional | `op_eq` | `==` | `==` |
| Relacional | `op_ne` | `!=` | `!=` |
| Relacional | `op_gt` | `>` | `>` |
| Relacional | `op_lt` | `<` | `<` |
| Relacional | `op_ge` | `>=` | `>=` |
| Relacional | `op_le` | `<=` | `<=` |
| Aritmetico | `op_plus` | `\+` | `+` |
| Aritmetico | `op_minus` | `-` | `-` |
| Aritmetico | `op_times` | `\*` | `*` |
| Aritmetico | `op_divide` | `/` | `/` |
| Delimitador | `l_paren` | `\(` | `(` |
| Delimitador | `r_paren` | `\)` | `)` |
| Delimitador | `l_brace` | `\{` | `{` |
| Delimitador | `r_brace` | `\}` | `}` |
| Delimitador | `l_bracket` | `\[` | `[` |
| Delimitador | `r_bracket` | `\]` | `]` |
| Delimitador | `semicolon` | `;` | `;` |
| Delimitador | `comma` | `,` | `,` |
| Delimitador | `colon` | `:` | `:` |

## Automatas por lexema

Los automatas se describen con estados `q0`, `q1`, etc. Un estado marcado como final acepta el token.

| Token | Automata |
| --- | --- |
| Palabras reservadas | `q0 --letras exactas de la palabra--> qf`. Despues se verifica que la lexema completa coincida con la tabla de reservadas. |
| `id` | `q0 --letra--> q1(final); q1 --letra/digito/_--> q1`. |
| `cte_int` | `q0 --digito--> q1(final); q1 --digito--> q1`. |
| `cte_float` | `q0 --digito--> q1; q1 --digito--> q1; q1 --.--> q2; q2 --digito--> q3(final); q3 --digito--> q3`. |
| `cte_str` | `q0 --"--> q1; q1 --cualquier caracter excepto " y salto de linea--> q1; q1 --"--> q2(final)`. |
| `comment` | `q0 --#--> q1(final); q1 --cualquier caracter hasta fin de linea--> q1`. |
| Operadores de dos caracteres | `q0 --primer simbolo--> q1; q1 --segundo simbolo--> q2(final)` para `==`, `!=`, `>=`, `<=`. |
| Operadores de un caracter | `q0 --simbolo--> q1(final)` para `=`, `>`, `<`, `+`, `-`, `*`, `/`. |
| Delimitadores | `q0 --simbolo--> q1(final)` para `(`, `)`, `{`, `}`, `[`, `]`, `;`, `,`, `:`. |

## Formato de salida

El programa imprime cada linea con su token stream y una tabla legible:

```text
Linea 1:    a = 14;
Token stream:  [ (id, 'a'), (op_assign, '='), (cte_int, '14'), (semicolon, ';') ]
  a    id
  =    op_assign
  14   cte_int
  ;    semicolon
```

Los simbolos no reconocidos se reportan con linea y columna. El tokenizer avanza un caracter y continua revisando el resto del archivo.

## Codigo a capturar

Para la seccion de capturas de pantalla del codigo en el PDF final, capturar estas partes:

- `patokenizer.py`, lineas 13-86: clase `Tokenizer`, algoritmo de longest match, tokenizacion por linea y recuperacion de errores.
- `patokenizer.py`, lineas 93-135: tabla de expresiones regulares y palabras reservadas.
- `patokenizer.py`, lineas 138-189: formato de salida y lectura del archivo de entrada.
- `run_casos.py`, lineas 17-44: ejecucion automatica de todos los casos de prueba.

## Ejecucion

Ejecutar un archivo:

```bash
python3 patokenizer.py casos-prueba/factorial.txt
```

Ejecutar todos los casos:

```bash
python3 run_casos.py
```

## Resultados de pruebas

La evidencia de salida puede generarse con:

```bash
python3 run_casos.py > resultados_pruebas.txt
```

Casos cubiertos:

- `factorial.txt`: programa completo con funciones, ciclos, condiciones, llamadas y constantes.
- `patoprograma.txt`: programa base de clase.
- `lexico.txt`: palabras reservadas, identificadores, constantes, operadores, delimitadores y errores.
- `lexico_extendido.txt`: cobertura propia de todo el lexico de Little Duck.
- `custom_test.txt`: programa propio con funciones, tipos, strings, relacionales y aritmetica.
- `errores_test.txt`: simbolos invalidos como `@`, `$`, `&`, `^` sin detener la ejecucion.

Resultados validados:

- `python3 -m py_compile patokenizer.py run_casos.py`: sin errores.
- `python3 run_casos.py`: ejecuta todos los archivos de `casos-prueba/`.
- Sin errores lexicos: `custom_test.txt`, `factorial.txt`, `lexico_extendido.txt`, `patoprograma.txt`.
- Errores esperados en `lexico.txt`: `&`, `!`, `!`, `%`.
- Errores esperados en `errores_test.txt`: `@`, `$`, `&`, `^`.
- La ejecucion continua despues de cada simbolo no reconocido y conserva los tokens validos posteriores.

## Link de Colab

Link para ejecutar el notebook desde GitHub en Google Colab:

```text
https://colab.research.google.com/github/garrza/compi-acts/blob/main/3.2-algoritmodetokenizacion/patokenizer_colab.ipynb
```

El link funcionara cuando `patokenizer_colab.ipynb` y los cambios del tokenizer esten subidos a la rama `main`.
