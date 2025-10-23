from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

@dataclass
class Token:
    type: str
    lexeme: str
    line: int
    col: int

###############################################################################
# 1) Mapeo token → símbolo de la gramática
###############################################################################

KEYWORDS = {
    "if","elif","else","while","for","in","def","return","pass",
    "and","or","not"
}

OPERATORS = {
    "(", ")", ",", ":", "=", "==", "!=", "<", ">", "<=", ">=",
    "+", "-", "*", "/", "//", "%"
}

def sym_of(tok: Token) -> str:
    """
    Normaliza el token a un terminal LL(1).
    """
    t = tok.type
    lx = tok.lexeme

    if t in {"NEWLINE", "INDENT", "DEDENT", "ENDMARKER"}:
        return t
    if t == "NAME":
        return lx if lx in KEYWORDS else "NAME"
    if t in {"NUMBER", "STRING"}:
        return t
    if lx in OPERATORS:
        return lx
    return lx

###############################################################################
# 2) Gramática y tabla LL(1) - VERSIÓN SIMPLIFICADA Y ROBUSTA
###############################################################################

NT = [
    "program","statements","statement",
    "simple_stmt","after_name","opt_expression",
    "compound_stmt","if_stmt","opt_elifs","opt_else","while_stmt","for_stmt","funcdef",  # CORREGIDO: agregado opt_elifs y opt_else
    "opt_params","param_list","param_tail",
    "suite",
    "expression","or_expr","or_tail","and_expr","and_tail","not_expr",
    "rel_expr","rel_tail","rel_op","arith_expr","arith_tail","term","term_tail",
    "factor","atom","name_or_call","call_opt","opt_args","arg_list","arg_tail"
]

PROD: Dict[int, Tuple[str, List[str]]] = {
    # Programa y statements - SIMPLIFICADO
    1: ("program", ["statements", "ENDMARKER"]),
    2: ("statements", ["statement", "statements"]),
    3: ("statements", []),  # Permite bloques vacíos
    
    # Statement
    4: ("statement", ["simple_stmt", "NEWLINE"]),
    5: ("statement", ["compound_stmt"]),
    
    # Simple statements
    6: ("simple_stmt", ["pass"]),
    7: ("simple_stmt", ["return", "opt_expression"]),
    8: ("simple_stmt", ["NAME", "after_name"]),
    9: ("after_name", ["=", "expression"]),
    10: ("after_name", ["(", "opt_args", ")"]),
    11: ("opt_expression", ["expression"]),
    12: ("opt_expression", []),
    
    # Compound statements
    13: ("compound_stmt", ["if_stmt"]),
    14: ("compound_stmt", ["while_stmt"]),
    15: ("compound_stmt", ["for_stmt"]),
    16: ("compound_stmt", ["funcdef"]),
    
    # If statement - VERSIÓN MUY SIMPLIFICADA
    17: ("if_stmt", ["if", "expression", ":", "suite", "opt_elifs", "opt_else"]),
    18: ("opt_elifs", ["elif", "expression", ":", "suite", "opt_elifs"]),
    19: ("opt_elifs", []),  # Puede no haber elif
    20: ("opt_else", ["else", ":", "suite"]),
    21: ("opt_else", []),   # Puede no haber else
    
    # While y for
    22: ("while_stmt", ["while", "expression", ":", "suite"]),
    23: ("for_stmt", ["for", "NAME", "in", "expression", ":", "suite"]),
    
    # Function definition
    24: ("funcdef", ["def", "NAME", "(", "opt_params", ")", ":", "suite"]),
    25: ("opt_params", ["param_list"]),
    26: ("opt_params", []),
    27: ("param_list", ["NAME", "param_tail"]),
    28: ("param_tail", [",", "NAME", "param_tail"]),
    29: ("param_tail", []),
    
    # Suite - VERSIÓN SIMPLE
    30: ("suite", ["NEWLINE", "INDENT", "statements", "DEDENT"]),
    31: ("suite", ["simple_stmt"]),  # Para one-line suites
    
    # Expresiones
    32: ("expression", ["or_expr"]),
    33: ("or_expr", ["and_expr", "or_tail"]),
    34: ("or_tail", ["or", "and_expr", "or_tail"]),
    35: ("or_tail", []),
    36: ("and_expr", ["not_expr", "and_tail"]),
    37: ("and_tail", ["and", "not_expr", "and_tail"]),
    38: ("and_tail", []),
    39: ("not_expr", ["not", "not_expr"]),
    40: ("not_expr", ["rel_expr"]),
    41: ("rel_expr", ["arith_expr", "rel_tail"]),
    42: ("rel_tail", ["rel_op", "arith_expr"]),
    43: ("rel_tail", []),
    44: ("rel_op", ["<"]),
    45: ("rel_op", [">"]),
    46: ("rel_op", ["=="]),
    47: ("rel_op", ["!="]),
    48: ("rel_op", ["<="]),
    49: ("rel_op", [">="]),
    50: ("arith_expr", ["term", "arith_tail"]),
    51: ("arith_tail", ["+", "term", "arith_tail"]),
    52: ("arith_tail", ["-", "term", "arith_tail"]),
    53: ("arith_tail", []),
    54: ("term", ["factor", "term_tail"]),
    55: ("term_tail", ["*", "factor", "term_tail"]),
    56: ("term_tail", ["/", "factor", "term_tail"]),
    57: ("term_tail", ["//", "factor", "term_tail"]),
    58: ("term_tail", ["%", "factor", "term_tail"]),
    59: ("term_tail", []),
    60: ("factor", ["+", "factor"]),
    61: ("factor", ["-", "factor"]),
    62: ("factor", ["not", "factor"]),
    63: ("factor", ["atom"]),
    64: ("atom", ["(", "expression", ")"]),
    65: ("atom", ["NUMBER"]),
    66: ("atom", ["STRING"]),
    67: ("atom", ["name_or_call"]),
    68: ("name_or_call", ["NAME", "call_opt"]),
    69: ("call_opt", ["(", "opt_args", ")"]),
    70: ("call_opt", []),
    71: ("opt_args", ["arg_list"]),
    72: ("opt_args", []),
    73: ("arg_list", ["expression", "arg_tail"]),
    74: ("arg_tail", [",", "expression", "arg_tail"]),
    75: ("arg_tail", []),
}

