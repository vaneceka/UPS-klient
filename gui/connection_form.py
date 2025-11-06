import tkinter as tk
from tkinter import messagebox
from gui.lobby_window import LobbyWindow
from network import NetworkClient
from gui.styled_button import StyledButton
from gui.utils import center_window

class ConnectionForm:
    def __init__(self, root):
        self.root = root
        self.root.title("Připojení k serveru")
        self.root.configure(bg="#F5F5F5")
        self.root.geometry("350x280")
        center_window(root,350, 280)

        # --- HLAVNÍ OBALOVACÍ FRAME ---
        main_frame = tk.Frame(root, bg="#F5F5F5")
        main_frame.pack(expand=True)

        # --- PŘEZDÍVKA ---
        tk.Label(
            main_frame, text="Přezdívka:", font=("Arial", 13),
            bg="#F5F5F5", fg="#333"
        ).pack(anchor="center", pady=(10, 3))
        self.entry_name = tk.Entry(
            main_frame, font=("Arial", 13),
            bg="white", fg="black", bd=2, relief="groove", insertbackground="black"
        )
        self.entry_name.pack(ipadx=5, ipady=3, pady=(0, 10))

        # --- ADRESA SERVERU ---
        tk.Label(
            main_frame, text="Adresa serveru:", font=("Arial", 13),
            bg="#F5F5F5", fg="#333"
        ).pack(anchor="center", pady=(5, 3))
        self.entry_host = tk.Entry(
            main_frame, font=("Arial", 13),
            bg="white", fg="black", bd=2, relief="groove", insertbackground="black"
        )
        self.entry_host.pack(ipadx=5, ipady=3, pady=(0, 10))
        self.entry_host.insert(0, "127.0.0.1")

        # --- PORT ---
        tk.Label(
            main_frame, text="Port:", font=("Arial", 13),
            bg="#F5F5F5", fg="#333"
        ).pack(anchor="center", pady=(5, 3))
        self.entry_port = tk.Entry(
            main_frame, font=("Arial", 13),
            bg="white", fg="black", bd=2, relief="groove", insertbackground="black"
        )
        self.entry_port.pack(ipadx=5, ipady=3, pady=(0, 10))
        self.entry_port.insert(0, "5001")

        # --- TLAČÍTKO ---
        self.connect_button = StyledButton(
            main_frame,
            text="Připojit",
            bg_color="#4CAF50",
            hover_color="#45A049",
            command=self.connect
        )
        self.connect_button.pack(pady=(15, 10))

    # ==== FUNKCE ====

    def connect(self):
        name = self.entry_name.get().strip()
        host = self.entry_host.get().strip()
        port = self.entry_port.get().strip()
        client = NetworkClient(host, port, on_message_callback=self.handle_server_message, root=self.root)

        if not name or not host or not port:
            messagebox.showwarning("Chyba", "Vyplňte všechna pole.")
            return

        try:
            port = int(port)
        except ValueError:
            messagebox.showerror("Chyba", "Port musí být číslo.")
            return

        # připojení k serveru
        client = NetworkClient(host, port, on_message_callback=self.handle_server_message)
        if not client.connect():
            messagebox.showerror("Chyba", "Nepodařilo se připojit k serveru.")
            return

        # pošli identifikaci
        client.send(f"HELLO NICK {name}")
        self.open_lobby(client, name)

    def handle_server_message(self, message):
        print("📩 Server:", message)

    def open_lobby(self, client, name):
        """Vyčistí aktuální obsah a zobrazí lobby ve stejném okně"""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("350x250")
        LobbyWindow(self.root, client, name)

    # def center_window(self, width, height):
    #     """Umístí okno doprostřed obrazovky."""
    #     screen_width = self.root.winfo_screenwidth()
    #     screen_height = self.root.winfo_screenheight()
    #     x = int((screen_width / 2) - (width / 2))
    #     y = int((screen_height / 2) - (height / 2))
    #     self.root.geometry(f"{width}x{height}+{x}+{y}")