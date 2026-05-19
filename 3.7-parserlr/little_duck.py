# Compiladores TC3002B
# Actividad 3.7 - Lexer + Parser LR de Little Duck con PLY
#
# Un solo archivo: lexer, parser, driver. Para correr:
#     python little_duck.py                   # corre todos los .txt en casos_prueba/
#     python little_duck.py archivo.txt       # corre un solo archivo

import os
import sys

import ply.lex as lex
import ply.yacc as yacc


# =================================================================
#                              LEXER
# =================================================================

# Diccionario de palabras reservadas: lexema -> label del token.
reserved = {
    "program": "KW_PROGRAM",
    "main":    "KW_MAIN",
    "end":     "KW_END",
    "var":     "KW_VAR",
    "int":     "KW_INT",
    "float":   "KW_FLOAT",
    "string":  "KW_STRING",
    "void":    "KW_VOID",
    "if":      "KW_IF",
    "else":    "KW_ELSE",
    "do":      "KW_DO",
    "while":   "KW_WHILE",
    "print":   "KW_PRINT",
}


# Lista de tokens. PLY exige esta variable.
tokens = [
    "IDENTIFIER", "CTE_INT", "CTE_FLOAT", "CTE_STRING",
    "OP_MAS", "OP_MENOS", "OP_POR", "OP_DIV",
    "OP_ASIGNA", "OP_EQ", "OP_NEQ", "OP_GEQ", "OP_LEQ",
    "OP_MAYOR", "OP_MENOR",
    "LPAREN", "RPAREN", "LBRACE", "RBRACE",
    "LBRACKET", "RBRACKET",
    "SEMICOL", "COMMA", "COLON",
] + list(reserved.values())


# Tokens de un solo caracter (variables string; PLY los ordena por longitud).
t_OP_MAS    = r"\+"
t_OP_MENOS  = r"-"
t_OP_POR    = r"\*"
t_OP_DIV    = r"/"
t_LPAREN    = r"\("
t_RPAREN    = r"\)"
t_LBRACE    = r"\{"
t_RBRACE    = r"\}"
t_LBRACKET  = r"\["
t_RBRACKET  = r"\]"
t_SEMICOL   = r";"
t_COMMA     = r","
t_COLON     = r":"

# Caracteres ignorados (la nueva linea se maneja aparte).
t_ignore = " \t\r"


# Reglas funcionales (orden importa: la primera que encaja gana).

def t_CTE_FLOAT(t):
    r"\d+\.\d+"
    # Va antes que CTE_INT para que "3.14" no se parta como 3 + . + 14.
    t.value = float(t.value)
    return t


