import tkinter as tk
from gui.connection_form import ConnectionForm

if __name__ == "__main__":
    root = tk.Tk()
    form = ConnectionForm(root)
    root.mainloop()