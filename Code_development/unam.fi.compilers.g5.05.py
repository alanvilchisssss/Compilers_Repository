import re

# =====================================================================
# BLOQUE 1: LECTURA DE ENTRADA (El mismo que ya teníamos)
# =====================================================================
def cadena_input():
    tipo = input("Ingrese '1' para ingresar una cadena de texto o '2' para ingresar el nombre de un archivo: ")
    if tipo.isdigit() and tipo == '1':
        cadena = input("Ingrese la cadena de texto: ")
    elif tipo.isdigit() and tipo == '2':
        nombre_archivo = input("Ingrese el nombre del archivo (debe estar en la misma carpeta): ")
        if not nombre_archivo.endswith('.txt'):
            nombre_archivo += '.txt'
        try:
            with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
                cadena = archivo.read()
        except FileNotFoundError:
            print("El archivo no se encontró.")
            cadena = ""
    else:
        print("Opción inválida. Por favor, ingrese '1' o '2'.")
        cadena = ""
    return cadena


# =====================================================================
# BLOQUE 2: ANALIZADOR LÉXICO (LEXER)
# =====================================================================
def identificar_tokens(cadena):
    # Expresión regular que busca comentarios, cadenas, flotantes, enteros, palabras y símbolos
    patron_general = r'//[^\n]*|/\*[\s\S]*?\*/|"[^"\n]*"|\d+\.\d+|\d+|[a-zA-Z_]\w*|==|!=|<=|>=|&&|\|\||[^\s\w]'
    
    palabras_reservadas = ['if', 'else', 'while', 'for', 'return', 'printf', 'print', 'int', 'float', 'char', 'void']
    operadores = ['+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>=', '&&', '||']
    puntuacion = ['(', ')', '{', '}', '[', ']', ';', ',']

    tokens_encontrados = {
        'keyword': [],
        'identifier': [],
        'operator': [],
        'constant': [],
        'punctuation': [],
        'no_reconocido': []
    }
    
    # Esta lista guarda los tokens en orden para pasárselos al Parser:
    # Cada elemento será un diccionario: {'tipo': ..., 'lexema': ..., 'linea': ...}
    lista_tokens_ordenados = []
    
    lineas = cadena.split('\n')
    
    for num_linea, contenido_linea in enumerate(lineas, start=1):
        lexemas = re.findall(patron_general, contenido_linea)
        
        for lexema in lexemas:
            # Ignorar comentarios
            if lexema.startswith('//') or lexema.startswith('/*'):
                continue
                
            if lexema in palabras_reservadas:
                tipo = 'keyword'
            elif lexema in operadores:
                tipo = 'operator'
            elif lexema in puntuacion:
                tipo = 'punctuation'
            elif re.fullmatch(r'\d+|\d+\.\d+|"[^"\n]*"', lexema):
                tipo = 'constant'
            elif re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', lexema):
                tipo = 'identifier'
            else:
                tipo = 'no_reconocido'
                
            tokens_encontrados[tipo].append(lexema)
            lista_tokens_ordenados.append({
                'tipo': tipo,
                'lexema': lexema,
                'linea': num_linea
            })

    # Agregamos el símbolo de fin de cadena '$' para el Parser
    ultima_linea = len(lineas) if lineas else 1
    lista_tokens_ordenados.append({'tipo': 'EOF', 'lexema': '$', 'linea': ultima_linea})
    
    return tokens_encontrados, lista_tokens_ordenados


