class Move():
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}

    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h":7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_pawn_promotion = None, promoted_piece = 'Q', is_enpassant_move = False, is_castle_move = False) -> None:
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.start_sq = start_sq
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.end_sq = end_sq
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        self.is_pawn_promotion = (self.piece_moved == 'wp' and self.end_row == 0) or (self.piece_moved == 'bp' and self.end_row == 7) if is_pawn_promotion == None else is_pawn_promotion
        self.is_enpassant_move = is_enpassant_move

        if self.is_enpassant_move:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'

        self.is_capture = self.piece_captured != "--"

        self.promoted_piece = promoted_piece

        self.is_castle_move = is_castle_move

        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

        self.same_type_pieces = ""

        self.makes_check = False

        self.makes_checkmate = False

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Move):
            return self.move_ID == value.move_ID
        return False


    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col) if not self.is_pawn_promotion else self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col) + self.promoted_piece.lower()

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]

    def __repr__(self) -> str:
        return f'{self.get_chess_notation()}'

    def __str__(self) -> str:
        if self.is_castle_move:
            return "O-O" if self.end_col == 6 else "O-O-O"

        end_square = self.get_rank_file(self.end_row, self.end_col)

        promotion = ""

        checks = ""
        if self.makes_checkmate:
            checks = "#"
        elif self.makes_check:
            checks = "+"

        if self.piece_moved[1] == 'p':
            if self.is_pawn_promotion == True:
                promotion = "=" + self.promoted_piece
            if self.is_capture:
                return self.cols_to_files[self.start_col] + "x" + end_square + promotion + checks
            else:
                return end_square + promotion + checks

        move_string = self.piece_moved[1] + self.same_type_pieces
        if self.is_capture:
            move_string += 'x'

        return move_string + end_square + checks