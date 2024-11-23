import happybase
import pandas as pd
from datetime import datetime

# Bloque principal de ejecución
try:
    # 1. Establecer conexión con HBase
    connection = happybase.Connection('localhost')
    print("Conexión establecida con HBase")
    
    # 2. Crear la tabla con las familias de columnas
    table_name = 'used_cars'
    families = {
        'basic': dict(),  # información básica del coche
        'specs': dict(),  # especificaciones técnicas
        'sales': dict(),  # información de venta
        'condition': dict()  # estado del vehículo
    }

    # Eliminar la tabla si ya existe
    if table_name.encode() in connection.tables():
        print(f"Eliminando tabla existente - {table_name}")
        connection.delete_table(table_name, disable=True)
    
    # Crear nueva tabla
    connection.create_table(table_name, families)
    table = connection.table(table_name)
    print("Tabla 'used_cars' creada exitosamente")

    # 3. Cargar datos del CSV
    car_data = pd.read_csv('Car_details_v3.csv')

    # Iterar sobre el DataFrame usando el índice
    for index, row in car_data.iterrows():
        # Generar row key basado en el índice
        row_key = f'car_{index}'.encode()

        # Organizar los datos en familias de columnas
        data = {
            b'basic:name': str(row['name']).encode(),
            b'basic:year': str(row['year']).encode(),
            b'basic:transmission': str(row['transmission']).encode(),
            b'basic:fuel': str(row['fuel']).encode(),
            b'specs:engine': str(row['engine']).encode(),
            b'specs:max_power': str(row['max_power']).encode(),
            b'specs:torque': str(row['torque']).encode(),
            b'specs:seats': str(row['seats']).encode(),
            b'specs:mileage': str(row['mileage']).encode(),
            b'sales:selling_price': str(row['selling_price']).encode(),
            b'sales:seller_type': str(row['seller_type']).encode(),
            b'condition:km_driven': str(row['km_driven']).encode(),
            b'condition:owner': str(row['owner']).encode()
        }

        table.put(row_key, data)

    print("Datos cargados exitosamente")

    # 4. Consultas y Análisis de Datos
    print("\n=== Todos los coches en la base de datos (primeros 3) ===")
    count = 0
    for key, data in table.scan():
        if count < 3:  # Limitamos a 3 para el ejemplo
            print(f"\nCoche ID: {key.decode()}")
            print(f"Nombre: {data[b'basic:name'].decode()}")
            print(f"Año: {data[b'basic:year'].decode()}")
            print(f"Precio: {data[b'sales:selling_price'].decode()}")
            count += 1

    # 5. Encontrar coches por rango de precio
    print("\n=== Coches con precio menor a 50000 ===")
    for key, data in table.scan():
        if int(data[b'sales:selling_price'].decode()) < 50000:
            print(f"\nCoche ID: {key.decode()}")
            print(f"Nombre: {data[b'basic:name'].decode()}")
            print(f"Precio: {data[b'sales:selling_price'].decode()}")

    # 6. Análisis de propietarios
    print("\n=== Coches por tipo de propietario ===")
    owner_stats = {}
    for key, data in table.scan():
        owner = data[b'condition:owner'].decode()
        owner_stats[owner] = owner_stats.get(owner, 0) + 1

    for owner, count in owner_stats.items():
        print(f"{owner}: {count} coches")

    # 7. Ejemplo de actualización de precio
    car_to_update = 'car_0'
    new_price = 460000
    table.put(car_to_update.encode(), {b'sales:selling_price': str(new_price).encode()})
    print(f"\nPrecio actualizado para el coche ID: {car_to_update}")

    # 8. Ejemplo de eliminación de un coche
    car_to_delete = 'car_2'  # Cambia esto por el ID del coche que deseas eliminar
    table.delete(car_to_delete.encode())
    print(f"\nCoche ID: {car_to_delete} eliminado exitosamente.")

except Exception as e:
    print(f"Error: {str(e)}")
finally:
    # Cerrar la conexión
    connection.close()
