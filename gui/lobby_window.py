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
        self.root.geometry("350x250")
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

        # Po připojení poslouchej zprávy ze serveru
        self.client.on_message_callback = self.handle_server_message

    # ======== Herní logika lobby ========

    def play(self):
        """Pošli požadavek na zahájení hry"""
        self.client.send("PLAY")
        self.status_label.config(text="⏳ Čekám na protihráče...")

    def handle_server_message(self, message):
        print("📩 Server:", message)

        if message.startswith("WAIT"):
            self.status_label.config(text="Čekám na druhého hráče...")

        elif message.startswith("GAME_START"):
            # očekává: GAME_START COLOR WHITE/BLACK
            parts = message.strip().split()
            my_color = parts[3] if len(parts) >= 4 else "WHITE"
            self.status_label.config(text=f"🎮 Hra začíná! ({my_color})")
            self.start_game(my_color)

        elif message.startswith("ERROR"):
            messagebox.showerror("Chyba", message)

    def start_game(self, my_color):
        """Skryje lobby a otevře herní okno"""
        self.root.withdraw()

        root_game = tk.Toplevel(self.root)
        root_game.title("Dáma")

        gui = CheckersGUI(root_game, my_color=my_color)
        gui.network = self.client

        # Přesměruj zprávy na GUI hry
        self.client.on_message_callback = gui.handle_server_message

        # POZOR: druhý mainloop NE!
        # root_game.mainloop()  ❌  -> hlavní loop už běží v main.py

    def disconnect(self):
        """Ukončí připojení a zavře okno"""
        try:
            self.client.close()
        except Exception:
            pass
        self.root.destroy()
        messagebox.showinfo("Odhlášení", "Byl jsi odpojen od serveru.")