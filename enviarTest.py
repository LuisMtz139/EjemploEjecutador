import os
import pandas as pd
import urllib.parse
import requests
import xml.etree.ElementTree as ET

class DataSender:
    def __init__(self):
        # Cargar el archivo de configuración
        tree = ET.parse('config.xml')
        root = tree.getroot()
        # Extraer la ruta desde el archivo de configuración
        self.path_from_config = root.find('RutaFinalService').text.replace('\\', '|')

    def enviar_datos(self, entries, dropdown, path, mostrar_vista_errores):
        escenario_id = entries['Escenario Id'].get().strip()
        quincena_no = entries['Quincena No.'].get().strip()
        registro_patronal = dropdown.get().strip()

        escenario_id_encoded = urllib.parse.quote(escenario_id)
        quincena_no_encoded = urllib.parse.quote(quincena_no)
        registro_patronal_encoded = urllib.parse.quote(registro_patronal)

        # Construir la base URL usando la ruta obtenida del archivo XML
        base_url = f"http://localhost:1234/RocencranService/Generanomina/{self.path_from_config}"
        full_url = f"{base_url}/{escenario_id_encoded}/{quincena_no_encoded}/{registro_patronal_encoded}/N"

        print("URL completa:", full_url)

        try:
            response = requests.get(full_url)
            response.raise_for_status()
            print("Respuesta recibida:", response.text)

            erroneos_dir = os.path.join(path, escenario_id, 'erroneos')
            if os.listdir(erroneos_dir):
                print("Se encontraron errores.")
            else:
                print("No se encontraron errores.")
        except requests.RequestException as e:
            print("Error al realizar la petición:", e)


        # Sección para explorar la carpeta 'universo' y mostrar el contenido de un archivo Excel
        universo_path = os.path.join(path, escenario_id, 'universo')
        print("Explorando la carpeta:", universo_path)

        if os.path.exists(universo_path):
            files = os.listdir(universo_path)
            print("Contenido de la carpeta 'universo':", files)
            excel_files = [file for file in files if file.endswith('.xlsx')]
            if excel_files:
                excel_path = os.path.join(universo_path, excel_files[0])

                # Especificar el formato de las columnas al leer el archivo para evitar la notación científica
                dtype_spec = {
                    'CuentaBancaria': str,
                    'NumEmpleado': str,
                    'NumSeguridadSocial': str
                }
                df = pd.read_excel(excel_path, dtype=dtype_spec)

                # Verificar y convertir columnas al formato deseado
                for col in dtype_spec:
                    df[col] = df[col].apply(lambda x: x if pd.isna(x) else str(x))

                # Filtrar las filas donde 'Unnamed: 0' no contiene 'OK'
                if "Unnamed: 0" in df.columns:
                    df = df[df["Unnamed: 0"] != "OK"]

                # Encontrar el índice de la columna 'ID' y eliminar la columna anterior si existe
                if "ID" in df.columns:
                    id_index = df.columns.get_loc("ID")  # Obtener el índice de la columna 'ID'
                    if id_index > 0:  # Asegurarse de que 'ID' no es la primera columna
                        # Eliminar la columna anterior a 'ID'
                        df.drop(df.columns[id_index - 1], axis=1, inplace=True)

                print("Guardando el archivo Excel modificado...")
                # Guardar el DataFrame modificado en el mismo archivo sin modificar nombres de columna ni agregar índice
                df.to_excel(excel_path, index=False)
                print("Archivo guardado. Filas con 'OK' eliminadas y columna previa a 'ID' eliminada.")

                # Eliminar los archivos dentro de la carpeta 'erroneos'
                for file in os.listdir(erroneos_dir):
                    file_path = os.path.join(erroneos_dir, file)
                    os.remove(file_path)
                print("Contenido de la carpeta 'erroneos' eliminado.")

                # Verificar si el DataFrame aún contiene filas y abrir el archivo Excel
                if not df.empty:
                    os.startfile(excel_path)
                    print("Archivo Excel abierto para edición.")
                else:
                    print("No hay datos para mostrar en el archivo Excel.")

            else:
                print("No se encontraron archivos Excel en la carpeta 'universo'.")
        else:
            print("No se encontró la carpeta 'universo' en la ruta especificada.")
