import tkinter as tk
from tkinter import messagebox
from gui.checkers_gui import CheckersGUI
from gui.styled_button import StyledButton

class LobbyWindow:
    def __init__(self, root, client, name):
        self.root = root
        self.client = client
        self.name = name

        self.root.title("Lobby")
        self.root.geometry("350x280")
        self.root.configure(bg="#F5F5F5")

        tk.Label(root, text="Lobby", font=("Arial", 18, "bold"),
                 bg="#F5F5F5", fg="#333").pack(pady=(15, 5))
        tk.Label(root, text=f"Přihlášený jako: {self.name}",
                 font=("Arial", 13), bg="#F5F5F5", fg="#333").pack(pady=(5, 10))

        self.status_label = tk.Label(root, text="Čekám na akci...",
                                     font=("Arial", 12), bg="#F5F5F5", fg="#555")
        self.status_label.pack(pady=10)

        self.play_button = StyledButton(root, text="Play",
                                        bg_color="#4CAF50",
                                        hover_color="#45A049",
                                        command=self.play)
        self.play_button.pack(pady=15)

        self.disconnect_button = StyledButton(root, text="Odhlásit se",
                                              bg_color="#E53935",
                                              hover_color="#C62828",
                                              command=self.disconnect)
        self.disconnect_button.pack(pady=(5, 10))

        self.root.protocol("WM_DELETE_WINDOW", self.disconnect)

        # Po připojení poslouchej zprávy ze serveru
        self.client.on_message_callback = self.handle_server_message
        self.client.send(f"HELLO NICK {self.name}")

    def play(self):
        """Pošli požadavek na zahájení hry (jen jednou)"""
        self.play_button.disable() 
        self.client.send("PLAY")
        self.status_label.config(text="Čekám na protihráče...")

    def handle_server_message(self, message):
        print("Server:", message)

        if message.startswith("WAIT"):
            self.status_label.config(text="Čekám na druhého hráče...")

        elif message.startswith("GAME_START"):
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
            self.start_game(my_color, opponent_name)

        elif message.startswith("ERROR"):
            messagebox.showerror("Chyba", message)

    def start_game(self, my_color,opponent_name):
        """Skryje lobby a otevře herní okno"""
        self.root.withdraw()

        root_game = tk.Toplevel(self.root)
        root_game.title("Dáma")

        # Předáme jméno hráče do hry
        gui = CheckersGUI(root_game, my_color=my_color, my_name=self.name, opponent_name=opponent_name, network=self.client)

        # Přesměruj zprávy na GUI hry
        self.client.on_message_callback = gui.handle_server_message

    def disconnect(self):
        try:
            self.client.send("BYE\n")
            self.client.close()
        except Exception:
            pass
        self.root.destroy()
        # messagebox.showinfo("Odhlášení", "Byl jsi odpojen od serveru.")