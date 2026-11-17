import random
from generation.models.point import Point
from generation.config import WALL_PERCENTAGE


def create_grid(n, m):

    total_cells = n * m

    num_walls = int(total_cells * WALL_PERCENTAGE)
    num_tunnels = total_cells - num_walls

    # Créer la grille
    grid = []
    cells = []

    for i in range(num_walls):
        cells.append(False)
    for i in range(num_tunnels):
        cells.append(True)

    random.shuffle(cells)

    cell_index = 0
    for i in range(n):
        row = []
        for j in range(m):
            state = cells[cell_index]
            row.append(Point(i, j, state))
            cell_index += 1
        grid.append(row)

    return grid


def create_empty_grid(n, m):
    grid = []

    for i in range(n):
        row = []
        for j in range(m):
            row.append(Point(i, j, False))  # tout est vide
        grid.append(row)

    return grid


def copy_grid_state(source, target):
    for x, source_row in enumerate(source):
        target_row = target[x]
        for y, source_cell in enumerate(source_row):
            target_row[y].state = source_cell.state


def is_in_grid(grid, x, y):
    return 0 <= x < len(grid) and 0 <= y < len(grid[0])


def get_neighbors(grid, x, y):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, 1), (-1, -1), (1, -1)]
    neighbors = []

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if is_in_grid(grid, nx, ny):
            neighbors.append(grid[nx][ny])

    return neighbors


def count_path_neighbors(grid, x, y):
    return sum(1 for p in get_neighbors(grid, x, y) if p.state)
