import tkinter as tk
from tkinter import Scrollbar
import os
import xml.etree.ElementTree as ET
import shutil

class TableError:
    def __init__(self, master, escenario_id):
        self.master = master
        self.escenario_id = escenario_id
        
        print(f"Escenario ID: {self.escenario_id}")
        self.master.title("Conalep-timbrado")
        self.master.state('zoomed')

        self.config_path = self.load_config_path()
        self.create_scenario_directory(self.escenario_id)
        
        # Listar los contenidos de la carpeta del escenario al iniciar la GUI
        self.list_directory_contents()

        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=1)
        
        self.inner_frame = tk.Frame(self.main_frame, bd=2, relief=tk.SOLID)
        self.inner_frame.pack(fill=tk.BOTH, expand=1, padx=20, pady=20)  

        self.new_frame = tk.Frame(self.inner_frame, bd=2, relief=tk.SOLID)
        self.new_frame.pack(fill=tk.BOTH, expand=1, padx=20, pady=(20, 70))

        self.column1 = tk.Frame(self.new_frame, bd=2, relief=tk.SOLID)
        self.column1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.column1_label = tk.Label(self.column1, text="Datos txt", font=("Helvetica", 12, "bold"))
        self.column1_label.pack(pady=10)

        self.listbox = tk.Listbox(self.column1, height=5)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.populate_listbox()  # Llama a la función para poblar la lista con los archivos
        self.listbox.bind("<<ListboxSelect>>", self.mostrar_contenido)

        self.column2 = tk.Frame(self.new_frame, bd=2, relief=tk.SOLID)
        self.column2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.column2_label = tk.Label(self.column2, text="Contenido", font=("Helvetica", 12, "bold"))
        self.column2_label.pack(pady=10)
        self.error_text = tk.Text(self.column2, wrap="word", height=10, width=50)
        self.error_text.pack(fill=tk.BOTH, expand=True)
        self.scrollbar = Scrollbar(self.column2, command=self.error_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.error_text.config(yscrollcommand=self.scrollbar.set)
        self.error_text.bind("<Key>", self.guardar_cambios)  # Asociar función a eventos de teclado

        self.column3 = tk.Frame(self.new_frame, bd=2, relief=tk.SOLID)
        self.column3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.column3_label = tk.Label(self.column3, text="Error", font=("Helvetica", 12, "bold"))
        self.column3_label.pack(pady=10)

        self.button = tk.Button(self.main_frame, text="Test", command=self.cerrar)
        self.button.place(relx=0.1, rely=0.94, anchor=tk.CENTER)
        self.button.config(width=20, height=2)

    def cerrar(self):
        self.master.destroy()

    def mostrar_contenido(self, event):
        # Obtener el nombre del archivo seleccionado en la lista
        seleccion = self.listbox.get(self.listbox.curselection())
        print(f"Archivo seleccionado: {seleccion}")
        
        # Construir la ruta completa del archivo universo_incidencias
        archivo_seleccionado_path = os.path.join(self.config_path, self.escenario_id, 'universo_incidencias', seleccion)
        
        # Construir la ruta completa del archivo errortimbrado.txt
        error_file_path = os.path.join(self.config_path, self.escenario_id, 'erroneos', 'errortimbrado.txt')

        try:
            # Leer el archivo errortimbrado.txt y buscar la línea correspondiente al archivo seleccionado
            with open(error_file_path, 'r') as file:
                for line in file:
                    parts = line.split('|')
                    if len(parts) > 4 and os.path.basename(parts[4].strip()) == seleccion:
                        # Se encontró la línea correspondiente al archivo seleccionado en errortimbrado.txt
                        print(line)
                        break
                else:
                    # Si no se encontró ninguna línea correspondiente, mostrar un mensaje
                    print(f"No se encontró información para el archivo '{seleccion}' en errortimbrado.txt")

        except FileNotFoundError:
            # Manejar la excepción si el archivo errortimbrado.txt no se encuentra
            print("El archivo errortimbrado.txt no se encontró en la carpeta especificada.")

        except Exception as e:
            # Manejar cualquier otra excepción que pueda ocurrir al intentar leer el archivo
            print(f"Ocurrió un error al intentar leer el archivo errortimbrado.txt: {e}")

        try:
            # Leer el archivo universo_incidencias y mostrar su contenido
            with open(archivo_seleccionado_path, 'r') as file:
                contenido = file.read()
                self.error_text.delete(1.0, tk.END)
                self.error_text.insert(tk.END, f"Contenido del archivo '{seleccion}':\n\n{contenido}")

        except FileNotFoundError:
            # Manejar la excepción si el archivo seleccionado no se encuentra
            print(f"El archivo '{seleccion}' no se encontró en la carpeta especificada.")
            # Limpiar el widget de texto en caso de archivo no encontrado
            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(tk.END, f"El archivo '{seleccion}' no se encontró.")

        except Exception as e:
            # Manejar cualquier otra excepción que pueda ocurrir al intentar leer el archivo
            print(f"Ocurrió un error al intentar leer el archivo '{seleccion}': {e}")
            # Limpiar el widget de texto en caso de error
            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(tk.END, f"Error al leer el archivo '{seleccion}': {str(e)}")


    def guardar_cambios(self, event):
        seleccion = self.listbox.get(self.listbox.curselection())
        error_file_path = os.path.join(self.config_path, self.escenario_id, 'universo_incidencias', seleccion)
        try:
            contenido = self.error_text.get(1.0, tk.END)
            with open(error_file_path, 'w') as file:
                file.write(contenido)
        except Exception as e:
            print(f"Ocurrió un error al intentar guardar los cambios en el archivo {seleccion}: {e}")

    def load_config_path(self):
        tree = ET.parse('config.xml')
        root = tree.getroot()
        return root.find('RutaCarpetas').text

    def create_scenario_directory(self, escenario_id):
        base_dir = os.path.join(self.config_path, escenario_id)
        os.makedirs(base_dir, exist_ok=True)
        os.makedirs(os.path.join(base_dir, 'universo_incidencias'), exist_ok=True)

    def list_directory_contents(self):
        base_dir = os.path.join(self.config_path, self.escenario_id)
        erroneos_folder_exists = False  # Flag para verificar si la carpeta erroneos existe

        if os.path.exists(base_dir):
            print(f"Listando contenidos de la carpeta: {base_dir}")
            with os.scandir(base_dir) as entries:
                for entry in entries:
                    print(entry.name)
                    if entry.is_dir() and entry.name == 'erroneos':
                        erroneos_folder_exists = True  # Se encuentra la carpeta erroneos

            if erroneos_folder_exists:
                self.handle_errors_and_move_files()  # Llamar al método para manejar errores y mover archivos
        else:
            print("La carpeta del escenario especificado no existe.")

    def handle_errors_and_move_files(self):
        error_file_path = os.path.join(self.config_path, self.escenario_id, 'erroneos', 'errortimbrado.txt')
        target_directory = os.path.join(self.config_path, self.escenario_id, 'universo_incidencias')

        if not os.path.exists(target_directory):
            os.makedirs(target_directory, exist_ok=True)

        try:
            # Leer y mostrar contenido de errortimbrado.txt
            with open(error_file_path, 'r') as file:
                contenido_errortimbrado = file.read()
                print(f"Contenido de errortimbrado.txt:\n\n{contenido_errortimbrado}")

            # Mover archivos de la carpeta erroneos a universo_incidencias
            with open(error_file_path, 'r') as file:
                for line in file:
                    parts = line.split('|')
                    if len(parts) > 4:
                        file_path = parts[4].replace('/', '\\').strip()  # Aseguramos el formato correcto
                        destination_path = os.path.join(target_directory, os.path.basename(file_path))
                        # Verificamos que el archivo a mover realmente existe
                        if os.path.exists(file_path):
                            shutil.move(file_path, destination_path)  # Mueve el archivo a la carpeta destino
                            print(f"Archivo movido: {file_path} -> {destination_path}")
                        else:
                            print(f"El archivo no existe: {file_path}")
        except FileNotFoundError:
            print("El archivo errortimbrado.txt no existe en la carpeta especificada.")
        except Exception as e:
            print(f"Ocurrió un error al intentar mover los archivos: {e}")

        # Eliminar la carpeta erroneos después de mover los archivos
        # shutil.rmtree(os.path.join(self.config_path, self.escenario_id, 'erroneos'))
        # print("Carpeta 'erroneos' eliminada.")

    def populate_listbox(self):
        incidencias_dir = os.path.join(self.config_path, self.escenario_id, 'universo_incidencias')
        if os.path.exists(incidencias_dir):
            files = os.listdir(incidencias_dir)
            for file in files:
                if os.path.isfile(os.path.join(incidencias_dir, file)):
                    self.listbox.insert(tk.END, file)

def main():
    root = tk.Tk()
    app = TableError(root )
    root.mainloop()

if __name__ == "__main__":
    main()
