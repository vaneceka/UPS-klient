import tkinter as tk
from tkinter import messagebox
from gui.lobby_window import LobbyWindow
from network import NetworkClient
from gui.styled_button import StyledButton
from gui.utils import center_window

class ConnectionForm:
    def __init__(self, root):
        self.root = root
        self._init_state()
        self._init_window()
        self._build_ui()
        
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
        self.client = NetworkClient(host, port, on_message_callback=self.handle_server_message)
        if not self.client.connect():
            messagebox.showerror("Chyba", "Nepodařilo se připojit k serveru.")
            return

        self.name = name
        self.client.nickname = name
        self.client.send(f"HELLO NICK {self.name}")


    def handle_server_message(self, message):
        print("Server:", message)

        if message.startswith("GAME_START"):
            return self._handle_game_start(message)

        if message.startswith("WELCOME"):
            return self._handle_welcome()

        elif message.startswith("ERROR NICK_IN_USE"):
            return self._handle_nick_in_use()

        elif message.startswith("GAME_OVER YOU_CAN_PLAY_AGAIN"):
            print("Reconnect potvrzen -> přecházím do lobby")
            return self.open_lobby(self.client, self.name)

        if self.lobby_window:
            self.lobby_window.handle_server_message(message)
            return
        
        
    def open_lobby(self, client, name):
        """Vyčistí aktuální obsah a zobrazí lobby ve stejném okně"""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("350x250")
        self.lobby_window = LobbyWindow(self.root, client, name)


    def _init_state(self):
        self.game_window = None
        self.lobby_window = None
        self.nickname = None
        self.client = None
        self.name = None
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
    
    def _init_window(self):
        self.root.title("Připojení k serveru")
        self.root.configure(bg="#F5F5F5")
        self.root.geometry("350x280")
        center_window(self.root, 350, 280)
    
    def _build_ui(self):
        main_frame = tk.Frame(self.root, bg="#F5F5F5")
        main_frame.pack(expand=True)

        self._build_name_field(main_frame)
        self._build_host_field(main_frame)
        self._build_port_field(main_frame)
        self._build_connect_button(main_frame)

    def _build_name_field(self, frame):
        tk.Label(
            frame, text="Přezdívka:", font=("Arial", 13),
            bg="#F5F5F5", fg="#333"
        ).pack(anchor="center", pady=(10, 3))

        self.entry_name = tk.Entry(
            frame, font=("Arial", 13),
            bg="white", fg="black", bd=2,
            relief="groove", insertbackground="black"
        )
        self.entry_name.pack(ipadx=5, ipady=3, pady=(0, 10))

    def _build_host_field(self, frame):
        tk.Label(
            frame, text="Adresa serveru:", font=("Arial", 13),
            bg="#F5F5F5", fg="#333"
        ).pack(anchor="center", pady=(5, 3))

        self.entry_host = tk.Entry(
            frame, font=("Arial", 13),
            bg="white", fg="black", bd=2,
            relief="groove", insertbackground="black"
        )
        self.entry_host.pack(ipadx=5, ipady=3, pady=(0, 10))
        self.entry_host.insert(0, "127.0.0.1")
    
    def _build_port_field(self, frame):
        tk.Label(
            frame, text="Port:", font=("Arial", 13),
            bg="#F5F5F5", fg="#333"
        ).pack(anchor="center", pady=(5, 3))

        self.entry_port = tk.Entry(
            frame, font=("Arial", 13),
            bg="white", fg="black", bd=2,
            relief="groove", insertbackground="black"
        )
        self.entry_port.pack(ipadx=5, ipady=3, pady=(0, 10))
        self.entry_port.insert(0, "5001")

    def _build_connect_button(self, frame):
        self.connect_button = StyledButton(
            frame,
            text="Připojit",
            bg_color="#4CAF50",
            hover_color="#45A049",
            command=self.connect
        )
        self.connect_button.pack(pady=(15, 10))

    def _handle_game_start(self, message):
        parts = message.split()
        my_color = parts[2]
        opponent = parts[4]

        root_game = tk.Toplevel(self.root)
        from gui.checkers_gui import CheckersGUI
        gui = CheckersGUI(
            root_game,
            my_color=my_color,
            my_name=self.name,
            opponent_name=opponent,
            network=self.client
        )

        self.client.on_message_callback = gui.handle_server_message
        self.root.withdraw()
    
    def _handle_welcome(self):
        self.nickname = self.name
        self.open_lobby(self.client, self.name)

    def _handle_nick_in_use(self):
        messagebox.showerror("Chyba", "Přezdívka je již používána.")
        try:
            self.client.close()
        except:
            pass
        self.client = None

    def quit_app(self):
        try:
            if self.client:
                self.client.send("BYE")
                self.client.close()
        except:
            pass
        self.root.destroy()