# =====================================================================
# BLOQUE 3: ANALIZADOR SINTÁCTICO (PARSER TOP-DOWN LL(1))
# Gramática Factorizada por la Izquierda:
#   S      -> Decl | Call
#   Decl   -> type id Decl'
#   Decl'  -> ; | = Expr ;
#   Call   -> print_kw ( string Call'
#   Call'  -> ) ; | , Arg ) ;
#   Expr   -> id | constant
#   Arg    -> id | constant
# =====================================================================
def parser_ll1(tokens):
    pos = 0
    arbol_sintactico = [] # Aquí guardamos las sentencias válidas para que las revise el SDT

    def token_actual():
        return tokens[pos]

    def consumir(tipo_esperado=None, lexema_esperado=None):
        nonlocal pos
        tok = token_actual()
        if tipo_esperado and tok['tipo'] != tipo_esperado:
            return None
        if lexema_esperado and tok['lexema'] != lexema_esperado:
            return None
        pos += 1
        return tok

    # Leemos todas las sentencias hasta llegar al fin de archivo '$'
    while token_actual()['tipo'] != 'EOF':
        tok = token_actual()

        # Regla 1: Decl -> type id Decl'
        if tok['tipo'] == 'keyword' and tok['lexema'] in ['int', 'float', 'char', 'void']:
            tok_tipo = consumir(tipo_esperado='keyword')
            
            tok_id = consumir(tipo_esperado='identifier')
            if not tok_id:
                return False, None, tok_tipo['linea']

            # Factorización por la izquierda: Decl' -> ; | = Expr ;
            if token_actual()['lexema'] == ';':
                consumir(lexema_esperado=';')
                arbol_sintactico.append({
                    'regla': 'Decl_Simple',
                    'tipo_var': tok_tipo['lexema'],
                    'id': tok_id['lexema'],
                    'linea': tok_tipo['linea']
                })
            elif token_actual()['lexema'] == '=':
                consumir(lexema_esperado='=')
                
                # Expr -> id | constant
                if token_actual()['tipo'] in ['identifier', 'constant']:
                    tok_expr = consumir()
                else:
                    return False, None, token_actual()['linea']
                    
                if not consumir(lexema_esperado=';'):
                    return False, None, tok_expr['linea']
                    
                arbol_sintactico.append({
                    'regla': 'Decl_Asignacion',
                    'tipo_var': tok_tipo['lexema'],
                    'id': tok_id['lexema'],
                    'valor': tok_expr['lexema'],
                    'tipo_token_valor': tok_expr['tipo'],
                    'linea': tok_tipo['linea']
                })
            else:
                return False, None, token_actual()['linea']

        # Regla 2: Call -> print/printf ( string Call'
        elif tok['tipo'] == 'keyword' and tok['lexema'] in ['printf', 'print']:
            tok_print = consumir(tipo_esperado='keyword')
            
            if not consumir(lexema_esperado='('):
                return False, None, tok_print['linea']
                
            # En el Parser aceptamos una constante o id dentro del paréntesis,
            # y el SDT verificará que realmente sea un string válido.
            if token_actual()['tipo'] in ['constant', 'identifier']:
                tok_arg1 = consumir()
            else:
                return False, None, token_actual()['linea']

            # Factorización por la izquierda: Call' -> ) ; | , Arg ) ;
            if token_actual()['lexema'] == ')':
                consumir(lexema_esperado=')')
                if not consumir(lexema_esperado=';'):
                    return False, None, tok_print['linea']
                arbol_sintactico.append({
                    'regla': 'Call_Simple',
                    'funcion': tok_print['lexema'],
                    'arg1': tok_arg1['lexema'],
                    'linea': tok_print['linea']
                })
            elif token_actual()['lexema'] == ',':
                consumir(lexema_esperado=',')
                if token_actual()['tipo'] in ['identifier', 'constant']:
                    tok_arg2 = consumir()
                else:
                    return False, None, token_actual()['linea']
                if not consumir(lexema_esperado=')'):
                    return False, None, tok_arg2['linea']
                if not consumir(lexema_esperado=';'):
                    return False, None, tok_arg2['linea']
                arbol_sintactico.append({
                    'regla': 'Call_Con_Arg',
                    'funcion': tok_print['lexema'],
                    'arg1': tok_arg1['lexema'],
                    'arg2': tok_arg2['lexema'],
                    'tipo_arg2': tok_arg2['tipo'],
                    'linea': tok_print['linea']
                })
            else:
                return False, None, token_actual()['linea']
        else:
            # Si empieza con cualquier otra cosa que no está en la gramática, es error sintáctico
            return False, None, tok['linea']

    # Si estaba vacío el texto, tampoco es válido
    if len(arbol_sintactico) == 0:
        return False, None, 1

    return True, arbol_sintactico, None


