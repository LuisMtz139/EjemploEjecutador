import os
import urllib.parse
import requests

class DataSender:
    def __init__(self, entries, dropdown, path, mostrar_vista_errores):
        self.entries = entries
        self.dropdown = dropdown
        self.path = path
        self.mostrar_vista_errores = mostrar_vista_errores

    def enviar_datos(self):
        escenario_id = self.entries['Escenario Id'].get().strip()
        quincena_no = self.entries['Quincena No.'].get().strip()
        registro_patronal = self.dropdown.get().strip()

        escenario_id_encoded = urllib.parse.quote(escenario_id)
        quincena_no_encoded = urllib.parse.quote(quincena_no)
        registro_patronal_encoded = urllib.parse.quote(registro_patronal)

        base_url = "http://localhost:1234/RocencranService/Generanomina/C:|Users|pssbo|Downloads|FinalServiceQRluisdesarrollo|FinalServiceQR|CNE781229BK4_TEST"
        full_url = f"{base_url}/{escenario_id_encoded}/{quincena_no_encoded}/{registro_patronal_encoded}/S"

        print("URL completa:", full_url)

        try:
            response = requests.get(full_url)
            response.raise_for_status()  # Lanza un error para respuestas no exitosas
            print("Respuesta recibida:", response.text)

            # Verificar la carpeta de erróneos después de la petición
            erroneos_dir = os.path.join(self.path, escenario_id, 'erroneos')
            if os.listdir(erroneos_dir):  # Verificar si la carpeta contiene archivos
                print("Se encontraron errores. Redireccionando a la vista de errores.")
                self.mostrar_vista_errores()
            else:
                print("No se encontraron errores.")
        except requests.RequestException as e:
            print("Error al realizar la petición:", e)
