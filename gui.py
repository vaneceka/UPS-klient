import tkinter as tk
from game import Game, WHITE, BLACK, EMPTY

COLORS = {
    "board_light": "#F0D9B5",
    "board_dark": "#B58863",
    "highlight": "#FFD700"
}

CELL_SIZE = 80  # velikost jednoho políčka (px)

class CheckersGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dáma")
        self.canvas = tk.Canvas(self.root, width=8*CELL_SIZE, height=8*CELL_SIZE)
        self.canvas.pack()
        self.game = Game()
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
                piece = self.game.board.get_piece(r, c)
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
        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE

        if not self.selected:
            piece = self.game.board.get_piece(r, c)
            if piece == self.game.current_player:
                self.selected = (r, c)
                self.highlight_square(r, c)
        else:
            fr_row, fr_col = self.selected
            success = self.game.move(fr_row, fr_col, r, c)
            self.selected = None
            self.draw_board()
            if not success:
                print("❌ Neplatný tah")

    def highlight_square(self, r, c):
        """Zvýrazní vybranou figurku"""
        x1, y1 = c * CELL_SIZE, r * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=COLORS["highlight"], width=4)