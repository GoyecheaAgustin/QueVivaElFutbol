import json
from datetime import date


def guardar_venta_diaria(venta):
    # Obtener la fecha actual en formato dd/mm/yyyy
    fecha_actual = date.today().strftime("%d/%m/%Y")

    # Cargar el archivo JSON existente o crear uno nuevo si no existe
    try:
        with open("ventas_diarias.json", "r") as file:
            ventas_diarias = json.load(file)
    except FileNotFoundError:
        ventas_diarias = {}

    # Verificar si ya hay ventas registradas para la fecha actual
    if fecha_actual in ventas_diarias:
        # Agregar la venta a las ventas existentes para esta fecha
        ventas_diarias[fecha_actual].append(venta)
    else:
        # Crear una nueva lista de ventas para esta fecha
        ventas_diarias[fecha_actual] = [venta]

    # Guardar las ventas actualizadas en el archivo JSON
    with open("ventas_diarias.json", "w") as file:
        json.dump(ventas_diarias, file)



def cargar_ventas_diarias():
    with open("ventas_diarias.json", "r") as file:
        return json.load(file)

def buscar_ventas_por_fecha(fecha_busqueda):
    ventas_diarias = cargar_ventas_diarias()
    return ventas_diarias.get(fecha_busqueda, [])