###############################################################################
# TABLA LL(1) - VERSIÓN SIMPLIFICADA
###############################################################################

M: Dict[str, Dict[str, int]] = {A: {} for A in NT}

def add(A: str, terms: List[str], pid: int):
    for a in terms:
        if a in M[A]:
            raise ValueError(f"Conflicto LL(1) en {A} con {a}")
        M[A][a] = pid

# --- Program ---
add("program", ["NAME","pass","return","if","while","for","def",
                "NEWLINE","(","NUMBER","STRING","+","-","not","ENDMARKER"], 1)

# --- statements ---
add("statements", ["NAME","pass","return","if","while","for","def","NEWLINE"], 2)
add("statements", ["DEDENT","ENDMARKER"], 3)  # CORRECCIÓN CRÍTICA: statements puede terminar con DEDENT

# --- statement ---
add("statement", ["pass","return","NAME"], 4)
add("statement", ["if","while","for","def"], 5)

# --- simple_stmt ---
add("simple_stmt", ["pass"], 6)
add("simple_stmt", ["return"], 7)
add("simple_stmt", ["NAME"], 8)

# --- after_name ---
add("after_name", ["="], 9)
add("after_name", ["("], 10)

# --- opt_expression ---
add("opt_expression", ["(","NUMBER","STRING","NAME","+","-","not"], 11)
add("opt_expression", ["NEWLINE",")",",",":","DEDENT","ENDMARKER"], 12)

# --- compound_stmt ---
add("compound_stmt", ["if"], 13)
add("compound_stmt", ["while"], 14)
add("compound_stmt", ["for"], 15)
add("compound_stmt", ["def"], 16)

# --- if_stmt - CORREGIDO ---
add("if_stmt", ["if"], 17)
add("opt_elifs", ["elif"], 18)
add("opt_elifs", ["else","NAME","pass","return","if","while","for","def","DEDENT","ENDMARKER","NEWLINE"], 19)
add("opt_else", ["else"], 20)
add("opt_else", ["NAME","pass","return","if","while","for","def","DEDENT","ENDMARKER","NEWLINE"], 21)

# --- while / for ---
add("while_stmt", ["while"], 22)
add("for_stmt", ["for"], 23)

# --- funcdef ---
add("funcdef", ["def"], 24)

# --- parámetros ---
add("opt_params", ["NAME"], 25)
add("opt_params", [")"], 26)
add("param_list", ["NAME"], 27)
add("param_tail", [","], 28)
add("param_tail", [")"], 29)

# --- suite ---
add("suite", ["NEWLINE"], 30)
add("suite", ["NAME","pass","return"], 31)

# --- expresión ---
add("expression", ["(","NUMBER","STRING","NAME","+","-","not"], 32)

# --- or/and/not/relacionales ---
add("or_expr", ["(","NUMBER","STRING","NAME","+","-","not"], 33)
add("or_tail", ["or"], 34)
add("or_tail", [")",",",":","NAME","pass","return","if","while","for","def",
                "DEDENT","ENDMARKER","NEWLINE","+","-","*","/","//","%","==","!=",
                "<",">","<=",">="], 35)

