import json

# Archivo JSON para el alumno
alumnos_FILE = 'alumnos.json'

# Función para cargar el alumno desde el archivo JSON
def cargar_alumnos():
    try:
        with open(alumnos_FILE, 'r') as file:
            print(json.load(file))
            return json.load(file)
    except FileNotFoundError:
        return {}

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
def modificar_alumno(dni, nombre, apellido, categoria, cuota_estado, dni_nuevo):
    alumnos = cargar_alumnos()  # Cargar la lista de alumnos
    alumno_encontrado = next((alumno for alumno in alumnos if alumno['dni'] == dni), None)

    if alumno_encontrado:
        # Verificar si el nuevo DNI ya existe en otro alumno
        if any(alumno['dni'] == dni_nuevo and alumno['nombre'] != nombre for alumno in alumnos):
            return False

        # Actualizar los datos del alumno
        alumno_encontrado['dni'] = dni_nuevo
        alumno_encontrado['nombre'] = nombre
        alumno_encontrado['apellido'] = apellido
        alumno_encontrado['categoria'] = categoria
        alumno_encontrado['cuota_estado'] = cuota_estado

        # Guardar los cambios
        guardar_alumno(alumnos)
        return True

    return False


# Función para agregar un nuevo alumno
def agregar_alumno(dni, nombre, apellido, categoria, cuota_estado):
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
        'cuota_estado': cuota_estado
    }
    alumnos.append(nuevo_alumno)

    # Guardar los cambios
    guardar_alumno(alumnos)
    return True


def eliminar(codigo):
    alumno = cargar_alumnos()
    if codigo in alumno:
        del alumno[codigo]
        guardar_alumno(alumno)
        return True
    else:
        return False