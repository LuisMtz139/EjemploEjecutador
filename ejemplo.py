from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import xml.etree.ElementTree as ET

from tableError import TableError

class VistaPrincipal:
    def __init__(self, master):
        self.master = master
        self.master.title("Conalep-timbrado")
        
        tree = ET.parse('config.xml')
        root = tree.getroot()
        self.path = root.find('Ruta').text


        # Maximiza la ventana para que ocupe el 100% de la pantalla
        self.master.state('zoomed')

        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=1)
        
        self.inner_frame = tk.Frame(self.main_frame, bd=2, relief=tk.SOLID)
        self.inner_frame.pack(fill=tk.BOTH, expand=1, padx=20, pady=20) 

        inputs = ['Escenario Id', 'Quincena No.']
        self.entries = {}  # Store references to entry widgets
        for i, input_text in enumerate(inputs):
            tk.Label(self.inner_frame, text=input_text, font=("Arial", 15)).grid(row=0, column=i, padx=10)
            entry = tk.Entry(self.inner_frame, width=20, bg='light yellow', font=("Arial", 15), justify='center')  # Adjusted font size and centered text here
            entry.grid(row=1, column=i, padx=45)
            self.entries[input_text] = entry
            

        button = tk.Button(self.inner_frame, text='Nuevo', font=("Arial", 13), bg='light yellow')
        button.grid(row=1, column=len(inputs), padx=10, sticky=tk.E)
        self.inner_frame.grid_columnconfigure(len(inputs), weight=1)
        self.inner_frame.grid_columnconfigure(len(inputs)+1, minsize=90)

        button2 = tk.Button(self.inner_frame, text='Crear ecenario', font=("Arial", 13), bg='light yellow', command=self.crear_escenario)
        button2.grid(row=1, column=len(inputs)+1, padx=10, sticky=tk.E)



        self.table = ttk.Treeview(self.inner_frame)
        self.table['columns'] = ('#1', '#2', '#3', '#4', '#5', '#6', '#7', '#8')
        self.table.column('#0', width=0, stretch=tk.NO)
        self.table.column('#1', width=150, stretch=tk.YES)  
        self.table.column('#2', width=150, stretch=tk.YES)
        self.table.column('#3', width=150, stretch=tk.YES)
        self.table.column('#4', width=150, stretch=tk.YES)
        self.table.column('#5', width=150, stretch=tk.YES)
        self.table.column('#6', width=150, stretch=tk.YES)
        self.table.column('#7', width=150, stretch=tk.YES)
        self.table.column('#8', width=150, stretch=tk.YES)
        
        self.table.heading('#1', text='ESCENARIO ID')
        self.table.heading('#2', text='QUINCENA NO.')
        self.table.heading('#3', text='TIPONOMINA')
        self.table.heading('#4', text='STATUS')
        self.table.heading('#5', text='NOXMLSCANDIDATOS')
        self.table.heading('#6', text='NOXMLSTIMBRADOS')
        self.table.heading('#7', text='NOXMLSERRONEOS')
        self.table.heading('#8', text='NOREVISION')
        
        # Estilo para las cabeceras de columna
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10))
        
        self.table.place(relx=0.5, rely=0.50, relwidth=0.99,relheight=0.7, anchor=tk.CENTER) 

        
        self.button = tk.Button(self.main_frame, text="Test", command=self.cambiar_vista)
        self.button.place(relx=0.1, rely=0.9, anchor=tk.CENTER)
        self.button.config(width=10, height=2, font=("Arial", 13))
    
    def crear_escenario(self):
        # Get current date and time
        now = datetime.now()

        # Convert to string
        now_str = now.strftime("%m%d%Y%H%M")

        # Set this value in the 'Escenario Id' entry widget
        self.entries['Escenario Id'].delete(0, tk.END)  # Remove any existing text
        self.entries['Escenario Id'].insert(0, now_str)  # Insert the current date and time
        os.makedirs(os.path.join(self.path, now_str), exist_ok=True)
    def cambiar_vista(self):
        self.new_window = tk.Toplevel(self.master)
        self.app = TableError(self.new_window)

        # Obtener la posición de la ventana principal
        window_x = self.master.winfo_x()
        window_y = self.master.winfo_y()

        # Establecer la posición de la nueva ventana en la misma ubicación
        self.new_window.geometry("+%d+%d" % (window_x, window_y))

    def cerrar(self):
        self.master.destroy()

def main():
    root = tk.Tk()
    app = VistaPrincipal(root)
    root.mainloop()

if __name__ == "__main__":
    main()