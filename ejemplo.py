import tkinter as tk

class VistaPrincipal:
    def __init__(self, master):
        self.master = master
        self.master.title("Ejemplo de Vista")
        
        self.label = tk.Label(master, text="Hola, esta es una vista de ejemplo")
        self.label.pack(pady=10)
        
        self.button = tk.Button(master, text="Cerrar", command=self.cerrar)
        self.button.pack(pady=5)
        
    def cerrar(self):
        self.master.destroy()

def main():
    root = tk.Tk()
    app = VistaPrincipal(root)
    root.mainloop()

if __name__ == "__main__":
    main()
