# Parser LL(1) para Subconjunto de Python

## Descripción
Este proyecto implementa un parser LL(1) que analiza sintácticamente un subconjunto del lenguaje Python. Incluye un lexer para tokenización y un parser para análisis sintáctico utilizando gramática LL(1).

## Ejecución del Proyecto

### Prerrequisitos
- Python 3.6 o superior

### Comando de Ejecución
```bash
python main.py <archivo_entrada.py> <archivo_salida.txt>
```

### Ejemplos de Uso
```bash
# Analizar archivo de entrada y guardar resultado en salida
python main.py prueba1.py salida1.txt
python main.py prueba2.py salida2.txt  
python main.py prueba4.py salida4.txt
```

## Casos de Uso Soportados

### 1. Funciones con Múltiples Parámetros
**Archivo: prueba1.py**
```python
def suma(a, b):
    resultado = a + b
    if resultado > 100:
        return resultado - 1
    else:
        return resultado + 1

x = 50
y = 25
z = suma(x, y)
```

**Características demostradas:**
- Definición de funciones con parámetros
- Expresiones aritméticas (+, -)
- Estructuras if-else
- Operadores relacionales (>)
- Llamadas a funciones
- Asignaciones de variables
- Manejo de indentación

### 2. Bucles y Condicionales Complejos
**Archivo: prueba2.py**
```python
contador = 10
while contador > 0:
    if contador % 2 == 0:
        resultado = contador * 2
    else:
        resultado = contador + 1
    contador = contador - 1

for i in range:
    valor = i * 3
```

**Características demostradas:**
- Bucles while con condición
- Bucles for con iteradores
- Expresiones aritméticas (+, -, *, %)
- Operadores relacionales (>, ==)
- Estructuras if-else anidadas
- Múltiples niveles de indentación

### 3. Casos Simples y Statements Básicos
**Archivo: prueba4.py**
```python
pass
return
x = 5
if x > 0:
    pass
```

**Características demostradas:**
- Statements simples (pass, return)
- Asignaciones básicas
- Condicionales simples
- Operadores relacionales (>)
- Manejo de bloques mínimos

## Estructura del Proyecto

```
proyecto/
├── main.py              # Programa principal
├── parser_ll1.py        # Parser LL(1) y gramática
├── lexer.py            # Tokenizador
├── entrada.py          # Ejemplo de entrada
├── prueba1.py          # Caso 1: Funciones
├── prueba2.py          # Caso 2: Bucles
├── prueba3.py          # Caso 4: Statements simples
└── salida*.txt         # Archivos de salida generados
```

## Resultados Esperados

Para cada archivo de prueba exitoso, el programa generará un archivo de salida con el mensaje:
```
El analisis sintactico ha finalizado exitosamente.
```

Si ocurre un error sintáctico, el archivo de salida contendrá un mensaje de error detallado indicando la línea, columna y tokens esperados.

## Limitaciones Conocidas

El parser no soporta:
- Operador de división (/) en ciertos contextos complejos
- Listas, diccionarios u otras estructuras de datos
- Clases y programación orientada a objetos
- Manejadores de excepciones (try/except)
- Algunos operadores avanzados (** , &, |, etc.)

## Gramática Implementada

La gramática LL(1) implementada cubre:
- Declaraciones de funciones con parámetros
- Estructuras de control (if, elif, else, while, for)
- Expresiones aritméticas y lógicas
- Asignaciones de variables
- Llamadas a funciones
- Manejo de indentación para bloques de código
