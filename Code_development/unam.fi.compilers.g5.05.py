import re

# =====================================================================
# FUNCIÓN 1: LECTURA DE ENTRADA (Consola o Archivo .txt)
# Esta es exactamente la misma función que ya teniamo en la Entrega 1.
# =====================================================================
def cadena_input():
    tipo = input("Ingrese '1' para ingresar una cadena de texto o '2' para ingresar el nombre de un archivo: ")
    
    # Opción 1: Leer directamente lo que el usuario escriba en la terminal
    if tipo.isdigit() and tipo == '1':
        cadena = input("Ingrese la cadena de texto: ")
        
    # Opción 2: Leer el contenido desde un archivo .txt en la misma carpeta
    elif tipo.isdigit() and tipo == '2':
        nombre_archivo = input("Ingrese el nombre del archivo (el archivo debe estar en la misma carpeta): ")
        # Si el usuario no escribió ".txt", se lo agregamos automáticamente
        if not nombre_archivo.endswith('.txt'):
            nombre_archivo += '.txt'
        try:
            with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
                cadena = archivo.read()
        except FileNotFoundError:
            print("El archivo no se encontró. Por favor, asegúrese de que el nombre del archivo sea correcto.")
            cadena = ""
    else:
        print("Opción inválida. Por favor, ingrese '1' o '2'.")
        cadena = ""
        
    return cadena


# =====================================================================
# FUNCIÓN 2: ANALIZADOR LÉXICO (LEXER)
# Conserva exactamente el mismo diccionario y patron_lexer que su equipo
# ya tenía en GitHub, pero ahora también guarda los tokens en una lista
# ordenada con su número de línea para pasárselos al Parser.
# =====================================================================
def identificar_tokens(cadena):
    # Diccionario con las expresiones regulares de las 5 categorías
    tokens = {
        'keyword': [r'^(print|printf|int|float|char|void|if|else|while|for|return|break|continue|switch|case)$'],
        'identifier': [r'^[a-zA-Z_][a-zA-Z0-9_]*$'],
        'operator': [r'^(\+|\-|\*|\/|\%|\=\=|\!\=|\<\=|\>\=|\=|\<|\>|\&\&|\|\||\!)$'],
        'constant': [r'^\d+\.\d+$', r'^\d+$', r'^"(?:\\.|[^"\\])*"$', r"^'(?:\\.|[^'\\])*'$"],
        'punctuation': [r'^(\(|\)|\{|\}|\[|\]|\;|\,|\.|\:|\?)$']
    }

    # Diccionario para agrupar los tokens encontrados (como en la Entrega 1)
    tokens_encontrados = {
        'keyword': [],
        'identifier': [],
        'operator': [],
        'constant': [],
        'punctuation': [],
        'no_reconocido': []
    }

    # Expresión regular que separa el código sin romper cadenas con espacios ni operadores dobles
    patron_lexer = (
        r'//[^\n]*'               # Comentario de una línea
        r'|/\*[\s\S]*?\*/'        # Comentario de varias líneas
        r'|"(?:\\.|[^"\\])*"'     # Cadena de texto entre comillas
        r"|'(?:\\.|[^'\\])*'"     # Carácter entre comillas simples
        r'|\d+\.\d+'              # Constante real (flotante, ej. 30.5)
        r'|\d+'                   # Constante entera (ej. 10)
        r'|[a-zA-Z_][a-zA-Z0-9_]*'# Identificador o palabra reservada (keyword)
        r'|==|!=|<=|>='           # Operadores relacionales de dos caracteres
        r'|\+|\-|\*|\/|\%|\=|\<|\>|\&\&|\|\||\!' # Operadores de un carácter
        r'|\(|\)|\{|\}|\[|\]|\;|\,|\.|\:|\?'     # Signos de puntuación
        r'|\S'                    # Cualquier otro carácter suelto no reconocido
    )

    # NUEVO PARA EL PARSER: Lista que guarda los tokens en el orden exacto en que aparecen
    lista_tokens = []
    N_tokens = 0

    # Separamos el código por saltos de línea (\n) para saber en qué línea está cada token
    lineas = cadena.split('\n')

    # Recorremos línea por línea empezando a contar desde la línea 1
    for numero_linea, texto_linea in enumerate(lineas, start=1):
        cadenas_encontradas = re.findall(patron_lexer, texto_linea)

        for lexema in cadenas_encontradas:
            # Si es un comentario, lo ignoramos y pasamos al siguiente
            if lexema.startswith('//') or lexema.startswith('/*'):
                continue

            # Clasificamos el lexema probando cada categoría en orden
            if re.match('|'.join(tokens['keyword']), lexema):
                categoria = 'keyword'
                N_tokens += 1
            elif re.match('|'.join(tokens['identifier']), lexema):
                categoria = 'identifier'
                N_tokens += 1
            elif re.match('|'.join(tokens['operator']), lexema):
                categoria = 'operator'
                N_tokens += 1
            elif re.match('|'.join(tokens['constant']), lexema):
                categoria = 'constant'
                N_tokens += 1
            elif re.match('|'.join(tokens['punctuation']), lexema):
                categoria = 'punctuation'
                N_tokens += 1
            else:
                categoria = 'no_reconocido'

            # Guardamos en el diccionario del Lexer
            tokens_encontrados[categoria].append(lexema)

            # Guardamos en la lista ordenada para el Parser:
            # Cada token es un diccionario simple con 3 datos: categoría, texto (lexema) y línea
            lista_tokens.append({
                'categoria': categoria,
                'lexema': lexema,
                'linea': numero_linea
            })

    return tokens_encontrados, N_tokens, lista_tokens


