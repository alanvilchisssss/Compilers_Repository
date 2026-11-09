import re


def cadena_input():
    tipo = input("Ingrese '1' para ingresar una cadena de texto o '2' para ingresar el nombre de un archivo: ")
    
    if tipo.isdigit() and tipo == '1':
        cadena = input("Ingrese la cadena de texto: ")
        
    elif tipo.isdigit() and tipo == '2':
        nombre_archivo = input("Ingrese el nombre del archivo (el archivo debe estar en la misma carpeta): ")
        
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


def identificar_tokens(cadena):
    tokens = {
        'keyword': [r'^(print|printf|int|float|char|void|if|else|while|for|return|break|continue|switch|case)$'],
        'identifier': [r'^[a-zA-Z_][a-zA-Z0-9_]*$'],
        'operator': [r'^(\+|\-|\*|\/|\%|\=\=|\!\=|\<\=|\>\=|\=|\<|\>|\&\&|\|\||\!)$'],
        'constant': [r'^\d+\.\d+$', r'^\d+$', r'^"(?:\\.|[^"\\])*"$', r"^'(?:\\.|[^'\\])*'$"],
        'punctuation': [r'^(\(|\)|\{|\}|\[|\]|\;|\,|\.|\:|\?)$']
    }

    tokens_encontrados = {
        'keyword': [],
        'identifier': [],
        'operator': [],
        'constant': [],
        'punctuation': [],
        'no_reconocido': []
    }

    patron_lexer = (
        r'//[^\n]*'
        r'|/\*[\s\S]*?\*/'
        r'|"(?:\\.|[^"\\])*"'
        r"|'(?:\\.|[^'\\])*'"
        r'|\d+\.\d+'
        r'|\d+'
        r'|[a-zA-Z_][a-zA-Z0-9_]*'
        r'|==|!=|<=|>='
        r'|\+|\-|\*|\/|\%|\=|\<|\>|\&\&|\|\||\!'
        r'|\(|\)|\{|\}|\[|\]|\;|\,|\.|\:|\?'
        r'|\S'
    )

    lista_tokens = []
    N_tokens = 0

    lineas = cadena.split('\n')

    for numero_linea, texto_linea in enumerate(lineas, start=1):
        cadenas_encontradas = re.findall(patron_lexer, texto_linea)

        for lexema in cadenas_encontradas:
            if lexema.startswith('//') or lexema.startswith('/*'):
                continue

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

            tokens_encontrados[categoria].append(lexema)

            lista_tokens.append({
                'categoria': categoria,
                'lexema': lexema,
                'linea': numero_linea
            })

    return tokens_encontrados, N_tokens, lista_tokens


def analizar_sintaxis_parser(lista_tokens):
    if len(lista_tokens) == 0:
        return False, [], 1

    arbol_instrucciones = []

    i = 0
    total = len(lista_tokens)

    while i < total:
        token_actual = lista_tokens[i]
        linea_actual = token_actual['linea']

        if token_actual['categoria'] == 'no_reconocido':
            return False, [], linea_actual

        if token_actual['categoria'] == 'keyword' and token_actual['lexema'] in ['int', 'float', 'char', 'void']:
            
            
            tipo_dato = token_actual['lexema']
            i += 1

            if i >= total or lista_tokens[i]['categoria'] != 'identifier':
                return False, [], linea_actual
            nombre_variable = lista_tokens[i]['lexema']
            i += 1

            if i >= total:
                return False, [], linea_actual

            if lista_tokens[i]['lexema'] == ';':
                i += 1
                
                arbol_instrucciones.append({
                    'tipo_instruccion': 'declaracion_simple',
                    'tipo_dato': tipo_dato,
                    'variable': nombre_variable,
                    'linea': linea_actual
                })

            elif lista_tokens[i]['lexema'] == '=':
                i += 1

                if i >= total or lista_tokens[i]['categoria'] not in ['constant', 'identifier']:
                    return False, [], linea_actual
                valor_asignado = lista_tokens[i]['lexema']
                categoria_valor = lista_tokens[i]['categoria']
                i += 1

                if i >= total or lista_tokens[i]['lexema'] != ';':
                    return False, [], linea_actual
                i += 1

                arbol_instrucciones.append({
                    'tipo_instruccion': 'declaracion_asignacion',
                    'tipo_dato': tipo_dato,
                    'variable': nombre_variable,
                    'valor': valor_asignado,
                    'categoria_valor': categoria_valor,
                    'linea': linea_actual
                })

            else:
                return False, [], lista_tokens[i]['linea']

        elif token_actual['categoria'] == 'keyword' and token_actual['lexema'] in ['printf', 'print']:
            
            funcion = token_actual['lexema']
            i += 1

            if i >= total or lista_tokens[i]['lexema'] != '(':
                return False, [], linea_actual
            i += 1

            if i >= total or lista_tokens[i]['categoria'] not in ['constant', 'identifier']:
                return False, [], linea_actual
            primer_argumento = lista_tokens[i]['lexema']
            i += 1

            if i >= total:
                return False, [], linea_actual

            if lista_tokens[i]['lexema'] == ')':
                i += 1
                if i >= total or lista_tokens[i]['lexema'] != ';':
                    return False, [], linea_actual
                i += 1

                arbol_instrucciones.append({
                    'tipo_instruccion': 'llamada_simple',
                    'funcion': funcion,
                    'arg1': primer_argumento,
                    'linea': linea_actual
                })

            elif lista_tokens[i]['lexema'] == ',':
                i += 1

                if i >= total or lista_tokens[i]['categoria'] not in ['constant', 'identifier']:
                    return False, [], linea_actual
                segundo_argumento = lista_tokens[i]['lexema']
                categoria_arg2 = lista_tokens[i]['categoria']
                i += 1

                if i >= total or lista_tokens[i]['lexema'] != ')':
                    return False, [], linea_actual
                i += 1

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

        else:
            return False, [], linea_actual

    return True, arbol_instrucciones, None


