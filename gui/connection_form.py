import tkinter as tk
from tkinter import messagebox
from gui.styled_button import StyledButton
from gui.utils import center_window


class ConnectionForm:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        self.client = None
        self.name = None

        self._init_window()
        self._build_ui()

    # ============ UI ============
    def _init_window(self):
        self.root.title("Připojení k serveru")
        self.root.configure(bg="#F5F5F5")
        self.root.geometry("350x280")
        center_window(self.root, 350, 280)
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

    def _build_ui(self):
        main_frame = tk.Frame(self.root, bg="#F5F5F5")
        main_frame.pack(expand=True)

        # Nick
        tk.Label(
            main_frame, text="Přezdívka:", font=("Arial", 13),
            bg="#F5F5F5", fg="#333"
        ).pack(anchor="center", pady=(10, 3))

        self.entry_name = tk.Entry(
            main_frame, font=("Arial", 13),
            bg="white", fg="black", bd=2,
            relief="groove", insertbackground="black"
        )
        self.entry_name.pack(ipadx=5, ipady=3, pady=(0, 10))

        # Host
        tk.Label(
            main_frame, text="Adresa serveru:", font=("Arial", 13),
            bg="#F5F5F5", fg="#333"
        ).pack(anchor="center", pady=(5, 3))

        self.entry_host = tk.Entry(
            main_frame, font=("Arial", 13),
            bg="white", fg="black", bd=2,
            relief="groove", insertbackground="black"
        )
        self.entry_host.pack(ipadx=5, ipady=3, pady=(0, 10))
        # self.entry_host.insert(0, "127.0.0.1") 
        self.entry_host.insert(0, "192.168.2.1") 

        # Port
        tk.Label(
            main_frame, text="Port:", font=("Arial", 13),
            bg="#F5F5F5", fg="#333"
        ).pack(anchor="center", pady=(5, 3))

        self.entry_port = tk.Entry(
            main_frame, font=("Arial", 13),
            bg="white", fg="black", bd=2,
            relief="groove", insertbackground="black"
        )
        self.entry_port.pack(ipadx=5, ipady=3, pady=(0, 10))
        self.entry_port.insert(0, "5001")

        # Connect button
        self.connect_button = StyledButton(
            main_frame,
            text="Připojit",
            bg_color="#4CAF50",
            hover_color="#45A049",
            command=self.connect
        )
        self.connect_button.pack(pady=(15, 10))

    # ============ LOGIKA ============
    def connect(self):
        name = self.entry_name.get().strip()
        host = self.entry_host.get().strip()
        port = self.entry_port.get().strip()

        if not name or not host or not port:
            messagebox.showwarning("Chyba", "Vyplňte všechna pole.")
            return

        try:
            port = int(port)
        except ValueError:
            messagebox.showerror("Chyba", "Port musí být číslo.")
            return
        
        success = self.controller.connect(host, port, name)
        if not success:
            messagebox.showerror("Chyba", "Nepodařilo se připojit k serveru.")
            return

        self.name = name
        self.client = self.controller.client

    # Tyhle metody volá controller:
    def on_welcome(self):
        self.controller.show_lobby(self.name)

    def on_nick_in_use(self):
        messagebox.showerror("Chyba", "Přezdívka je již používána.")
    
    def on_invalid_nick(self):
        messagebox.showerror("Chyba", "Neplatná přezdívka!")
        self.connect_button.config(state="normal")
        try:
            if self.client:
                self.client.close()
        except:
            pass

        self.client = None

    def on_server_full(self):
        messagebox.showerror("Server plný", "Kapacita serveru je plná. Zkuste to prosím později.")
        try:
            if self.client:
                self.client.close()
        except:
            pass
        self.client = None
        self.connect_button.config(state="normal")

    def handle_server_message(self, message: str):
        # ConnectionForm už nic dalšího neřeší
        print("[ConnectionForm] Ignoruju:", message)

    def quit_app(self):
        try:
            if self.client:
                self.client.send("BYE")
                self.client.close()
        except Exception:
            pass
        self.root.destroy()