# =====================================================================
# FUNCIÓN 3: ANALIZADOR SINTÁCTICO (PARSER)
# Revisa que los tokens vengan en el orden correcto según la Gramática
# Factorizada por la Izquierda que pusimos en el Reporte 1:
#   1) Declaración:  type id ;          ó   type id = Expr ;
#   2) Impresión:    printf ( Expr ) ;  ó   printf ( Expr , Arg ) ;
# =====================================================================
def analizar_sintaxis_parser(lista_tokens):
    # Si no hay ningún token (entrada vacía), es un error en la línea 1
    if len(lista_tokens) == 0:
        return False, [], 1

    # Esta lista guardará las instrucciones ya validadas (nuestro Árbol Sintáctico)
    # para que después las revise el analizador semántico (SDT)
    arbol_instrucciones = []

    # Usamos una variable 'i' como índice para ir avanzando token por token
    i = 0
    total = len(lista_tokens)

    while i < total:
        token_actual = lista_tokens[i]
        linea_actual = token_actual['linea']

        # Si el Lexer encontró un símbolo raro no reconocido (ej. @ o $), hay error sintáctico
        if token_actual['categoria'] == 'no_reconocido':
            return False, [], linea_actual

        # -----------------------------------------------------------------
        # CASO 1 DE LA GRAMÁTICA: Declaraciones (Decl -> type id Decl')
        # Ejemplo: int x = 10 ;   ó   int x ;
        # -----------------------------------------------------------------
        if token_actual['categoria'] == 'keyword' and token_actual['lexema'] in ['int', 'float', 'char', 'void']:
            # Paso 1: Guardamos el tipo de dato (int, float, char o void) y avanzamos
            tipo_dato = token_actual['lexema']
            i += 1

            # Paso 2: Después del tipo, OBLIGATORIAMENTE debe venir un identificador (nombre de variable)
            if i >= total or lista_tokens[i]['categoria'] != 'identifier':
                return False, [], linea_actual
            nombre_variable = lista_tokens[i]['lexema']
            i += 1

            # Paso 3 (Factorización por la izquierda Decl'):
            # Después del identificador solo pueden venir dos cosas: un ';' o un '='
            if i >= total:
                return False, [], linea_actual

            # Opción 3A (Decl' -> ;): Declaración simple como "int x;"
            if lista_tokens[i]['lexema'] == ';':
                i += 1  # Consumimos el ';'
                arbol_instrucciones.append({
                    'tipo_instruccion': 'declaracion_simple',
                    'tipo_dato': tipo_dato,
                    'variable': nombre_variable,
                    'linea': linea_actual
                })

            # Opción 3B (Decl' -> = Expr ;): Declaración con asignación como "int x = 10;"
            elif lista_tokens[i]['lexema'] == '=':
                i += 1  # Consumimos el '='

                # Después del '=' debe venir una Expresión (una constante o un identificador)
                if i >= total or lista_tokens[i]['categoria'] not in ['constant', 'identifier']:
                    return False, [], linea_actual
                valor_asignado = lista_tokens[i]['lexema']
                categoria_valor = lista_tokens[i]['categoria']
                i += 1

                # Después del valor, OBLIGATORIAMENTE debe cerrar con ';'
                if i >= total or lista_tokens[i]['lexema'] != ';':
                    return False, [], linea_actual
                i += 1  # Consumimos el ';'

                # Guardamos el nodo en el árbol para que el SDT revise si los tipos coinciden
                arbol_instrucciones.append({
                    'tipo_instruccion': 'declaracion_asignacion',
                    'tipo_dato': tipo_dato,
                    'variable': nombre_variable,
                    'valor': valor_asignado,
                    'categoria_valor': categoria_valor,
                    'linea': linea_actual
                })

            # Si después del nombre de la variable no vino ni ';' ni '=', es error sintáctico
            else:
                return False, [], lista_tokens[i]['linea']

        # -----------------------------------------------------------------
        # CASO 2 DE LA GRAMÁTICA: Llamadas a función (Call -> printf ( string Call')
        # Ejemplo: printf("Hola");   ó   printf("Hola", x);
        # -----------------------------------------------------------------
        elif token_actual['categoria'] == 'keyword' and token_actual['lexema'] in ['printf', 'print']:
            funcion = token_actual['lexema']
            i += 1  # Consumimos 'printf' o 'print'

            # Paso 1: Debe abrir paréntesis '('
            if i >= total or lista_tokens[i]['lexema'] != '(':
                return False, [], linea_actual
            i += 1  # Consumimos '('

            # Paso 2: Debe venir el primer argumento (una constante o un identificador)
            if i >= total or lista_tokens[i]['categoria'] not in ['constant', 'identifier']:
                return False, [], linea_actual
            primer_argumento = lista_tokens[i]['lexema']
            i += 1

            # Paso 3 (Factorización por la izquierda Call'):
            # Después del primer argumento puede cerrar con ');' o tener una coma ', Arg );'
            if i >= total:
                return False, [], linea_actual

            # Opción 3A (Call' -> ) ;): Ejemplo printf("This is an example");
            if lista_tokens[i]['lexema'] == ')':
                i += 1  # Consumimos ')'
                if i >= total or lista_tokens[i]['lexema'] != ';':
                    return False, [], linea_actual
                i += 1  # Consumimos ';'

                arbol_instrucciones.append({
                    'tipo_instruccion': 'llamada_simple',
                    'funcion': funcion,
                    'arg1': primer_argumento,
                    'linea': linea_actual
                })

            # Opción 3B (Call' -> , Arg ) ;): Ejemplo printf("Valor: ", x);
            elif lista_tokens[i]['lexema'] == ',':
                i += 1  # Consumimos ','

                # Debe venir el segundo argumento (identificador o constante)
                if i >= total or lista_tokens[i]['categoria'] not in ['constant', 'identifier']:
                    return False, [], linea_actual
                segundo_argumento = lista_tokens[i]['lexema']
                categoria_arg2 = lista_tokens[i]['categoria']
                i += 1

                # Debe cerrar paréntesis ')'
                if i >= total or lista_tokens[i]['lexema'] != ')':
                    return False, [], linea_actual
                i += 1  # Consumimos ')'

                # Debe terminar con punto y coma ';'
                if i >= total or lista_tokens[i]['lexema'] != ';':
                    return False, [], linea_actual
                i += 1  # Consumimos ';'

                arbol_instrucciones.append({
                    'tipo_instruccion': 'llamada_con_arg',
                    'funcion': funcion,
                    'arg1': primer_argumento,
                    'arg2': segundo_argumento,
                    'categoria_arg2': categoria_arg2,
                    'linea': linea_actual
                })

            else:
                return False, [], lista_tokens[i]['linea']

        # Si la oración empieza con cualquier otra cosa que no sea un tipo o un print, es error sintáctico
        else:
            return False, [], linea_actual

    # Si terminó el ciclo while sin errores, el Parsing fue exitoso
    return True, arbol_instrucciones, None


