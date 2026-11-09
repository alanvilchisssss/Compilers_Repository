import re  # Importamos 're' (Regular Expressions) para buscar patrones de texto como si fuera un filtro inteligente.


# =========================================================================================
# BLOQUE 1: LECTURA DE ENTRADA (cadena_input)
# 💡 ANALOGÍA: Es la "ventanilla de recepción". Pregunta si vas a dictarle el código
#    en vivo por teclado (opción 1) o si le vas a entregar una hoja impresa .txt (opción 2).
# =========================================================================================
def cadena_input():
    # Pedimos al usuario que elija '1' o '2' y lo guardamos en la variable 'tipo'
    tipo = input("Ingrese '1' para ingresar una cadena de texto o '2' para ingresar el nombre de un archivo: ")
    
    # .isdigit() verifica que haya escrito un número y no letras. Si eligió '1':
    if tipo.isdigit() and tipo == '1':
        cadena = input("Ingrese la cadena de texto: ")
        
    # Si eligió '2', leemos un archivo .txt de la misma carpeta:
    elif tipo.isdigit() and tipo == '2':
        nombre_archivo = input("Ingrese el nombre del archivo (el archivo debe estar en la misma carpeta): ")
        
        # POR QUÉ PUSIMOS ESTO: Si el compañero o el profe escribe solo "prueba_40_tokens"
        # sin el ".txt", este 'if' se lo pega al final para que Python no falle al buscarlo.
        if not nombre_archivo.endswith('.txt'):
            nombre_archivo += '.txt'
            
        # Usamos try/except como "red de seguridad": si el archivo no existe, en vez de que
        # el programa explote con letras rojas, muestra un mensaje amigable y devuelve "".
        try:
            with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
                cadena = archivo.read()  # Lee todo el archivo de golpe y lo mete en 'cadena'
        except FileNotFoundError:
            print("El archivo no se encontró. Por favor, asegúrese de que el nombre del archivo sea correcto.")
            cadena = ""
    else:
        print("Opción inválida. Por favor, ingrese '1' o '2'.")
        cadena = ""
        
    return cadena  # Entregamos el texto recolectado para que lo use el Lexer


