from board import Board
from move import Move
from castle_rights import CastleRights


class GameState():
    def __init__(self) -> None:
        self.fen_string = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                           "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
                           "4r3/4r3/4k3/8/8/8/8/4K3 w - - 0 1", "8/k7/3p4/p2P1p2/P2P1P2/8/8/K7 w - - 0 1",
                           "qrb5/rk1p1K2/p2P4/Pp6/1N2n3/6p1/5nB1/6b1 w - - 0 1",
                           "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"]

        self.fen_obj = Board(self.fen_string[0])
        self.board = self.fen_obj.board
        self.move_functions = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                               'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}

        self.white_to_move = self.fen_obj.white_to_move
        self.move_log = []
        self.classical_move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.three_fold_repitition = False
        self.enpassant_possible = ()
        self.enpassant_possible_log = [self.enpassant_possible]
        self.current_castle_right = CastleRights(True, True, True, True)
        self.castle_rights_log = [
            CastleRights(self.current_castle_right.wks, self.current_castle_right.bks, self.current_castle_right.wqs,
                         self.current_castle_right.bqs)]

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.classical_move_log.append(str(move))
        self.white_to_move = not self.white_to_move

        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)

        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + move.promoted_piece

        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = '--'

        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = (int((move.start_row + move.end_row) // 2), move.start_col)
        else:
            self.enpassant_possible = ()

        if move.is_castle_move:
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = '--'
            else:
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = '--'

        self.enpassant_possible_log.append(self.enpassant_possible)

        self.update_castle_rights(move)
        self.castle_rights_log.append(
            CastleRights(self.current_castle_right.wks, self.current_castle_right.bks, self.current_castle_right.wqs,
                         self.current_castle_right.bqs))

        if len(self.move_log) >= 10:
            if (self.move_log[-1] == self.move_log[-5] and self.move_log[-1] == self.move_log[-9] and self.move_log[
                -2] == self.move_log[-6] and self.move_log[-2] == self.move_log[-10]) or (
                    self.move_log[-1] == self.move_log[-5] and self.move_log[-1] == self.move_log[-10] and
                    self.move_log[-2] == self.move_log[-6] and self.move_log[-2] == self.move_log[-12] and
                    self.move_log[-3] == self.move_log[-7]):
                self.three_fold_repitition = True

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()

            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move

            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_col)

            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = '--'
                self.board[move.start_row][move.end_col] = move.piece_captured

            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]

        if move.is_castle_move:
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                self.board[move.end_row][move.end_col - 1] = '--'
            else:
                self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = '--'

        self.castle_rights_log.pop()
        self.current_castle_right = self.castle_rights_log[-1]

        self.checkmate = False
        self.stalemate = False

    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':
            self.current_castle_right.wks = False
            self.current_castle_right.wqs = False
        elif move.piece_moved == 'bK':
            self.current_castle_right.bks = False
            self.current_castle_right.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castle_right.wqs = False
                elif move.start_col == 7:
                    self.current_castle_right.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castle_right.bqs = False
                elif move.start_col == 7:
                    self.current_castle_right.bks = False

    def get_valid_moves(self):
        temp_enpassant_possible = self.enpassant_possible
        moves = []
        self.in_check, self.pins, self.checks = self.checks_for_pins_and_checks()

        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]

        if self.in_check:
            self.move_log[-1].makes_check = True

            if len(self.checks) == 1:
                moves = self.get_all_possible_moves()

                check = self.checks[0]

                check_row = check[0]
                check_col = check[1]

                piece_checking = self.board[check_row][check_col]
                valid_squares = []

                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)

                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break

                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved[1] != 'K':
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:
                            moves.remove(moves[i])
            else:
                self.get_king_moves(king_row, king_col, moves)
        else:
            moves = self.get_all_possible_moves()

        if len(moves) == 0:
            if self.in_check:
                self.move_log[-1].makes_checkmate = True
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.enpassant_possible = temp_enpassant_possible

        self.find_same_type_pieces(moves)

        return moves

    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]

                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)

        return moves

    def checks_for_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False

        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))

        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()

            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    elif end_piece[0] == enemy_color:
                        piece_type = end_piece[1]

                        if (0 <= j <= 3 and piece_type == 'R') or \
                                (4 <= j <= 7 and piece_type == 'B') or \
                                (i == 1 and piece_type == 'p' and ((enemy_color == 'w' and 6 <= j <= 7) or (
                                        enemy_color == 'b' and 4 <= j <= 5))) or \
                                (piece_type == 'Q') or (i == 1 and piece_type == 'K'):
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break
                else:
                    break
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))

        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]

                if end_piece[0] == enemy_color and end_piece[1] == 'N':
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))

        return in_check, pins, checks

    def get_pawn_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:
            move_amount = -1
            start_row = 6
            enemy_color = 'b'
            ally_color = 'w'
            king_row, king_col = self.white_king_location
        else:
            move_amount = 1
            start_row = 1
            enemy_color = 'w'
            ally_color = 'b'
            king_row, king_col = self.black_king_location

        # if self.white_to_move:
        if self.board[r + move_amount][c] == "--":
            if not piece_pinned or pin_direction == (move_amount, 0):
                moves.append(Move((r, c), (r + move_amount, c), self.board))
                if r == start_row and self.board[r + 2 * move_amount][c] == "--":
                    moves.append(Move((r, c), (r + 2 * move_amount, c), self.board))
                if (ally_color == 'w' and r + move_amount == 0) or (ally_color == 'b' and r + move_amount == 7):
                    for promoted_piece in {'Q', 'N', 'B', 'R'}:
                        moves.append(Move((r, c), (r + move_amount, c), self.board, is_pawn_promotion=True,
                                          promoted_piece=promoted_piece))

        if c - 1 >= 0:
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[r + move_amount][c - 1][0] == enemy_color:
                    if (ally_color == 'w' and r + move_amount == 0) or (ally_color == 'b' and r + move_amount == 7):
                        for promoted_piece in {'Q', 'N', 'B', 'R'}:
                            moves.append(Move((r, c), (r + move_amount, c - 1), self.board, is_pawn_promotion=True,
                                              promoted_piece=promoted_piece))
                    else:
                        moves.append(Move((r, c), (r + move_amount, c - 1), self.board))
                elif (r + move_amount, c - 1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == r:
                        if king_col < c:
                            inside_range = range(king_col + 1, c - 1)
                            outside_range = range(c + 1, 8)
                        else:
                            inside_range = range(king_col - 1, c, -1)
                            outside_range = range(c - 2, -1, -1)

                        for i in inside_range:
                            if self.board[r][i] != "--":
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[r][i]

                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((r, c), (r + move_amount, c - 1), self.board, is_enpassant_move=True))
        if c + 1 <= 7:
            if not piece_pinned or pin_direction == (move_amount, 1):
                if self.board[r + move_amount][c + 1][0] == enemy_color:
                    if (ally_color == 'w' and r + move_amount == 0) or (ally_color == 'b' and r + move_amount == 7):
                        for promoted_piece in {'Q', 'N', 'B', 'R'}:
                            moves.append(Move((r, c), (r + move_amount, c + 1), self.board, is_pawn_promotion=True,
                                              promoted_piece=promoted_piece))
                    else:
                        moves.append(Move((r, c), (r + move_amount, c + 1), self.board))
                elif (r + move_amount, c + 1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == r:
                        if king_col < c:
                            inside_range = range(king_col + 2, c)
                            outside_range = range(c + 2, 8)
                        else:
                            inside_range = range(king_col - 1, c + 1, -1)
                            outside_range = range(c - 1, -1, -1)

                        for i in inside_range:
                            if self.board[r][i] != "--":
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[r][i]

                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((r, c), (r + move_amount, c + 1), self.board, is_enpassant_move=True))

        # else:
        #     if self.board[r + 1][c] == "--":
        #         if not piece_pinned or pin_direction == (1, 0):
        #             moves.append(Move((r, c), (r + 1, c), self.board))
        #             if r == 1 and self.board[r + 2][c] == "--":
        #                 moves.append(Move((r, c), (r + 2, c), self.board))

        #     if c - 1 >= 0:
        #         if self.board[r + 1][c - 1][0] == "w":
        #             if not piece_pinned or pin_direction == (1, -1):
        #                 moves.append(Move((r, c), (r + 1, c - 1), self.board))
        #         elif  (r + 1, c - 1) == self.enpassant_possible:
        #             if not piece_pinned or pin_direction == (1, -1):
        #                 moves.append(Move((r, c), (r + 1, c - 1), self.board, is_enpassant_move=True))
        #     if c + 1 <= 7:
        #         if self.board[r + 1][c + 1][0] == "w":
        #             if not piece_pinned or pin_direction == (1, 1):
        #                 moves.append(Move((r, c), (r + 1, c + 1), self.board))
        #         elif  (r + 1, c + 1) == self.enpassant_possible:
        #             if not piece_pinned or pin_direction == (1, 1):
        #                 moves.append(Move((r, c), (r + 1, c - 1), self.board, is_enpassant_move=True))

    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]

                        if end_piece == "--":
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def get_knight_moves(self, r, c, moves):
        piece_pinned = False

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))

        ally_color = "w" if self.white_to_move else "b"

        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]

                    if end_piece[0] != ally_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))

        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]

                        if end_piece == "--":
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)

        ally_color = "w" if self.white_to_move else "b"

        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # Ensure the king doesn't move to a square occupied by its own piece
                    # Temporarily move the king to the new square to check for checks
                    original_king_location = (
                        self.white_king_location if ally_color == 'w' else self.black_king_location)
                    if ally_color == 'w':
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)

                    in_check, _, _ = self.checks_for_pins_and_checks()

                    # Only add the move if it doesn't put the king in check
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))

                    # Restore the original king location after the check
                    if ally_color == 'w':
                        self.white_king_location = original_king_location
                    else:
                        self.black_king_location = original_king_location

        self.get_castle_moves(r, c, moves, ally_color)

    def get_castle_moves(self, r, c, moves, ally_color):
        if self.in_check:
            return

        if (self.white_to_move and self.current_castle_right.wks) or (
                not self.white_to_move and self.current_castle_right.bks):
            self.get_king_side_castle_moves(r, c, moves, ally_color)
        if (self.white_to_move and self.current_castle_right.wqs) or (
                not self.white_to_move and self.current_castle_right.bqs):
            self.get_queen_side_castle_moves(r, c, moves, ally_color)

    def get_king_side_castle_moves(self, r, c, moves, ally_color):

        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--' and self.board[r][c + 3][1] == 'R':
            if ally_color == "w":
                original_king_location = self.white_king_location
                self.white_king_location = (self.white_king_location[0], self.white_king_location[1] + 1)
                in_check1, _, _ = self.checks_for_pins_and_checks()
                self.white_king_location = (self.white_king_location[0], self.white_king_location[1] + 1)
                in_check2, _, _ = self.checks_for_pins_and_checks()

                self.white_king_location = original_king_location

            else:
                original_king_location = self.black_king_location
                self.black_king_location = (self.black_king_location[0], self.black_king_location[1] + 1)
                in_check1, _, _ = self.checks_for_pins_and_checks()
                self.black_king_location = (self.black_king_location[0], self.black_king_location[1] + 1)
                in_check2, _, _ = self.checks_for_pins_and_checks()

                self.black_king_location = original_king_location

            if not in_check1 and not in_check2:
                moves.append(Move((r, c), (r, c + 2), self.board, is_castle_move=True))

    def get_queen_side_castle_moves(self, r, c, moves, ally_color):

        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--' and \
                self.board[r][c - 4][1] == 'R':
            if ally_color == "w":
                original_king_location = self.white_king_location
                self.white_king_location = (self.white_king_location[0], self.white_king_location[1] - 1)
                in_check1, _, _ = self.checks_for_pins_and_checks()
                self.white_king_location = (self.white_king_location[0], self.white_king_location[1] - 1)
                in_check2, _, _ = self.checks_for_pins_and_checks()

                self.white_king_location = original_king_location

            else:
                original_king_location = self.black_king_location
                self.black_king_location = (self.black_king_location[0], self.black_king_location[1] - 1)
                in_check1, _, _ = self.checks_for_pins_and_checks()
                self.black_king_location = (self.black_king_location[0], self.black_king_location[1] - 1)
                in_check2, _, _ = self.checks_for_pins_and_checks()

                self.black_king_location = original_king_location

            if not in_check1 and not in_check2:
                moves.append(Move((r, c), (r, c - 2), self.board, is_castle_move=True))

    def find_same_type_pieces(self, valid_moves):
        check_moves = valid_moves

        for check_move in check_moves:
            for move in valid_moves:
                if str(check_move.get_chess_notation()) != str(move.get_chess_notation()):
                    if str(check_move.get_chess_notation())[-1] == str(move.get_chess_notation())[-1] and \
                            str(check_move.get_chess_notation())[-2] == str(move.get_chess_notation())[
                        -2] and check_move.piece_moved == move.piece_moved:
                        if str(check_move.get_chess_notation())[0] == str(move.get_chess_notation())[0]:
                            move.same_type_pieces = str(move.get_chess_notation())[1]
                            check_move.same_type_pieces = str(check_move.get_chess_notation())[1]
                        else:
                            move.same_type_pieces = str(move.get_chess_notation())[0]
                            check_move.same_type_pieces = str(check_move.get_chess_notation())[0]
