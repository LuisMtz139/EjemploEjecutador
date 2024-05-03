import csv
import os
import pandas as pd
import urllib.parse
import requests
import xml.etree.ElementTree as ET

class DataSender:
    def __init__(self):
        tree = ET.parse('config.xml')
        root = tree.getroot()
        self.path_from_config = root.find('RutaFinalService').text.replace('\\', '|')

    def enviar_datos(self, entries, dropdown, path, mostrar_vista_errores):
        escenario_id = entries['Escenario Id'].get().strip()
        quincena_no = entries['Quincena No.'].get().strip()
        registro_patronal = dropdown.get().strip()
        erroneos_dir = os.path.join(path, escenario_id, 'erroneos')
        
        
        
        if os.listdir(erroneos_dir):
                        print("Se encontraron erssssssrores.", erroneos_dir)
                        #imprimr el contendio de la carpeta erroneos
                        print("Contenido de la carpeta 'erroneos':", os.listdir(erroneos_dir))
                        #eliminar el contenido de la carpeta erroneos   
                        for file in os.listdir(erroneos_dir):
                            os.remove(os.path.join(erroneos_dir, file))
        else:
                        print("No se encontraron errores.")

        escenario_id_encoded = urllib.parse.quote(escenario_id)
        quincena_no_encoded = urllib.parse.quote(quincena_no)
        registro_patronal_encoded = urllib.parse.quote(registro_patronal)

        base_url = f"http://localhost:1234/RocencranService/Generanomina/{self.path_from_config}"
        full_url = f"{base_url}/{escenario_id_encoded}/{quincena_no_encoded}/{registro_patronal_encoded}/N"

        print("URL completa:", full_url)
            

        universo_path = os.path.join(path, escenario_id, 'universo')
        if os.path.exists(universo_path):
            files = os.listdir(universo_path)
            num_files = len(files)
            print("Número de archivos en la carpeta 'universo':", num_files)

            # Leer el archivo CSV
            with open('escenario_ids.csv', 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                lines = list(csv_reader)

            # Agregar el número de archivos a la última línea
            lines[-1].append(num_files)

            # Escribir las líneas modificadas de vuelta al archivo CSV
            with open('escenario_ids.csv', 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerows(lines)
        else:
            print("No se encontró la carpeta 'universo' en la ruta especificada.")

        try:
            response = requests.get(full_url)
            response.raise_for_status()
            print("Respuesta recibida:", response.text)

            erroneos_dir = os.path.join(path, escenario_id, 'erroneos')
            if os.listdir(erroneos_dir):
                print("Se encontraron errores.")
            else:
                print("No se encontraron errores.")
            universo_path = os.path.join(path, escenario_id, 'universo')
        except requests.RequestException as e:
            print("Error al realizar la petición:", e)


        universo_path = os.path.join(path, escenario_id, 'universo')
        print("Explorando la carpeta:", universo_path)

        if os.path.exists(universo_path):
            files = os.listdir(universo_path)
            print("Contenido de la carpeta 'universo':", files)
            excel_files = [file for file in files if file.endswith('.xlsx')]
            if excel_files:
                excel_path = os.path.join(universo_path, excel_files[0])

                dtype_spec = {
                    'CuentaBancaria': str,
                    'NumEmpleado': str,
                    'NumSeguridadSocial': str
                }
                df = pd.read_excel(excel_path, dtype=dtype_spec)

                for col in dtype_spec:
                    df[col] = df[col].apply(lambda x: x if pd.isna(x) else str(x))

                if "Unnamed: 0" in df.columns:
                    df = df[df["Unnamed: 0"] != "OK"]

                if "ID" in df.columns:
                    id_index = df.columns.get_loc("ID")  
                    if id_index > 0:  
                        df.drop(df.columns[id_index - 1], axis=1, inplace=True)

                print("Guardando el archivo Excel modificado...")
                df.to_excel(excel_path, index=False)
                print("Archivo guardado. Filas con 'OK' eliminadas y columna previa a 'ID' eliminada.")

                if not df.empty:
                    os.startfile(excel_path)
                    print('path', excel_path)
                    print("Archivo Excel abierto para edición.")
                    
                    erroneos_dir = os.path.join(path, escenario_id, 'erroneos')
                    if os.listdir(erroneos_dir):
                        print("Se encontraron erssssssrores.", erroneos_dir)
                        #imprimr el contendio de la carpeta erroneos
                        print("Contenido de la carpeta 'erroneos':", os.listdir(erroneos_dir))
                        #abrrir el arhcivo errortimbrado.txt
                        os.startfile(os.path.join(erroneos_dir, 'errortimbrado.txt'))
                    else:
                        print("No se encontraron errores.")
                    universo_path = os.path.join(path, escenario_id, 'universo')
                else:
                    print("No hay datos para mostrar en el archivo Excel.")
                    
                
                    
                num_rows_after_cleaning = df.shape[0]
                print("Número de filas en el archivo Excel después de eliminar 'OK' y la columna previa a 'ID':", num_rows_after_cleaning)

                # Eliminar valores previos con el mismo escenario_id del archivo de texto
                with open('num_rows_after_cleaning.txt', 'r') as file:
                    lines = file.readlines()
                
                with open('num_rows_after_cleaning.txt', 'w') as file:
                    for line in lines:
                        if not line.startswith(f"Escenario ID: {escenario_id}"):
                            file.write(line)
                    
                    # Escribir el último valor
                    file.write(f"Escenario ID: {escenario_id}\n")
                    file.write(f"Número de filas limpiadas: {num_rows_after_cleaning}\n")
                    file.write("\n")  # Agregar una línea en blanco para separar los registros

                print("Información actualizada en 'num_rows_after_cleaning.txt'.")

            else:
                print("No se encontraron archivos Excel en la carpeta 'universo'.")
        else:
            print("No se encontró la carpeta 'universo' en la ruta especificada.")

        if any(file.endswith('.txt') for file in files):
            print("Mostrar vista de errores")
            mostrar_vista_errores()