# =====================================================================
# FUNCIÓN AUXILIAR: Saber de qué tipo es una constante
# Nos dice si un valor constante es 'string', 'char', 'float' o 'int'.
# =====================================================================
def deducir_tipo_constante(texto_constante):
    if texto_constante.startswith('"') and texto_constante.endswith('"'):
        return 'string'
    elif texto_constante.startswith("'") and texto_constante.endswith("'"):
        return 'char'
    elif '.' in texto_constante:
        return 'float'
    else:
        return 'int'


# =====================================================================
# FUNCIÓN 4: ANALIZADOR SEMÁNTICO (SDT - Syntax Directed Translation)
# Aunque la oración esté bien escrita (Parsing Success), aquí revisamos
# que tenga sentido lógico:
#   1) Que los tipos coincidan (ej. no meter un texto "hola" en un int).
#   2) Que no se declaren variables de tipo 'void'.
#   3) Que no se repitan variables ya declaradas ni se usen variables que no existen.
# =====================================================================
def verificar_reglas_sdt(arbol_instrucciones):
    # Tabla de símbolos: diccionario que guarda { 'nombre_variable': 'tipo_dato' }
    # Ejemplo: { 'x': 'int', 'b': 'float' }
    tabla_simbolos = {}

    # Recorremos una por una las instrucciones que el Parser dio por buenas
    for instruccion in arbol_instrucciones:
        tipo_inst = instruccion['tipo_instruccion']
        linea = instruccion['linea']

        # -----------------------------------------------------------------
        # REGLA SDT 1: Declaración simple (ej. int a;)
        # -----------------------------------------------------------------
        if tipo_inst == 'declaracion_simple':
            tipo_var = instruccion['tipo_dato']
            nombre_var = instruccion['variable']

            # Error semántico si intentan declarar "void a;" o si la variable ya existía antes
            if tipo_var == 'void' or nombre_var in tabla_simbolos:
                return False, linea

            # Si todo está bien, registramos la variable en la tabla de símbolos
            tabla_simbolos[nombre_var] = tipo_var

        # -----------------------------------------------------------------
        # REGLA SDT 2: Declaración con asignación (ej. int x = 10;)
        # -----------------------------------------------------------------
        elif tipo_inst == 'declaracion_asignacion':
            tipo_var = instruccion['tipo_dato']
            nombre_var = instruccion['variable']
            valor = instruccion['valor']
            categoria_valor = instruccion['categoria_valor']

            # Error si la variable es 'void' o si ya fue declarada antes
            if tipo_var == 'void' or nombre_var in tabla_simbolos:
                return False, linea

            # Averiguamos el tipo del valor que está a la derecha del signo '='
            if categoria_valor == 'constant':
                tipo_del_valor = deducir_tipo_constante(valor)
            else:
                # Si a la derecha pusieron otra variable (ej. int y = x;),
                # revisamos que esa variable 'x' ya exista en la tabla de símbolos
                if valor not in tabla_simbolos:
                    return False, linea
                tipo_del_valor = tabla_simbolos[valor]

            # VERIFICACIÓN PRINCIPAL SDT:
            # El tipo declarado a la izquierda DEBE coincidir con el tipo del valor a la derecha.
            # Ejemplo: Si escribieron int x = "hola"; -> 'int' != 'string' -> ¡Error SDT!
            if tipo_var != tipo_del_valor:
                return False, linea

            # Si los tipos coinciden (ej. 'int' == 'int'), guardamos la variable en la tabla
            tabla_simbolos[nombre_var] = tipo_var

        # -----------------------------------------------------------------
        # REGLA SDT 3: Llamada simple a print/printf (ej. printf("Hola");)
        # -----------------------------------------------------------------
        elif tipo_inst == 'llamada_simple':
            arg1 = instruccion['arg1']
            # En C, el primer argumento dentro de printf(...) debe ser una cadena entre comillas ("...")
            if deducir_tipo_constante(arg1) != 'string':
                return False, linea

        # -----------------------------------------------------------------
        # REGLA SDT 4: Llamada a printf con 2 argumentos (ej. printf("Valor", x);)
        # -----------------------------------------------------------------
        elif tipo_inst == 'llamada_con_arg':
            arg1 = instruccion['arg1']
            arg2 = instruccion['arg2']
            categoria_arg2 = instruccion['categoria_arg2']

            # El primer argumento debe ser string
            if deducir_tipo_constante(arg1) != 'string':
                return False, linea

            # Si el segundo argumento es una variable, debe existir previamente en la tabla de símbolos
            if categoria_arg2 == 'identifier' and arg2 not in tabla_simbolos:
                return False, linea

    # Si todas las instrucciones cumplieron las reglas de tipos, el SDT es válido
    return True, None


