import re
from dataclasses import dataclass

@dataclass
class Token:
    type: str
    lexeme: str
    line: int
    col: int

###############################################################################
# 1) Definición de patrones
###############################################################################

KEYWORDS = {
    "if","elif","else","while","for","in","def","return","pass",
    "and","or","not"
}

TOKEN_REGEX = [
    ("NUMBER",   r'\d+(\.\d+)?'),
    ("STRING",   r'(\".*?\"|\'.*?\')'),
    ("NAME",     r'[A-Za-z_][A-Za-z_0-9]*'),
    ("OP",       r'==|!=|<=|>=|\+|\-|\*|/|//|%|=|<|>'),
    ("DELIM",    r'[()\[\]:,]'),
    ("NEWLINE",  r'\n'),
    ("SKIP",     r'[ \t]+'),
    ("MISMATCH", r'.')
]

TOKEN_RE = re.compile('|'.join(f'(?P<{t}>{p})' for t, p in TOKEN_REGEX))

###############################################################################
# 2) Función principal del lexer - CORREGIDA
###############################################################################

def tokenizar(codigo: str):
    tokens = []
    indent_stack = [0]
    line_num = 1

    lines = codigo.splitlines(keepends=True)
    
    for line in lines:
        # Detectar indentación (solo espacios)
        indent = 0
        for char in line:
            if char == ' ':
                indent += 1
            elif char == '\t':
                # Convertir tabs a espacios (4 espacios por tab)
                indent += 4
            else:
                break
        
        # Manejar DEDENTs si la indentación actual es menor
        while indent < indent_stack[-1]:
            indent_stack.pop()
            tokens.append(Token("DEDENT", "DEDENT", line_num, 0))
        
        # Manejar INDENT si la indentación actual es mayor
        if indent > indent_stack[-1]:
            indent_stack.append(indent)
            tokens.append(Token("INDENT", "INDENT", line_num, 0))
        
        # Procesar tokens de la línea (ignorando espacios iniciales)
        line_content = line.strip()
        if line_content:  # Solo procesar si la línea no está vacía
            line_start = len(line) - len(line.lstrip())
            for mo in TOKEN_RE.finditer(line_content):
                tipo = mo.lastgroup
                valor = mo.group()
                token_col = line_start + mo.start()

                if tipo == "SKIP":
                    continue
                if tipo == "MISMATCH":
                    continue

                if tipo == "NAME" and valor in KEYWORDS:
                    tokens.append(Token(valor, valor, line_num, token_col))
                elif tipo in {"NAME", "NUMBER", "STRING"}:
                    tokens.append(Token(tipo, valor, line_num, token_col))
                elif tipo == "OP":
                    tokens.append(Token(valor, valor, line_num, token_col))
                elif tipo == "DELIM":
                    tokens.append(Token(valor, valor, line_num, token_col))
                elif tipo == "NEWLINE":
                    # Los NEWLINE dentro de la línea se ignoran, solo importa el final
                    continue
            
            # Agregar NEWLINE al final de cada línea no vacía
            tokens.append(Token("NEWLINE", "\\n", line_num, len(line.rstrip())))
        
        line_num += 1

    # Cerrar todas las indentaciones abiertas al final del archivo
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token("DEDENT", "DEDENT", line_num, 0))

    tokens.append(Token("ENDMARKER", "", line_num, 0))
    return tokens