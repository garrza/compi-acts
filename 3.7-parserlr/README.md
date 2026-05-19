# Actividad 3.7 — Lexer + Parser LR de Little Duck con PLY

Julen Hoppenstedt Mandiola · Ramiro Alejandro Garza Villarreal

## Entregables

### Codigo
- `little_duck.py` — un solo archivo con lexer, parser, manejo de errores, token-stream printer y driver.
- `casos_prueba/01_completo_anidado.txt` — happy path, todas las estructuras y anidamiento.
- `casos_prueba/02_error_lexico.txt` — caracter `@` invalido.
- `casos_prueba/03_falta_punto_y_coma.txt` — recuperacion limpia tras un `;` faltante.
- `casos_prueba/04_error_sintactico_anidado.txt` — error sintactico dentro de if/do-while anidados.

### Notebook
- `Llittle-Duck-v2.ipynb` — version Colab (8 celdas tematicas, casos embebidos).
- Subido a Drive: <https://colab.research.google.com/drive/1m73NNnhP0PZgbtSNUpiwanAH8zGbfHbw>

## Como correr

```
python3 little_duck.py                              # corre los 4 casos de prueba
python3 little_duck.py casos_prueba/<archivo>.txt   # corre uno solo
```

Cada caso imprime: la fuente con numero de linea, el token stream con tipo/valor/linea/columna, el resultado (OK/ERROR) y la lista de errores lexicos y sintacticos si los hay.

## Rubrica cubierta

- Lexer (15 pts): regex unicas por token, longest match, conteo de columnas, recuperacion lexica. Token stream impreso.
- Parser (35 pts): gramatica LR completa con recursion izquierda; alternativas con `|` en funciones separadas; cero conflictos shift/reduce.
- Manejo de errores: estrategia hibrida documentada en PLY (`statement : error SEMICOL` + `var_decl : error SEMICOL` + `p_error` solo registra).
- 4 casos de prueba (10 pts): cubren happy path, error lexico, error sintactico simple, error sintactico anidado.
- Salidas legibles (10 pts): fuente numerada + tabla de tokens + resultado.
