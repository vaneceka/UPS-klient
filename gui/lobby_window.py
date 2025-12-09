import tkinter as tk
import sys
from tkinter import messagebox
from gui.styled_button import StyledButton


class LobbyWindow:
    def __init__(self, root, client, name, controller):
        self.root = root
        self.client = client
        self.controller = controller
        self.name = name

        self._init_window()
        self._build_header()
        self._build_status()
        self._build_buttons()
        self._bind_events()

    def _init_window(self):
        self.root.title("Lobby")
        self.root.geometry("380x280")
        self.root.configure(bg="#F5F5F5")

    def _build_header(self):
        tk.Label(
            self.root, text="Lobby",
            font=("Arial", 18, "bold"),
            bg="#F5F5F5", fg="#333"
        ).pack(pady=(15, 5))

        tk.Label(
            self.root,
            text=f"Přihlášený jako: {self.name}",
            font=("Arial", 13),
            bg="#F5F5F5", fg="#333"
        ).pack(pady=(5, 10))

    def _build_status(self):
        self.status_label = tk.Label(
            self.root,
            text="Čekám na akci...",
            font=("Arial", 12),
            bg="#F5F5F5",
            fg="#555"
        )
        self.status_label.pack(pady=10)

    def _build_buttons(self):
        self.play_button = StyledButton(
            self.root,
            text="Hrát",
            bg_color="#4CAF50",
            hover_color="#45A049",
            command=self.play
        )
        self.play_button.pack(pady=15)

        self.disconnect_button = StyledButton(
            self.root,
            text="Odhlásit se",
            bg_color="#E53935",
            hover_color="#C62828",
            command=self.exit_app
        )
        self.disconnect_button.pack(pady=(5, 10))

    def _bind_events(self):
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def play(self):
        self.play_button.disable()
        self.client.send("PLAY\n")
        self.status_label.config(text="Čekám na druhého hráče...")

    def handle_server_message(self, message: str):
        print("[Lobby] Server:", message)

        if message.startswith("WAIT"):
            self.status_label.config(text="Čekám na protihráče...")
        elif message.startswith("ERROR"):
            messagebox.showerror("Chyba", message)

    def exit_app(self):
        try:
            if self.client:
                self.client.send("BYE\n")
                self.client.close()
        except Exception:
            pass
        self.root.destroy()
        sys.exit(0)

    def show_server_unreachable(self):
        """Zobrazí v lobby, že je server nedostupný."""
        self.status_label.config(
            text="Spojení se serverem bylo ztraceno.\nZkouším se znovu připojit...",
            fg="red"
        )
        # volitelně: zakázat tlačítka
        try:
            self.play_button.disable()
        except Exception:
            pass

        try:
            self.disconnect_button.disable()
        except Exception:
            pass