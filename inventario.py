import json

# Archivo JSON para el inventario
INVENTARIO_FILE = 'inventario.json'

# Función para cargar el inventario desde el archivo JSON
def cargar_inventario():
    try:
        with open(INVENTARIO_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Función para guardar el inventario en el archivo JSON
def guardar_inventario(inventario):
    with open(INVENTARIO_FILE, 'w') as file:
        json.dump(inventario, file, indent=4)

# Función para escanear un producto
def escanear_producto(codigo_de_barras):
    inventario = cargar_inventario()
    return inventario.get(codigo_de_barras, None)

# Función para modificar un producto
def modificar_producto(codigo, nombre, precio, cantidad, codigonuevo):
    inventario = cargar_inventario()
    if codigo in inventario:
        if codigonuevo in inventario:
            if inventario[codigonuevo]["nombre"]!=nombre:
                return False
        del inventario[codigo]
        inventario[codigonuevo] = {'nombre': nombre, 'precio': precio, 'cantidad': cantidad}
        guardar_inventario(inventario)
        return True
    return False


# Función para agregar un nuevo producto
def agregar_producto(codigo_de_barras, nombre, precio, cantidad):
    inventario = cargar_inventario()
    if codigo_de_barras in inventario:
        return False
    inventario[codigo_de_barras] = {'nombre': nombre, 'precio': precio, 'cantidad': cantidad}
    guardar_inventario(inventario)
    return True


def eliminar(codigo):
    inventario = cargar_inventario()
    if codigo in inventario:
        del inventario[codigo]
        guardar_inventario(inventario)
        return True
    else:
        return False