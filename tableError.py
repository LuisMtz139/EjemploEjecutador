import tkinter as tk
from tkinter import ttk

class TableError:
    def __init__(self, master):
        self.master = master
        self.master.title("Ejemplo de Vista")

        self.master.geometry("1100x650")
        
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=1)
        
        self.inner_frame = tk.Frame(self.main_frame, bd=2, relief=tk.SOLID)
        self.inner_frame.pack(fill=tk.BOTH, expand=1, padx=20, pady=20)  



        self.button = tk.Button(self.main_frame, text="Test", command=self.cerrar)
        self.button.place(relx=0.1, rely=0.9, anchor=tk.CENTER)

    def cerrar(self):
        self.master.destroy()

def main():
    root = tk.Tk()
    app = TableError(root)
    root.mainloop()

if __name__ == "__main__":
    main()
