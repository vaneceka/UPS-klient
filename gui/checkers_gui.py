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
    def __init__(self, root, my_color="WHITE", my_name = "?", opponent_name = "?"):
        self.root = root
        self.root.title("Dáma")
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.in_game = True
        self.my_color = my_color
        self.my_name = my_name
        self.opponent_name = opponent_name

        # Horní informační panel
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", pady=4)

        # Levá strana
        self.info_label = tk.Label(
            top_frame,
            text=f"Hraješ za: {'BÍLÉ' if self.my_color.upper() == 'WHITE' else 'ČERNÉ'}",
            font=("Arial", 12)
        )
        self.info_label.pack(side="left", padx=8)

        # Pravá strana – soupeř
        self.opponent_label = tk.Label(
            top_frame,
            text=f"Hraješ proti: {self.opponent_name}",
            font=("Arial", 12,)
        )
        self.opponent_label.pack(side="right", padx=10)
        
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
                if piece != 0:
                    x = c * CELL_SIZE + CELL_SIZE / 2
                    y = r * CELL_SIZE + CELL_SIZE / 2
                    radius = CELL_SIZE * 0.35

                    # Barvy figurky
                    color = "white" if piece in (1, 3) else "black"
                    outline = "gold" if piece in (3, 4) else "gray"

                    # Nakresli ovál
                    self.canvas.create_oval(
                        x - radius, y - radius, x + radius, y + radius,
                        fill=color, outline=outline, width=3, tags="piece"
                    )

                    # Pokud je to dáma, přidej korunku
                    if piece in (3, 4):
                        self.canvas.create_text(
                            x, y, text="♛", font=("Arial", 20, "bold"),
                            fill="gold" if piece == 3 else "white",
                            tags="piece"
                        )

    def on_click(self, event):
        if not getattr(self, "my_turn", False):
            print("⏳ Není tvůj tah!")
            return

        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE

        if not self.selected:
            piece = self.board[r][c]
            # ✅ Povolit i výběr dámy (3 a 4)
            if (self.my_color == "WHITE" and piece in (WHITE, 3)) or \
            (self.my_color == "BLACK" and piece in (BLACK, 4)):
                self.selected = (r, c)
                self.highlight_square(r, c)
        else:
            from_row, from_col = self.selected
            # Pošli tah serveru
            self.network.send(f"MOVE {from_row} {from_col} {r} {c}\n")
            self.selected = None
            self.canvas.delete("highlight")
        

    def highlight_square(self, r, c):
        x1, y1 = c * CELL_SIZE, r * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=COLORS["highlight"],
            width=4,
            tags="highlight"
        )

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
            parts = message.strip().split()
            result_text = "🎯 Konec hry!"
            color = None

            if "WIN" in parts:
                if "WHITE" in parts:
                    result_text = "🎉 Vyhrály bílé!"
                    color = "green"
                elif "BLACK" in parts:
                    result_text = "🎉 Vyhrály černé!"
                    color = "green"
                else:
                    result_text = "🎉 Vyhrál jsi!"
                    color = "green"
            elif "LOSE" in parts:
                result_text = "💀 Prohrál jsi!"
                color = "red"

            self.turn_label.config(text=result_text, fg=color)
            self.my_turn = False  # vypne možnost hrát
            self.in_game = False

            # 💬 otevři Game Over okno
            self.show_game_over_screen(result_text)

    def show_game_over_screen(self, result_text):
        """Zobrazí okno s výsledkem hry a tlačítky StyledButton."""
        from gui.styled_button import StyledButton  # import tvé classy

        win = tk.Toplevel(self.root)
        win.title("Konec hry")
        win.geometry("320x200")
        win.configure(bg="#F5F5F5")
        win.resizable(False, False)

        # 🏁 Výsledek
        label = tk.Label(
            win,
            text=result_text,
            font=("Arial", 16, "bold"),
            bg="#F5F5F5",
            fg="green" if "Vyhrál" in result_text or "🎉" in result_text else "red"
        )
        label.pack(pady=25)

        # 🔁 Hrát znovu (jen pokud má smysl)
        StyledButton(
            win,
            text="🔁 Hrát znovu",
            bg_color="#4CAF50",
            hover_color="#45A049",
            command=lambda: self.restart_to_lobby(win)
        ).pack(pady=6)

        # 🚪 Ukončit hru
        StyledButton(
            win,
            text="🚪 Ukončit hru",
            bg_color="#E53935",
            hover_color="#C62828",
            command=lambda: self.quit_game(win)
        ).pack(pady=6)
        
    def restart_to_lobby(self, win):
        """Vrátí hráče zpět do lobby (ve stejném okně)."""
        from gui.lobby_window import LobbyWindow
        win.destroy()

        # Vyčisti hlavní okno hry
        for widget in self.root.winfo_children():
            widget.destroy()

        LobbyWindow(self.root, self.network, self.my_name)

    def quit_game(self, win):
        """Odpojí hráče a zavře aplikaci."""
        win.destroy()
        try:
            self.network.send("BYE\n")
        except Exception:
            pass
        self.root.destroy()

    def on_window_close(self):
        """Zachytí klik na křížek v herním okně."""
        try:
            # pošli BYE jen pokud jsme stále „ve hře“
            if getattr(self, "in_game", False) and hasattr(self, "network"):
                self.network.send("BYE\n")
        except Exception:
            pass
        # zavři hlavní herní okno
        self.root.destroy()