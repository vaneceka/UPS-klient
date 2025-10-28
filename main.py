import tkinter as tk
from gui import CheckersGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = CheckersGUI(root)
    root.mainloop()