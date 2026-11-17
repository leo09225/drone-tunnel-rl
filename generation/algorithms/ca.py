from generation.config import GRID_HEIGHT, GRID_WIDTH, ITERATION
from generation.models.grid import copy_grid_state, create_grid
from generation.rules.rules import rules_update


def create_ca_grid(n=GRID_WIDTH, m=GRID_HEIGHT):
    return create_grid(n, m)


def grid_to_matrix(grid):
    return [[1 if cell.state else 0 for cell in row] for row in grid]


def ca_step(grid_old, grid_new):
    rules_update(grid_old, grid_new)


def clone_grid(grid):
    cloned_grid = create_grid(len(grid), len(grid[0]))
    copy_grid_state(grid, cloned_grid)
    return cloned_grid


def generate_tunnel_ca(n=GRID_WIDTH, m=GRID_HEIGHT, iterations=ITERATION):
    grid_1 = create_ca_grid(n, m)
    grid_2 = create_ca_grid(n, m)

    for i in range(iterations):
        if i % 2 == 0:
            ca_step(grid_1, grid_2)
        else:
            ca_step(grid_2, grid_1)

    return grid_1 if iterations % 2 == 0 else grid_2
