from dataclasses import dataclass

@dataclass
class Token:
    type: str
    lexeme: str
    line: int
    col: int

###############################################################################
# 1) Definición general
###############################################################################

KEYWORDS = {
    "if","elif","else","while","for","in","def","return","pass",
    "and","or","not"
}

OPERATORS = {
    "==","!=", "<=", ">=", "+","-","*","/","//","%","=","<",">"
}

DELIMITERS = {"(",")","[","]",":",","}

###############################################################################
# 2) Clases de caracteres
###############################################################################

def cls(c):
    if c.isalpha() or c == "_": return "LETTER"
    if c.isdigit(): return "DIGIT"
    if c in {" ", "\t"}: return "SPACE"
    if c in {"'", '"'}: return "QUOTE"
    if c == ".": return "DOT"
    return c  # cada otro char literal

###############################################################################
# 3) AFDs individuales (formalizados)
###############################################################################

def afd_identificador(line, i):
    """AFD para identificadores o palabras clave"""
    state = 0
    lexeme = ""
    start = i
    while i < len(line):
        c = line[i]
        cat = cls(c)
        if state == 0:
            if cat == "LETTER":
                state = 1
                lexeme += c
                i += 1
            else:
                break
        elif state == 1:
            if cat in {"LETTER", "DIGIT"}:
                lexeme += c
                i += 1
            else:
                break
    if state == 1:
        tipo = lexeme if lexeme in KEYWORDS else "NAME"
        return Token(tipo, lexeme, 0, start), i
    return None, i


def afd_numero(line, i):
    """AFD para números enteros o decimales"""
    state = 0
    lexeme = ""
    start = i
    while i < len(line):
        c = line[i]
        cat = cls(c)
        if state == 0:
            if cat == "DIGIT":
                lexeme += c
                state = 1
                i += 1
            else:
                break
        elif state == 1:
            if cat == "DIGIT":
                lexeme += c
                i += 1
            elif cat == "DOT":
                lexeme += c
                state = 2
                i += 1
            else:
                break
        elif state == 2:
            if cat == "DIGIT":
                lexeme += c
                state = 3
                i += 1
            else:
                break
        elif state == 3:
            if cat == "DIGIT":
                lexeme += c
                i += 1
            else:
                break
    if state in {1,3}:  # aceptación
        return Token("NUMBER", lexeme, 0, start), i
    return None, i


def afd_cadena(line, i):
    """AFD para cadenas con comillas simples o dobles"""
    start = i
    quote = line[i]
    state = 0
    lexeme = ""
    i += 1
    state = 1
    lexeme += quote
    while i < len(line):
        c = line[i]
        if c == quote:
            lexeme += c
            i += 1
            return Token("STRING", lexeme, 0, start), i
        else:
            lexeme += c
            i += 1
    # no se cerró -> aún así aceptamos para no bloquear
    return Token("STRING", lexeme, 0, start), i


def afd_operador_delim(line, i):
    """AFD para operadores y delimitadores"""
    start = i
    if i+1 < len(line) and line[i:i+2] in OPERATORS:
        lex = line[i:i+2]
        return Token(lex, lex, 0, start), i+2
    if line[i] in OPERATORS:
        return Token(line[i], line[i], 0, start), i+1
    if line[i] in DELIMITERS:
        return Token(line[i], line[i], 0, start), i+1
    return None, i

###############################################################################
# 4) Lexer principal
###############################################################################

def tokenizar(codigo: str):
    tokens = []
    indent_stack = [0]
    line_num = 1
    lines = codigo.splitlines(keepends=True)

    for line in lines:
        # ---- Indentación ----
        indent = 0
        i = 0
        while i < len(line) and line[i] in {" ", "\t"}:
            indent += 4 if line[i] == "\t" else 1
            i += 1

        rest = line[i:]
        if rest.strip() == "" or rest.lstrip().startswith("#"):
            line_num += 1
            continue

        while indent < indent_stack[-1]:
            indent_stack.pop()
            tokens.append(Token("DEDENT", "DEDENT", line_num, 0))
        if indent > indent_stack[-1]:
            indent_stack.append(indent)
            tokens.append(Token("INDENT", "INDENT", line_num, 0))

        # ---- Escaneo de tokens ----
        while i < len(line):
            c = line[i]
            if c in {" ", "\t"}:
                i += 1
                continue
            if c == "\n":
                break
            if c == "#":
                break  # comentario
            token = None

            if c.isalpha() or c == "_":
                token, i = afd_identificador(line, i)
            elif c.isdigit():
                token, i = afd_numero(line, i)
            elif c in {"'", '"'}:
                token, i = afd_cadena(line, i)
            else:
                token, i = afd_operador_delim(line, i)

            if token:
                token.line = line_num
                tokens.append(token)
            else:
                i += 1  # carácter desconocido

        tokens.append(Token("NEWLINE", "\\n", line_num, len(line.rstrip())))
        line_num += 1

    # ---- Final ----
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token("DEDENT", "DEDENT", line_num, 0))
    tokens.append(Token("ENDMARKER", "", line_num, 0))
    return tokens
