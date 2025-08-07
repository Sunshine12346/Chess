import pygame as p
import engine, ai as ai
from multiprocessing import Process, Queue
from draw import *
from config import *
from dragger import Dragger

logs = []


def load_images():
    pieces = ["bp", "bR", "bN", "bB", "bQ", "bK", "wp", "wR", "wN", "wB", "wQ", "wK"]

    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"assets/images/{piece}.png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    move_log_font = p.font.SysFont("Arial", 18, True, False)
    gs = engine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False
    animate = False

    load_images()
    dragger = Dragger()  # Initialize the dragger
    running = True
    sq_selected = ()
    player_clicks = []
    game_over = False

    AIThinking = False
    move_finder_process = None
    move_undone = False

    while running:
        human_turn = (gs.white_to_move and PLAYER1) or (not gs.white_to_move and PLAYER2)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # Get mouse (x, y) position
                    col = int(location[0] // SQ_SIZE)
                    row = int(location[1] // SQ_SIZE)
                    
                    # Convert display coordinates to actual board coordinates if needed
                    actual_row = row
                    actual_col = col
                    if PLAYER2 and not PLAYER1:
                        actual_row = 7 - row
                        actual_col = 7 - col

                    if sq_selected == (actual_row, actual_col) or col >= 8:  # Deselect if clicked same square or outside board
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (actual_row, actual_col)
                        player_clicks.append(sq_selected)

                        # Start dragging the piece on mouse down
                        if gs.board[actual_row][actual_col] != "--":
                            dragger.start_dragging(gs.board[actual_row][actual_col], (actual_row, actual_col))

            elif e.type == p.MOUSEMOTION:
                if dragger.dragging:
                    dragger.update_mouse(p.mouse.get_pos())  # Update mouse position while dragging

            elif e.type == p.MOUSEBUTTONUP:
                if dragger.dragging:
                    dragger.stop_dragging()  # Stop dragging when mouse button is released
                    location = p.mouse.get_pos()
                    col = int(location[0] // SQ_SIZE)
                    row = int(location[1] // SQ_SIZE)
                    
                    # Convert display coordinates to actual board coordinates if needed
                    actual_row = row
                    actual_col = col
                    if PLAYER2 and not PLAYER1:
                        actual_row = 7 - row
                        actual_col = 7 - col
                    
                    move = engine.Move((dragger.initial_row, dragger.initial_col), (actual_row, actual_col), gs.board)

                    if move.is_pawn_promotion:
                        promoted_piece = input("Enter what do you want the pawn to promote into: ")
                        move.promoted_piece = promoted_piece

                    for i in range(len(valid_moves)):
                        if move.get_chess_notation() == valid_moves[i].get_chess_notation():
                            gs.make_move(valid_moves[i])
                            move_made = True
                            animate = False
                            sq_selected = ()
                            player_clicks = []
                    if not move_made:
                        player_clicks = [sq_selected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                    if AIThinking:
                        move_finder_process.terminate()
                        AIThinking = False
                    move_undone = True
                if e.key == p.K_r:
                    gs = engine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if AIThinking:
                        move_finder_process.terminate()
                        AIThinking = False
                    move_undone = True

        if not game_over and not human_turn and not move_undone:
            if not AIThinking:
                AIThinking = True
                print("thinking...")
                returnQueue = Queue()
                move_finder_process = Process(target=ai.find_best_move, args=(gs, valid_moves, returnQueue))
                move_finder_process.start()

            if not move_finder_process.is_alive():
                print("done thinking!")
                AIMove = returnQueue.get()
                if AIMove is None:
                    print("x")
                    AIMove = ai.find_random_move(valid_moves)
                gs.make_move(AIMove)
                move_made = True
                animate = True
                AIThinking = False

        if move_made:
            if animate:
                animate_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False
            move_undone = False

            if gs.checkmate:
                if gs.white_to_move:
                    print("Black Won by checkmate!")
                else:
                    print("White Won by checkmate!")
            if gs.stalemate:
                print("Draw by Stalemate!")

        draw_game_state(screen, gs, valid_moves, sq_selected, move_log_font, dragger)

        if gs.checkmate:
            game_over = True
            if gs.white_to_move:
                draw_end_game_text(screen, "Black wins by Checkmate")
            else:
                draw_end_game_text(screen, "White wins by Checkmate")
        elif gs.stalemate:
            game_over = True
            draw_end_game_text(screen, "Stalemate")

        # Render the dragged piece on top of everything
        dragger.render(screen)

        clock.tick(MAX_FPS)
        p.display.flip()


if __name__ == "__main__":
    main()