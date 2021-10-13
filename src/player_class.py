import pygame
import math
from settings import *
from random import randint
from a_star_algorithm import a_star

vec = pygame.math.Vector2


class Player:
    def __init__(self, app, pos):
        self.app = app
        self.grid_pos = pos
        self.starting_pos = [pos.x, pos.y]
        self.pixel_pos = self.get_pixel_pos()
        self.direction = vec(1, 0)
        self.stored_direction = None
        self.speed = 2
        self.able_to_move = True
        self.angry = False
        self.angry_start_time = None
        self.kill_multiplier = 1
        self.current_score = 0
        self.current_score_saved = 0
        self.high_score = 0
        self.lives = 3
        self.winner = False
        self.auto_play = True
        self.coin_target = None
        if self.auto_play:
            self.speed = 1

    def update(self):
        if self.able_to_move:
            self.pixel_pos += self.direction * self.speed
        if self.auto_play:
            self.auto_move()
        elif self.time_to_move():
            if self.stored_direction is not None:
                self.direction = self.stored_direction
            self.able_to_move = self.can_move()
        if self.is_angry():
            if self.angry_start_time is None:
                self.angry_start_time = pygame.time.get_ticks()
            seconds = (pygame.time.get_ticks() - self.angry_start_time) / 1000
            if seconds > 6:
                self.set_angry(False)
            
        # Grid position in reference to pixel position
        self.grid_pos[0] = (self.pixel_pos[0] + self.app.cell_width // 2) // self.app.cell_width
        self.grid_pos[1] = (self.pixel_pos[1] - TOP_BOTTOM_MARGIN + self.app.cell_height // 2) // self.app.cell_height + 1

        if self.on_food(self.app.coins):
            self.eat_coin()
        if self.on_food(self.app.super_food):
            self.eat_super_food()

    def draw(self):
        pygame.draw.circle(self.app.screen, PLAYER_COLOR, (int(self.pixel_pos.x + self.app.cell_width // 2), int(self.pixel_pos.y)),
                           self.app.cell_width // 2 - 2)

        # Player's lives
        for x in range(self.lives):
            pygame.draw.circle(self.app.screen, PLAYER_COLOR, (15 + x * 25, HEIGHT - 15), 10)

        # Grid position rectangle
        # pygame.draw.rect(self.app.screen, RED, (self.grid_pos[0] * self.app.cell_width, self.grid_pos[1]
        #                                         * self.app.cell_height + TOP_BOTTOM_MARGIN // 2, self.app.cell_width,
        #                                         self.app.cell_height), 1)

    def auto_move(self):
        if not self.coin_target:
            self.coin_target = self.set_coin_target()
        self.pixel_pos += self.direction * self.speed
        if self.time_to_move():
            self.auto_move_action()

    def auto_move_action(self):
        self.direction = self.get_path_direction(self.coin_target)

    def get_neighbours(self, node, grid):
        neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
        neighbour_nodes = list(filter(
            lambda current: (node[0] + current[0] >= 0 and node[0] + current[0] < len(grid[0])) and
            (node[1] + current[1] >= 0 and node[1] + current[1] < len(grid)) and
            (grid[node[1] + current[1]][node[0] + current[0]] != 1), neighbours
        ))
        return neighbour_nodes
    
    def get_path_direction(self, target):
        next_cell = self.find_next_cell_in_path(target)
        xdir = next_cell[0] - self.grid_pos[0]
        ydir = next_cell[1] - self.grid_pos[1]
        return vec(xdir, ydir)

    def find_next_cell_in_path(self, target):
        # path = self.BFS([int(self.grid_pos.x), int(self.grid_pos.y)], [int(target[0]), int(target[1])])
        path = a_star(self.app.walls,
                        [int(self.grid_pos.x), int(self.grid_pos.y)],
                        [int(target[0]), int(target[1])])
        if len(path) < 2:
            self.coin_target = None
        else:
            return path[1]

    def set_coin_target(self):
        return self.app.coins[randint(0, len(self.app.coins) - 1)]

    # def BFS(self, start, target):
    #     grid = [[0 for x in range(28)] for x in range(30)]
    #     for cell in self.app.walls:
    #         if cell.x < 28 and cell.y < 30:
    #             grid[int(cell.y)][int(cell.x)] = 1
    #     queue = [start]
    #     path = []
    #     visited = []
    #     while queue:
    #         current = queue[0]
    #         queue.remove(queue[0])
    #         visited.append(current)
    #         if current == target:
    #             break
    #         else:
    #             neighbours = self.get_neighbours(current, grid)
    #             for neighbour in neighbours:
    #                 next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]
    #                 if next_cell not in visited:
    #                     queue.append(next_cell)
    #                     path.append({'Current': current, 'Next': next_cell})
    #     shortest = [target]
    #     while target != start:
    #         for step in path:
    #             if step['Next'] == target:
    #                 target = step['Current']
    #                 shortest.insert(0, step['Current'])

    #     return shortest

    def on_food(self, food):
        if self.grid_pos in food:
            if self.pixel_pos.x % self.app.cell_width == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            if int(self.pixel_pos.y + TOP_BOTTOM_MARGIN // 2) % self.app.cell_height == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    def eat_coin(self):
        self.app.coins.remove(self.grid_pos)
        self.coin_target = None
        self.current_score += 10
        if self.app.coins.__len__() == 0:
            self.app.win()

    def eat_super_food(self):
        self.app.super_food.remove(self.grid_pos)
        self.current_score += 50
        self.set_angry(True)
    
    def set_angry(self, value):
        self.angry = value
        if self.angry:
            for ghost in self.app.ghosts:
                ghost.personality = 'scared'
                ghost.color = (50, 50, 216)
                # ghost.target = vec(ghost.starting_pos[0], ghost.starting_pos[1])
        else:
            self.kill_multiplier = 1
            self.angry_start_time = None
            for ghost in self.app.ghosts:
                ghost.personality = ghost.initial_personality
                ghost.color = ghost.initial_color
                # ghost.target = vec(ghost.starting_pos[0], ghost.starting_pos[1])

    def is_angry(self):
        if self.angry:
            return True
        return False

    def move(self, direction):
        self.stored_direction = direction

    def get_pixel_pos(self):
        return vec(
            (self.grid_pos.x * self.app.cell_width) + self.app.cell_width // 2,
            (self.grid_pos.y * self.app.cell_height) + TOP_BOTTOM_MARGIN // 2 + self.app.cell_height // 2
        )

    def reset_position(self):
        self.grid_pos = vec(self.starting_pos)
        self.pixel_pos = self.get_pixel_pos()
        self.direction *= 0

    def time_to_move(self):
        if self.pixel_pos.x % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pixel_pos.y + TOP_BOTTOM_MARGIN // 2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True
        else:
            return False

    def can_move(self):
        for wall in self.app.walls:
            if vec(self.grid_pos + self.direction) == wall:
                return False
        return True
