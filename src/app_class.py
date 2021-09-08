import pygame
import sys
import os.path
import copy
from settings import *
from player_class import *
from ghost_class import *

pygame.init()
vec = pygame.math.Vector2


class App:
    def __init__(self):
        pygame.display.set_caption('Pac-Man')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'start'
        self.cell_width = MAZE_WIDTH // COLS
        self.cell_height = MAZE_HEIGHT // ROWS
        self.walls = []
        self.coins = []
        self.super_food = []
        self.ghosts = []
        self.g_pos = []
        self.p_pos = None
        self.pause_time = None
        self.load()
        self.player = Player(self, vec(self.p_pos))
        self.get_high_score()
        self.make_ghosts()

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
            elif self.state == 'game over':
                self.game_over_events()
                self.game_over_update()
                self.game_over_draw()
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
        self.background = pygame.image.load('assets/maze.png')
        self.background = pygame.transform.scale(self.background, (MAZE_WIDTH, MAZE_HEIGHT))

        # Opening maze file and creating walls list with their coords
        with open('assets/walls.txt', 'r') as file:
            for yidx, line in enumerate(file):
                for xidx, char in enumerate(line):
                    if char == '1':
                        self.walls.append(vec(xidx, yidx))
                    elif char == 'C':
                        self.coins.append(vec(xidx, yidx))
                    elif char == 'S':
                        self.super_food.append(vec(xidx, yidx))
                    elif char == 'P':
                        self.p_pos = [xidx, yidx]
                    elif char in ['2', '3', '4', '5']:
                        self.g_pos.append([xidx, yidx])
                    elif char == 'B':
                        pygame.draw.rect(self.background, BLACK, (xidx * self.cell_width, yidx * self.cell_height, self.cell_width, self.cell_height))

    # Getting high score from a file
    def get_high_score(self):
        # Check if file exists
        if os.path.isfile('../highscore.txt'):
            with open('../highscore.txt', 'r') as file:
                self.player.high_score = int(file.read())
        else:
            self.set_high_score(0)

    def set_high_score(self, new_score):
        self.player.high_score = new_score
        with open('../highscore.txt', 'w') as file:
            file.write(str(new_score))

    def make_ghosts(self):
        for idx, pos in enumerate(self.g_pos):
            self.ghosts.append(Ghost(self, vec(pos), idx))

    def draw_grid(self):
        for x in range(MAZE_WIDTH // self.cell_width):
            pygame.draw.line(self.background, GREY, (x * self.cell_width, 0), (x * self.cell_width, MAZE_HEIGHT))
        for y in range(MAZE_HEIGHT // self.cell_height):
            pygame.draw.line(self.background, GREY, (0, y * self.cell_height), (MAZE_WIDTH, y * self.cell_height))
        # for wall in self.walls:
        #     pygame.draw.rect(self.background, (0, 255, 0), (wall.x * self.cell_width, wall.y * self.cell_height, self.cell_width, self.cell_height))
        for coin in self.coins:
            pygame.draw.rect(self.background, (167, 167, 0), (coin.x * self.cell_width, coin.y * self.cell_height, self.cell_width, self.cell_height))

    def restart(self, is_after_win = False):
        if not is_after_win:
            self.player.lives = 3
            self.player.current_score = 0
        self.player.reset_position()
        for ghost in self.ghosts:
            ghost.reset_position()
            ghost.personality = 'slow'

        self.coins = []
        self.super_food = []
        with open('assets/walls.txt', 'r') as file:
            for yidx, line in enumerate(file):
                for xidx, char in enumerate(line):
                    if char == 'C':
                        self.coins.append(vec(xidx, yidx))
                    if char == 'S':
                        self.super_food.append(vec(xidx, yidx))
        self.state = 'play'

    def win(self):
        self.player.winner = True
        self.player.direction *= 0
        
        for ghost in self.ghosts:
            ghost.personality = 'stay'
            ghost.direction *= 0
        
        

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
        self.draw_text('HIGH SCORE: {}'.format(self.player.high_score), self.screen, [3, 0], START_TEXT_SIZE,
                       WHITE, START_FONT)
        pygame.display.update()

# PLAY
    def play_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and self.player.winner == False:
                if event.key == pygame.K_UP:
                    self.player.move(vec(0, -1))
                if event.key == pygame.K_RIGHT:
                    self.player.move(vec(1, 0))
                if event.key == pygame.K_DOWN:
                    self.player.move(vec(0, 1))
                if event.key == pygame.K_LEFT:
                    self.player.move(vec(-1, 0))

    def play_update(self):
        if self.player.winner:
            if self.pause_time is None:
                self.pause_time = pygame.time.get_ticks()
            seconds = (pygame.time.get_ticks() - self.pause_time) / 1000
            if seconds > 3:
                self.pause_time = None
                self.player.winner = False
                self.restart(True)

        self.player.update()
        for ghost in self.ghosts:
            ghost.update()

        for ghost in self.ghosts:
            if ghost.grid_pos == self.player.grid_pos:
                if ghost.personality not in ['scared', 'died']:
                    self.decrease_lives()
                else:
                    self.player.current_score += (2 ** self.player.kill_multiplier) * 100
                    if self.player.kill_multiplier < 4:
                        self.player.kill_multiplier += 1
                    ghost.start_respawn()


    def play_draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.background, (0, TOP_BOTTOM_MARGIN // 2))
        self.draw_coins()
        self.draw_super_food()
        # self.draw_grid()
        self.draw_text('CURRENT SCORE: {}'.format(self.player.current_score), self.screen, [20, 0], 18, WHITE, START_FONT)
        self.draw_text('HIGH SCORE: {}'.format(self.player.high_score), self.screen, [WIDTH // 2 + 40, 0], 18, WHITE, START_FONT)
        self.player.draw()
        for ghost in self.ghosts:
            ghost.draw()

        pygame.display.update()

    def decrease_lives(self):
        self.player.lives -= 1
        if self.player.lives == 0:
            self.state = 'game over'
            self.player.current_score_saved = self.player.current_score
            if self.player.current_score > self.player.high_score:
                self.set_high_score(self.player.current_score)
        else:
            self.player.reset_position()
            for ghost in self.ghosts:
                ghost.reset_position()

    def draw_coins(self):
        for coin in self.coins:
            pygame.draw.circle(self.screen, (167, 167, 0),
                               (int(coin.x * self.cell_width + self.cell_width // 2),
                                int(coin.y * self.cell_height + self.cell_height // 2 + TOP_BOTTOM_MARGIN // 2)), 2)

    def draw_super_food(self):
        for food in self.super_food:
            pygame.draw.circle(self.screen, (167, 167, 0),
                               (int(food.x * self.cell_width + self.cell_width // 2),
                                int(food.y * self.cell_height + self.cell_height // 2 + TOP_BOTTOM_MARGIN // 2)), 6)


# GAME OVER
    def game_over_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.restart()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def game_over_update(self):
        pass

    def game_over_draw(self):
        self.screen.fill(BLACK)
        quit_text = 'PRESS ESC TO QUIT'
        replay_text = 'PRESS SPACE BAR TO PLAY AGAIN'
        high_score_text = 'HIGH SCORE: {}'.format(self.player.high_score)
        current_score_text = 'CURRENT SCORE: {}'.format(self.player.current_score_saved)
        self.draw_text('GAME OVER', self.screen, [WIDTH // 2, 80], 52, RED, 'arial black', True)
        self.draw_text(current_score_text, self.screen, [WIDTH // 2, 170], 24, WHITE, 'arial', True)
        self.draw_text(high_score_text, self.screen, [WIDTH // 2, 200], 24, WHITE, 'arial', True)
        self.draw_text(replay_text, self.screen, [WIDTH // 2, HEIGHT // 2], 28, WHITE, 'arial', True)
        self.draw_text(quit_text, self.screen, [WIDTH // 2,  HEIGHT // 2 + 100], 24, GREY, 'arial', True)
        pygame.display.update()
