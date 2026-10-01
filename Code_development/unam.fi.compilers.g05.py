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
        'keyword':['if', 'else', 'while', 'for', 'return'],
        'identifier':[],
        'operator':['+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>='],
        'constant':[],
        'punctuation':['(', ')', '{', '}', '[', ']', ';', ',']
    }
    tokens_encontrados= {
        'keyword':[],
        'identifier':[],
        'operator':[],
        'constant':[],
        'punctuation':[],
        'no_reconocido':[]
    }
    cadenas_encontradas= cadena.split()
    for token in cadenas_encontradas:
        if token in tokens['keyword']:
            tokens_encontrados['keyword'].append(token)
        elif token.isidentifier():
            tokens_encontrados['identifier'].append(token)
        elif token in tokens['operator']:
            tokens_encontrados['operator'].append(token)
        elif token.isdigit():
            tokens_encontrados['constant'].append(token)
        elif token in tokens['punctuation']:
            tokens_encontrados['punctuation'].append(token)
        else:
            print(f"Token no reconocido: {token}")
            tokens_encontrados['no_reconocido'].append(token)
    return tokens_encontrados
#3. 

def main(): 
    N_tokens=0
    cadena= cadena_input()
    tokens= identificar_tokens(cadena)
    print("Cadena ingresada:", cadena)
    print("--------------------------------")
    print("Tokens encontrados:")
    for tipo, lista in tokens.items():
        if lista:
            print(f"{tipo}: {', '.join(lista)}")
            N_tokens += len(lista)
    print("--------------------------------")
    print("Cantidad de tokens encontrados:", N_tokens)

if __name__ == "__main__": 
    main()

