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
        self.able_to_move = True
        self.current_score = 0

    def update(self):
        if self.able_to_move:
            self.pixel_pos += self.direction
        if self.time_to_move():
            if self.stored_direction is not None:
                self.direction = self.stored_direction
            self.able_to_move = self.can_move()

        # Grid position in reference to pixel position
        self.grid_pos[0] = (self.pixel_pos[0] + self.app.cell_width // 2) // self.app.cell_width
        self.grid_pos[1] = (self.pixel_pos[1] - TOP_BOTTOM_MARGIN + self.app.cell_height // 2) // self.app.cell_height + 1

        if self.on_coin():
            self.eat_coin()

    def draw(self):
        pygame.draw.circle(self.app.screen, PLAYER_COLOR, (int(self.pixel_pos.x + self.app.cell_width // 2), int(self.pixel_pos.y)),
                           self.app.cell_width // 2 - 2)

        # Grid position rectangle
        # pygame.draw.rect(self.app.screen, RED, (self.grid_pos[0] * self.app.cell_width, self.grid_pos[1]
        #                                         * self.app.cell_height + TOP_BOTTOM_MARGIN // 2, self.app.cell_width,
        #                                         self.app.cell_height), 1)

    def on_coin(self):
        if self.grid_pos in self.app.coins:
            return True
        return False

    def eat_coin(self):
        self.app.coins.remove(self.grid_pos)
        self.current_score += 1

    def move(self, direction):
        self.stored_direction = direction

    def get_pixel_pos(self):
        return vec(
            (self.grid_pos.x * self.app.cell_width) + self.app.cell_width // 2,
            (self.grid_pos.y * self.app.cell_height) + TOP_BOTTOM_MARGIN // 2 + self.app.cell_height // 2
        )

    def time_to_move(self):
        if self.pixel_pos.x % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                return True
        if int(self.pixel_pos.y + TOP_BOTTOM_MARGIN // 2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                return True
        else:
            return False

    def can_move(self):
        for wall in self.app.walls:
            if vec(self.grid_pos + self.direction) == wall:
                return False
        return True