add("and_expr", ["(","NUMBER","STRING","NAME","+","-","not"], 36)
add("and_tail", ["and"], 37)
add("and_tail", [")",",",":","NAME","pass","return","if","while","for","def",
                 "DEDENT","ENDMARKER","NEWLINE","+","-","*","/","//","%","==","!=",
                 "<",">","<=",">=","or"], 38)

add("not_expr", ["not"], 39)
add("not_expr", ["(","NUMBER","STRING","NAME","+","-"], 40)

add("rel_expr", ["(","NUMBER","STRING","NAME","+","-","not"], 41)
add("rel_tail", ["<",">","==","!=","<=",">="], 42)
add("rel_tail", [")",",",":","NAME","pass","return","if","while","for","def",
                 "DEDENT","ENDMARKER","NEWLINE","+","-","*","/","//","%","or","and"], 43)

# --- aritméticas ---
add("arith_expr", ["(","NUMBER","STRING","NAME","+","-","not"], 50)
add("arith_tail", ["+"], 51)
add("arith_tail", ["-"], 52)
add("arith_tail", [")",",",":","NAME","pass","return","if","while","for","def",
                   "DEDENT","ENDMARKER","NEWLINE","*","/","//","%","==","!=",
                   "<",">","<=",">=","or","and"], 53)

add("term", ["(","NUMBER","STRING","NAME","+","-","not"], 54)
add("term_tail", ["*"], 55)
add("term_tail", ["/"], 56)
add("term_tail", ["//"], 57)
add("term_tail", ["%"], 58)
add("term_tail", [")",",",":","NAME","pass","return","if","while","for","def",
                  "DEDENT","ENDMARKER","NEWLINE","+","-","==","!=","<",">","<=",">=",
                  "or","and"], 59)

# --- factor / atom ---
add("factor", ["+"], 60)
add("factor", ["-"], 61)
add("factor", ["not"], 62)
add("factor", ["(","NUMBER","STRING","NAME"], 63)
add("atom", ["("], 64)
add("atom", ["NUMBER"], 65)
add("atom", ["STRING"], 66)
add("atom", ["NAME"], 67)
add("name_or_call", ["NAME"], 68)
add("call_opt", ["("], 69)
add("call_opt", [")",",",":","NAME","pass","return","if","while","for","def",
                 "DEDENT","ENDMARKER","NEWLINE","+","-","*","/","//","%","==","!=",
                 "<",">","<=",">=","or","and"], 70)

# --- argumentos ---
add("opt_args", ["(","NUMBER","STRING","NAME","+","-","not"], 71)
add("opt_args", [")"], 72)
add("arg_list", ["(","NUMBER","STRING","NAME","+","-","not"], 73)
add("arg_tail", [","], 74)
add("arg_tail", [")"], 75)

# --- rel_op ---
add("rel_op", ["<"], 44)
add("rel_op", [">"], 45)
add("rel_op", ["=="], 46)
add("rel_op", ["!="], 47)
add("rel_op", ["<="], 48)
add("rel_op", [">="], 49)

###############################################################################
# 3) Parser LL(1)
###############################################################################

class SyntaxErrorAbort(Exception):
    pass

class LL1Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0
        self.stack: List[str] = []

    def current(self) -> Token:
        if self.i < len(self.tokens):
            return self.tokens[self.i]
        return Token("ENDMARKER", "", -1, -1)

    def advance(self):
        if self.i < len(self.tokens) - 1:
            self.i += 1

    def error(self, expected_syms: List[str]):
        tok = self.current()
        found_lex = tok.lexeme if tok.type != "ENDMARKER" else "EOF"
        esperados = ", ".join(f"\"{s}\"" for s in expected_syms)
        msg = f"<{tok.line},{tok.col}> Error sintactico: se encontro: \"{found_lex}\"; se esperaba: {esperados}."
        raise SyntaxErrorAbort(msg)

    def parse(self) -> str:
        self.stack = ["ENDMARKER", "program"]

        while self.stack:
            X = self.stack.pop()
            tok = self.current()
            look = sym_of(tok)

            # Terminal
            if X not in NT:
                if X == "ε":
                    continue
                if X == look:
                    self.advance()
                    continue
                self.error([X])

            # No terminal
            if look in M[X]:
                pid = M[X][look]
                _, rhs = PROD[pid]
                # Manejo especial para producciones vacías
                if not rhs:
                    continue
                for sym in reversed(rhs):
                    self.stack.append(sym)
            else:
                expected = sorted(M[X].keys()) or ["<no-predict>"]
                self.error(expected)

        return "El analisis sintactico ha finalizado exitosamente."

###############################################################################
# 4) Interfaz
###############################################################################

def analizar(tokens: List[Token]) -> str:
    parser = LL1Parser(tokens)
    return parser.parse()