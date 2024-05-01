import os
import urllib.parse
import requests

class DataSender:
    def enviar_datos(self, entries, dropdown, path, mostrar_vista_errores):
        escenario_id = entries['Escenario Id'].get().strip()
        quincena_no = entries['Quincena No.'].get().strip()
        registro_patronal = dropdown.get().strip()

        escenario_id_encoded = urllib.parse.quote(escenario_id)
        quincena_no_encoded = urllib.parse.quote(quincena_no)
        registro_patronal_encoded = urllib.parse.quote(registro_patronal)

        base_url = "http://localhost:1234/RocencranService/Generanomina/C:|Users|pssbo|Downloads|FinalServiceQRluisdesarrollo|FinalServiceQR|CNE781229BK4_TEST"
        full_url = f"{base_url}/{escenario_id_encoded}/{quincena_no_encoded}/{registro_patronal_encoded}/S"

        print("URL completa:", full_url)

        try:
            response = requests.get(full_url)
            response.raise_for_status()
            print("Respuesta recibida:", response.text)

            erroneos_dir = os.path.join(path, escenario_id, 'erroneos')
            if os.listdir(erroneos_dir):
                print("Se encontraron errores. Redireccionando a la vista de errores.")
                mostrar_vista_errores()
            else:
                print("No se encontraron errores.")
        except requests.RequestException as e:
            print("Error al realizar la petición:", e)