# =========================================================================================
# BLOQUE 2: ANALIZADOR LÉXICO / LEXER (identificar_tokens)
# 💡 ANALOGÍA: Es una máquina clasificadora de monedas. Recibe todo el texto revuelto,
#    tira a la basura la tierra (los comentarios // y /* */), y separa cada pieza poniéndole
#    su etiqueta ('keyword', 'identifier', 'operator', 'constant', 'punctuation')
#    y anotando en qué renglón (línea) venía.
# =========================================================================================
def identificar_tokens(cadena):
    # 🧠 NEMOTECNIA DE SÍMBOLOS REGEX (Por si pregunta el profe):
    #   ^  = "Que empiece exactamente aquí"
    #   $  = "Que termine exactamente aquí" (Ponemos ^ y $ para que la variable 'int_num' NO la confunda con 'int')
    #   \d = Cualquier dígito del 0 al 9 (d de digit)
    #   +  = Uno o más repetidos (ej. \d+ atrapa el '10' o el '5432')
    #   |  = Significa "O" (ej. print|printf significa 'print' O 'printf')
    tokens = {
        'keyword': [r'^(print|printf|int|float|char|void|if|else|while|for|return|break|continue|switch|case)$'],
        'identifier': [r'^[a-zA-Z_][a-zA-Z0-9_]*$'],  # Empieza con letra o guion bajo, seguido de letras/números
        'operator': [r'^(\+|\-|\*|\/|\%|\=\=|\!\=|\<\=|\>\=|\=|\<|\>|\&\&|\|\||\!)$'],
        'constant': [r'^\d+\.\d+$', r'^\d+$', r'^"(?:\\.|[^"\\])*"$', r"^'(?:\\.|[^'\\])*'$"], # Flotantes, enteros, "textos", 'chars'
        'punctuation': [r'^(\(|\)|\{|\}|\[|\]|\;|\,|\.|\:|\?)$']
    }

    # Estas son las 6 "cajitas" donde guardamos los tokens agrupados por tipo (para imprimir el resumen del Lexer)
    tokens_encontrados = {
        'keyword': [],
        'identifier': [],
        'operator': [],
        'constant': [],
        'punctuation': [],
        'no_reconocido': []
    }

    # ⚠️ POR QUÉ EL ORDEN DE ESTE PATRÓN ES VITAL (Conclusión 1 de nuestro reporte):
    # Siempre ponemos PRIMERO las cosas largas y DESPUÉS las cortas.
    # Ejemplo: Ponemos '==' y '<=' ANTES que '=' y '<'. Si pusiéramos '=' primero,
    # al ver '<=' lo partiría en dos pedazos ('<' y '=') en vez de leerlo junto.
    patron_lexer = (
        r'//[^\n]*'               # 1. Comentario de una línea (desde // hasta el final del renglón)
        r'|/\*[\s\S]*?\*/'        # 2. Comentario multilínea (desde /* hasta */)
        r'|"(?:\\.|[^"\\])*"'     # 3. Cadena completa entre comillas dobles (conserva sus espacios adentro)
        r"|'(?:\\.|[^'\\])*'"     # 4. Carácter entre comillas simples (ej. 'a')
        r'|\d+\.\d+'              # 5. Número con punto decimal (va ANTES del entero para que 30.5 no se parta en 30 y 5)
        r'|\d+'                   # 6. Número entero (ej. 10)
        r'|[a-zA-Z_][a-zA-Z0-9_]*'# 7. Palabras (pueden ser keywords como 'int' o variables como 'x')
        r'|==|!=|<=|>='           # 8. Operadores dobles (van ANTES de los operadores de 1 solo signo)
        r'|\+|\-|\*|\/|\%|\=|\<|\>|\&\&|\|\||\!' # 9. Operadores individuales
        r'|\(|\)|\{|\}|\[|\]|\;|\,|\.|\:|\?'     # 10. Signos de puntuación (; , ( ) etc.)
        r'|\S'                    # 11. Cualquier símbolo raro que no sea espacio (para atrapar errores como @ o #)
    )

    # 🔥 LO NUEVO QUE AGREGAMOS PARA CONECTAR CON EL PARSER:
    # En la Entrega 1 solo teníamos el diccionario 'tokens_encontrados', pero ese diccionario
    # desordena el código porque mete todos los keywords juntos y todos los signos juntos.
    # Por eso creamos 'lista_tokens': una fila india donde cada token guarda su orden exacto y su renglón.
    lista_tokens = []
    N_tokens = 0

    # Partimos el texto cada vez que hay un Enter (\n) para poder contar en qué renglón vamos.
    # Esto es OBLIGATORIO porque el PDF del profe pide imprimir: "error in line n".
    lineas = cadena.split('\n')

    # enumerate(..., start=1) nos da dos cosas en cada vuelta: el número de renglón (1, 2, 3...) y el texto de ese renglón
    for numero_linea, texto_linea in enumerate(lineas, start=1):
        # re.findall recorta todas las piezas de ese renglón usando nuestra plantilla 'patron_lexer'
        cadenas_encontradas = re.findall(patron_lexer, texto_linea)

        for lexema in cadenas_encontradas:
            # Si la pieza recortada empieza con // o /*, es un comentario: lo saltamos con 'continue'
            if lexema.startswith('//') or lexema.startswith('/*'):
                continue

            # Probamos en qué categoría encaja la pieza (primero keyword antes que identifier,
            # porque 'int' tiene letras como un identifier, pero tiene prioridad como palabra reservada)
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

            # 1) Lo metemos en la cajita por categoría (para el reporte del Lexer)
            tokens_encontrados[categoria].append(lexema)

            # 2) Lo formamos en la fila india para el Parser con su gafete completo (categoría, texto y línea)
            lista_tokens.append({
                'categoria': categoria,
                'lexema': lexema,
                'linea': numero_linea
            })

    # Devolvemos las 3 cosas: el diccionario por categorías, el conteo total y la fila ordenada para el Parser
    return tokens_encontrados, N_tokens, lista_tokens


