# game.py
from board import Board, WHITE, BLACK, EMPTY

class Game:
    def __init__(self):
        self.board = Board()
        self.current_player = WHITE

    def opponent(self):
        return BLACK if self.current_player == WHITE else WHITE

    def can_move(self, from_row, from_col, to_row, to_col):
        piece = self.board.get_piece(from_row, from_col)
        if piece == EMPTY or piece != self.current_player:
            return False

        target = self.board.get_piece(to_row, to_col)
        if target != EMPTY:
            return False

        dr = to_row - from_row
        dc = abs(to_col - from_col)

        # běžný tah o 1 diagonálně
        if abs(dr) == 1 and dc == 1:
            if piece == WHITE and dr == -1:
                return True
            if piece == BLACK and dr == 1:
                return True

        # braní o 2 diagonálně
        if abs(dr) == 2 and dc == 2:
            mid_row = (from_row + to_row) // 2
            mid_col = (from_col + to_col) // 2
            middle_piece = self.board.get_piece(mid_row, mid_col)
            if middle_piece == self.opponent():
                return True

        return False

    def move(self, fr_row, fr_col, to_row, to_col):
        if not self.can_move(fr_row, fr_col, to_row, to_col):
            return False

        dr = to_row - fr_row
        dc = to_col - fr_col

        # Pokud jde o braní, odstraníme přeskočenou figurku
        if abs(dr) == 2 and abs(dc) == 2:
            mid_row = (fr_row + to_row) // 2
            mid_col = (fr_col + to_col) // 2
            self.board.grid[mid_row][mid_col] = EMPTY

        # provedeme tah
        self.board.move_piece(fr_row, fr_col, to_row, to_col)
        self.switch_turn()
        return True

    def switch_turn(self):
        self.current_player = self.opponent()

    