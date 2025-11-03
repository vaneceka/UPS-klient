import tkinter as tk

WHITE = 1
BLACK = 2
EMPTY = 0

COLORS = {
    "board_light": "#F0D9B5",
    "board_dark": "#B58863",
    "highlight": "#FFD700"
}

CELL_SIZE = 80  # velikost jednoho políčka (px)
BOARD_SIZE = 8

class CheckersGUI:
    def __init__(self, root, my_color="WHITE"):
        self.root = root
        self.root.title("Dáma")
        self.my_color = my_color

        # Horní informační panel
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", pady=4)

        self.info_label = tk.Label(
            top_frame,
            text=f"Hraješ za: {'BÍLÉ' if self.my_color.upper() == 'WHITE' else 'ČERNÉ'}",
            font=("Arial", 12)
        )
        self.info_label.pack(side="left", padx=8)

        self.turn_label = tk.Label(
            top_frame,
            text="Čekám na server...",
            font=("Arial", 12)
        )
        self.turn_label.pack(side="right", padx=8)


        self.canvas = tk.Canvas(self.root, width=8*CELL_SIZE, height=8*CELL_SIZE)
        self.canvas.pack()
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.selected = None
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_board(self):
        """Vykreslí celou šachovnici"""
        for r in range(8):
            for c in range(8):
                color = COLORS["board_dark"] if (r + c) % 2 else COLORS["board_light"]
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

        self.update_board()

    def update_board(self):
        """Vykreslí figurky"""
        self.canvas.delete("piece")
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != EMPTY:
                    x = c * CELL_SIZE + CELL_SIZE / 2
                    y = r * CELL_SIZE + CELL_SIZE / 2
                    radius = CELL_SIZE * 0.35
                    color = "white" if piece == WHITE else "black"
                    self.canvas.create_oval(
                        x - radius, y - radius, x + radius, y + radius,
                        fill=color, outline="gray", width=2, tags="piece"
                    )

    def on_click(self, event):
        if not self.my_turn:
            print("⏳ Není tvůj tah!")
            return

        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE

        if not self.selected:
            piece = self.board[r][c]
            if (self.my_color == "WHITE" and piece == WHITE) or (self.my_color == "BLACK" and piece == BLACK):
                self.selected = (r, c)
                self.highlight_square(r, c)
        else:
            from_row, from_col = self.selected
            self.network.send(f"MOVE {from_row} {from_col} {r} {c}\n")
            self.selected = None

    def highlight_square(self, r, c):
        """Zvýrazní vybranou figurku"""
        x1, y1 = c * CELL_SIZE, r * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=COLORS["highlight"], width=4)

    def update_from_server(self, board_message: str):
        """Aktualizuje hrací desku podle zprávy BOARD ..."""
        parts = board_message.strip().split()
        values = parts[1:]
        if len(values) < 64:
            print("⚠️ BOARD nekompletní:", board_message)
            return

        # Převeď data do 8x8 matice
        nums = [int(x) for x in values[:64]]
        self.board = [nums[i*8:(i+1)*8] for i in range(8)]

        # Vykresli figurky
        self.update_board()

    def handle_server_message(self, message: str):
        print("📩 [GUI] Server:", message)

        if message.startswith("BOARD"):
            self.update_from_server(message)
        elif message.startswith("TURN"):
            parts = message.strip().split()
            if len(parts) >= 2:
                color = parts[1].upper()
                text = "Na tahu: BÍLÉ" if color == "WHITE" else "Na tahu: ČERNÉ"
                self.turn_label.config(text=text)
                self.my_turn = (color == self.my_color)  # ✅ tvůj tah
        elif message.startswith("GAME_OVER"):
            self.turn_label.config(text="🎯 Konec hry!")