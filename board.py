# board.py
EMPTY, WHITE, BLACK = ".", "w", "b"

class Board:
    def __init__(self):
        self.grid = self._create_initial_board()

    def _create_initial_board(self):
        board = [[EMPTY for _ in range(8)] for _ in range(8)]
        # černé figurky nahoře
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = BLACK
        # bílé figurky dole
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = WHITE
        return board

    def move_piece(self, from_row, from_col, to_row, to_col):
        piece = self.grid[from_row][from_col]
        self.grid[from_row][from_col] = EMPTY
        self.grid[to_row][to_col] = piece

    def get_piece(self, row, col):
        return self.grid[row][col]

    def print_board(self):
        for row in self.grid:
            print(" ".join(row))