def suma(a, b):
    resultado = a + b
    if resultado > 100:
        return resultado - 1
    else:
        return resultado + 1

x = 50
y = 25
z = suma(x, y)