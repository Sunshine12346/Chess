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
        self.offset_x = 0  # Add offset for smooth dragging
        self.offset_y = 0  # Add offset for smooth dragging

    def update_mouse(self, pos):
        self.mouse_x, self.mouse_y = pos

    def start_dragging(self, piece, initial_pos):
        self.piece = piece
        self.initial_row, self.initial_col = initial_pos
        self.dragging = True
        self.mouse_x, self.mouse_y = p.mouse.get_pos()

        # Calculate the offset based on where in the square the mouse was clicked
        self.offset_x = self.mouse_x - self.initial_col * SQ_SIZE
        self.offset_y = self.mouse_y - self.initial_row * SQ_SIZE

    def stop_dragging(self):
        self.dragging = False
        self.piece = None

    def render(self, screen):
        # Render the piece at the current mouse position, adjusting for the offset
        if self.dragging and self.piece:
            pos_x = self.mouse_x - self.offset_x
            pos_y = self.mouse_y - self.offset_y
            screen.blit(IMAGES[self.piece], p.Rect(pos_x, pos_y, SQ_SIZE, SQ_SIZE))