def deducir_tipo_constante(texto_constante):
    if texto_constante.startswith('"') and texto_constante.endswith('"'):
        return 'string'
    elif texto_constante.startswith("'") and texto_constante.endswith("'"):
        return 'char'
    elif '.' in texto_constante:
        return 'float'
    else:
        return 'int'


def verificar_reglas_sdt(arbol_instrucciones):
    tabla_simbolos = {}

    for instruccion in arbol_instrucciones:
        tipo_inst = instruccion['tipo_instruccion']
        linea = instruccion['linea']

        if tipo_inst == 'declaracion_simple':
            tipo_var = instruccion['tipo_dato']
            nombre_var = instruccion['variable']

            if tipo_var == 'void' or nombre_var in tabla_simbolos:
                return False, linea

            tabla_simbolos[nombre_var] = tipo_var

        elif tipo_inst == 'declaracion_asignacion':
            tipo_var = instruccion['tipo_dato']
            nombre_var = instruccion['variable']
            valor = instruccion['valor']
            categoria_valor = instruccion['categoria_valor']

            if tipo_var == 'void' or nombre_var in tabla_simbolos:
                return False, linea

            if categoria_valor == 'constant':
                tipo_del_valor = deducir_tipo_constante(valor)
            else:
                if valor not in tabla_simbolos:
                    return False, linea
                tipo_del_valor = tabla_simbolos[valor]

            if tipo_var != tipo_del_valor:
                return False, linea

            tabla_simbolos[nombre_var] = tipo_var

        elif tipo_inst == 'llamada_simple':
            arg1 = instruccion['arg1']
            if deducir_tipo_constante(arg1) != 'string':
                return False, linea

        elif tipo_inst == 'llamada_con_arg':
            arg1 = instruccion['arg1']
            arg2 = instruccion['arg2']
            categoria_arg2 = instruccion['categoria_arg2']

            if deducir_tipo_constante(arg1) != 'string':
                return False, linea

            if categoria_arg2 == 'identifier' and arg2 not in tabla_simbolos:
                return False, linea

    return True, None


def main():
    cadena = cadena_input()
    if not cadena:
        return

    tokens, N_tokens, lista_tokens = identificar_tokens(cadena)

    print("Cadena ingresada:", cadena)
    print("--------------------------------")
    print("Tokens encontrados:")
    for tipo, lista in tokens.items():
        if lista:
            print(f"{tipo}: {', '.join(lista)}")
    print(f"Total de tokens encontrados: {N_tokens}")
    print("--------------------------------")

    parsing_exitoso, arbol_instrucciones, linea_error_parser = analizar_sintaxis_parser(lista_tokens)

    if not parsing_exitoso:
        print("Parsing error...")
        print("SDT error...")
        print(f"error in line {linea_error_parser}")
        return

    print("Parsing Success!")

    sdt_exitoso, linea_error_sdt = verificar_reglas_sdt(arbol_instrucciones)

    if sdt_exitoso:
        print("SDT Verified!")
    else:
        print("SDT error...")
        print(f"error in line {linea_error_sdt}")


if __name__ == "__main__":
    main()