# =====================================================================
# BLOQUE 4: ANALIZADOR SEMÁNTICO (SDT - Syntax Directed Translation)
# Verifica tipos de datos y tabla de símbolos sobre el árbol del Parser
# =====================================================================
def obtener_tipo_constante(lexema):
    if lexema.startswith('"') and lexema.endswith('"'):
        return 'string'
    elif '.' in lexema:
        return 'float'
    else:
        return 'int'

def verificar_sdt(arbol_sintactico):
    tabla_simbolos = {} # Guarda { 'nombre_variable': 'tipo_dato' }

    for nodo in arbol_sintactico:
        regla = nodo['regla']
        linea = nodo['linea']

        # SDT Regla 1: Declaración simple (ej. int a;)
        if regla == 'Decl_Simple':
            tipo_var = nodo['tipo_var']
            nombre_id = nodo['id']
            # No se pueden declarar variables de tipo void ni repetir nombres
            if tipo_var == 'void' or nombre_id in tabla_simbolos:
                return False, linea
            tabla_simbolos[nombre_id] = tipo_var

        # SDT Regla 2: Declaración con asignación (ej. int x = 10;)
        elif regla == 'Decl_Asignacion':
            tipo_var = nodo['tipo_var']
            nombre_id = nodo['id']
            valor = nodo['valor']
            tipo_token_valor = nodo['tipo_token_valor']

            if tipo_var == 'void' or nombre_id in tabla_simbolos:
                return False, linea

            # Averiguar de qué tipo es el valor asignado
            if tipo_token_valor == 'constant':
                tipo_valor = obtener_tipo_constante(valor)
            else:
                # Si le asignaron otra variable (ej. int y = x;), revisar que exista en la tabla
                if valor not in tabla_simbolos:
                    return False, linea
                tipo_valor = tabla_simbolos[valor]

            # Regla principal SDT: El tipo de la variable debe coincidir con el tipo del valor
            if tipo_var != tipo_valor:
                return False, linea

            tabla_simbolos[nombre_id] = tipo_var

        # SDT Regla 3: Llamada a print/printf (ej. printf("This is an example");)
        elif regla == 'Call_Simple':
            arg1 = nodo['arg1']
            # El primer argumento de printf debe ser obligatoriamente una cadena entre comillas
            if obtener_tipo_constante(arg1) != 'string':
                return False, linea

        # SDT Regla 4: Llamada a printf con segundo argumento (ej. printf("Valor", x);)
        elif regla == 'Call_Con_Arg':
            arg1 = nodo['arg1']
            arg2 = nodo['arg2']
            tipo_arg2 = nodo['tipo_arg2']
            if obtener_tipo_constante(arg1) != 'string':
                return False, linea
            # Si el segundo argumento es una variable, debe haber sido declarada antes
            if tipo_arg2 == 'identifier' and arg2 not in tabla_simbolos:
                return False, linea

    return True, None


# =====================================================================
# BLOQUE 5: FUNCIÓN PRINCIPAL (MAIN)
# =====================================================================
def main():
    cadena = cadena_input()
    if not cadena:
        return

    tokens_encontrados, lista_tokens_ordenados = identificar_tokens(cadena)

    # 1. Ejecutar el Parser
    parsing_ok, arbol, linea_error_parser = parser_ll1(lista_tokens_ordenados)

    if not parsing_ok:
        print("Parsing error...")
        print("SDT error...")
        print(f"error in line {linea_error_parser}")
        return

    # Si la sintaxis estuvo bien:
    print("Parsing Success!")

    # 2. Ejecutar la verificación SDT sobre el árbol generado
    sdt_ok, linea_error_sdt = verificar_sdt(arbol)

    if sdt_ok:
        print("SDT Verified!")
    else:
        print("SDT error...")
        print(f"error in line {linea_error_sdt}")


if __name__ == "__main__":
    main()