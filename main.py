import sys
from lexer import tokenizar
from parser_ll1 import LL1Parser, SyntaxErrorAbort

def main():
   
    if len(sys.argv) != 3:
        print("Uso: python main.py <archivo_entrada.py> <archivo_salida.txt>")
        sys.exit(1)

    archivo_entrada = sys.argv[1]
    archivo_salida = sys.argv[2]

    try:
       
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            codigo = f.read()

     
        tokens = tokenizar(codigo)

       
        parser = LL1Parser(tokens)
        parser.parse()  # si termina sin excepciones, todo bien


        with open(archivo_salida, 'w', encoding='utf-8') as out:
            out.write("El analisis sintactico ha finalizado exitosamente.\n")

        print("Analisis completado exitosamente.")
        print(f"Salida escrita en: {archivo_salida}")

    except SyntaxErrorAbort as e:
       
        mensaje_error = str(e)
        with open(archivo_salida, 'w', encoding='utf-8') as out:
            out.write(mensaje_error + "\n")

        print("Se detectó un error sintáctico:")
        print(mensaje_error)

    except FileNotFoundError:
        print(f"Error: no se encontró el archivo '{archivo_entrada}'.")

    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()
