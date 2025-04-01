import json
from collections import Counter

def count_duplicates(json_file, key):
    # Cargar los datos del archivo JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Asegurarse de que los datos son una lista
    if not isinstance(data, list):
        raise ValueError("El JSON debe ser una lista de objetos.")
    
    # Extraer los valores del campo especificado (key)
    values = [item.get(key) for item in data if key in item]
    
    # Contar las ocurrencias de cada valor
    count = Counter(values)
    
    # Filtrar solo los valores que se repiten (v > 1)
    duplicates = {k: v for k, v in count.items() if v > 1}
    
    return duplicates

# Usar la función para encontrar duplicados en un archivo JSON
json_file = 'alumnos.json'  # Asegúrate de que el nombre de tu archivo sea correcto
key_to_check = 'dni'  # La clave que quieres verificar

duplicates = count_duplicates(json_file, key_to_check)

if duplicates:
    print("Valores repetidos:")
    for value, count in duplicates.items():
        print(f"{value}: {count} veces")
else:
    print("No hay valores repetidos.")