# =========================================================================================
# BLOQUE 3: ANALIZADOR SINTÁCTICO / PARSER TOP-DOWN LL(1) (analizar_sintaxis_parser)
# 💡 ANALOGÍA: Es un guardia con una lista de control (Checklist). Va caminando por la fila
#    de tokens usando su dedo índice (la variable 'i'). En cada paso dice:
#    "A ver, aquí toca un tipo de dato... bien, avanzo el dedo (i += 1). Ahora toca un
#    nombre de variable... bien, avanzo el dedo (i += 1)". Si en algún paso no está lo que
#    toca, suena la alarma y devuelve False con el número de línea.
#
# 🧠 NEMOTECNIA DE LA GRAMÁTICA CON FACTORIZACIÓN POR LA IZQUIERDA (Reporte 1):
#     En nuestro Reporte 1 teníamos dos formas de declarar:
#       Forma A:  int x ;
#       Forma B:  int x = 10 ;
#    Como ambas empiezan igual ("int x"), eso es el PREFIJO COMÚN (type id).
#    Factorizar por la izquierda en código es simplemente:
#       1. Leo primero lo que tienen en común: el tipo ('int') y el id ('x').
#       2. Luego pongo un 'if/elif' para ver qué camino tomó el usuario:
#          - Camino A: ¿Siguió un ';'? -> Declaración simple.
#          - Camino B: ¿Siguió un '='? -> Leo el valor y luego el ';' -> Declaración con asignación.
# =========================================================================================
def analizar_sintaxis_parser(lista_tokens):
    # Si la fila de tokens llegó vacía, marcamos error en la línea 1
    if len(lista_tokens) == 0:
        return False, [], 1

    # 'arbol_instrucciones' es donde iremos guardando los paquetes de oraciones que SÍ estuvieron
    # bien escritas, para pasárselas después al verificador semántico (SDT).
    arbol_instrucciones = []

    # 'i' es nuestro dedo índice. Empieza apuntando al primer token de la fila (posición 0)
    i = 0
    total = len(lista_tokens)

    # Mientras nuestro dedo 'i' no haya terminado de recorrer toda la fila de tokens:
    while i < total:
        token_actual = lista_tokens[i]
        linea_actual = token_actual['linea']

        # Si el token actual ni siquiera existe en nuestro idioma (ej. un '@' o '$'), abortamos de inmediato
        if token_actual['categoria'] == 'no_reconocido':
            return False, [], linea_actual

        # =================================================================================
        # REGLA GRAMATICAL 1: DECLARACIONES (Decl -> type id Decl')
        # Se activa cuando la oración empieza con: int, float, char o void
        # =================================================================================
        if token_actual['categoria'] == 'keyword' and token_actual['lexema'] in ['int', 'float', 'char', 'void']:
            
            # --- PREFIJO COMÚN (Lo que todas las declaraciones tienen al inicio: type + id) ---
            
            # PASO 1: Ya vimos que el token actual es un tipo (ej. 'int'). Lo anotamos y movemos el dedo (+1)
            tipo_dato = token_actual['lexema']
            i += 1

            # PASO 2: Revisamos el siguiente token. ¡CUIDADO CON 'i >= total'!
            # ¿Por qué siempre preguntamos 'if i >= total'? Porque si alguien escribió solo "int" y ahí
            # se acabó el archivo, al buscar la siguiente posición el programa se saldría de la lista.
            # Si se acabó la lista O lo que sigue NO es un identificador (nombre de variable), es Error Sintáctico.
            if i >= total or lista_tokens[i]['categoria'] != 'identifier':
                return False, [], linea_actual
            nombre_variable = lista_tokens[i]['lexema']
            i += 1  # Todo bien, ya leímos el nombre de la variable (ej. 'x'), movemos el dedo (+1)

            # --- FACTORIZACIÓN POR LA IZQUIERDA (Decl' -> ;  |  = Expr ;) ---
            # Aquí es donde nuestro Parser LL(1) mira el siguiente token (Lookahead) para decidir el camino sin regresarse:
            if i >= total:
                return False, [], linea_actual

            # CAMINO 1A: El siguiente token es un punto y coma ';' (Ejemplo: int x;)
            if lista_tokens[i]['lexema'] == ';':
                i += 1  # Avanzamos el dedo dejando atrás el ';'
                
                # Guardamos la instrucción validada en nuestro árbol sintáctico:
                arbol_instrucciones.append({
                    'tipo_instruccion': 'declaracion_simple',
                    'tipo_dato': tipo_dato,
                    'variable': nombre_variable,
                    'linea': linea_actual
                })

            # CAMINO 1B: El siguiente token es un signo igual '=' (Ejemplo: int x = 10;)
            elif lista_tokens[i]['lexema'] == '=':
                i += 1  # Avanzamos el dedo dejando atrás el '='

                # Después del '=' tiene que venir forzosamente un valor (una constante como 10 o "hola", o una variable)
                if i >= total or lista_tokens[i]['categoria'] not in ['constant', 'identifier']:
                    return False, [], linea_actual
                valor_asignado = lista_tokens[i]['lexema']
                categoria_valor = lista_tokens[i]['categoria']
                i += 1  # Avanzamos el dedo dejando atrás el valor

                # Y para cerrar la oración, tiene que haber un punto y coma ';' obligatorio
                if i >= total or lista_tokens[i]['lexema'] != ';':
                    return False, [], linea_actual
                i += 1  # Avanzamos el dedo dejando atrás el ';'

                # Guardamos la instrucción completa en nuestro árbol sintáctico:
                # Nota cómo aquí el Parser NO revisa si '10' o '"hola"' combinan con 'int';
                # el Parser solo dice: "La estructura gramatical está completa, que el SDT revise los tipos".
                arbol_instrucciones.append({
                    'tipo_instruccion': 'declaracion_asignacion',
                    'tipo_dato': tipo_dato,
                    'variable': nombre_variable,
                    'valor': valor_asignado,
                    'categoria_valor': categoria_valor,
                    'linea': linea_actual
                })

            # Si después de "int x" no pusieron ni ';' ni '=', está mal escrito -> Error Sintáctico
            else:
                return False, [], lista_tokens[i]['linea']

        # =================================================================================
        # REGLA GRAMATICAL 2: IMPRESIÓN EN PANTALLA (Call -> printf ( string Call')
        # Se activa cuando la oración empieza con: printf o print
        # =================================================================================
        elif token_actual['categoria'] == 'keyword' and token_actual['lexema'] in ['printf', 'print']:
            
            # --- PREFIJO COMÚN: printf + ( + primer_argumento ---
            funcion = token_actual['lexema']
            i += 1  # Avanzamos después de 'printf'

            # PASO 1: Debe abrir paréntesis '('
            if i >= total or lista_tokens[i]['lexema'] != '(':
                return False, [], linea_actual
            i += 1  # Avanzamos después de '('

            # PASO 2: Debe venir lo que queremos imprimir (constante o variable)
            if i >= total or lista_tokens[i]['categoria'] not in ['constant', 'identifier']:
                return False, [], linea_actual
            primer_argumento = lista_tokens[i]['lexema']
            i += 1  # Avanzamos después del primer argumento

            # --- FACTORIZACIÓN POR LA IZQUIERDA (Call' -> );  |  , Arg );) ---
            if i >= total:
                return False, [], linea_actual

            # CAMINO 2A: Cierra paréntesis ')' y punto y coma ';' (Ejemplo: printf("This is an example");)
            if lista_tokens[i]['lexema'] == ')':
                i += 1  # Avanzamos después de ')'
                if i >= total or lista_tokens[i]['lexema'] != ';':
                    return False, [], linea_actual
                i += 1  # Avanzamos después de ';'

                arbol_instrucciones.append({
                    'tipo_instruccion': 'llamada_simple',
                    'funcion': funcion,
                    'arg1': primer_argumento,
                    'linea': linea_actual
                })

            # CAMINO 2B: Viene una coma ',' para imprimir una segunda cosa (Ejemplo: printf("Valor: ", x);)
            elif lista_tokens[i]['lexema'] == ',':
                i += 1  # Avanzamos después de ','

                # Leemos el segundo argumento después de la coma
                if i >= total or lista_tokens[i]['categoria'] not in ['constant', 'identifier']:
                    return False, [], linea_actual
                segundo_argumento = lista_tokens[i]['lexema']
                categoria_arg2 = lista_tokens[i]['categoria']
                i += 1

                # Debe cerrar con ')'
                if i >= total or lista_tokens[i]['lexema'] != ')':
                    return False, [], linea_actual
                i += 1

                # Debe cerrar con ';'
                if i >= total or lista_tokens[i]['lexema'] != ';':
                    return False, [], linea_actual
                i += 1

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

        # Si una instrucción empieza con cualquier otra palabra que no sea ni Declaración ni Print:
        else:
            return False, [], linea_actual

    # Si el dedo 'i' llegó hasta el final sin toparse con ningún error, devolvemos True (¡Parsing Success!)
    return True, arbol_instrucciones, None


