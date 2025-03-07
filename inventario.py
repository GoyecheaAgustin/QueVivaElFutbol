import json
import os

# Archivo JSON para el alumno
alumnos_FILE = 'alumnos.json'

def cargar_alumnos():
    if not os.path.exists(alumnos_FILE):  # Si el archivo no existe, crea uno vacío
        return []
    
    with open(alumnos_FILE, 'r') as file:
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
        
# Función para guardar el alumno en el archivo JSON
def guardar_alumno(alumno):
    with open(alumnos_FILE, 'w') as file:
        print("holaaaaa")
        json.dump(alumno, file, indent=4)

# Función para escanear un alumno
def escanear_alumno(codigo_de_barras):
    alumno = cargar_alumnos()
    return alumno.get(codigo_de_barras, None)


# Función para modificar un alumno
def modificar_alumno(dni, nombre, apellido, categoria, cuota_estado, dni_nuevo, email):
    alumnos = cargar_alumnos()  # Cargar la lista de alumnos
    alumno_encontrado = next((alumno for alumno in alumnos if alumno['dni'] == dni), None)

    if alumno_encontrado:
        # Actualizar los datos del alumno
        alumno_encontrado.update({
            'dni': dni_nuevo,
            'nombre': nombre,
            'apellido': apellido,
            'categoria': categoria,
            'cuota_estado': cuota_estado,
            'email' : email
        })

        # Guardar los cambios
        guardar_alumno(alumnos)
        return True

    return False





# Función para agregar un nuevo alumno
def agregar_alumno(dni, nombre, apellido, categoria, cuota_estado, email):
    alumnos = cargar_alumnos()  # Cargar la lista de alumnos

    # Verificar si el DNI ya existe
    if any(alumno['dni'] == dni for alumno in alumnos):
        return False

    # Agregar el nuevo alumno
    nuevo_alumno = {
        'dni': dni,
        'nombre': nombre,
        'apellido': apellido,
        'categoria': categoria,
        'cuota_estado': cuota_estado,
        'email': email
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

