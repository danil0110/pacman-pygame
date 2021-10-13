from math import sqrt


class Node:
    def __init__(self, coord, parent_node=None):
        self.coord = coord
        self.parent_node = parent_node
        self.g = 0  # path's cosst
        self.h = 0  # distance to target
        self.f = 0  # total path's cost


def get_neighbours(node, grid):
    (coord_x, coord_y) = node
    neighbour_nodes = [(coord_x + 1, coord_y), (coord_x, coord_y + 1), (coord_x - 1, coord_y), (coord_x, coord_y - 1)]
    
    # Delete adjacent nodes which are out of the grid
    i = 0
    while i != len(neighbour_nodes):
        (x, y) = neighbour_nodes[i]
        if y < 0 or y >= len(grid) or x < 0 or x >= len(grid[0]):
            neighbour_nodes.pop(i)
        else:
            i += 1

    # Filter the nodes
    neighbour_nodes = list(filter(
        lambda node: grid[node[1]][node[0]] != 1 and node[1] >= 0 and node[1] < len(
            grid) and node[0] >= 0 and node[0] < len(grid[0]),
        neighbour_nodes
    ))

    return neighbour_nodes

# Distance between 2 points
def euclidean_distance(start_coord, finish_coord):
    return sqrt(((start_coord[0] - finish_coord[0]) ** 2) + ((start_coord[1] - finish_coord[1]) ** 2))

# Get the actual path
def get_path(finish_node):
    path = []
    current = finish_node
    while current is not None:
        path.append(current.coord)
        current = current.parent_node

    path.reverse()
    return path

# A* algorithm
def a_star(walls, start_coord, finish_coord):
    grid = [[0 for x in range(28)] for x in range(30)]
    for cell in walls:
        if cell.x < 28 and cell.y < 30:
            grid[int(cell.y)][int(cell.x)] = 1

    start_node = Node(start_coord)
    visited = []
    to_visit = []
    to_visit.append(start_node)
    counter = len(grid) * len(grid[0])

    while len(to_visit) != 0 and counter >= 0:
        counter -= 1
        curr_node = to_visit[0]
        curr_index = 0
        for i in range(len(to_visit)):
            # If path cost is less than on the current node
            if to_visit[i].f < curr_node.f:
                curr_node = to_visit[i]
                curr_index = i

        to_visit.pop(curr_index)
        visited.append(curr_node)

        # If reached the target
        if curr_node.coord == finish_coord:
            return get_path(curr_node)

        # Get all neighbours nodes
        neighbours = list(map(lambda coord: Node(coord, curr_node),
                                     get_neighbours(curr_node.coord, grid)))

        # If already visited neighbour nodes exist
        for neighbour in neighbours:
            if len([
                visited_neighbour
                for visited_neighbour in visited
                if visited_neighbour.coord == neighbour.coord
            ]) > 0:
                continue

            neighbour.g = curr_node.g + 1                                   # Increment path's cost
            neighbour.h = euclidean_distance(neighbour.coord, finish_coord) # Calculate distance
            neighbour.f = neighbour.g + neighbour.h                         # Calculate total cost

            # If nodes which we need to visit is already visited, or nodes which path's cost is less exist
            if len([
                    to_visit_node
                    for to_visit_node in to_visit
                    if to_visit_node.coord == neighbour.coord
                    and to_visit_node.g < neighbour.g]) > 0:
                continue

            # Otherwise - append current neighbour
            to_visit.append(neighbour)

    return []