# =========================================================================================
# FUNCIÓN AUXILIAR: deducir_tipo_constante
# 💡 ANALOGÍA: Es una lupa que mira una constante y nos dice qué tipo de dato es en realidad.
#    Porque para el Lexer, tanto 10 como 30.5 como "Hola" se llaman simplemente 'constant'.
#    Aquí las distinguimos fijándonos en cómo están escritas:
#    - ¿Tiene comillas dobles "..."? -> Es un 'string'
#    - ¿Tiene comillas simples '.'?  -> Es un 'char'
#    - ¿Tiene un punto decimal '.'?  -> Es un 'float'
#    - ¿No tiene nada de lo anterior? -> Es un 'int'
# =========================================================================================
def deducir_tipo_constante(texto_constante):
    if texto_constante.startswith('"') and texto_constante.endswith('"'):
        return 'string'
    elif texto_constante.startswith("'") and texto_constante.endswith("'"):
        return 'char'
    elif '.' in texto_constante:
        return 'float'
    else:
        return 'int'


# =========================================================================================
# BLOQUE 4: ANALIZADOR SEMÁNTICO / SDT (verificar_reglas_sdt)
# 💡 ANALOGÍA: Es el "Contador con Libro de Registro".
#    Tiene un cuaderno llamado 'tabla_simbolos' donde anota cada variable que nace y su tipo.
#    Revisa 3 leyes de sentido común:
#      Ley 1: No puedes crear variables de tipo 'void' (vacío) ni bautizar dos variables con el mismo nombre.
#      Ley 2: La caja de la izquierda (ej. int) DEBE ser del mismo tipo que lo que metes a la derecha (ej. 10).
#      Ley 3: No puedes usar una variable que no haya sido anotada antes en el cuaderno.
#
# 🧠 CONCEPTOS TEÓRICOS DEL PROFE EN ESTE BLOQUE:
#    - Atributo Heredado: Es el tipo que imponemos desde la izquierda (`tipo_var = 'int'`).
#    - Atributo Sintetizado: Es el tipo que deducimos del valor de la derecha (`tipo_del_valor = 'int'`).
#    - Regla SDT: Comparar que Atributo Heredado == Atributo Sintetizado (`tipo_var == tipo_del_valor`).
# =========================================================================================
def verificar_reglas_sdt(arbol_instrucciones):
    # Nuestro cuaderno de registro (Tabla de Símbolos). Empieza vacío.
    # Cuando registremos 'int x = 10;', se verá así: {'x': 'int'}
    tabla_simbolos = {}

    # Revisamos una por una las oraciones que el Parser nos mandó ya aprobadas:
    for instruccion in arbol_instrucciones:
        tipo_inst = instruccion['tipo_instruccion']
        linea = instruccion['linea']

        # ---------------------------------------------------------------------------------
        # CASO SDT 1: Declaración sin valor (ej. int a;)
        # ---------------------------------------------------------------------------------
        if tipo_inst == 'declaracion_simple':
            tipo_var = instruccion['tipo_dato']
            nombre_var = instruccion['variable']

            # En C no existen variables de tipo 'void', ni puedes declarar dos veces la misma variable 'a'
            if tipo_var == 'void' or nombre_var in tabla_simbolos:
                return False, linea

            # La anotamos en nuestro cuaderno:
            tabla_simbolos[nombre_var] = tipo_var

        # ---------------------------------------------------------------------------------
        # CASO SDT 2: Declaración con asignación (ej. int x = 10;  ó  int x = "hola";)
        # 🔥 AQUÍ OCURRE LA MAGIA QUE PIDE EL PDF DEL PROFE ("Parsing Success! pero SDT error...")
        # ---------------------------------------------------------------------------------
        elif tipo_inst == 'declaracion_asignacion':
            tipo_var = instruccion['tipo_dato']          # Atributo heredado (ej. 'int')
            nombre_var = instruccion['variable']         # Nombre (ej. 'x')
            valor = instruccion['valor']                 # Lo que hay a la derecha del '=' (ej. '10' o '"hola"')
            categoria_valor = instruccion['categoria_valor']

            # Verificamos Ley 1 (que no sea void ni repetida)
            if tipo_var == 'void' or nombre_var in tabla_simbolos:
                return False, linea

            # Averiguamos el Atributo Sintetizado (de qué tipo es lo que está a la derecha del '=')
            if categoria_valor == 'constant':
                # Si es una constante, usamos nuestra lupa auxiliar:
                tipo_del_valor = deducir_tipo_constante(valor)
            else:
                # Si a la derecha pusieron el nombre de otra variable (ej. int y = x;),
                # buscamos a 'x' en el cuaderno. Si 'x' no existe en el cuaderno -> ¡Error SDT!
                if valor not in tabla_simbolos:
                    return False, linea
                tipo_del_valor = tabla_simbolos[valor]

            # Ley 2 (Choque de tipos): Si la caja es 'int' pero el valor es 'string' o 'float' -> ¡Error SDT!
            if tipo_var != tipo_del_valor:
                return False, linea

            # Si todo cuadró ('int' == 'int'), anotamos la variable en el cuaderno:
            tabla_simbolos[nombre_var] = tipo_var

        # ---------------------------------------------------------------------------------
        # CASO SDT 3: Print simple (ej. printf("This is an example");)
        # ---------------------------------------------------------------------------------
        elif tipo_inst == 'llamada_simple':
            arg1 = instruccion['arg1']
            # En C, printf exige que el primer argumento sea una cadena de texto ("string").
            # Si alguien escribió printf(10); -> El Parser lo dejó pasar, pero el SDT lo reprueba aquí.
            if deducir_tipo_constante(arg1) != 'string':
                return False, linea

        # ---------------------------------------------------------------------------------
        # CASO SDT 4: Print con variable (ej. printf("Resultado: ", x);)
        # ---------------------------------------------------------------------------------
        elif tipo_inst == 'llamada_con_arg':
            arg1 = instruccion['arg1']
            arg2 = instruccion['arg2']
            categoria_arg2 = instruccion['categoria_arg2']

            if deducir_tipo_constante(arg1) != 'string':
                return False, linea

            # Si el segundo argumento es una variable, revisamos que ya esté anotada en el cuaderno:
            if categoria_arg2 == 'identifier' and arg2 not in tabla_simbolos:
                return False, linea

    # Si pasó todas las pruebas sin errores, devolvemos True (¡SDT Verified!)
    return True, None


