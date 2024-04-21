import tkinter as tk
from tkinter import ttk

from tableError import TableError

class VistaPrincipal:
    def __init__(self, master):
        self.master = master
        self.master.title("Conalep-timbrado")

        self.master.geometry("1800x1800")

        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=1)
        
        self.inner_frame = tk.Frame(self.main_frame, bd=2, relief=tk.SOLID)
        self.inner_frame.pack(fill=tk.BOTH, expand=1, padx=20, pady=20) 

        inputs = ['Escenario', 'Leyenda', 'Crear']
        for i, input_text in enumerate(inputs):
            tk.Label(self.inner_frame, text=input_text, font=("Arial", 10)).grid(row=0, column=i)
            entry = tk.Entry(self.inner_frame, width=15)  
            entry.grid(row=1, column=i, padx=0)  

            if input_text == 'Crear':
                self.inner_frame.grid_columnconfigure(i, weight=1)

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
        
        self.table.heading('#1', text='ESCENARIOID')
        self.table.heading('#2', text='QUINCENANO')
        self.table.heading('#3', text='TIPONOMINA')
        self.table.heading('#4', text='STATUS')
        self.table.heading('#5', text='NOXMLSCANDIDATOS')
        self.table.heading('#6', text='NOXMLSTIMBRADOS')
        self.table.heading('#7', text='NOXMLSERRONEOS')
        self.table.heading('#8', text='NOREVISION')
        
        # Estilo para las cabeceras de columna
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10))
        
        self.table.place(relx=0.5, rely=0.50, relwidth=0.95,relheight=0.7, anchor=tk.CENTER) 

        
        self.button = tk.Button(self.main_frame, text="Test", command=self.cambiar_vista)
        self.button.place(relx=0.1, rely=0.9, anchor=tk.CENTER)

        
        
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
