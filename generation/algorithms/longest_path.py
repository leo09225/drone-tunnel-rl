from collections import deque
from generation.models.grid import is_in_grid


def get_connected_component(grid, start_x, start_y):
    queue = deque([(start_x, start_y)])
    visited = set()

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

    return visited


def get_largest_connected_component(grid):
    visited_global = set()
    largest_component = set()

    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if not grid[x][y].state:
                continue

            if (x, y) in visited_global:
                continue

            component = get_connected_component(grid, x, y)
            visited_global.update(component)

            if len(component) > len(largest_component):
                largest_component = component

    return largest_component


def keep_largest_connected_component(grid):
    """
    Garde uniquement le plus grand chemin connecté en 4-voisinage.
    Toutes les autres cellules tunnel deviennent des murs.
    """
    largest_component = get_largest_connected_component(grid)

    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if grid[x][y].state and (x, y) not in largest_component:
                grid[x][y].state = False

    return grid
