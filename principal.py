from datetime import datetime
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle  # Importar ThemedStyle para acceder a más opciones de estilo
import os
import xml.etree.ElementTree as ET
import subprocess
import csv
import urllib.parse
import requests 
from enviarTest import DataSender
from tableError import TableError
import re


class VistaPrincipal:
    
    def validar_quincena(self, input):
        # Permite la entrada si es dígito y tiene menos de dos caracteres o es vacío para manejar el borrado
        if input.isdigit() or input == "":
            return True
        return False

    def __init__(self, master):
        self.master = master
        self.master.title("Conalep-timbrado")
        
        tree = ET.parse('config.xml')
        root = tree.getroot()
        self.path = root.find('RutaCarpetas').text
        
        # Corrección aquí: usar self.validar_quincena para referenciar el método correcto
        vcmd = self.master.register(self.validar_quincena)  # Usa self para referenciar el método de instancia
        
        self.master.state('zoomed')
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=1)
        
        self.inner_frame = tk.Frame(self.main_frame, bd=2, relief=tk.SOLID)
        self.inner_frame.pack(fill=tk.BOTH, expand=1, padx=20, pady=20) 

        inputs = ['Escenario Id', 'Quincena No.']
        self.entries = {} 
    
        for i, input_text in enumerate(inputs):
            tk.Label(self.inner_frame, text=input_text, font=("Arial", 15)).grid(row=0, column=i, padx=10)
            if input_text == 'Quincena No.':
                entry = tk.Entry(self.inner_frame, validate="key", validatecommand=(vcmd, '%P'),
                                width=20, bg='light yellow', font=("Arial", 15), justify='center')
            else:
                entry = tk.Entry(self.inner_frame, width=20, bg='light yellow', font=("Arial", 15), justify='center')
            entry.grid(row=1, column=i, padx=45)
            self.entries[input_text] = entry
            
        tk.Label(self.inner_frame, text="Registro Patronal", font=("Arial", 15)).grid(row=0, column=len(inputs), padx=20, sticky=tk.W)

    
        #agrega cuandots faltan por timbrar
        
        options = ['ORDINARIA IMSSS', 'ORDINARIA ISSSTE', 'EXTRAORDINARIA IMSSS', 'EXTRAORDINARIA ISSSTE']
        self.dropdown = ttk.Combobox(self.inner_frame, values=options, font=("Arial", 15), state="readonly", style="Custom.TCombobox", width=30)
        self.dropdown.grid(row=1, column=len(inputs), padx=20, sticky=tk.W)

        self.inner_frame.style = ttk.Style()
        self.inner_frame.style.theme_use("default")
        self.inner_frame.style.configure("Custom.TCombobox", selectbackground=self.inner_frame.cget("background"), selectforeground="black", anchor="center", background="lightyellow") 

        self.inner_frame.style.configure("Custom.TCombobox.Listbox", background="lightyellow")

        button = tk.Button(self.inner_frame, text='Nuevo', font=("Arial", 13), bg='light yellow')
        button.grid(row=1, column=len(inputs), padx=10, sticky=tk.E)
        self.inner_frame.grid_columnconfigure(len(inputs), weight=1)
        self.inner_frame.grid_columnconfigure(len(inputs)+1, minsize=90)

        button2 = tk.Button(self.inner_frame, text='Crear escenario', font=("Arial", 13), bg='light yellow', command=self.crear_escenario)
        button2.grid(row=1, column=len(inputs)+1, padx=10, sticky=tk.E)
        
        self.table = ttk.Treeview(self.inner_frame)
        self.table['columns'] = ('#1', '#2', '#3', '#4', '#5')
        self.table.column('#0', width=0, stretch=tk.NO)
        self.table.column('#1', width=150, stretch=tk.YES, anchor='center')
        self.table.column('#2', width=150, stretch=tk.YES, anchor='center')
        self.table.column('#3', width=150, stretch=tk.YES, anchor='center')
        self.table.column('#4', width=150, stretch=tk.YES)
        self.table.column('#5', width=150, stretch=tk.YES)


        self.table.heading('#1', text='ESCENARIO ID', anchor='center')
        self.table.heading('#2', text='QUINCENA NO.', anchor='center')
        self.table.heading('#3', text='TIPONOMINA', anchor='center')
        self.table.heading('#4', text='STATUS')
        self.table.heading('#5', text='POR_TIMBRAR')


        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10))

        self.table.place(relx=0.5, rely=0.50, relwidth=0.99,relheight=0.7, anchor=tk.CENTER) 

        self.cargar_datos_escenario()
        self.configurar_envio_datos()
        
        self.configure_row_colors()


    def configurar_envio_datos(self):
        data_sender = DataSender()
        self.button = tk.Button(self.main_frame, text="Iniciar Proceso de Timbrado",
                                command=lambda: data_sender.enviar_datos(self.entries, self.dropdown, self.path, self.mostrar_vista_errores))
        self.button.place(relx=0.1, rely=0.9, anchor=tk.CENTER)
        self.button.config(width=25, height=2, font=("Arial", 13))
    

    def cargar_datos_escenario(self):
        try:
            with open("escenario_ids.csv", "r", newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row: 
                        escenario_id = row[0]
                        quincena_no = row[2] if len(row) > 2 else ''
                        registro_patronal = row[3] if len(row) > 3 else ''
                        self.table.insert('', 'end', values=(escenario_id, quincena_no, registro_patronal, '', '', '', '', ''))
        except FileNotFoundError:
            print("El archivo no existe, se creará al guardar un nuevo escenario.")
            

    def crear_escenario(self):
        now = datetime.now()
        now_str = now.strftime("%m%d%Y%H%M")
        quincena_no = self.entries['Quincena No.'].get()
        tipo_nomina = self.dropdown.get()
        registro_patronal = self.dropdown.get()

        self.entries['Escenario Id'].delete(0, tk.END)
        self.entries['Escenario Id'].insert(0, now_str)
        self.entries['Escenario Id'].config(state="readonly")  # Bloquear la entrada de texto
        self.entries['Escenario Id'].bind("<FocusIn>", lambda event: self.entries['Escenario Id'].config(state="readonly"))  # Bloquear la entrada de texto cuando el campo gana el foco

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

        self.table.insert('', 'end', values=(now_str, quincena_no, tipo_nomina, 'STATUS', 'NOXMLSCANDIDATOS', 'NOXMLSTIMBRADOS', 'NOXMLSERRONEOS', 'NOREVISION'))

    def configure_row_colors(self):
        self.table.tag_configure('oddrow', background='#E0E0F8')  # Color azul claro
        self.table.tag_configure('evenrow', background='white')  # Color blanco

        for i, row in enumerate(self.table.get_children()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            self.table.item(row, tags=(tag,))

    def mostrar_vista_errores(self):
        if hasattr(self, 'new_window') and self.new_window.winfo_exists():
            # Si la ventana de errores ya está abierta, no hacer nada
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

def main():
    root = tk.Tk()
    app = VistaPrincipal(root)
    root.mainloop()

if __name__ == "__main__":
    main()