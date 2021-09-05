import pygame
import sys
from settings import *
from player_class import *

pygame.init()
vec = pygame.math.Vector2


class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'start'
        self.cell_width = MAZE_WIDTH // 28
        self.cell_height = MAZE_HEIGHT // 30
        self.player = Player(self, PLAYER_START_POS)

        self.load()

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

    def load(self):
        self.background = pygame.image.load('maze.png')
        self.background = pygame.transform.scale(self.background, (MAZE_WIDTH, MAZE_HEIGHT))

    def draw_grid(self):
        for x in range(MAZE_WIDTH // self.cell_width):
            pygame.draw.line(self.background, GREY, (x * self.cell_width, 0), (x * self.cell_width, MAZE_HEIGHT))
        for y in range(MAZE_HEIGHT // self.cell_height):
            pygame.draw.line(self.background, GREY, (0, y * self.cell_height), (MAZE_WIDTH, y * self.cell_height))

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
                       WHITE, START_FONT)
        pygame.display.update()

# PLAY
    def play_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.player.move(vec(0, -1))
                if event.key == pygame.K_RIGHT:
                    self.player.move(vec(1, 0))
                if event.key == pygame.K_DOWN:
                    self.player.move(vec(0, 1))
                if event.key == pygame.K_LEFT:
                    self.player.move(vec(-1, 0))

    def play_update(self):
        self.player.update()

    def play_draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.background, (0, TOP_BOTTOM_MARGIN // 2))
        self.draw_grid()
        self.draw_text('CURRENT SCORE: 0', self.screen, [40, 0], 18, WHITE, START_FONT)
        self.draw_text('HIGH SCORE: 0', self.screen, [WIDTH // 2 + 50, 0], 18, WHITE, START_FONT)
        self.player.draw()
        pygame.display.update()
