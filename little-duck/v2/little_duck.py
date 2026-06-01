# Compiladores TC3002B
# Entrega 2 - Analisis semantico y representacion intermedia de Little Duck con PLY

import ply.lex as lex
import ply.yacc as yacc

# ----- LEXER -----

# Diccionario de palabras reservadas: lexema -> label del token.
reserved = {
    "program": "KW_PROGRAM",
    "main": "KW_MAIN",
    "end": "KW_END",
    "var": "KW_VAR",
    "int": "KW_INT",
    "float": "KW_FLOAT",
    "string": "KW_STRING",
    "void": "KW_VOID",
    "if": "KW_IF",
    "else": "KW_ELSE",
    "do": "KW_DO",
    "while": "KW_WHILE",
    "print": "KW_PRINT",
    "return": "KW_RETURN",
    "break": "KW_BREAK",
}

# Lista de tokens. PLY exige esta variable.
tokens = [
    "IDENTIFIER",
    "CTE_INT",
    "CTE_FLOAT",
    "CTE_STRING",
    "OP_MAS",
    "OP_MENOS",
    "OP_POR",
    "OP_DIV",
    "OP_ASIGNA",
    "OP_EQ",
    "OP_NEQ",
    "OP_GEQ",
    "OP_LEQ",
    "OP_MAYOR",
    "OP_MENOR",
    "LPAREN",
    "RPAREN",
    "LBRACE",
    "RBRACE",
    "LBRACKET",
    "RBRACKET",
    "SEMICOL",
    "COMMA",
    "COLON",
] + list(reserved.values())

# Tokens de un solo caracter.
t_OP_MAS = r"\+"
t_OP_MENOS = r"-"
t_OP_POR = r"\*"
t_OP_DIV = r"/"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_SEMICOL = r";"
t_COMMA = r","
t_COLON = r":"

t_ignore = " \t\r"


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
    pass