# =====================================================================
# FUNCIÓN 5: PROGRAMA PRINCIPAL (MAIN)
# Conecta el Lexer -> Parser -> SDT e imprime exactamente las salidas
# que pide el PDF del profesor.
# =====================================================================
def main():
    # 1. Leer el código desde consola o archivo
    cadena = cadena_input()
    if not cadena:
        return

    # 2. Ejecutar el Lexer
    tokens, N_tokens, lista_tokens = identificar_tokens(cadena)

    print("Cadena ingresada:", cadena)
    print("--------------------------------")
    print("Tokens encontrados:")
    for tipo, lista in tokens.items():
        if lista:
            print(f"{tipo}: {', '.join(lista)}")
    print(f"Total de tokens encontrados: {N_tokens}")
    print("--------------------------------")

    # 3. Ejecutar el Parser (Análisis Sintáctico)
    parsing_exitoso, arbol_instrucciones, linea_error_parser = analizar_sintaxis_parser(lista_tokens)

    # Si falló el Parser, tanto el Parsing como el SDT fallan (Salida 2 del PDF)
    if not parsing_exitoso:
        print("Parsing error...")
        print("SDT error...")
        print(f"error in line {linea_error_parser}")
        return

    # Si el orden de los tokens fue correcto, imprimimos éxito de Parsing
    print("Parsing Success!")

    # 4. Ejecutar el SDT (Análisis Semántico de tipos)
    sdt_exitoso, linea_error_sdt = verificar_reglas_sdt(arbol_instrucciones)

    # Si los tipos de datos coincidieron (Salida 1 del PDF)
    if sdt_exitoso:
        print("SDT Verified!")
    # Si la sintaxis estaba bien pero los tipos no coincidieron (Salida 3 del PDF)
    else:
        print("SDT error...")
        print(f"error in line {linea_error_sdt}")


if __name__ == "__main__":
    main()