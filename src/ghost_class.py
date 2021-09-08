import pygame
import random
from settings import *

vec = pygame.math.Vector2


class Ghost:
    def __init__(self, app, pos, number):
        self.app = app
        self.grid_pos = pos
        self.starting_pos = [pos.x, pos.y]
        self.pixel_pos = self.get_pixel_pos()
        self.radius = self.app.cell_width // 2.3
        self.number = number
        self.initial_color = self.set_color()
        self.color = self.initial_color
        self.direction = vec(0, 0)
        # self.initial_personality = self.set_personality()
        self.initial_personality = 'slow'
        self.personality = self.initial_personality
        self.target = None
        # self.speed = self.set_speed()
        self.speed = 1
        self.respawn_start_time = None

    def update(self):
        if self.is_dead():
            if self.respawn_start_time is None:
                self.respawn_start_time = pygame.time.get_ticks()
            seconds = (pygame.time.get_ticks() - self.respawn_start_time) / 1000
            if seconds > 3:
                self.respawn()
        elif self.target != self.grid_pos or self.personality != 'scared' and self.target == self.starting_pos:
            self.target = self.set_target()
            self.pixel_pos += self.direction * self.speed
            if self.time_to_move():
                self.move()

        # Grid position in reference to pixel position
        self.grid_pos[0] = (self.pixel_pos[0] + self.app.cell_width // 2) // self.app.cell_width
        self.grid_pos[1] = (self.pixel_pos[1] - TOP_BOTTOM_MARGIN + self.app.cell_height // 2) // self.app.cell_height + 1

    def draw(self):
        pygame.draw.circle(self.app.screen, self.color, (int(self.pixel_pos.x + self.app.cell_width // 2), int(self.pixel_pos.y)), self.radius)

    def start_respawn(self):
        self.reset_position()
        self.personality = 'died'
        self.color = (50, 50, 50)

    def respawn(self):
        self.respawn_start_time = None
        self.personality = self.initial_personality
        self.color = self.initial_color

    def is_dead(self):
        if self.personality == 'died':
            return True
        return False

    # def set_speed(self):
    #     if self.personality == 'speedy':
    #         speed = 2
    #     else:
    #         speed = 1
    #     return speed

    def set_target(self):
        if self.personality == 'speedy' or self.personality == 'slow':
            return self.app.player.grid_pos
        elif self.personality == 'scared':
            return self.starting_pos
        # else:
        #     if self.app.player.grid_pos[0] > COLS // 2 and self.app.player.grid_pos[1] > ROWS // 2:
        #         return vec(1, 1)
        #     if self.app.player.grid_pos[0] > COLS // 2 and self.app.player.grid_pos[1] < ROWS // 2:
        #         return vec(1, ROWS - 2)
        #     if self.app.player.grid_pos[0] < COLS // 2 and self.app.player.grid_pos[1] > ROWS // 2:
        #         return vec(COLS - 2, 1)
        #     else:
        #         return vec(COLS - 2, ROWS - 2)

    def time_to_move(self):
        if self.pixel_pos.x % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pixel_pos.y + TOP_BOTTOM_MARGIN // 2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True
        else:
            return False

    def move(self):
        if self.personality == 'random':
            self.direction = self.get_random_direction()
        elif self.personality == 'speedy':
            self.direction = self.get_path_direction(self.target)
        elif self.personality == 'slow':
            self.direction = self.get_path_direction(self.target)
        elif self.personality == 'scared':
            self.direction = self.get_path_direction(self.target)
        # self.direction = self.get_random_direction()

    def get_path_direction(self, target):
        next_cell = self.find_next_cell_in_path(target)
        xdir = next_cell[0] - self.grid_pos[0]
        ydir = next_cell[1] - self.grid_pos[1]
        return vec(xdir, ydir)

    def find_next_cell_in_path(self, target):
        path = self.BFS([int(self.grid_pos.x), int(self.grid_pos.y)],
                        [int(target[0]), int(target[1])])
        return path[1]

    def BFS(self, start, target):
        grid = [[0 for x in range(28)] for x in range(30)]
        for cell in self.app.walls:
            if cell.x < 28 and cell.y < 30:
                grid[int(cell.y)][int(cell.x)] = 1
        queue = [start]
        path = []
        visited = []
        while queue:
            current = queue[0]
            queue.remove(queue[0])
            visited.append(current)
            if current == target:
                break
            else:
                neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                for neighbour in neighbours:
                    if neighbour[0] + current[0] >= 0 and neighbour[0] + current[0] < len(grid[0]):
                        if neighbour[1] + current[1] >= 0 and neighbour[1] + current[1] < len(grid):
                            next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]
                            if next_cell not in visited:
                                if grid[next_cell[1]][next_cell[0]] != 1:
                                    queue.append(next_cell)
                                    path.append({'Current': current, 'Next': next_cell})
        shortest = [target]
        while target != start:
            for step in path:
                if step['Next'] == target:
                    target = step['Current']
                    shortest.insert(0, step['Current'])

        return shortest

    def get_random_direction(self):
        while True:
            number = random.randint(-2, 1)
            if number == -2:
                x_dir, y_dir = 1, 0
            elif number == -1:
                x_dir, y_dir = 0, 1
            elif number == 0:
                x_dir, y_dir = -1, 0
            else:
                x_dir, y_dir = 0, -1
            next_pos = vec(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
            if next_pos not in self.app.walls:
                break
        return vec(x_dir, y_dir)


    def get_pixel_pos(self):
        return vec(
            (self.grid_pos.x * self.app.cell_width),
            (self.grid_pos.y * self.app.cell_height) + TOP_BOTTOM_MARGIN // 2 + self.app.cell_height // 2
        )

    def reset_position(self):
        self.grid_pos = vec(self.starting_pos)
        self.pixel_pos = self.get_pixel_pos()
        self.direction *= 0

    def set_color(self):
        if self.number == 0:
            return (0, 255, 255)
        elif self.number == 1:
            return (255, 192, 203)
        elif self.number == 2:
            return (189, 29, 29)
        elif self.number == 3:
            return (215, 159, 33)

    # def set_personality(self):
    #     if self.number == 0:
    #         return 'slow'
    #     # elif self.number == 1:
    #     #     return 'slow'
    #     # elif self.number == 2:
    #     #     return 'random'
    #     # elif self.number == 3:
    #     #     return 'scared'
    #     else:
    #         return 'slow'
