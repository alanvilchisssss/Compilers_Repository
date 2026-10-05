import re
#funciones a realizar 
#1. Lectura de cadena de texto / archivo 
def cadena_input():
    tipo= input("Ingrese '1' para ingresar una cadena de texto o '2' para ingresar el nombre de un archivo: ")
    if tipo.isdigit() and tipo == '1': 
        cadena= input("Ingrese la cadena de texto: ")
    elif tipo.isdigit() and tipo == '2':
        nombre_archivo=input("ingrese el nombre del archivo(el archivo debe estar en la misma carpeta):")
        if not nombre_archivo.endswith('.txt'):
            nombre_archivo += '.txt'
        try: 
            with open(nombre_archivo, 'r') as archivo:
                cadena= archivo.read()
        except FileNotFoundError:
            print("El archivo no se encontró. Por favor, asegúrese de que el nombre del archivo sea correcto y que esté en la misma carpeta.")
            cadena= ""
    else:
        print("Opción inválida. Por favor, ingrese '1' o '2'.")
        cadena= ""
    return cadena

#2. Identificación de tokens 
def identificar_tokens(cadena):
    tokens= {
        #keyword identifier operator constant punctuation
        # Se tienen 40 tokens base entre keywords, operadores y punctuation.
        'keyword':[r'print|printf|int|float|char|void|if|else|while|for|return|break|continue|switch|case'],
        'identifier':[r'[a-zA-Z_][a-zA-Z0-9_]*'],
        # Los operadores de mas de un caracter se reconocen completos.
        'operator':[r'\+|\-|\*|\/|\%|\=|\=\=|\!\=|\<|\>|\<\=|\>\=|\&\&|\|\||\!'],
        # Se agregaron constantes reales, cadenas y caracteres, ademas de enteros.
        'constant':[r'\d+\.\d+', r'\d+', r'"(?:\\.|[^"\\])*"', r"'(?:\\.|[^'\\])*'"],
        'punctuation':[r'\(|\)|\{|\}|\[|\]|\;|\,|\.|\:|\?']
    }

    tokens_encontrados= {
        'keyword':[],
        'identifier':[],
        'operator':[],
        'constant':[],
        'punctuation':[],
        'no_reconocido':[]
    }

    # Se hace un solo recorrido para no separar por error operadores como ==, !=, <= y >=
    # ni las cadenas de texto que contienen espacios.
    patron_lexer = (
        r'//[^\n]*'                                  # comentario de una linea
        r'|/\*[\s\S]*?\*/'                           # comentario de varias lineas
        r'|"(?:\\.|[^"\\])*"'                        # cadena de texto
        r"|\'(?:\\.|[^\'\\])*\'"                     # caracter
        r'|\d+\.\d+'                                 # constante real
        r'|\d+'                                      # constante entera
        r'|[a-zA-Z_][a-zA-Z0-9_]*'                   # identificador o keyword
        r'|\=\=|\!\=|\<\=|\>\='                     # operadores de dos caracteres
        r'|\+|\-|\*|\/|\%|\=|\<|\>|\&\&|\|\||\!'   # operadores de un caracter
        r'|\(|\)|\{|\}|\[|\]|\;|\,|\.|\:|\?'        # punctuation
        r'|\S'                                       # cualquier otro caracter
    )

    cadenas_encontradas= re.findall(patron_lexer, cadena)
    N_tokens=0

    for token in cadenas_encontradas:
        # Los comentarios no se consideran tokens.
        if token.startswith('//') or token.startswith('/*'):
            continue

        if re.fullmatch('|'.join(tokens['keyword']), token):
            tokens_encontrados['keyword'].append(token)
            N_tokens+=1
        elif re.fullmatch('|'.join(tokens['identifier']), token):
            tokens_encontrados['identifier'].append(token)
            N_tokens+=1
        elif re.fullmatch('|'.join(tokens['operator']), token):
            tokens_encontrados['operator'].append(token)
            N_tokens+=1
        elif re.fullmatch('|'.join(tokens['constant']), token):
            tokens_encontrados['constant'].append(token)
            N_tokens+=1
        elif re.fullmatch('|'.join(tokens['punctuation']), token):
            tokens_encontrados['punctuation'].append(token)
            N_tokens+=1
        else:
            print(f"Token no reconocido: {token}")
            tokens_encontrados['no_reconocido'].append(token)

    return tokens_encontrados, N_tokens
#3. 

def main(): 
    cadena= cadena_input()
    tokens, N_tokens= identificar_tokens(cadena)
    print("Cadena ingresada:", cadena)
    print("--------------------------------")
    print("Tokens encontrados:")
    for tipo, lista in tokens.items():
        if lista:
            print(f"{tipo}: {', '.join(lista)}")
    print(f"Total de tokens encontrados: {N_tokens}")
    print("--------------------------------")

if __name__ == "__main__": 
    main()
