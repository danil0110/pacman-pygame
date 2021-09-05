import pygame
from settings import *

vec = pygame.math.Vector2


class Ghost:
    def __init__(self, app, pos):
        self.app = app
        self.grid_pos = pos
        self.pixel_pos = self.get_pixel_pos()

    def get_pixel_pos(self):
        return vec(
            (self.grid_pos.x * self.app.cell_width) + self.app.cell_width // 2,
            (self.grid_pos.y * self.app.cell_height) + TOP_BOTTOM_MARGIN // 2 + self.app.cell_height // 2
        )

    def update(self):
        pass

    def draw(self):
        pygame.draw.circle(self.app.screen, (255, 0, 0), self.pixel_pos, 10)
