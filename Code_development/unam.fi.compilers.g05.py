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
#3. 

def main(): 
    cadena= cadena_input()
    #print("Cadena ingresada:", cadena)

if __name__ == "__main__": 
    main()