# =========================================================================================
# BLOQUE 5: FUNCIÓN PRINCIPAL (main)
# 💡 ANALOGÍA: Es el Director de Orquesta. Llama en orden al Recepcionista (input),
#    al Clasificador (Lexer), al Inspector de Orden (Parser) y al Contador de Tipos (SDT),
#    imprimiendo los mensajes exactos en inglés que pide la hoja del profesor.
# =========================================================================================
def main():
    # Paso 1: Pedir el texto o archivo
    cadena = cadena_input()
    if not cadena:
        return

    # Paso 2: Correr el Lexer y mostrar su tabla de tokens encontrados
    tokens, N_tokens, lista_tokens = identificar_tokens(cadena)

    print("Cadena ingresada:", cadena)
    print("--------------------------------")
    print("Tokens encontrados:")
    for tipo, lista in tokens.items():
        if lista:
            print(f"{tipo}: {', '.join(lista)}")
    print(f"Total de tokens encontrados: {N_tokens}")
    print("--------------------------------")

    # Paso 3: Correr el Parser pasándole la fila ordenada de tokens
    parsing_exitoso, arbol_instrucciones, linea_error_parser = analizar_sintaxis_parser(lista_tokens)

    # ESCENARIO A: Si falló la sintaxis (ej. faltó el ';' en "int x = 10"),
    # el árbol ni siquiera se termina de construir, así que fallan AMBOS (Parsing y SDT):
    if not parsing_exitoso:
        print("Parsing error...")
        print("SDT error...")
        print(f"error in line {linea_error_parser}")
        return

    # Si no falló el Parser, cantamos victoria sintáctica:
    print("Parsing Success!")

    # Paso 4: Correr el SDT pasándole el árbol de instrucciones
    sdt_exitoso, linea_error_sdt = verificar_reglas_sdt(arbol_instrucciones)

    # ESCENARIO B: Sintaxis bien Y tipos de datos bien (ej. "int x = 10;")
    if sdt_exitoso:
        print("SDT Verified!")
    # ESCENARIO C: Sintaxis bien PERO tipos incompatibles (ej. "int x = 30.5;" o 'int x = "hola";')
    else:
        print("SDT error...")
        print(f"error in line {linea_error_sdt}")


# Esta última línea le dice a Python: "Cuando ejecuten este archivo, arranca por la función main()"
if __name__ == "__main__":
    main()