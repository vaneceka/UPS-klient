import tkinter as tk
from tkinter import messagebox
from gui.lobby_window import LobbyWindow
from network import NetworkClient
from gui.styled_button import StyledButton

class ConnectionForm:
    def __init__(self, root):
        self.root = root
        self.root.title("Připojení k serveru")
        self.root.configure(bg="#F5F5F5")  # světle šedé pozadí
        self.root.geometry("350x250")

        # -- LABELY --
        tk.Label(root, text="Přezdívka:", font=("Arial", 13), bg="#F5F5F5", fg="#333").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        tk.Label(root, text="Adresa serveru:", font=("Arial", 13), bg="#F5F5F5", fg="#333").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        tk.Label(root, text="Port:", font=("Arial", 13), bg="#F5F5F5", fg="#333").grid(row=2, column=0, padx=10, pady=10, sticky="e")

        # -- TEXTOVÁ POLE --
        entry_style = {"font": ("Arial", 13), "bg": "white", "fg": "black", "bd": 2, "relief": "groove", "insertbackground": "black"}

        self.entry_name = tk.Entry(root, **entry_style)
        self.entry_host = tk.Entry(root, **entry_style)
        self.entry_port = tk.Entry(root, **entry_style)

        self.entry_name.grid(row=0, column=1, padx=10, pady=10, ipadx=5, ipady=3)
        self.entry_host.grid(row=1, column=1, padx=10, pady=10, ipadx=5, ipady=3)
        self.entry_port.grid(row=2, column=1, padx=10, pady=10, ipadx=5, ipady=3)

        self.entry_host.insert(0, "127.0.0.1")
        self.entry_port.insert(0, "5000")

        # -- TLAČÍTKO --
        self.connect_button = StyledButton(
            root,
            text="Připojit",
            bg_color="#4CAF50",
            hover_color="#45A049",
            command=self.connect
        )
        self.connect_button.grid(row=3, column=0, columnspan=2, pady=15)

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
        """Zavře formulář a otevře lobby"""
        self.root.destroy()
        root_lobby = tk.Tk()
        lobby = LobbyWindow(root_lobby, client, name)
        root_lobby.mainloop()