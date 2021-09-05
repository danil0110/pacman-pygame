import pygame
import sys
from settings import *

pygame.init()
vec = pygame.math.Vector2


class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'start'

    def run(self):
        while self.running:
            if self.state == 'start':
                self.start_events()
                self.start_update()
                self.start_draw()
            elif self.state == 'play':
                self.play_events()
                self.play_update()
                self.play_draw()
            else:
                self.running = False
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

# HELPERS
    def draw_text(self, string, screen, pos, size, color, font_name, centered = False):
        font = pygame.font.SysFont(font_name, size)
        text = font.render(string, False, color)
        text_size = text.get_size()
        if centered:
            pos[0] = pos[0] - text_size[0] // 2
            pos[1] = pos[1] - text_size[1] // 2
        screen.blit(text, pos)

# START
    def start_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = 'play'

    def start_update(self):
        pass

    def start_draw(self):
        self.screen.fill(BLACK)
        self.draw_text('PUSH SPACE BAR', self.screen, [WIDTH // 2, HEIGHT // 2 - 25], START_TEXT_SIZE,
                       (170, 132, 58), START_FONT, True)
        self.draw_text('1 PLAYER ONLY', self.screen, [WIDTH // 2, HEIGHT // 2 + 25], START_TEXT_SIZE,
                       (44, 167, 198), START_FONT, True)
        self.draw_text('HIGH SCORE', self.screen, [3, 0], START_TEXT_SIZE,
                       (255, 255, 255), START_FONT)
        pygame.display.update()

# PLAY
    def play_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def play_update(self):
        pass

    def play_draw(self):
        self.screen.fill(RED)
        pygame.display.update()
