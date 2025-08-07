import pygame as p
from config import *


def draw_game_state(screen, gs, valid_moves, sq_selected, move_log_font, dragger):
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board, dragger)
    draw_move_log(screen, gs, move_log_font)


def draw_board(screen):
    colors = [p.Color(238, 216, 192), p.Color(171, 122, 101)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == (
        'w' if gs.white_to_move else 'b'):  # Check if the selected piece belongs to the current player
            # Convert actual coordinates to display coordinates
            display_r = r
            display_c = c
            if PLAYER2 and not PLAYER1:
                display_r = 7 - r
                display_c = 7 - c
                
            # Highlight the selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Transparency value for selected square
            s.fill(p.Color('yellow'))
            screen.blit(s, (display_c * SQ_SIZE, display_r * SQ_SIZE))

            # Highlight the valid move destinations
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    # Convert move end coordinates to display coordinates
                    move_display_r = move.end_row
                    move_display_c = move.end_col
                    if PLAYER2 and not PLAYER1:
                        move_display_r = 7 - move.end_row
                        move_display_c = 7 - move.end_col
                        
                    # Create a transparent surface
                    transparent_circle = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                    transparent_circle.set_alpha(50)  # Set alpha for transparency (0-255)

                    center_x = SQ_SIZE // 2
                    center_y = SQ_SIZE // 2
                    radius = SQ_SIZE // 4
                    color = p.Color('black')

                    # Check if a piece can be captured at the move destination
                    if gs.board[move.end_row][move.end_col] != "--" or move.is_enpassant_move:
                        # Draw a hollow circle (capture move)
                        p.draw.circle(transparent_circle, color, (center_x, center_y), radius * 2, width=5)
                    else:
                        # Draw a filled circle (regular move)
                        p.draw.circle(transparent_circle, color, (center_x, center_y), radius / 2)

                    # Blit the transparent surface onto the main screen
                    screen.blit(transparent_circle, (move_display_c * SQ_SIZE, move_display_r * SQ_SIZE))


def draw_pieces(screen, board, dragger=None):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            # Get the actual board position (not display position)
            actual_r = r
            actual_c = c
            
            # If we're in PLAYER2 mode (black player), flip the coordinates for display
            display_r = r
            display_c = c
            if PLAYER2 and not PLAYER1:
                display_r = 7 - r
                display_c = 7 - c
                actual_r = 7 - r  
                actual_c = 7 - c

            piece = board[actual_r][actual_c]
            if piece != "--":
                # Check if this piece is being dragged - use actual coordinates for comparison
                if dragger and dragger.dragging and (dragger.initial_row == actual_r and dragger.initial_col == actual_c):
                    continue
                # Draw at display coordinates
                screen.blit(IMAGES[piece], p.Rect(display_c * SQ_SIZE, display_r * SQ_SIZE, SQ_SIZE, SQ_SIZE))




def draw_move_log(screen, gs, font):
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("Black"), move_log_rect)
    move_log = gs.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + ". " + str(move_log[i]) + " " * 30
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)
    padding = 5
    line_spacing = 2
    textY = padding

    moves_per_row = 1
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]
        text_object = font.render(text, True, p.Color('White'))
        text_location = move_log_rect.move(padding, textY)

        screen.blit(text_object, text_location)

        textY += text_object.get_height() + line_spacing


def animate_move(move, screen, board, clock):
    # Create flipped view of board and temporary move coordinates if needed
    flipped = PLAYER2 and not PLAYER1

    display_board = [row[::-1] for row in board[::-1]] if flipped else board
    start_row = 7 - move.start_row if flipped else move.start_row
    start_col = 7 - move.start_col if flipped else move.start_col
    end_row = 7 - move.end_row if flipped else move.end_row
    end_col = 7 - move.end_col if flipped else move.end_col

    colors = [p.Color("white"), p.Color("grey")]
    dR = end_row - start_row
    dC = end_col - start_col
    frames_per_square = 10
    frame_count = (abs(dR) + abs(dC)) * frames_per_square

    for frame in range(frame_count + 1):
        r = start_row + dR * frame / frame_count
        c = start_col + dC * frame / frame_count
        draw_board(screen)
        draw_pieces(screen, display_board)

        color = colors[(end_row + end_col) % 2]
        end_square = p.Rect(end_col * SQ_SIZE, end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)

        if move.piece_captured != '--':
            if move.is_enpassant_move:
                enpassant_row = end_row + 1 if move.piece_captured[0] == 'b' else end_row - 1
                end_square = p.Rect(end_col * SQ_SIZE, enpassant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)

        screen.blit(IMAGES[move.piece_moved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

        p.display.flip()
        clock.tick(120)


def draw_end_game_text(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    text_object = font.render(text, 0, p.Color('Grey'))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - text_object.get_height() / 2)

    screen.blit(text_object, text_location)

    text_object = font.render(text, 0, p.Color('Black'))

    screen.blit(text_object, text_location.move(2, 2))