import numpy as np
import config


class Board():
    def __init__(self, fen_str) -> None:
        self.board = [
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"]
        ]
        self.piece_mapping = {
            'r': 'bR',
            'n': 'bN',
            'b': 'bB',
            'q': 'bQ',
            'k': 'bK',
            'p': 'bp',
            'R': 'wR',
            'N': 'wN',
            'B': 'wB',
            'Q': 'wQ',
            'K': 'wK',
            'P': 'wp'
        }
        self.white_to_move = True
        self.load_fen(fen_str)

    def load_fen(self, fen):
        # Split the FEN string
        parts = fen.split(" ")
        # Set the board from the first part
        self.set_board_from_fen(parts[0])
        # Set the turn
        self.white_to_move = parts[1] == "w"

    def set_board_from_fen(self, fen_board):
        rows = fen_board.split("/")
        for r in range(8):
            row = rows[r]
            c = 0  # Column index
            for char in row:
                if char.isdigit():
                    c += int(char)  # Skip the empty squares
                else:
                    print(f"Processing piece: {char}")  # Debugging line
                    if c < 8:  # Ensure column index is within bounds
                        if char in self.piece_mapping:  # Ensure the piece is recognized
                            self.board[r][c] = self.piece_mapping[char]  # Place the piece

                        else:
                            print(f"KeyError: Unrecognized piece '{char}'")  # Debugging line
                    c += 1  # Move to the next column

    def set_board_to_fen(self, board):
        fen_rows = []
        for row in board:
            empty_count = 0
            fen_row = ""
            for square in row:
                if square == "--":
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    # Reverse mapping of pieces
                    for key, value in self.piece_mapping.items():
                        if square == value:
                            fen_row += key
                            break
            if empty_count > 0:
                fen_row += str(empty_count)
            fen_rows.append(fen_row)

        # Combine rows into the full FEN string for the board state
        fen_board = "/".join(fen_rows)

        # Add turn information ('w' or 'b')
        fen_turn = "w" if self.white_to_move else "b"

        return f"{fen_board} {fen_turn}"