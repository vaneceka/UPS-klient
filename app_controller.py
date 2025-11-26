import tkinter as tk
from network import NetworkClient
from gui.connection_form import ConnectionForm
from gui.lobby_window import LobbyWindow
from gui.checkers_gui import CheckersGUI


class AppController:
    def __init__(self):
        self.root = tk.Tk()

        self.client = None # NetworkClient
        self.current_window = None # ConnectionForm / LobbyWindow / CheckersGUI
        self.nickname = None
        self.show_connection_form()

    # Window management
    def show_connection_form(self):
        self.root.deiconify()
        self._clear_window()
        self.current_window = ConnectionForm(self.root, controller=self)

    def show_lobby(self, nickname):
        self.root.deiconify() 
        self._clear_window()
        self.current_window = LobbyWindow(self.root, self.client, nickname, controller=self)

    def show_game(self, color, my_name, opponent):
        self.root.withdraw()
        win = tk.Toplevel(self.root)
        self.current_window = CheckersGUI(
            win,
            controller=self,
            my_color=color,
            my_name=my_name,
            opponent_name=opponent,
            network=self.client
        )


    def _clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # Network
    def connect(self, host, port, nickname) -> bool:
        self.nickname = nickname
        self.client = NetworkClient(
            host,
            port,
            on_message_callback=self._handle_message,
            root=self.root
        )

        self.client.on_disconnect = self.on_disconnect

        if not self.client.connect():
            self.client = None
            return False

        # HELLO pošle controller, ne ConnectionForm
        self.client.send(f"HELLO NICK {nickname}")
        return True

    # Routing mezi okny
    def _handle_message(self, message: str):
        print("[Controller] Received:", message)

        # Přihlášení
        if message.startswith("WELCOME"):
            if hasattr(self.current_window, "on_welcome"):
                return self.current_window.on_welcome()

        if message.startswith("ERROR NICK_IN_USE"):
            if hasattr(self.current_window, "on_nick_in_use"):
                return self.current_window.on_nick_in_use()
        
        if message.startswith("ERROR INVALID_NICK"):
            self.current_window.on_invalid_nick()
            return

        # Začátek hry
        if message.startswith("GAME_START"):
            parts = message.split()
            color = parts[2]
            opponent = parts[4]
            self.show_game(color, self.nickname, opponent)
            return

        # Hra skončila – možno hrát znovu
        if message.startswith("GAME_OVER YOU_CAN_PLAY_AGAIN"):
            return self.show_lobby(self.nickname)

        # Všechno ostatní pošli aktuálnímu oknu (Lobby / CheckersGUI)
        if hasattr(self.current_window, "handle_server_message"):
            self.current_window.handle_server_message(message)

    def run(self):
        self.root.mainloop()

    def on_disconnect(self):
        # zavřít lobby okno a vrátit ConnectionForm
        self.show_connection_form()