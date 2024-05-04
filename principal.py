from datetime import datetime
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
import os
import xml.etree.ElementTree as ET
import subprocess
import csv
from enviarCorreo import EnviarCorreo
from enviarTest import DataSender
from tableError import TableError
import re

class VistaPrincipal:
    
    def validar_quincena(self, input):
        if input.isdigit() or input == "":
            return True
        return False

    def validar_campos(self, *args):
        if self.entries['Quincena No.'].get() and self.dropdown.get():
            self.button.config(state=tk.NORMAL)
        else:
            self.button.config(state=tk.DISABLED)
    def __init__(self, master):
        self.master = master
        self.master.title("Conalep-timbrado")
        self.num_filas = 0
        
        tree = ET.parse('config.xml')
        root = tree.getroot()
        self.path = root.find('RutaCarpetas').text
        
        vcmd = self.master.register(self.validar_quincena) 
        
        self.master.state('zoomed')
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=1)
        
        self.inner_frame = tk.Frame(self.main_frame, bd=2, relief=tk.SOLID)
        self.inner_frame.pack(fill=tk.BOTH, expand=1, padx=20, pady=20) 

        inputs = ['Escenario Id', 'Quincena No.']
        self.entries = {} 
        self.num_rows_cleaned = {}
        
        for i, input_text in enumerate(inputs):
            tk.Label(self.inner_frame, text=input_text, font=("Arial", 15)).grid(row=0, column=i, padx=10)
            if input_text == 'Quincena No.':
                self.quincena_var = StringVar()
                self.quincena_var.trace('w', self.validar_campos)
                entry = tk.Entry(self.inner_frame, textvariable=self.quincena_var, validate="key", validatecommand=(vcmd, '%P'),
                                width=20, bg='light yellow', font=("Arial", 15), justify='center')
            else:
                entry = tk.Entry(self.inner_frame, width=20, bg='light yellow', font=("Arial", 15), justify='center')
            entry.grid(row=1, column=i, padx=45)
            self.entries[input_text] = entry
            
        tk.Label(self.inner_frame, text="Registro Patronal", font=("Arial", 15)).grid(row=0, column=len(inputs), padx=20, sticky=tk.W)
        
        options = ['ORDINARIA IMSSS', 'ORDINARIA ISSSTE', 'EXTRAORDINARIA IMSSS', 'EXTRAORDINARIA ISSSTE']
        self.dropdown = ttk.Combobox(self.inner_frame, values=options, font=("Arial", 15), state="readonly", style="Custom.TCombobox", width=30)
        self.dropdown.grid(row=1, column=len(inputs), padx=20, sticky=tk.W)

        self.inner_frame.style = ttk.Style()
        self.inner_frame.style.theme_use("default")
        self.inner_frame.style.configure("Custom.TCombobox", selectbackground=self.inner_frame.cget("background"), selectforeground="black", anchor="center", background="lightyellow") 

        self.inner_frame.style.configure("Custom.TCombobox.Listbox", background="lightyellow")
        button = tk.Button(self.inner_frame, text='Nuevo', font=("Arial", 13), bg='light yellow', command=self.resetear_campos)
        button.grid(row=1, column=len(inputs), padx=10, sticky=tk.E)

        self.inner_frame.grid_columnconfigure(len(inputs), weight=1)
        self.inner_frame.grid_columnconfigure(len(inputs)+1, minsize=90)

        button2 = tk.Button(self.inner_frame, text='Crear escenario', font=("Arial", 13), bg='light yellow', command=self.crear_escenario)
        button2.grid(row=1, column=len(inputs)+1, padx=10, sticky=tk.E)
        
        self.table = ttk.Treeview(self.inner_frame)
        self.table['columns'] = ('#1', '#2', '#3', '#4')
        self.table.column('#0', width=0, stretch=tk.NO)
        self.table.column('#1', width=150, stretch=tk.YES, anchor='center')
        self.table.column('#2', width=150, stretch=tk.YES, anchor='center')
        self.table.column('#3', width=150, stretch=tk.YES, anchor='center')
        self.table.column('#4', width=150, stretch=tk.YES)

        self.table.heading('#1', text='ESCENARIO ID', anchor='center')
        self.table.heading('#2', text='QUINCENA NO.', anchor='center')
        self.table.heading('#3', text='TIPONOMINA', anchor='center')
        self.table.heading('#4', text='POR_TIMBRAR')
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10))
        self.table.place(relx=0.5, rely=0.50, relwidth=0.99,relheight=0.7, anchor=tk.CENTER) 

        self.cargar_datos_escenario()
        self.configurar_envio_datos()
        self.configure_row_colors()

        self.num_rows_cleaned = {}

    def configurar_envio_datos(self):
        self.button = tk.Button(self.main_frame, text="Timbrado",
                                command=self.iniciar_proceso_de_timbrado)
        self.button.place(relx=0.1, rely=0.9, anchor=tk.CENTER)
        self.button.config(width=25, height=2, font=("Arial", 13))
        self.button.config(state=tk.DISABLED)
    
        # Agregar un observador al estado del botón
        self.button_state = tk.StringVar()
        self.button_state.trace('w', self.on_button_state_change)
        self.button_state.set(self.button['state'])
    
        self.other_button = tk.Button(self.main_frame, text="Otro Botón",
                                      command=lambda: self.mandar_correo())
        self.other_button.place(relx=0.3, rely=0.9, anchor=tk.E)  # Ajusta 'relx' a 1.0 y 'anchor' a tk.E (este)
        self.other_button.config(width=25, height=2, font=("Arial", 13))
    

    
    def mandar_correo(self):
    
        try:
            escenario_id = None
            with open("escenario_ids.csv", "r", newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row: 
                        escenario_id = row[0]  # Save the last escenario_id
    
            if escenario_id is not None:
                full_path = os.path.join(self.path, escenario_id, 'timbrado')
                #print(full_path)
    
                # # Print the contents of the directory
                # print("Contents of the directory:")
                # for filename in os.listdir(full_path):
                #     print(filename)
    
                # Copy procesados.txt to procesados2.txt
                shutil.copy(os.path.join(full_path, 'procesados.txt'), os.path.join(full_path, 'procesados2.txt'))
                correo = EnviarCorreo()
                correo.otro(escenario_id)
    
                # # Read and print the contents of procesados2.txt
                # with open(os.path.join(full_path, 'procesados2.txt'), 'r') as file:
                #     print(file.read())
            else:
                print("No escenario_id found.")
        except FileNotFoundError:
            print("El archivo no existe.")
        
        

    def iniciar_proceso_de_timbrado(self):
        data_sender = DataSender()
        data_sender.enviar_datos(self.entries, self.dropdown, self.path, self.mostrar_vista_errores)
        self.cargar_datos_escenario()

    def on_button_state_change(self, *args):
        if self.button_state.get() == 'normal':
            self.cargar_datos_escenario()

    def obtener_num_filas_limpiadas(self, escenario_id):
        self.filas_limpiadas = {}  # initialize the dictionary
        try:
            with open('num_rows_after_cleaning.txt', 'r') as file:
                for line in file:
                    if line.startswith(f"Escenario ID: {escenario_id}"):
                        self.num_filas = int(line.split(":")[-1].strip())
                        self.filas_limpiadas[escenario_id] = self.num_filas  # store the number of cleaned rows in the dictionary
                        #print(f"Escenario ID: {escenario_id}, Número de filas limpiadas: {self.num_filas}")
                        return self.num_filas
        except FileNotFoundError:
            print("El archivo num_rows_after_cleaning.txt no se encontró.")
        except ValueError:
            print("Error al leer el número de filas limpiadas para el Escenario ID:", escenario_id)
        return 0
    def check_and_refresh_table(self):
        rows = self.table.get_children()
        if not rows:
            return
        last_row = rows[-1]
        por_timbrar_value = self.table.item(last_row, 'values')[3]
        if por_timbrar_value == '0':
            self.cargar_datos_escenario()
        
    def cargar_datos_escenario(self):
        for row in self.table.get_children():
            self.table.delete(row)

        try:
            with open("escenario_ids.csv", "r", newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row: 
                        num_filas = ''  # Inicializar num_filas en cada iteración del bucle
                        escenario_id = row[0]
                        quincena_no = row[2] if len(row) > 2 else ''
                        registro_patronal = row[3] if len(row) > 3 else ''
                        status = row[4] if len(row) > 4 else ''
                        # Mandar a llamar a comparar_escenario_ids
                        comparar = self.comparar_escenario_ids()
                        #print('comparar', comparar)  
                        # Si el escenario_id está en comparar, obtener su num_filas
                        if escenario_id in comparar:
                            num_filas = comparar[escenario_id]
                            #print('escenario_id_comparar', escenario_id)
                            #print('num_filas', num_filas)
                        if not num_filas:  # Si num_filas está vacío
                            #print('', status)
                            num_filas = status
                        else:  # Si num_filas no está vacío
                            print( num_filas)

                        # Insertar en la tabla
                        self.table.insert('', 'end', values=(escenario_id, quincena_no, registro_patronal, num_filas))
                    
            for row in self.table.get_children():
                values = self.table.item(row, 'values')
                #print("Datos en la tabla:", values)
        except FileNotFoundError:
            print("El archivo no existe, se creará al guardar un nuevo escenario.")

    def obtener_num_rows(self):
        print('obtner valores txt')
        try:
            with open('num_rows_after_cleaning.txt', 'r') as file:
                for line in file:
                    if line.startswith("Escenario ID:"):
                        escenario_id = line.split(":")[1].strip()
                        print(escenario_id)
        except FileNotFoundError:
            pass
        return 0
    
    def leer_primero_valor_escenario_ids(self):
        print('archivo csv')
        try:
            with open("escenario_ids.csv", "r", newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row: 
                        primer_valor = row[0]
                        print(primer_valor)
        except FileNotFoundError:
            print("El archivo no existe.")
            
    def comparar_escenario_ids(self):
            #print("Comparando valores del Escenario ID entre el archivo de texto y el archivo CSV...")
            
            valores_texto = {}  # Almacenar los valores del archivo de texto y el número de filas limpiadas
            valores_csv = set()  # Almacenar los valores del archivo CSV
            
            #print("Obteniendo valores del archivo de texto...")
            try:
                with open('num_rows_after_cleaning.txt', 'r') as file:
                    for line in file:
                        if line.startswith("Escenario ID:"):
                            escenario_id = line.split(":")[1].strip()
                            num = next(file).split(":")[1].strip()  # Obtener el número de filas limpiadas de la siguiente línea
                            valores_texto[escenario_id] = num
                            #print(f"Escenario ID del archivo de texto: {escenario_id}, aaaaaaNúmero de filas limpiadas: {num}")
                    return valores_texto
            except FileNotFoundError:
                print("El archivo de texto no existe.")
            
           # print("Obteniendo valores del archivo CSV...")
            try:
                with open("escenario_ids.csv", "r", newline='') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        if row: 
                            primer_valor = row[0]
                            valores_csv.add(primer_valor)
                            print(f"Primer valor del archivo CSV: {primer_valor}")
            except FileNotFoundError:
                print("El archivo CSV no existe.")
                return None
            
            valores_comunes = set(valores_texto.keys()).intersection(valores_csv)
            
            if valores_comunes:
                print("Valores presentes tanto en el archivo de texto como en el archivo CSV:")
                for valor in valores_comunes:
                    print(f"Escenario ID: {valor}, Número de filas limpiadas: {valores_texto[valor]}")
            else:
                print("No hay valores comunes entre el archivo de texto y el archivo CSV.")
                return None
            
    def agrupar_valores(self):
        valores_agrupados = {}

        try:
            with open('num_rows_after_cleaning.txt', 'r') as file:
                for line in file:
                    if line.startswith("Escenario ID:"):
                        escenario_id = line.split(":")[1].strip()
                        valores_agrupados.setdefault(escenario_id, [])
        except FileNotFoundError:
            print("El archivo num_rows_after_cleaning.txt no se encontró.")

        try:
            with open("escenario_ids.csv", "r", newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row: 
                        primer_valor = row[0]
                        valores_agrupados.setdefault(primer_valor, [])
        except FileNotFoundError:
            print("El archivo escenario_ids.csv no existe.")

        for key, value in valores_agrupados.items():
            print(f"Valor: {key}, Apariciones: {len(value)}")


    def crear_escenario(self):
        now = datetime.now()
        now_str = now.strftime("%m%d%Y%H%M")
        quincena_no = self.entries['Quincena No.'].get()
        tipo_nomina = self.dropdown.get()
        registro_patronal = self.dropdown.get()

        self.entries['Escenario Id'].delete(0, tk.END)
        self.entries['Escenario Id'].insert(0, now_str)
        self.entries['Escenario Id'].config(state="readonly")  
        self.entries['Escenario Id'].bind("<FocusIn>", lambda event: self.entries['Escenario Id'].config(state="readonly")) 

        with open("escenario_ids.csv", "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerow([now_str, now.strftime("%Y-%m-%d %H:%M"), quincena_no, registro_patronal])

        base_dir = os.path.join(self.path, now_str)
        os.makedirs(base_dir, exist_ok=True)
        os.makedirs(os.path.join(base_dir, 'erroneos'), exist_ok=True)
        universo_dir = os.path.join(base_dir, 'universo')
        os.makedirs(universo_dir, exist_ok=True)
        os.makedirs(os.path.join(base_dir, 'timbrado'), exist_ok=True)
        subprocess.run(['explorer', universo_dir])
        self.table.insert('', 'end', values=(now_str, quincena_no, tipo_nomina, ''))


    def configure_row_colors(self):
        self.table.tag_configure('oddrow', background='#E0E0F8')  # Color azul claro
        self.table.tag_configure('evenrow', background='white')  # Color blanco

        for i, row in enumerate(self.table.get_children()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            self.table.item(row, tags=(tag,))
    def mostrar_vista_errores(self):
        if hasattr(self, 'new_window') and self.new_window.winfo_exists():
            return
        
        escenario_id = self.entries['Escenario Id'].get().strip()
        quincena_no = self.entries['Quincena No.'].get().strip()
        registro_patronal_text = self.dropdown.get().strip()
        registro_patronal = ''.join(re.findall(r'\d+', registro_patronal_text))

        self.new_window = tk.Toplevel(self.master)
        self.app = TableError(self.new_window, escenario_id, quincena_no, registro_patronal_text)
        window_x = self.master.winfo_x()
        window_y = self.master.winfo_y()
        self.new_window.geometry("+%d+%d" % (window_x, window_y))


    def cerrar(self):
        self.master.destroy()
        
    def resetear_campos(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        
        self.dropdown.set('')
        
        self.entries['Escenario Id'].config(state=tk.NORMAL)
        self.entries['Escenario Id'].delete(0, tk.END)
        
    def refresh_table_periodically(self):
        self.check_and_refresh_table()
        self.master.after(1000, self.refresh_table_periodically)  # Call this method again after 1000 milliseconds

def main():
    root = tk.Tk()
    app = VistaPrincipal(root)
    root.mainloop()

if __name__ == "__main__":
    main()