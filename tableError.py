import tkinter as tk
from tkinter import ttk

class TableError:
    def __init__(self, master):
        self.master = master
        self.master.title("Conalep-timbrado")
        self.master.state('zoomed')

        
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=1)
        
        self.inner_frame = tk.Frame(self.main_frame, bd=2, relief=tk.SOLID)
        self.inner_frame.pack(fill=tk.BOTH, expand=1, padx=20, pady=20)  

        # Nuevo recuadro dentro del recuadro existente con relleno adicional arriba y abajo
        self.new_frame = tk.Frame(self.inner_frame, bd=2, relief=tk.SOLID)
        self.new_frame.pack(fill=tk.BOTH, expand=1, padx=20, pady=(20, 70))

        # Cuadro 1 - Datos txt
        self.column1 = tk.Frame(self.new_frame, bd=2, relief=tk.SOLID)
        self.column1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.column1_label = tk.Label(self.column1, text="Datos txt", font=("Helvetica", 12, "bold"))
        self.column1_label.pack(pady=10)

        # Lista de elementos seleccionables
        self.listbox = tk.Listbox(self.column1, height=5)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.insert(1, "Dato 1")
        self.listbox.insert(2, "Dato 2")
        self.listbox.insert(3, "Dato 3")
        self.listbox.bind("<<ListboxSelect>>", self.mostrar_error)

        # Cuadro 2 - Error
        self.column2 = tk.Frame(self.new_frame, bd=2, relief=tk.SOLID)
        self.column2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.column2_label = tk.Label(self.column2, text="Error", font=("Helvetica", 12, "bold"))
        self.column2_label.pack(pady=10)
        self.error_label = tk.Label(self.column2, text="", font=("Helvetica", 12))
        self.error_label.pack(pady=10)

        # Cuadro 3 - Contenido txt
        self.column3 = tk.Frame(self.new_frame, bd=2, relief=tk.SOLID)
        self.column3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.column3_label = tk.Label(self.column3, text="Contenido txt", font=("Helvetica", 12, "bold"))
        self.column3_label.pack(pady=10)

        self.button = tk.Button(self.main_frame, text="Test", command=self.cerrar)
        self.button.place(relx=0.1, rely=0.94, anchor=tk.CENTER)
        self.button.config(width=20, height=2)

    def cerrar(self):
        self.master.destroy()

    def mostrar_error(self, event):
        seleccion = self.listbox.get(self.listbox.curselection())
        self.error_label.config(text=f"Dato seleccionado: {seleccion}")

def main():
    root = tk.Tk()
    app = TableError(root)
    root.mainloop()

if __name__ == "__main__":
    main()
