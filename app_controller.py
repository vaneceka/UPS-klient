import socket
import threading
import time
import tkinter as tk
from network import NetworkClient
from gui.connection_form import ConnectionForm
from gui.lobby_window import LobbyWindow
from gui.checkers_gui import CheckersGUI

RECONNECT_TIMEOUT = 25
RECONNECT_RETRY_DELAY = 1  

class AppController:
    def __init__(self):
        self.root = tk.Tk()

        self.server_host = None
        self.server_port = None
        self.client = None # NetworkClient
        self.current_window = None # ConnectionForm / LobbyWindow / CheckersGUI
        self.nickname = None

        self.reconnecting = False 
        self.disconnected = False
        
        self.show_connection_form()

    def show_connection_form(self):
        if self.client:
            print("dostanu se sem???????")
            self.client.on_disconnect = None
            self.client.stop()
        self.client = None
        
        self.reconnecting = False
        self.disconnected = False
        self.root.deiconify()
        self._clear_window()
        self.current_window = ConnectionForm(self.root, controller=self)

    def show_lobby(self, nickname):
        self.root.deiconify() 
        self._clear_window()
        self.current_window = LobbyWindow(self.root, self.client, nickname, controller=self)

    def show_game(self, color, my_name, opponent):
        if isinstance(self.current_window, CheckersGUI):
            try:
                self.current_window.root.destroy()
            except Exception:
                pass

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

    def connect(self, host, port, nickname) -> bool:
        self.nickname = nickname
        self.server_host = host       
        self.server_port = port 

        self.reconnecting = False
        self.disconnected = False
        
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

        self.client.send(f"HELLO NICK {nickname}\n")
        return True

    # Routing mezi okny
    def _handle_message(self, message: str):
        if message.startswith("WELCOME"):
            if isinstance(self.current_window, ConnectionForm):
                return self.current_window.on_welcome()
            if isinstance(self.current_window, LobbyWindow) and self.reconnecting:
                self.reconnecting = False
                if hasattr(self.current_window, "on_reconnected"):
                    self.current_window.on_reconnected()
                return

        if message.startswith("ERROR NICK_IN_USE"):
            if hasattr(self.current_window, "on_nick_in_use"):
                return self.current_window.on_nick_in_use()
        
        if message.startswith("ERROR INVALID_NICK"):
            self.current_window.on_invalid_nick()
            return

        if message.startswith("ERROR SERVER_FULL"):
            if hasattr(self.current_window, "on_server_full"):
                return self.current_window.on_server_full()

        if message.startswith("GAME_START"):
            parts = message.split()
            color = parts[2]
            opponent = parts[4]
            self.show_game(color, self.nickname, opponent)
            return

        if message.startswith("GAME_OVER YOU_CAN_PLAY_AGAIN"):
            return self.show_lobby(self.nickname)

        # Všechno ostatní se pošle aktuálnímu oknu(Lobby / CheckersGUI)
        if hasattr(self.current_window, "handle_server_message"):
            self.current_window.handle_server_message(message)

    def run(self):
        self.root.mainloop()

    def on_disconnect(self, client):
        if self.reconnecting:
            return

        self.disconnected = True

        if isinstance(self.current_window, CheckersGUI):
            self.root.after(0, self.current_window.show_server_unreachable)
        elif isinstance(self.current_window, LobbyWindow):
            self.root.after(0, self.current_window.show_server_unreachable)

        print("Odpojeno od serveru – zkouším reconnect...")
        self.reconnecting = True
        threading.Thread(target=self._reconnect_loop, daemon=True).start()

    def _reconnect_loop(self):
        if not self.server_host or not self.server_port or not self.nickname:
            print("Nemám info o serveru/nicku, jdu zpět na ConnectionForm.")
            self.reconnecting = False
            self.root.after(0, self.show_connection_form)
            return

        start = time.time()

        while time.time() - start < RECONNECT_TIMEOUT:
            try:
                print("Zkouším nové připojení...")

                new_client = NetworkClient(
                    self.server_host,
                    self.server_port,
                    on_message_callback=self._handle_message,
                    root=self.root
                )
                new_client.on_disconnect = self.on_disconnect

                if new_client.connect():
                    print("Reconnect OK, přepínám klienta...")

                    # stopneme starého klienta
                    old = self.client
                    self.client = new_client
                    
                    new_client.last_ping_time = time.time()

                    if old:
                        old.stop()

                    # po přepnutí klienta pošleme opět HELLO
                    self.client.send(f"HELLO NICK {self.nickname}\n")

                    # obnovíme UI
                    self.root.after(0, lambda: (
                        hasattr(self.current_window, "on_reconnected")
                        and self.current_window.on_reconnected()
                    ))

                    self.reconnecting = False
                    self.disconnected = False
                    return

            except Exception as e:
                print("Chyba při reconnectu:", e)

            time.sleep(RECONNECT_RETRY_DELAY)

        print("Reconnect se nepodařil včas, vracím do ConnectionForm.")
        self.reconnecting = False
        self.root.after(0, self.show_connection_form)