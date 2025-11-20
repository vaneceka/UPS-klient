import tkinter as tk
import sys
from tkinter import messagebox
from gui.checkers_gui import CheckersGUI
from gui.styled_button import StyledButton

class LobbyWindow:
    def __init__(self, root, client, name):
        self.root = root
        self.client = client
        self.name = name
        self.lobby_active = True

        self._init_window()
        self._build_header()
        self._build_status()
        self._build_buttons()
        self._bind_events()

        # Network → posílej zprávy sem
        self.client.on_message_callback = self.handle_server_message

    def _init_window(self):
        self.root.title("Lobby")
        self.root.geometry("350x280")
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
            self.root, text="Čekám na akci...",
            font=("Arial", 12), bg="#F5F5F5", fg="#555"
        )
        self.status_label.pack(pady=10)

    def _build_buttons(self):
        self.play_button = StyledButton(
            self.root, text="Play",
            bg_color="#4CAF50", hover_color="#45A049",
            command=self.play
        )
        self.play_button.pack(pady=15)

        self.disconnect_button = StyledButton(
            self.root, text="Odhlásit se",
            bg_color="#E53935", hover_color="#C62828",
            command=self.exit_app
        )
        self.disconnect_button.pack(pady=(5, 10))

    def _bind_events(self):
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)


    def play(self):
        """Pošli požadavek na zahájení hry (jen jednou)"""
        self.play_button.disable() 
        self.client.send("PLAY")
        self.status_label.config(text="Čekám na protihráče...")

    def handle_server_message(self, message):
        print("Server:", message)

        if not self.lobby_active:
            # předat zprávu GUI hry
            if hasattr(self, "game_window"):
                self.game_window.handle_server_message(message)
            return

        if message.startswith("WAIT"):
            self.status_label.config(text="Čekám na druhého hráče...")
            return

        elif message.startswith("GAME_START"):
            return self._handle_game_start(message)
            
        elif message.startswith("ERROR"):
            messagebox.showerror("Chyba", message)

    def _handle_game_start(self, message):
        parts = message.strip().split()
        if len(parts) >= 3 and parts[1].upper() == "COLOR":
            my_color = parts[2].upper()
        else:
            my_color = "WHITE"

        if "OPPONENT" in parts:
            idx = parts.index("OPPONENT")
            if idx + 1 < len(parts):
                opponent_name = parts[idx + 1]
            else:
                opponent_name = "?"
        else:
            opponent_name = "?"

        print(f"Přidělená barva: {my_color}, soupeř {opponent_name}")
        self._start_game(my_color, opponent_name)

    def _start_game(self, my_color, opponent_name):
        """Skryje lobby a otevře herní okno"""
        self.root.withdraw()
        self.lobby_active = False 

        root_game = tk.Toplevel(self.root)
        root_game.title("Dáma")

        # Předáme jméno hráče do hry
        gui = CheckersGUI(root_game, my_color=my_color, my_name=self.name, opponent_name=opponent_name, network=self.client)

        # Přesměruj zprávy na GUI hry
        self.client.on_message_callback = gui.handle_server_message

    def exit_app(self):
        try:
            if self.network:
                self.network.send("BYE")
                self.network.close()
        except:
            pass
        self.root.destroy()
        sys.exit(0)