def t_IDENTIFIER(t):
    r"[A-Za-z][A-Za-z0-9_]*"
    t.type = reserved.get(t.value, "IDENTIFIER")
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    column = _compute_column(t.lexer.lexdata, t.lexpos)
    msg = (
        "Error lexico en linea %d, columna %d: caracter no reconocido '%s'"
        % (t.lexer.lineno, column, t.value[0])
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


# ----- ESTRUCTURAS DE LA SEMANTICA -----
#
# Estas son las estructuras que pide la entrega 2:
#   - func_dir      directorio de funciones (incluye sus tablas de variables)
#   - cube          cubo semantico (tipo resultante de cada operacion)
#   - PilaO         pila de operandos
#   - PTipos        pila de tipos
#   - POper         pila de operadores
#   - PSaltos       pila de saltos (para control de flujo)
#   - quads         lista de cuadruplos (representacion intermedia)
#   - loop_starts   contador/pila de regresos de ciclo
#   - break_stack   listas de saltos pendientes por cada break
#   - const_table   tabla de constantes
#   - temp_count    contador de variables temporales

# Clave interna del alcance global. Empieza con '$' que el lexer nunca puede
# producir para un IDENTIFIER, asi una funcion del usuario llamada 'global' no
# choca con esta clave.
GLOBAL = "$global"


class _SyntaxAbort(Exception):
    """Se lanza al primer error sintactico para detener el parseo limpiamente
    (sin recuperacion en modo panico, que en LALR podria no terminar)."""
    pass


func_dir = {}
current_scope = GLOBAL
current_return_type = None

PilaO = []
PTipos = []
POper = []
PSaltos = []

quads = []
temp_count = 0
loop_starts = []
break_stack = []

const_table = {}
semantic_errors = []
syntax_errors = []

goto_main_idx = None
program_name = "?"


def reset_state():
    """Reinicia todas las estructuras globales antes de compilar."""
    global func_dir, current_scope, current_return_type
    global PilaO, PTipos, POper, PSaltos
    global quads, temp_count, loop_starts, break_stack
    global const_table, semantic_errors, syntax_errors
    global goto_main_idx, program_name

    func_dir = {
        GLOBAL: {
            "return_type": None,
            "params": [],
            "vars": {},
            "start_quad": None,
        }
    }
    current_scope = GLOBAL
    current_return_type = None

    PilaO = []
    PTipos = []
    POper = []
    PSaltos = []

    quads = []
    temp_count = 0
    loop_starts = []
    break_stack = []

    const_table = {}
    semantic_errors = []
    syntax_errors = []

    goto_main_idx = None
    program_name = "?"


# ----- Cubo semantico -----
#
# cube[(tipo_izq, operador, tipo_der)] -> tipo_resultado, o ausente = error.
# Tipos: int, float, string y bool (resultado de operaciones relacionales).


def build_cube():
    c = {}
    numeric = ("int", "float")

    # Aritmeticos: + - * /
    for op in ("+", "-", "*", "/"):
        c[("int", op, "int")] = "int"
        c[("int", op, "float")] = "float"
        c[("float", op, "int")] = "float"
        c[("float", op, "float")] = "float"

    # Relacionales de orden: < > <= >=  (solo numericos) -> bool
    for op in ("<", ">", "<=", ">="):
        for a in numeric:
            for b in numeric:
                c[(a, op, b)] = "bool"

    # Igualdad: == !=  (numericos y string entre si) -> bool
    for op in ("==", "!="):
        for a in numeric:
            for b in numeric:
                c[(a, op, b)] = "bool"
        c[("string", op, "string")] = "bool"

    # Asignacion / paso de parametros / retorno: =
    c[("int", "=", "int")] = "int"
    c[("float", "=", "float")] = "float"
    c[("float", "=", "int")] = "float"   # ensancha int a float
    c[("string", "=", "string")] = "string"

    return c


cube = build_cube()


# ----- Helpers de la representacion intermedia -----


def emit(op, left, right, res, rtype="-"):
    """Agrega un cuadruplo y devuelve su indice (0-based)."""
    quads.append([op, left, right, res, rtype])
    return len(quads) - 1


def next_q():
    """Numero (1-based) que tendra el proximo cuadruplo."""
    return len(quads) + 1


def new_temp():
    """Crea una variable temporal contada a partir de 1."""
    global temp_count
    temp_count += 1
    return "t" + str(temp_count)


def sem_err(msg, line=0):
    if line:
        semantic_errors.append("Error semantico (linea %d): %s" % (line, msg))
    else:
        semantic_errors.append("Error semantico: %s" % msg)


def declare_var(name, vtype, kind):
    table = func_dir[current_scope]["vars"]
    if name in table:
        scope_name = "global" if current_scope == GLOBAL else current_scope
        sem_err("variable '%s' ya declarada en el alcance '%s'" % (name, scope_name))
    else:
        table[name] = {"type": vtype, "kind": kind}


def lookup_var(name):
    """Busca una variable en el alcance actual y luego en el global."""
    if name in func_dir[current_scope]["vars"]:
        return func_dir[current_scope]["vars"][name]["type"]
    if name in func_dir[GLOBAL]["vars"]:
        return func_dir[GLOBAL]["vars"][name]["type"]
    return None


# ----- PARSER LR -----
#
# Gramatica LALR(1) con recursion izquierda y prioridad de operadores
# embebida en la gramatica (exp / termino / factor). Las acciones
# semanticas estan embebidas en los puntos neuralgicos: algunos como
# reducciones normales y otros como no terminales marcadores vacios.

start = "program"


# ----- 1. PROGRAMA RAIZ -----


def p_program(p):
    """program : KW_PROGRAM IDENTIFIER SEMICOL np_prog vars_opt funcs_opt KW_MAIN np_main body KW_END"""
    global program_name
    program_name = p[2]
    emit("END", "-", "-", "-", "-")


def p_np_prog(p):
    """np_prog :"""
    # Punto neuralgico: estamos en el alcance global y reservamos el primer
    # cuadruplo GOTO que saltara al inicio de main.
    global goto_main_idx, current_scope
    current_scope = GLOBAL
    goto_main_idx = emit("GOTO", "-", "-", None, "-")


def p_np_main(p):
    """np_main :"""
    # Punto neuralgico: main comienza aqui; se rellena el GOTO inicial.
    quads[goto_main_idx][3] = next_q()


# ----- 2. VARS OPCIONALES -----


def p_vars_opt_present(p):
    """vars_opt : vars"""


def p_vars_opt_empty(p):
    """vars_opt :"""


def p_vars(p):
    """vars : KW_VAR var_decl_list"""


def p_var_decl_list_multi(p):
    """var_decl_list : var_decl_list var_decl"""


def p_var_decl_list_single(p):
    """var_decl_list : var_decl"""


def p_var_decl(p):
    """var_decl : id_list COLON type SEMICOL"""
    kind = "global" if current_scope == GLOBAL else "local"
    for name in p[1]:
        declare_var(name, p[3], kind)


def p_id_list_multi(p):
    """id_list : id_list COMMA IDENTIFIER"""
    p[0] = p[1] + [p[3]]


def p_id_list_single(p):
    """id_list : IDENTIFIER"""
    p[0] = [p[1]]


# ----- 3. TIPOS -----


def p_type_int(p):
    """type : KW_INT"""
    p[0] = "int"


def p_type_float(p):
    """type : KW_FLOAT"""
    p[0] = "float"


def p_type_string(p):
    """type : KW_STRING"""
    p[0] = "string"


# ----- 4. FUNCIONES -----


def p_funcs_opt_present(p):
    """funcs_opt : funcs_list"""


def p_funcs_opt_empty(p):
    """funcs_opt :"""


def p_funcs_list_multi(p):
    """funcs_list : funcs_list func"""


def p_funcs_list_single(p):
    """funcs_list : func"""


def p_func(p):
    """func : func_header LBRACKET vars_opt np_func_body body RBRACKET SEMICOL"""
    global current_scope, current_return_type
    emit("ENDFUNC", "-", "-", "-", "-")
    current_scope = GLOBAL
    current_return_type = None


def p_func_header(p):
    """func_header : func_ret IDENTIFIER LPAREN param_list_opt RPAREN"""
    # Punto neuralgico: se registra la funcion en el directorio, se cambia el
    # alcance y se agregan los parametros a su tabla de variables.
    global current_scope, current_return_type
    name = p[2]
    ret = p[1]
    # Se arma una entrada nueva; los parametros se validan entre si.
    entry = {"return_type": ret, "params": [], "vars": {}, "start_quad": None}
    for (pn, pt) in p[4]:
        if pn in entry["vars"]:
            sem_err("parametro '%s' duplicado en '%s'" % (pn, name), p.lineno(2))
        else:
            entry["vars"][pn] = {"type": pt, "kind": "param"}
            entry["params"].append((pn, pt))
    if name in func_dir:
        # Redeclaracion: se reporta y se usa un alcance desechable para no
        # contaminar la entrada original de la funcion.
        sem_err("funcion '%s' ya declarada" % name, p.lineno(2))
        scope_key = "$dup_%d" % len(func_dir)
    else:
        scope_key = name
    func_dir[scope_key] = entry
    current_scope = scope_key
    current_return_type = ret


def p_np_func_body(p):
    """np_func_body :"""
    # Punto neuralgico: el codigo de la funcion comienza en este cuadruplo.
    func_dir[current_scope]["start_quad"] = next_q()


def p_func_ret_type(p):
    """func_ret : type"""
    p[0] = p[1]


def p_func_ret_void(p):
    """func_ret : KW_VOID"""
    p[0] = "void"


def p_param_list_opt_present(p):
    """param_list_opt : param_list"""
    p[0] = p[1]


def p_param_list_opt_empty(p):
    """param_list_opt :"""
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


def p_statement_list_opt_present(p):
    """statement_list_opt : statement_list"""


def p_statement_list_opt_empty(p):
    """statement_list_opt :"""


def p_statement_list_multi(p):
    """statement_list : statement_list statement"""


def p_statement_list_single(p):
    """statement_list : statement"""


# ----- 6. STATEMENT -----


def p_statement_assign(p):
    """statement : assign"""


def p_statement_condition(p):
    """statement : condition"""


def p_statement_cycle(p):
    """statement : cycle"""


def p_statement_fcall(p):
    """statement : f_call"""


def p_statement_print(p):
    """statement : print_stmt"""


def p_statement_return(p):
    """statement : return_stmt"""


def p_statement_break(p):
    """statement : KW_BREAK SEMICOL"""
    if not break_stack:
        sem_err("'break' fuera de un ciclo", p.lineno(1))
    else:
        idx = emit("GOTO", "-", "-", None, "-")
        break_stack[-1].append(idx)


# ----- 7. ASSIGN -----


def p_assign(p):
    """assign : IDENTIFIER OP_ASIGNA expresion SEMICOL"""
    op = PilaO.pop()
    st = PTipos.pop()
    tt = lookup_var(p[1])
    if tt is None:
        sem_err("variable '%s' no declarada" % p[1], p.lineno(1))
        return
    res = cube.get((tt, "=", st), "error")
    if res == "error":
        sem_err(
            "no se puede asignar un valor %s a '%s' que es %s" % (st, p[1], tt),
            p.lineno(1),
        )
        return
    emit("=", op, "-", p[1], tt)


# ----- 8. CONDITION (if / if-else) -----


def p_cond_if(p):
    """cond_if : KW_IF LPAREN expresion RPAREN"""
    # Punto neuralgico: se valida que la condicion sea booleana y se emite el
    # GOTOF pendiente.
    op = PilaO.pop()
    t = PTipos.pop()
    if t != "bool":
        sem_err(
            "la condicion del 'if' debe ser una expresion booleana (se obtuvo %s)" % t,
            p.lineno(1),
        )
    idx = emit("GOTOF", op, "-", None, "-")
    PSaltos.append(idx)


def p_condition_noelse(p):
    """condition : cond_if body SEMICOL"""
    f = PSaltos.pop()
    quads[f][3] = next_q()


def p_cond_else(p):
    """cond_else : KW_ELSE"""
    # Punto neuralgico: el then termina con un GOTO que brinca el else, y se
    # rellena el GOTOF para que caiga al inicio del else.
    idx = emit("GOTO", "-", "-", None, "-")
    f = PSaltos.pop()
    quads[f][3] = next_q()
    PSaltos.append(idx)


def p_condition_else(p):
    """condition : cond_if body cond_else body SEMICOL"""
    g = PSaltos.pop()
    quads[g][3] = next_q()


# ----- 9. CYCLE (do-while con break) -----


def p_cycle_start(p):
    """cycle_start : KW_DO"""
    # Punto neuralgico: se guarda el punto de regreso y se abre una lista de
    # breaks para este ciclo.
    loop_starts.append(next_q())
    break_stack.append([])


def p_cycle(p):
    """cycle : cycle_start body KW_WHILE LPAREN expresion RPAREN SEMICOL"""
    op = PilaO.pop()
    t = PTipos.pop()
    if t != "bool":
        sem_err(
            "la condicion del 'while' debe ser una expresion booleana (se obtuvo %s)"
            % t,
            p.lineno(3),
        )
    start = loop_starts.pop()
    emit("GOTOT", op, "-", start, "-")
    after = next_q()
    for b in break_stack.pop():
        quads[b][3] = after


# ----- 10. LLAMADA A FUNCION -----


def p_call(p):
    """call : IDENTIFIER LPAREN arg_list_opt RPAREN"""
    name = p[1]
    argc = p[3]
    # Se sacan los argumentos de la pila de operandos en orden.
    args = []
    for _ in range(argc):
        a = PilaO.pop()
        at = PTipos.pop()
        args.append((a, at))
    args.reverse()

    if name not in func_dir:
        sem_err("funcion '%s' no declarada" % name, p.lineno(1))
        PilaO.append("__err__")
        PTipos.append("error")
        p[0] = "error"
        return

    info = func_dir[name]
    params = info["params"]
    ret = info["return_type"]

    if len(args) != len(params):
        sem_err(
            "la funcion '%s' espera %d argumento(s) y recibio %d"
            % (name, len(params), len(args)),
            p.lineno(1),
        )

    emit("ERA", name, "-", "-", "-")
    for i in range(len(args)):
        a, at = args[i]
        if i < len(params):
            pname, ptype = params[i]
            if cube.get((ptype, "=", at), "error") == "error":
                sem_err(
                    "argumento %d de '%s': se esperaba %s y se recibio %s"
                    % (i + 1, name, ptype, at),
                    p.lineno(1),
                )
            emit("PARAM", a, "-", "par" + str(i + 1), ptype)
        else:
            emit("PARAM", a, "-", "par" + str(i + 1), at)
    emit("GOSUB", name, "-", info["start_quad"], ret)

    if ret != "void":
        tmp = new_temp()
        emit("=", name, "-", tmp, ret)
        PilaO.append(tmp)
        PTipos.append(ret)
        p[0] = ret
    else:
        PilaO.append("__void__")
        PTipos.append("void")
        p[0] = "void"


def p_f_call(p):
    """f_call : call SEMICOL"""
    # Llamada usada como sentencia: se descarta el valor que dejo la llamada.
    PilaO.pop()
    PTipos.pop()


def p_arg_list_opt_present(p):
    """arg_list_opt : arg_list"""
    p[0] = p[1]


def p_arg_list_opt_empty(p):
    """arg_list_opt :"""
    p[0] = 0


def p_arg_list_multi(p):
    """arg_list : arg_list COMMA expresion"""
    p[0] = p[1] + 1


def p_arg_list_single(p):
    """arg_list : expresion"""
    p[0] = 1


# ----- 11. PRINT -----


def p_print_stmt(p):
    """print_stmt : KW_PRINT LPAREN print_arg_list RPAREN SEMICOL"""


def p_print_arg_list_multi(p):
    """print_arg_list : print_arg_list COMMA print_arg"""


def p_print_arg_list_single(p):
    """print_arg_list : print_arg"""


def p_print_arg(p):
    """print_arg : expresion"""
    op = PilaO.pop()
    t = PTipos.pop()
    emit("print", op, "-", "-", t)


# ----- 12. RETURN -----


def p_return_value(p):
    """return_stmt : KW_RETURN expresion SEMICOL"""
    op = PilaO.pop()
    t = PTipos.pop()
    if current_return_type is None:
        sem_err("'return' fuera de una funcion", p.lineno(1))
    elif current_return_type == "void":
        sem_err("una funcion 'void' no puede retornar un valor", p.lineno(1))
    elif cube.get((current_return_type, "=", t), "error") == "error":
        sem_err(
            "el valor retornado (%s) no coincide con el tipo de la funcion (%s)"
            % (t, current_return_type),
            p.lineno(1),
        )
    else:
        emit("RETURN", op, "-", "-", current_return_type)


def p_return_void(p):
    """return_stmt : KW_RETURN SEMICOL"""
    if current_return_type is None:
        sem_err("'return' fuera de una funcion", p.lineno(1))
    elif current_return_type != "void":
        sem_err(
            "la funcion debe retornar un valor de tipo %s" % current_return_type,
            p.lineno(1),
        )
    else:
        emit("RETURN", "-", "-", "-", "void")


# ----- 13. EXPRESION (relacional) -----


def p_expresion_simple(p):
    """expresion : exp"""


def p_expresion_relop(p):
    """expresion : exp op_rel exp"""
    right = PilaO.pop()
    rt = PTipos.pop()
    left = PilaO.pop()
    lt = PTipos.pop()
    op = POper.pop()
    res = cube.get((lt, op, rt), "error")
    if res == "error":
        sem_err("operacion relacional invalida: %s %s %s" % (lt, op, rt))
        PilaO.append("__err__")
        PTipos.append("error")
    else:
        t = new_temp()
        emit(op, left, right, t, res)
        PilaO.append(t)
        PTipos.append(res)


def p_op_rel_gt(p):
    """op_rel : OP_MAYOR"""
    POper.append(">")


def p_op_rel_lt(p):
    """op_rel : OP_MENOR"""
    POper.append("<")


def p_op_rel_geq(p):
    """op_rel : OP_GEQ"""
    POper.append(">=")


def p_op_rel_leq(p):
    """op_rel : OP_LEQ"""
    POper.append("<=")


def p_op_rel_eq(p):
    """op_rel : OP_EQ"""
    POper.append("==")


def p_op_rel_neq(p):
    """op_rel : OP_NEQ"""
    POper.append("!=")


# ----- 14. EXP (suma / resta) -----


def gen_arith():
    """Genera el cuadruplo del operador aritmetico que esta en POper."""
    right = PilaO.pop()
    rt = PTipos.pop()
    left = PilaO.pop()
    lt = PTipos.pop()
    op = POper.pop()
    res = cube.get((lt, op, rt), "error")
    if res == "error":
        sem_err("operacion aritmetica invalida: %s %s %s" % (lt, op, rt))
        PilaO.append("__err__")
        PTipos.append("error")
    else:
        t = new_temp()
        emit(op, left, right, t, res)
        PilaO.append(t)
        PTipos.append(res)


def p_exp_plus(p):
    """exp : exp OP_MAS m_add termino"""
    gen_arith()


def p_exp_minus(p):
    """exp : exp OP_MENOS m_sub termino"""
    gen_arith()


def p_exp_termino(p):
    """exp : termino"""


def p_m_add(p):
    """m_add :"""
    # Punto neuralgico: se mete el operador a la pila de operadores.
    POper.append("+")


def p_m_sub(p):
    """m_sub :"""
    POper.append("-")


# ----- 15. TERMINO (multiplicacion / division) -----


def p_termino_times(p):
    """termino : termino OP_POR m_mul factor"""
    gen_arith()


def p_termino_div(p):
    """termino : termino OP_DIV m_div factor"""
    gen_arith()


def p_termino_factor(p):
    """termino : factor"""


def p_m_mul(p):
    """m_mul :"""
    POper.append("*")


def p_m_div(p):
    """m_div :"""
    POper.append("/")


# ----- 16. FACTOR -----


def p_factor_paren(p):
    """factor : LPAREN expresion RPAREN"""
    # El operando de la expresion interna ya quedo en la pila.


def p_factor_pos(p):
    """factor : OP_MAS atom"""
    # '+' unario: el operando se queda igual.


def p_factor_neg(p):
    """factor : OP_MENOS atom"""
    op = PilaO.pop()
    t = PTipos.pop()
    if t not in ("int", "float"):
        sem_err("el operador unario '-' requiere int o float (se obtuvo %s)" % t)
        PilaO.append("__err__")
        PTipos.append("error")
    else:
        tmp = new_temp()
        emit("NEG", op, "-", tmp, t)
        PilaO.append(tmp)
        PTipos.append(t)


def p_factor_atom(p):
    """factor : atom"""


def p_atom_call(p):
    """atom : call"""
    if p[1] == "void":
        sem_err("no se puede usar el resultado de una funcion 'void' en una expresion")


def p_atom_id(p):
    """atom : IDENTIFIER"""
    tt = lookup_var(p[1])
    if tt is None:
        sem_err("variable '%s' no declarada" % p[1], p.lineno(1))
        PilaO.append(p[1])
        PTipos.append("error")
    else:
        PilaO.append(p[1])
        PTipos.append(tt)


def p_atom_cte(p):
    """atom : cte"""


# ----- 17. CTE -----


def p_cte_int(p):
    """cte : CTE_INT"""
    PilaO.append(str(p[1]))
    PTipos.append("int")
    const_table[str(p[1])] = "int"


def p_cte_float(p):
    """cte : CTE_FLOAT"""
    PilaO.append(str(p[1]))
    PTipos.append("float")
    const_table[str(p[1])] = "float"


def p_cte_string(p):
    """cte : CTE_STRING"""
    PilaO.append(p[1])
    PTipos.append("string")
    const_table[p[1]] = "string"


# ----- MANEJO DE ERRORES SINTACTICOS (aborta al primer error) -----


def p_error(p):
    # Se reporta el primer error sintactico y se aborta el parseo. No se usa la
    # recuperacion en modo panico de PLY porque, con la gramatica de un paso y
    # los marcadores vacios, puede entrar en un ciclo que no termina.
    if p is None:
        syntax_errors.append(
            "Error sintactico: fin de archivo inesperado "
            "(probablemente falta 'end', '}' o ';')"
        )
        raise _SyntaxAbort()

    column = "?"
    if hasattr(p.lexer, "lexdata"):
        column = _compute_column(p.lexer.lexdata, p.lexpos)

    syntax_errors.append(
        "Error sintactico en linea %s, columna %s: token inesperado %s ('%s')"
        % (p.lineno, column, p.type, p.value)
    )
    raise _SyntaxAbort()


# ----- COMPILACION -----


def compile_source(text):
    """Analiza el texto. Devuelve (lex_errors, syntax_errors, semantic_errors)."""
    reset_state()

    lexer = lex.lex()
    lexer.lex_errors = []
    parser = yacc.yacc(write_tables=False, debug=False, errorlog=yacc.NullLogger())

    try:
        parser.parse(text, lexer=lexer)
    except _SyntaxAbort:
        # Se detuvo en el primer error sintactico; el mensaje ya quedo registrado.
        pass
    except Exception as exc:  # red de seguridad ante un parseo irrecuperable
        syntax_errors.append("Error sintactico irrecuperable: %s" % exc)

    lex_errs = list(getattr(lexer, "lex_errors", []))
    return lex_errs, list(syntax_errors), list(semantic_errors)


# ----- SALIDAS LEGIBLES -----


def format_quads():
    lines = []
    lines.append("Representacion intermedia (cuadruplos)")
    lines.append(
        "%-5s %-8s %-12s %-12s %-12s %-8s"
        % ("#", "OP", "IZQ", "DER", "RES", "TIPO")
    )
    for i, q in enumerate(quads):
        op, left, right, res, rtype = q
        res = "-" if res is None else res
        lines.append(
            "%-5d %-8s %-12s %-12s %-12s %-8s"
            % (i + 1, str(op), str(left), str(right), str(res), str(rtype))
        )
    return "\n".join(lines)


def format_symbols():
    lines = []
    lines.append("Tabla de simbolos")
    lines.append("Programa: " + program_name)

    glob = func_dir[GLOBAL]["vars"]
    lines.append("Variables globales:")
    if glob:
        for name, info in glob.items():
            lines.append("  %-14s %s" % (name, info["type"]))
    else:
        lines.append("  (ninguna)")

    funcs = [k for k in func_dir if k != GLOBAL and not k.startswith("$")]
    lines.append("Funciones:")
    if not funcs:
        lines.append("  (ninguna)")
    for fn in funcs:
        info = func_dir[fn]
        if info["params"]:
            plist = ", ".join("%s:%s" % (pn, pt) for pn, pt in info["params"])
        else:
            plist = "sin parametros"
        lines.append(
            "  %s -> %s | params: %s | inicio cuad: %s"
            % (fn, info["return_type"], plist, info["start_quad"])
        )
        locales = [
            (n, i) for n, i in info["vars"].items() if i["kind"] == "local"
        ]
        if locales:
            lines.append("    Variables locales:")
            for n, i in locales:
                lines.append("      %-14s %s" % (n, i["type"]))

    if const_table:
        lines.append("Constantes:")
        for c, t in const_table.items():
            lines.append("  %-14s %s" % (c, t))

    return "\n".join(lines)


# ----- PUNTO DE ENTRADA -----

input = open("prueba.txt").read()
lex_errs, syn_errs, sem_errs = compile_source(input)

if lex_errs or syn_errs:
    print("Compilacion con errores.")
    if lex_errs:
        print("Errores lexicos:")
        for e in lex_errs:
            print("  " + e)
    if syn_errs:
        print("Errores sintacticos:")
        for e in syn_errs:
            print("  " + e)
elif sem_errs:
    print("Compilacion con errores.")
    print("Errores semanticos:")
    for e in sem_errs:
        print("  " + e)
else:
    ir = format_quads()
    syms = format_symbols()
    print(ir)
    print()
    print(syms)
    open("prueba-ir.txt", "w").write(ir + "\n")
