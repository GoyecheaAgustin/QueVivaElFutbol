import json
import os

# Archivo JSON para el alumno
alumnos_FILE = 'alumnos.json'

def cargar_alumnos():
    if not os.path.exists(alumnos_FILE):  # Si el archivo no existe, crea uno vacío
        return []
    
    with open(alumnos_FILE, 'r', encoding='utf-8') as file:
        contenido = file.read().strip()  # Leer y eliminar espacios en blanco
        if not contenido:  # Si está vacío, devuelve una lista vacía
            return []
        
        try:
            alumnos = json.loads(contenido)
            
            
            if isinstance(alumnos, list):  # Asegurar que es una lista
                return alumnos
            else:
                print("Error: El archivo JSON no contiene una lista, se reiniciará.")
                return []
        except json.JSONDecodeError:
            print("Error: El archivo JSON está corrupto. Se reiniciará.")
            return [] 
        
def guardar_alumno(alumnos):
    """Sobrescribe el archivo con la lista actualizada de alumnos"""
    with open(alumnos_FILE, 'w', encoding='utf-8') as file:
        json.dump(alumnos, file, indent=4, ensure_ascii=False)
    print("Datos guardados correctamente.")

# Función para escanear un alumno
def escanear_alumno(codigo_de_barras):
    alumno = cargar_alumnos()
    return alumno.get(codigo_de_barras, None)


# Función para modificar un alumno
def modificar_alumno(dni, nombre, apellido, categoria, cuota_estado, dni_nuevo, email, ficha, telefono, tutor):
    alumnos = cargar_alumnos()  # Cargar la lista de alumnos
    alumno_encontrado = next((alumno for alumno in alumnos if alumno['dni'] == dni), None)

    if alumno_encontrado:
        # Actualizar datos del alumno
        alumno_encontrado.update({
            'dni': dni_nuevo.upper(),
            'nombre': nombre.upper(),
            'apellido': apellido.upper(),
            'categoria': categoria,
            'cuota_estado': cuota_estado.upper(),
            'tutor': tutor.upper(),
            'email': email.upper(),
            'ficha': ficha.upper(),
            'telefono': telefono
        })

        # Guardar la lista completa sin duplicar
        guardar_alumno(alumnos)
        return True

    return False






# Función para agregar un nuevo alumno
def agregar_alumno(dni, nombre, apellido, categoria, cuota_estado, email,tutor,ficha,telefono):
    alumnos = cargar_alumnos()  # Cargar la lista de alumnos

    # Verificar si el DNI ya existe
    if any(alumno['dni'] == dni for alumno in alumnos):
        return False

    # Agregar el nuevo alumno
    nuevo_alumno = {
        'Tutor': tutor.upper(),
        'dni': dni.upper(),
        'nombre': nombre.upper(),
        'apellido': apellido.upper(),
        'categoria': categoria,  # Si es número, convertirlo a string
        'cuota_estado': cuota_estado.upper(),
        'email': email.upper(),
        'telefono': telefono,
        'ficha': ficha.upper()
    }
    alumnos.append(nuevo_alumno)

    # Guardar los cambios
    guardar_alumno(alumnos)
    return True

def eliminar(dni):
    alumnos = cargar_alumnos()  # Cargar la lista de alumnos

    # Buscar el alumno con el DNI especificado
    alumno_encontrado = None
    for alumno in alumnos:
        if alumno['dni'] == dni:
            alumno_encontrado = alumno
            break

    if alumno_encontrado:
        # Eliminar el alumno de la lista
        alumnos.remove(alumno_encontrado)
        guardar_alumno(alumnos)  # Guardar los cambios en el archivo
        return True
    else:
        # Si no se encontró el alumno, retornar False
        return False



# def convertir_mayusculas(dato):
#     if isinstance(dato, dict):  
#         return {k: convertir_mayusculas(v) for k, v in dato.items()}
#     elif isinstance(dato, list):  
#         return [convertir_mayusculas(item) for item in dato]
#     elif isinstance(dato, str):  
#         return dato.upper()
#     else:  
#         return dato

# # Leer el archivo JSON
# with open(alumnos_FILE, 'r', encoding='utf-8') as file:
#     contenido = file.read().strip()  

# # Verificar si el archivo no está vacío
# if contenido:
#     alumnos = json.loads(contenido)  # Convertir el texto JSON en un diccionario
#     alumnos_mayus = convertir_mayusculas(alumnos)  # Convertir a mayúsculas

#     # Guardar el JSON con los valores en mayúsculas
#     with open(alumnos_FILE, 'w', encoding='utf-8') as file:
#         json.dump(alumnos_mayus, file, indent=4, ensure_ascii=False)

#     print("JSON convertido a mayúsculas y guardado correctamente.")
# else:
#     print("El archivo está vacío.")