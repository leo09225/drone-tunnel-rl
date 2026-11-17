DIRECTIONS = [
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
]


def is_border_cell(grid, x, y):
    return x == 0 or y == 0 or x == len(grid) - 1 or y == len(grid[0]) - 1


def count_tunnel_neighbors(grid, x, y):
    count = 0

    for dx, dy in DIRECTIONS:
        nx = x + dx
        ny = y + dy

        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
            if grid[nx][ny].state:
                count += 1

    return count


def find_start_cell(grid):
    border_tunnel_cells = []
    tunnel_cells = []

    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if grid[x][y].state:
                tunnel_cells.append((x, y))
                if is_border_cell(grid, x, y):
                    border_tunnel_cells.append((x, y))

    if not border_tunnel_cells:
        if tunnel_cells:
            return tunnel_cells[0]
        return None

    endpoints = [
        (x, y)
        for x, y in border_tunnel_cells
        if count_tunnel_neighbors(grid, x, y) == 1
    ]

    if endpoints:
        return endpoints[0]

    return border_tunnel_cells[0]


def mark_start_cell(grid):
    start = find_start_cell(grid)

    if start is None:
        return

    x, y = start
    grid[x][y].depart = True
