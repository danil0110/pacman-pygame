import pygame
from settings import *

vec = pygame.math.Vector2


class Ghost:
    def __init__(self, app, pos, number):
        self.app = app
        self.grid_pos = pos
        self.pixel_pos = self.get_pixel_pos()
        self.radius = self.app.cell_width // 2.3
        self.number = number
        self.color = self.set_color()
        self.direction = vec(1, 0)
        self.personality = self.set_personality()
        print(self.personality)

    def update(self):
        self.pixel_pos += self.direction
        if self.time_to_move():
            self.move()

    def draw(self):
        pygame.draw.circle(self.app.screen, self.color, self.pixel_pos, self.radius)

    def time_to_move(self):
        pass

    def move(self):
        pass

    def get_pixel_pos(self):
        return vec(
            (self.grid_pos.x * self.app.cell_width) + self.app.cell_width // 2,
            (self.grid_pos.y * self.app.cell_height) + TOP_BOTTOM_MARGIN // 2 + self.app.cell_height // 2
        )

    def set_color(self):
        if self.number == 0:
            return (0, 255, 255)
        elif self.number == 1:
            return (255, 192, 203)
        elif self.number == 2:
            return (189, 29, 29)
        elif self.number == 3:
            return (215, 159, 33)

    def set_personality(self):
        if self.number == 0:
            return 'speedy'
        elif self.number == 1:
            return 'slow'
        elif self.number == 2:
            return 'random'
        elif self.number == 3:
            return 'scared'
