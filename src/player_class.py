from settings import *
from minimax_class import *

vec = pygame.math.Vector2


class Player:
    def __init__(self, app, pos):
        self.app = app
        self.starting_pos = [pos.x, pos.y]
        self.grid_pos = pos
        self.pix_pos = self.get_pix_pos()
        self.direction = vec(0, 0)
        self.search_type = "minimax"
        self.stored_direction = None
        self.able_to_move = True
        self.current_score = 0
        self.speed = SPEED
        self.lives = LIVES

    def update(self, real_update):

        if self.able_to_move:
            self.pix_pos += self.direction * self.speed

        self.grid_pos = self.get_grid_pos_from_pix_pos(self.pix_pos)

        if real_update == "yes":
            if self.time_to_move():
                self.change_direction_if_possible()

            if self.on_coin():
                self.eat_coin()

    def draw(self):
        pygame.draw.circle(self.app.screen, PLAYER_COLOUR, (int(self.pix_pos.x),
                                                            int(self.pix_pos.y)), self.app.cell_width // 2 - 10)

        # Drawing player lives
        for x in range(self.lives):
            pygame.draw.circle(self.app.screen, PLAYER_COLOUR, (30 + 20 * x, HEIGHT - 15), 7)

    def on_coin(self):
        if self.grid_pos in self.app.coins:
            if int(self.pix_pos.x - TOP_BOTTOM_BUFFER // 2 - self.app.cell_width // 2) % self.app.cell_width == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            if int(self.pix_pos.y - TOP_BOTTOM_BUFFER // 2 - self.app.cell_height // 2) % self.app.cell_height == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    def eat_coin(self):
        self.app.coins.remove(self.grid_pos)
        self.current_score += 1

    def move(self, direction):
        self.stored_direction = direction

    def get_grid_pos_from_pix_pos(self, pix_pos):
        return vec((pix_pos[0] - TOP_BOTTOM_BUFFER // 2 - self.app.cell_width // 2) // self.app.cell_width,
                (pix_pos[1] - TOP_BOTTOM_BUFFER // 2 - self.app.cell_height // 2) // self.app.cell_height)

    def get_pix_pos(self):
        return vec((self.grid_pos[0] * self.app.cell_width) + TOP_BOTTOM_BUFFER // 2 + self.app.cell_width // 2,
                   (self.grid_pos[1] * self.app.cell_height) +
                   TOP_BOTTOM_BUFFER // 2 + self.app.cell_height // 2)

    def get_pix_pos_from_grid_pos(self, grid_cell):
        return vec((grid_cell[0] * self.app.cell_width) + TOP_BOTTOM_BUFFER // 2 + self.app.cell_width // 2,
                   (grid_cell[1] * self.app.cell_height) +
                   TOP_BOTTOM_BUFFER // 2 + self.app.cell_height // 2)

    def get_pix_pos_from_grid_pos_for_rect(self, x, y):
        return vec(int((x * self.app.cell_width) + TOP_BOTTOM_BUFFER // 2),
                   int((y * self.app.cell_height) + TOP_BOTTOM_BUFFER // 2))

    def time_to_move(self):
        if (self.pix_pos.x - TOP_BOTTOM_BUFFER // 2 - self.app.cell_width // 2) % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True

        if (self.pix_pos.y - TOP_BOTTOM_BUFFER // 2 - self.app.cell_height // 2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True

    def change_direction_if_possible(self):
        if self.stored_direction is not None and (self.grid_pos + self.stored_direction) not in self.app.walls:
            self.direction = self.stored_direction
            self.able_to_move = True
        elif (self.grid_pos + self.direction) not in self.app.walls:
            self.able_to_move = True
        else:
            self.able_to_move = False

    def bfs(self, start, target):
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
                    next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]
                    if next_cell not in visited and self.app.game_field[int(next_cell[1])][int(next_cell[0])] != 1:
                        queue.append(next_cell)
                        path.append({"Current": current, "Next": next_cell})

        real_path = [target]
        while target != start:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    real_path.insert(0, step["Current"])

        return real_path
