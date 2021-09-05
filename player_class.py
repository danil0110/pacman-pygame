import pygame
import math
from settings import *

vec = pygame.math.Vector2


class Player:
    def __init__(self, app, pos):
        self.app = app
        self.grid_pos = pos
        self.pixel_pos = self.get_pixel_pos()
        self.direction = vec(1, 0)
        self.stored_direction = None

    def update(self):
        self.pixel_pos += self.direction
        if self.pixel_pos.x % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                if self.stored_direction is not None:
                    self.direction = self.stored_direction
        if int(self.pixel_pos.y + TOP_BOTTOM_MARGIN // 2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                if self.stored_direction is not None:
                    self.direction = self.stored_direction

        # Grid position in reference to pixel position
        self.grid_pos[0] = (self.pixel_pos[0] + self.app.cell_width // 2) // self.app.cell_width
        self.grid_pos[1] = (self.pixel_pos[1] - TOP_BOTTOM_MARGIN + self.app.cell_height // 2) // self.app.cell_height + 1

    def draw(self):
        pygame.draw.circle(self.app.screen, PLAYER_COLOR, (int(self.pixel_pos.x + self.app.cell_width // 2), int(self.pixel_pos.y)),
                           self.app.cell_width // 2 - 2)

        # Grid position rectangle
        pygame.draw.rect(self.app.screen, RED, (self.grid_pos[0] * self.app.cell_width, self.grid_pos[1]
                                                * self.app.cell_height + TOP_BOTTOM_MARGIN // 2, self.app.cell_width,
                                                self.app.cell_height), 1)

    def move(self, direction):
        self.stored_direction = direction

    def get_pixel_pos(self):
        return vec(
            (self.grid_pos.x * self.app.cell_width) + self.app.cell_width // 2,
            (self.grid_pos.y * self.app.cell_height) + TOP_BOTTOM_MARGIN // 2 + self.app.cell_height // 2
        )
