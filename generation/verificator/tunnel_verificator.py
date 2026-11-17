from collections import deque
from generation.algorithms.digging_agent import get_full_2x2_positions
from generation.models.grid import is_in_grid


def get_tunnel_cells(grid):
    cells = []

    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if grid[x][y].state:
                cells.append((x, y))

    return cells


def is_connected_4(grid):
    tunnel_cells = get_tunnel_cells(grid)

    if len(tunnel_cells) == 0:
        return False

    start = tunnel_cells[0]
    visited = set()
    queue = deque([start])

    directions = [
        (-1, 0),  # haut
        (1, 0),  # bas
        (0, -1),  # gauche
        (0, 1),  # droite
    ]

    while queue:
        x, y = queue.popleft()

        if (x, y) in visited:
            continue

        visited.add((x, y))

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if (
                is_in_grid(grid, nx, ny)
                and grid[nx][ny].state
                and (nx, ny) not in visited
            ):
                queue.append((nx, ny))

    return len(visited) == len(tunnel_cells)


def has_width_one(grid):
    """
    Retourne False s'il existe un carré 2x2 rempli de tunnels.
    """
    height = len(grid)
    width = len(grid[0])

    for x in range(height - 1):
        for y in range(width - 1):
            if (
                grid[x][y].state
                and grid[x + 1][y].state
                and grid[x][y + 1].state
                and grid[x + 1][y + 1].state
            ):
                return False

    return True


def verify_tunnel(grid):
    return is_connected_4(grid) and has_width_one(grid)


def get_verification_report(grid):
    return {
        "is_connected_4": is_connected_4(grid),
        "has_width_one": has_width_one(grid),
        "is_valid": verify_tunnel(grid),
        "full_2x2_positions": get_full_2x2_positions(grid),
    }
