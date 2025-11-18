# from enum import Enum, auto

# class ClientState(Enum):
#     CONNECTED = auto()
#     LOBBY = auto()
#     WAITING = auto()
#     WHITE_MOVE = auto()
#     BLACK_MOVE = auto()
#     EVALUATE_MOVE = auto()
#     GAME_OVER = auto()
#     DISCONNECTED = auto()

# class ClientStateMachine:
#     def __init__(self, network, gui):
#         self.network = network
#         self.gui = gui
#         self.state = ClientState.CONNECTED
#         self.color = None  # 'WHITE' nebo 'BLACK'

#     def handle_message(self, message):
#         """Zpracování zpráv ze serveru podle aktuálního stavu."""
#         print(f"[STATE {self.state.name}] {message}")

#         if message.startswith("WELCOME"):
#             self.to_lobby()

#         elif message.startswith("GAME_START"):
#             parts = message.split()
#             if len(parts) >= 3:
#                 self.color = parts[2]
#             self.state = ClientState.WHITE_MOVE if self.color == "WHITE" else ClientState.WAITING
#             print(f"Hra začala, barva: {self.color}")

#         elif message.startswith("BOARD"):
#             # aktualizuj hrací pole v GUI
#             self.gui.update_from_server(message)

#         elif message.startswith("YOUR_TURN"):
#             if self.color == "WHITE":
#                 self.state = ClientState.WHITE_MOVE
#             else:
#                 self.state = ClientState.BLACK_MOVE
#             print("Na tahu jsi ty!")

#         elif message.startswith("OPPONENT_MOVE"):
#             # druhý hráč udělal tah -> aktualizuj GUI
#             self.gui.update_from_server(message)
#             print("♟️ Protihráč táhl")

#         elif message.startswith("GAME_OVER"):
#             self.state = ClientState.GAME_OVER
#             self.gui.show_game_over(message)

#         elif message.startswith("DISCONNECT"):
#             self.state = ClientState.DISCONNECTED
#             print("Server ukončil spojení")

#     def to_lobby(self):
#         self.state = ClientState.LOBBY
#         print("Vstoupil jsi do lobby")

#     def play_game(self):
#         """Odešle žádost o start hry."""
#         if self.state == ClientState.LOBBY:
#             self.network.send("PLAY")
#             self.state = ClientState.WAITING
#             print("⏳ Čekám na protihráče...")

#     def make_move(self, fr, fc, tr, tc):
#         """Odešle tah, pokud je to povoleno."""
#         if self.state in [ClientState.WHITE_MOVE, ClientState.BLACK_MOVE]:
#             self.network.send(f"MOVE {fr} {fc} {tr} {tc}")
#             self.state = ClientState.EVALUATE_MOVE
#             print("Odeslán tah, čekám na potvrzení...")
#         else:
#             print("Není tvůj tah, nemůžeš hrát.")