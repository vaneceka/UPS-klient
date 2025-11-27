import tkinter as tk
import sys
from gui.utils import center_window
from gui.game_over_window import GameOverWindow

WHITE = 1
BLACK = 2
WHITE_KING = 3
BLACK_KING = 4
EMPTY = 0

COLORS = {
    "board_light": "#F0D9B5",
    "board_dark": "#B58863",
    "highlight": "#FFD700"
}

BOARD_SIZE = 8

class CheckersGUI:
    def __init__(self, root, controller, my_color="WHITE", my_name="?", opponent_name="?", network=None):
        self.root = root
        self.controller = controller
        self.root.title("Dáma")
        center_window(root, 680, 690)
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self.in_game = True
        self.my_color = my_color
        self.my_name = my_name
        self.my_turn = False
        self.opponent_name = opponent_name
        self.network = network
        self.selected = None
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        self.cell = None
        self.offset_x = 0
        self.offset_y = 0

        self._build_top_panel()
        self._build_board_canvas()
        self.root.after(0, self.redraw_board)

    def _build_top_panel(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", pady=4)

        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)
        top_frame.columnconfigure(2, weight=1)

        # LEFT
        left = tk.Frame(top_frame)
        left.grid(row=0, column=0, sticky="w")

        self.info_label = tk.Label(
            left,
            text=f"Hraješ za: {'BÍLÉ' if self.my_color.upper() == 'WHITE' else 'ČERNÉ'}",
            font=("Arial", 12)
        )
        self.info_label.pack(side="left", padx=8)

        # CENTER (error)
        self.error_label = tk.Label(
            top_frame,
            text="",
            fg="red",
            font=("Arial", 12)
        )
        self.error_label.place(relx=0.5, rely=0.5, anchor="center")

        # RIGHT
        right = tk.Frame(top_frame)
        right.grid(row=0, column=2, sticky="e")

        self.turn_label = tk.Label(right, text="Na tahu:", font=("Arial", 12))
        self.turn_label.pack(side="right", padx=(0, 10))

        self.opponent_label = tk.Label(
            right,
            text=f"Hraješ proti: {self.opponent_name}",
            font=("Arial", 12)
        )
        self.opponent_label.pack(side="right", padx=8)
    
    def _build_board_canvas(self):
        system_bg = self.root.cget("bg") 
        self.canvas = tk.Canvas(self.root, bg=system_bg, highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")

        self.canvas.bind("<Configure>", self.redraw_board)
        self.canvas.bind("<Button-1>", self.on_click)

    # Při změně velikosti okna, se hra překreslí
    def redraw_board(self, event=None):
        self.canvas.delete("all")

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        # ještě není pořádně změřeno
        if w <= 1 or h <= 1:
            return  

        size = min(w, h)
        self.cell = size // BOARD_SIZE

        self.offset_x = (w - size) // 2
        self.offset_y = (h - size) // 2

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x1 = self.offset_x + c * self.cell
                y1 = self.offset_y + r * self.cell
                x2 = x1 + self.cell
                y2 = y1 + self.cell

                color = COLORS["board_dark"] if (r + c) % 2 else COLORS["board_light"]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

        self.draw_pieces()

    # Vykreslení figurek
    def draw_pieces(self):
        # pokud je spočítaná velikost pole pokračuj
        if not self.cell:
            return

        self.canvas.delete("piece")

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.board[r][c]
                if piece == EMPTY:
                    continue

                x = self.offset_x + c * self.cell + self.cell / 2
                y = self.offset_y + r * self.cell + self.cell / 2
                radius = self.cell * 0.35

                color = "white" if piece in (WHITE, WHITE_KING) else "black"
                outline = "gold" if piece in (WHITE_KING, BLACK_KING) else "gray"

                self.canvas.create_oval(
                    x - radius, y - radius, x + radius, y + radius,
                    fill=color, outline=outline, width=3, tags="piece"
                )

                if piece in (WHITE_KING, BLACK_KING):
                    self.canvas.create_text(
                        x, y, text="♛",
                        font=("Arial", int(self.cell * 0.4), "bold"),
                        fill="gold" if piece == WHITE_KING else "white",
                        tags="piece"
                    )

    def on_click(self, event):
        if not self.my_turn:
            print("Není tvůj tah!")
            return

        if not self.cell:
            return

        # klik mimo desku -> ignorujeme
        if event.x < self.offset_x or event.y < self.offset_y:
            return
        if event.x >= self.offset_x + self.cell * 8:
            return
        if event.y >= self.offset_y + self.cell * 8:
            return

        c = (event.x - self.offset_x) // self.cell
        r = (event.y - self.offset_y) // self.cell

        c = int(c)
        r = int(r)

        # Pokud není zatím žádná figurka vybrána
        if not self.selected:
            piece = self.board[r][c]
            if (self.my_color == "WHITE" and piece in (WHITE, WHITE_KING)) or \
            (self.my_color == "BLACK" and piece in (BLACK, BLACK_KING)):
                self.selected = (r, c)
                self.highlight_square(r, c)
        # Pokud mám vybranou figurku -> tah
        else:
            from_row, from_col = self.selected
            self.network.send(f"MOVE {from_row} {from_col} {r} {c}")
            self.selected = None
            self.canvas.delete("highlight")
    
    # Zvýrazní vybranou figurku
    def highlight_square(self, r, c):
        if not hasattr(self, "cell"):
            return

        x1 = self.offset_x + c * self.cell
        y1 = self.offset_y + r * self.cell
        x2 = x1 + self.cell
        y2 = y1 + self.cell

        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=COLORS["highlight"],
            width=4,
            tags="highlight"
        )

    def update_from_server(self, board_message: str):
        parts = board_message.strip().split()

        # BOARD + 64 hodnot
        if len(parts) < 65:
            print("Nekompletní BOARD:", board_message)
            return

        values = parts[1:65]

        board = []
        index = 0

        # Naplň 8 řádků po 8 hodnotách
        for _ in range(8):
            row = []
            for _ in range(8):
                row.append(int(values[index]))
                index += 1
            board.append(row)

        self.board = board
        self.draw_pieces() 

    def handle_server_message(self, message: str):
        print("[GUI] Server:", message)

        if message.startswith("BOARD"):
            self.update_from_server(message)

        elif message.startswith("TURN"):
            self.handle_turn_message(message)
        
        elif message.startswith("UPDATE"):
            self.handle_update(message)

        elif message.startswith("CAPTURE"):
            self.handle_capture(message)

        elif message.startswith("PROMOTION"):
            self.handle_promotion(message)

        elif message.startswith("OPPONENT_DISCONNECTED"):
            self.turn_label.config(text="Soupeř se odpojil, čekám...", fg="orange")

        elif message.startswith("OPPONENT_RECONNECTED"):
            self.turn_label.config(text="Soupeř se připojil zpět", fg="green")

        elif message.startswith("GAME_OVER"):
            self.handle_game_over(message)

        elif message.startswith("ERROR"):
            err = message.split(" ", 1)[1].strip() if " " in message else "Neznámá chyba"

            # Reset výběru
            self.selected = None
            self.canvas.delete("highlight")

            # Zobraz chybu jako text
            self.error_label.config(text=f"Chyba: {err}")

            # Auto-hide za 2 sekundy
            self.root.after(2000, lambda: self.error_label.config(text=""))
            return
        
    def restart_to_lobby(self, win):
        win.destroy()
        self.controller.show_lobby(self.my_name)

    def quit_game(self, win):
        """Odpojí hráče a zavře aplikaci."""
        win.destroy()
        try:
            self.network.send("BYE\n")
        except Exception:
            pass
        self.root.destroy()
        sys.exit(0)


    def on_window_close(self):
        try:
            if self.network:
                self.network.send("BYE")
                self.network.close()
        except:
            pass

        # Zavře celé GUI včetně hlavního root
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass

        sys.exit(0)
    
    def handle_turn_message(self, message):
        parts = message.strip().split()
        if len(parts) >= 2:
            color = parts[1].upper()
            text = "Na tahu: BÍLÉ" if color == "WHITE" else "Na tahu: ČERNÉ"
            self.turn_label.config(text=text, fg="#ffffff")
            self.turn_label.config(text=text)
            self.my_turn = (color == self.my_color) 

    def handle_update(self, message):
        # UPDATE fr fc tr tc
        parts = message.strip().split()
        fr, fc, tr, tc = map(int, parts[1:5])

        piece = self.board[fr][fc]
        self.board[fr][fc] = 0
        self.board[tr][tc] = piece

        self.draw_pieces()

    def handle_capture(self, message):
        # CAPTURE r c
        parts = message.strip().split()
        r, c = map(int, parts[1:3])

        self.board[r][c] = 0
        self.draw_pieces()

    def handle_promotion(self, message):
        # PROMOTION r c new_type
        parts = message.strip().split()
        r, c, new_type = map(int, parts[1:4])

        self.board[r][c] = new_type
        self.draw_pieces()
    

    def handle_game_over(self, message):
        parts = message.strip().split()
        result_text = "Konec hry!"
        color = None

        if "WIN" in parts and "DISCONNECT_TIMEOUT" in parts:
            result_text = "Soupeř se odpojil – vyhrál jsi!"
            color = "green"

        elif "WIN" in parts:
            if "WHITE" in parts:
                result_text = "Vyhrály bílé!"
                color = "green"
            elif "BLACK" in parts:
                result_text = "Vyhrály černé!"
                color = "green"
            else:
                result_text = "Vyhrál jsi!"
                color = "green"
            
        elif "LOSE" in parts:
            if "WHITE" in parts:
                result_text = "Prohrál jsi! Vyhrály černé"
                color = "red"
            elif "BLACK" in parts:
                result_text = "Prohrál jsi! Vyhrály bílé"
                color = "red"
            else:
                result_text = "Prohrál jsi!"
                color = "red"

        self.turn_label.config(text=result_text, fg=color)
        self.my_turn = False  # vypne možnost hrát
        self.in_game = False

        # otevři Game Over okno
        GameOverWindow(
            parent=self.root,
            result_text=result_text,
            color=color,
            on_restart=self.restart_to_lobby,
            on_quit=self.quit_game
        )
