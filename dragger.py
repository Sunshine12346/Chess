from config import IMAGES, SQ_SIZE
import pygame as p

class Dragger:
    def __init__(self):
        self.piece = None
        self.dragging = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.initial_row = 0
        self.initial_col = 0

    def update_mouse(self, pos):
        self.mouse_x, self.mouse_y = pos

    def start_dragging(self, piece, initial_pos):
        self.piece = piece
        self.initial_row, self.initial_col = initial_pos
        self.dragging = True
        self.mouse_x, self.mouse_y = p.mouse.get_pos()

    def stop_dragging(self):
        self.dragging = False
        self.piece = None

    def render(self, screen):
        # Render the piece centered at the current mouse position
        if self.dragging and self.piece:
            pos_x = self.mouse_x - SQ_SIZE // 2
            pos_y = self.mouse_y - SQ_SIZE // 2
            screen.blit(IMAGES[self.piece], p.Rect(pos_x, pos_y, SQ_SIZE, SQ_SIZE))