def t_CTE_INT(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_CTE_STRING(t):
    r'"[^"\n]*"'
    return t


# Operadores compuestos antes que los simples (longest match).
def t_OP_EQ(t):
    r"=="
    return t


def t_OP_NEQ(t):
    r"!="
    return t


def t_OP_GEQ(t):
    r">="
    return t


def t_OP_LEQ(t):
    r"<="
    return t


def t_OP_ASIGNA(t):
    r"="
    return t


def t_OP_MAYOR(t):
    r">"
    return t


def t_OP_MENOR(t):
    r"<"
    return t


def t_COMMENT(t):
    r"\#[^\n]*"
    # Comentarios de linea. No se emite token (return None implicito).
    pass


def t_IDENTIFIER(t):
    r"[A-Za-z][A-Za-z0-9_]*"
    # Si el lexema es palabra reservada, cambia el tipo. Si no, queda IDENTIFIER.
    t.type = reserved.get(t.value, "IDENTIFIER")
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    # Hook de errores lexicos: reporta caracter infractor y avanza 1 char.
    column = _compute_column(t.lexer.lexdata, t.lexpos)
    msg = (
        f"Error lexico en linea {t.lexer.lineno}, columna {column}: "
        f"caracter no reconocido '{t.value[0]}'"
    )
    if not hasattr(t.lexer, "lex_errors"):
        t.lexer.lex_errors = []
    t.lexer.lex_errors.append(msg)
    t.lexer.skip(1)


def _compute_column(input_text, lexpos):
    """Calcula columna 1-indexed a partir de lexpos."""
    last_newline = input_text.rfind("\n", 0, lexpos)
    if last_newline < 0:
        return lexpos + 1
    return lexpos - last_newline


# =================================================================
#                            PARSER LR
# =================================================================
#
# Gramatica LR (LALR(1)) escrita con RECURSION IZQUIERDA. Cada
# alternativa con | va en su propia funcion p_.

syntax_errors = []


# ----- 1. PROGRAMA RAIZ -----

def p_program(p):
    """program : KW_PROGRAM IDENTIFIER SEMICOL vars_opt funcs_opt KW_MAIN body KW_END"""
    p[0] = ("program", p[2])


# ----- 2. VARS OPCIONALES -----

def p_vars_opt_present(p):
    """vars_opt : vars"""
    p[0] = p[1]


def p_vars_opt_empty(p):
    """vars_opt : """
    p[0] = []


def p_vars(p):
    """vars : KW_VAR var_decl_list"""
    p[0] = p[2]


def p_var_decl_list_multi(p):
    """var_decl_list : var_decl_list var_decl"""
    # Recursion izquierda: acumula declaraciones var a:int; b:float;
    p[0] = p[1] + [p[2]]


def p_var_decl_list_single(p):
    """var_decl_list : var_decl"""
    p[0] = [p[1]]


def p_var_decl(p):
    """var_decl : id_list COLON type SEMICOL"""
    p[0] = (p[1], p[3])


def p_id_list_multi(p):
    """id_list : id_list COMMA IDENTIFIER"""
    p[0] = p[1] + [p[3]]


def p_id_list_single(p):
    """id_list : IDENTIFIER"""
    p[0] = [p[1]]


# ----- 3. TIPOS (cada alternativa en su funcion) -----

def p_type_int(p):
    """type : KW_INT"""
    p[0] = "int"


def p_type_float(p):
    """type : KW_FLOAT"""
    p[0] = "float"


def p_type_string(p):
    """type : KW_STRING"""
    p[0] = "string"


# ----- 4. FUNCIONES OPCIONALES -----

def p_funcs_opt_present(p):
    """funcs_opt : funcs_list"""
    p[0] = p[1]


def p_funcs_opt_empty(p):
    """funcs_opt : """
    p[0] = []


def p_funcs_list_multi(p):
    """funcs_list : funcs_list func"""
    p[0] = p[1] + [p[2]]


def p_funcs_list_single(p):
    """funcs_list : func"""
    p[0] = [p[1]]


def p_func(p):
    """func : KW_VOID IDENTIFIER LPAREN param_list_opt RPAREN LBRACKET vars_opt body RBRACKET SEMICOL"""
    p[0] = ("func", p[2], p[4], p[7], p[8])


def p_param_list_opt_present(p):
    """param_list_opt : param_list"""
    p[0] = p[1]


def p_param_list_opt_empty(p):
    """param_list_opt : """
    p[0] = []


def p_param_list_multi(p):
    """param_list : param_list COMMA param"""
    p[0] = p[1] + [p[3]]


def p_param_list_single(p):
    """param_list : param"""
    p[0] = [p[1]]


def p_param(p):
    """param : IDENTIFIER COLON type"""
    p[0] = (p[1], p[3])


# ----- 5. BODY -----

def p_body(p):
    """body : LBRACE statement_list_opt RBRACE"""
    p[0] = p[2]


def p_statement_list_opt_present(p):
    """statement_list_opt : statement_list"""
    p[0] = p[1]


def p_statement_list_opt_empty(p):
    """statement_list_opt : """
    p[0] = []


def p_statement_list_multi(p):
    """statement_list : statement_list statement"""
    p[0] = p[1] + [p[2]]


def p_statement_list_single(p):
    """statement_list : statement"""
    p[0] = [p[1]]


# ----- 6. STATEMENT (las cinco alternativas en funciones separadas) -----

def p_statement_assign(p):
    """statement : assign"""
    p[0] = p[1]


def p_statement_condition(p):
    """statement : condition"""
    p[0] = p[1]


def p_statement_cycle(p):
    """statement : cycle"""
    p[0] = p[1]


def p_statement_fcall(p):
    """statement : f_call"""
    p[0] = p[1]


def p_statement_print(p):
    """statement : print_stmt"""
    p[0] = p[1]


def p_statement_error(p):
    """statement : error SEMICOL"""
    # Error-production de PLY: cuando un statement falla, el parser pop-ea
    # hasta este nivel, consume tokens marcandolos como 'error' y resume
    # al siguiente SEMICOL. Esto evita la cascada de errores que aparece
    # cuando solo se usa p_error con sync manual.
    p[0] = ("error", "statement invalido")


def p_var_decl_error(p):
    """var_decl : error SEMICOL"""
    # Misma idea, aplicada al nivel de declaracion de variables.
    p[0] = ("error", "declaracion invalida")


# ----- 7. ASSIGN -----

def p_assign(p):
    """assign : IDENTIFIER OP_ASIGNA expresion SEMICOL"""
    p[0] = ("assign", p[1], p[3])


# ----- 8. CONDITION -----

def p_condition_no_else(p):
    """condition : KW_IF LPAREN expresion RPAREN body SEMICOL"""
    p[0] = ("if", p[3], p[5], None)


def p_condition_with_else(p):
    """condition : KW_IF LPAREN expresion RPAREN body KW_ELSE body SEMICOL"""
    p[0] = ("if", p[3], p[5], p[7])


# ----- 9. CYCLE -----

def p_cycle(p):
    """cycle : KW_DO body KW_WHILE LPAREN expresion RPAREN SEMICOL"""
    p[0] = ("do_while", p[2], p[5])


# ----- 10. F_CALL -----

def p_f_call(p):
    """f_call : IDENTIFIER LPAREN arg_list_opt RPAREN SEMICOL"""
    p[0] = ("call", p[1], p[3])


def p_arg_list_opt_present(p):
    """arg_list_opt : arg_list"""
    p[0] = p[1]


def p_arg_list_opt_empty(p):
    """arg_list_opt : """
    p[0] = []


def p_arg_list_multi(p):
    """arg_list : arg_list COMMA expresion"""
    p[0] = p[1] + [p[3]]


def p_arg_list_single(p):
    """arg_list : expresion"""
    p[0] = [p[1]]


# ----- 11. PRINT -----

def p_print_stmt(p):
    """print_stmt : KW_PRINT LPAREN print_arg_list RPAREN SEMICOL"""
    p[0] = ("print", p[3])


def p_print_arg_list_multi(p):
    """print_arg_list : print_arg_list COMMA print_arg"""
    p[0] = p[1] + [p[3]]


def p_print_arg_list_single(p):
    """print_arg_list : print_arg"""
    p[0] = [p[1]]


def p_print_arg_expr(p):
    """print_arg : expresion"""
    # Nota: CTE_STRING ya es una expresion valida (via cte -> atom -> ...),
    # asi que no hay alternativa explicita para evitar reduce/reduce.
    p[0] = p[1]


# ----- 12. EXPRESION -----

def p_expresion_simple(p):
    """expresion : exp"""
    p[0] = p[1]


def p_expresion_relop(p):
    """expresion : exp op_rel exp"""
    p[0] = ("relop", p[2], p[1], p[3])


def p_op_rel_gt(p):
    """op_rel : OP_MAYOR"""
    p[0] = ">"


def p_op_rel_lt(p):
    """op_rel : OP_MENOR"""
    p[0] = "<"


def p_op_rel_geq(p):
    """op_rel : OP_GEQ"""
    p[0] = ">="


def p_op_rel_leq(p):
    """op_rel : OP_LEQ"""
    p[0] = "<="


def p_op_rel_eq(p):
    """op_rel : OP_EQ"""
    p[0] = "=="


def p_op_rel_neq(p):
    """op_rel : OP_NEQ"""
    p[0] = "!="


# ----- 13. EXP (recursion izquierda) -----

def p_exp_plus(p):
    """exp : exp OP_MAS termino"""
    p[0] = ("+", p[1], p[3])


def p_exp_minus(p):
    """exp : exp OP_MENOS termino"""
    p[0] = ("-", p[1], p[3])


def p_exp_termino(p):
    """exp : termino"""
    p[0] = p[1]


# ----- 14. TERMINO (recursion izquierda) -----

def p_termino_times(p):
    """termino : termino OP_POR factor"""
    p[0] = ("*", p[1], p[3])


def p_termino_div(p):
    """termino : termino OP_DIV factor"""
    p[0] = ("/", p[1], p[3])


def p_termino_factor(p):
    """termino : factor"""
    p[0] = p[1]


# ----- 15. FACTOR -----

def p_factor_paren(p):
    """factor : LPAREN expresion RPAREN"""
    p[0] = p[2]


def p_factor_pos(p):
    """factor : OP_MAS atom"""
    p[0] = ("u+", p[2])


def p_factor_neg(p):
    """factor : OP_MENOS atom"""
    p[0] = ("u-", p[2])


def p_factor_atom(p):
    """factor : atom"""
    p[0] = p[1]


def p_atom_id(p):
    """atom : IDENTIFIER"""
    p[0] = ("id", p[1])


def p_atom_cte(p):
    """atom : cte"""
    p[0] = p[1]


# ----- 16. CTE (cada alternativa en su funcion) -----

def p_cte_int(p):
    """cte : CTE_INT"""
    p[0] = ("cte_int", p[1])


def p_cte_float(p):
    """cte : CTE_FLOAT"""
    p[0] = ("cte_float", p[1])


def p_cte_string(p):
    """cte : CTE_STRING"""
    p[0] = ("cte_str", p[1])


# =================================================================
#  MANEJO DE ERRORES SINTACTICOS CON RECUPERACION (panic mode)
# =================================================================

def p_error(p):
    if p is None:
        syntax_errors.append(
            "Error sintactico: fin de archivo inesperado "
            "(probablemente falta 'end', '}' o ';')"
        )
        return

    column = "?"
    if hasattr(p.lexer, "lexdata"):
        column = _compute_column(p.lexer.lexdata, p.lexpos)

    syntax_errors.append(
        f"Error sintactico en linea {p.lineno}, columna {column}: "
        f"token inesperado {p.type} ('{p.value}')"
    )

    # Estrategia documentada en PLY: las producciones 'statement : error
    # SEMICOL' y 'var_decl : error SEMICOL' se encargan de la recuperacion.
    # Aqui solo registramos el error; PLY descartara tokens hasta encontrar
    # un SEMICOL valido y continuara.


# =================================================================
#                FUNCIONES DE CONVENIENCIA
# =================================================================

def _ensure_module_file():
    """PLY accede a __file__ del modulo. En IPython/Jupyter falta."""
    this_module = sys.modules[__name__]
    if not hasattr(this_module, "__file__"):
        this_module.__file__ = "<little_duck>"
    return this_module


def print_token_stream(text):
    """Corre el lexer en aislado y imprime el token stream de la fuente."""
    this_module = _ensure_module_file()
    lexer = lex.lex(module=this_module)
    lexer.lex_errors = []
    lexer.input(text)

    print("TOKEN STREAM")
    print("-" * 60)
    print(f"{'#':>3}  {'TYPE':<14} {'VALUE':<24} {'LINE':>4}  {'COL':>3}")
    print("-" * 60)
    i = 1
    while True:
        tok = lexer.token()
        if tok is None:
            break
        column = _compute_column(lexer.lexdata, tok.lexpos)
        value_repr = repr(tok.value)
        if len(value_repr) > 22:
            value_repr = value_repr[:19] + "...'"
        print(f"{i:>3}  {tok.type:<14} {value_repr:<24} {tok.lineno:>4}  {column:>3}")
        i += 1
    print("-" * 60)
    if lexer.lex_errors:
        print(f"({len(lexer.lex_errors)} error(es) lexico(s) detectado(s) durante el escaneo)")


def parse_text(text):
    """Parsea un string. Devuelve (ok, lex_errors, syn_errors)."""
    global syntax_errors
    syntax_errors = []

    this_module = _ensure_module_file()

    # Pasandole module=this_module explicitamente a PLY, se asegura que
    # use el dict de este modulo (que ya tiene __file__) en vez de buscar
    # en el frame del caller.
    lexer = lex.lex(module=this_module)
    lexer.lex_errors = []
    parser = yacc.yacc(module=this_module, write_tables=False, debug=False)

    parser.parse(text, lexer=lexer)

    ok = (not syntax_errors) and (not lexer.lex_errors)
    return ok, list(lexer.lex_errors), list(syntax_errors)


def analyze_file(path):
    """Analiza un archivo: imprime token stream y resultado del parser."""
    with open(path) as f:
        source = f.read()

    print("=" * 72)
    print(f"Archivo: {path}")
    print("=" * 72)
    print("FUENTE")
    print("-" * 60)
    for i, line in enumerate(source.splitlines(), start=1):
        print(f"{i:>3} | {line}")
    print()

    print_token_stream(source)
    print()

    ok, lex_errs, syn_errs = parse_text(source)

    print(f"Resultado: {'OK' if ok else 'ERROR'}")

    if lex_errs:
        print("\nERRORES LEXICOS")
        print("=" * 60)
        for e in lex_errs:
            print(f"  {e}")

    if syn_errs:
        print("\nERRORES SINTACTICOS")
        print("=" * 60)
        for e in syn_errs:
            print(f"  {e}")

    if ok:
        print("\nPrograma sintacticamente valido.")
    print()


# =================================================================
#                          DRIVER PRINCIPAL
# =================================================================

def _default_test_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "casos_prueba")


def main(argv):
    if len(argv) == 2:
        analyze_file(argv[1])
        return 0

    test_dir = _default_test_dir()
    if not os.path.isdir(test_dir):
        print(f"No se encontro el directorio {test_dir}", file=sys.stderr)
        return 2

    files = sorted(f for f in os.listdir(test_dir) if f.endswith(".txt"))
    if not files:
        print(f"No hay archivos .txt en {test_dir}", file=sys.stderr)
        return 2

    for name in files:
        analyze_file(os.path.join(test_dir, name))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
