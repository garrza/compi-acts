#  Léxico de Little Duck

## 1. Palabras reservadas

Son tokens con significado fijo en el lenguaje:

```
program
var
int
float
string
void
main
end
print
if
else
do
while
```

---

##  2. Identificadores

```
id
```

**Regla típica:**

* Empieza con letra
* Puede contener letras y números
* Ejemplo:

```
x
contador
valor1
temp123
```

---

##  3. Constantes alfanuméricas

```
cte_int
cte_float
cte_string
```

**Ejemplos:**

```
123
0
999

3.14
0.001
10.0

"hola"
"test"
"123abc"
```

---

##  4. Operadores aritméticos

```
+
-
*
/
```

**Ejemplos:**

```
a + b
x - 5
y * 3
z / 2
```

---

##  5. Operadores relacionales

Del diagrama:

```
>
<
!=
==
>=
<=
```

**Ejemplos:**

```
a > b
x < 10
y != 0
```

---

##  6. Operador de asignación

```
=
```

**Ejemplo:**

```
x = 5;
```

---

##  7. Delimitadores y símbolos especiales

```
;
:
,
(
)
{
}
```

**Ejemplos:**

```
a = 5;
print(a);
if (x > 0) { ... }
var x : int;
```

---

##  8. Comentarios

Formato:

```
# comentario
```

**Ejemplos:**

```
# este es un comentario
# TODO: arreglar esto
```

---

#  Casos de prueba (propios)

##  Caso 1: Programa completo

```
program test;
var x : int;
main {
    x = 10;
    print(x);
}
end
```

---

## Caso 2: Uso de todos los tipos

```
program tipos;
var a : int;
var b : float;
var c : string;

main {
    a = 5;
    b = 3.14;
    c = "hola";
    print(a, b, c);
}
end
```

---

## Caso 3: Condiciones y ciclos

```
program control;
var x : int;

main {
    x = 0;
    do {
        x = x + 1;
    } while (x < 10);

    if (x != 0) {
        print(x);
    } else {
        print(0);
    }
}
end
```

---

## Caso 4: Comentarios

```
# inicio del programa
program demo;

# variable
var x : int;

main {
    x = 1; # asignación
    print(x);
}
end
```

---

## Resumen

El léxico de Little Duck incluye:

* Palabras reservadas
* Identificadores
* Constantes (int, float, string)
* Operadores aritméticos y relacionales
* Operador de asignación
* Delimitadores
* Comentarios con `#`

