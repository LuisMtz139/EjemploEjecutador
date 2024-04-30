import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import Scrollbar
import os
import xml.etree.ElementTree as ET

class TableError:
    def __init__(self, master, escenario_id, quincena_no, registro_patronal):
        self.master = master
        self.escenario_id = escenario_id
        self.quincena_no = quincena_no
        self.registro_patronal = registro_patronal
        
        self.files_edited = {}  # Diccionario para rastrear qué archivos han sido editados
        
        print('ecenario id', escenario_id)
        print('numero de quincena ', quincena_no),
        print('registro patronal', registro_patronal)
        
        print(f"Escenario ID: {self.escenario_id}")
        self.master.title("Conalep-timbrado")
        self.master.state('zoomed')

        self.config_path = self.load_config_path()
        self.create_scenario_directory(self.escenario_id)
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
        self.populate_listbox()
        self.listbox.bind("<<ListboxSelect>>", self.mostrar_contenido)

        # Separator between column 1 and column 2
        separator1 = ttk.Separator(self.new_frame, orient='vertical')
        separator1.pack(side=tk.LEFT, fill='y', padx=5)

        self.column2 = tk.Frame(self.new_frame, bd=2, relief=tk.SOLID)
        self.column2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.column2_label = tk.Label(self.column2, text="Contenido", font=("Helvetica", 12, "bold"))
        self.column2_label.pack(pady=10)
        self.error_text = tk.Text(self.column2, wrap="word", height=10, width=50)
        self.error_text.pack(fill=tk.BOTH, expand=True)
        self.scrollbar = Scrollbar(self.column2, command=self.error_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.error_text.config(yscrollcommand=self.scrollbar.set)
        self.error_text.bind("<Key>", self.guardar_cambios)

        # Separator between column 2 and column 3
        separator2 = ttk.Separator(self.new_frame, orient='vertical')
        separator2.pack(side=tk.LEFT, fill='y', padx=5)

        # Increased the width of column3 to 400
        self.column3 = tk.Frame(self.new_frame, bd=4, relief=tk.SOLID, width=400)
        self.column3.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self.column3.pack_propagate(False)  # Prevent resizing based on content
        self.error_title_label = tk.Label(self.column3, text="Error", font=("Helvetica", 12, "bold"))
        self.error_title_label.pack(pady=(10, 0))

        # Separator between title "Error" and the content in column 3
        separator3 = ttk.Separator(self.column3, orient='horizontal')
        separator3.pack(fill='x', padx=5, pady=5)

        self.escenario_id_label = tk.Label(self.column3, font=("Helvetica", 10), wraplength=380, justify=tk.LEFT)
        self.escenario_id_label.pack(pady=(0, 10))
        
        self.button = tk.Button(self.main_frame, text="Test", command=self.execute_test, state=tk.DISABLED)
        self.button.place(relx=0.1, rely=0.94, anchor=tk.CENTER)
        self.button.config(width=20, height=2)
    
    def cerrar(self):
        self.master.destroy()

    def mostrar_contenido(self, event):
        # Verificar si hay una selección en la Listbox
        if self.listbox.curselection():
            seleccion = self.listbox.get(self.listbox.curselection())
            print(f"Archivo seleccionado: {seleccion}")
            archivo_seleccionado_path = os.path.join(self.config_path, self.escenario_id, 'universo', seleccion)
            error_file_path = os.path.join(self.config_path, self.escenario_id, 'erroneos', 'errortimbrado.txt')
            error_line = "No se encontró información para el archivo"  # Mensaje predeterminado si no se encuentra la línea
            try:
                with open(error_file_path, 'r') as file:
                    for line in file:
                        parts = line.split('|')
                        if len(parts) > 4 and os.path.basename(parts[4].strip()) == seleccion:
                            error_line = f"Error identificado: {line.strip()}"  # Actualizar el mensaje con la línea de error
                            break
                    else:
                        error_line = f"No se encontró información para el archivo '{seleccion}' en errortimbrado.txt"
            except FileNotFoundError:
                error_line = "El archivo errortimbrado.txt no se encontró en la carpeta especificada."
            except Exception as e:
                error_line = f"Ocurrió un error al intentar leer el archivo errortimbrado.txt: {e}"

            self.escenario_id_label.config(text=error_line)

            try:
                with open(archivo_seleccionado_path, 'r') as file:
                    contenido = file.read()
                    self.error_text.delete(1.0, tk.END)
                    self.error_text.insert(tk.END, f"Contenido del archivo '{seleccion}':\n\n{contenido}")
            except FileNotFoundError:
                print(f"El archivo '{seleccion}' no se encontró en la carpeta especificada.")
                self.error_text.delete(1.0, tk.END)
                self.error_text.insert(tk.END, f"El archivo '{seleccion}' no se encontró.")
            except Exception as e:
                print(f"Ocurrió un error al intentar leer el archivo '{seleccion}': {e}")
                self.error_text.delete(1.0, tk.END)
                self.error_text.insert(tk.END, f"Error al leer el archivo '{seleccion}': {str(e)}")
        else:
            print("No hay selección en la lista")
            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(tk.END, "No hay archivo seleccionado.")


    def guardar_cambios(self, event):
        if self.listbox.curselection():  # Verifica si hay una selección
            seleccion = self.listbox.get(self.listbox.curselection())
            self.files_edited[seleccion] = True
            if all(self.files_edited.values()):
                self.button.config(state=tk.NORMAL)
            
            try:
                contenido = self.error_text.get(1.0, tk.END)
                with open(seleccion, 'w') as file:
                    file.write(contenido)
            except Exception as e:
                print(f"Ocurrió un error al intentar guardar los cambios en el archivo {seleccion}: {e}")
        else:
            print("No hay archivo seleccionado para guardar cambios")

            
    def populate_listbox(self):
        universo_dir = os.path.join(self.config_path, self.escenario_id, 'universo')
        if os.path.exists(universo_dir):
            files = os.listdir(universo_dir)
            for file in files:
                if os.path.isfile(os.path.join(universo_dir, file)):
                    self.listbox.insert(tk.END, file)
                    self.files_edited[file] = False  
                    
                    
    def load_config_path(self):
        tree = ET.parse('config.xml')
        root = tree.getroot()
        return root.find('RutaCarpetas').text

    def create_scenario_directory(self, escenario_id):
        base_dir = os.path.join(self.config_path, escenario_id)
        os.makedirs(base_dir, exist_ok=True)
        # No es necesario crear la carpeta 'universo' aquí
        
    def execute_test(self):
        # Navegar a la ruta del archivo de configuración
        os.chdir(self.config_path)  # Cambiar el directorio de trabajo al directorio de configuración
        print("Directorio actual:", os.getcwd())  # Mostrar el directorio actual para verificar
        
        # Construir la ruta al escenario específico
        scenario_path = os.path.join(self.config_path, self.escenario_id)
        
        # Verificar si el directorio del escenario existe y listar su contenido
        if os.path.exists(scenario_path):
            print("Contenido de la carpeta del escenario:", self.escenario_id, scenario_path)
            with os.scandir(scenario_path) as entries:
                for entry in entries:
                    print(entry.name)  # Mostrar cada archivo o carpeta en el directorio del escenario
        else:
            print(f"La carpeta '{scenario_path}' no existe.")

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

    def populate_listbox(self):
        universo_dir = os.path.join(self.config_path, self.escenario_id, 'universo')
        if os.path.exists(universo_dir):
            files = os.listdir(universo_dir)
            for file in files:
                if os.path.isfile(os.path.join(universo_dir, file)):
                    self.listbox.insert(tk.END, file)

def main():
    root = tk.Tk()
    app = TableError(root )
    root.mainloop()

if __name__ == "__main__":
    main()
