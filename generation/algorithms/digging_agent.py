import random

from generation.models.grid import create_empty_grid, is_in_grid, copy_grid_state


DIRECTIONS = [
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
]


def clone_grid(grid):
    cloned_grid = create_empty_grid(len(grid), len(grid[0]))
    copy_grid_state(grid, cloned_grid)
    return cloned_grid


def get_full_2x2_positions(grid):
    positions = []

    for x in range(len(grid) - 1):
        for y in range(len(grid[0]) - 1):
            if (
                grid[x][y].state
                and grid[x + 1][y].state
                and grid[x][y + 1].state
                and grid[x + 1][y + 1].state
            ):
                positions.append((x, y))

    return positions


def count_neighbors_4(grid, x, y):
    count = 0

    for dx, dy in DIRECTIONS:
        nx = x + dx
        ny = y + dy

        if is_in_grid(grid, nx, ny) and grid[nx][ny].state:
            count += 1

    return count


def would_create_full_2x2(grid, x, y):
    for sx in [x - 1, x]:
        for sy in [y - 1, y]:
            if sx < 0 or sy < 0:
                continue

            if sx >= len(grid) - 1 or sy >= len(grid[0]) - 1:
                continue

            cells = [
                (sx, sy),
                (sx + 1, sy),
                (sx, sy + 1),
                (sx + 1, sy + 1),
            ]

            if all(grid[i][j].state or (i, j) == (x, y) for i, j in cells):
                return True

    return False


def is_valid_dig(grid, x, y):
    if not is_in_grid(grid, x, y):
        return False

    if grid[x][y].state:
        return False

    if count_neighbors_4(grid, x, y) != 1:
        return False

    if would_create_full_2x2(grid, x, y):
        return False

    return True


def is_valid_loop_cell(grid, x, y):
    if not is_in_grid(grid, x, y):
        return False

    if grid[x][y].state:
        return False

    neighbors = count_neighbors_4(grid, x, y)

    if neighbors != 2:
        return False

    if would_create_full_2x2(grid, x, y):
        return False

    return True


def get_frontier_cells(grid):
    frontier = []

    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if not grid[x][y].state:
                continue

            valid_moves = []

            for dx, dy in DIRECTIONS:
                nx = x + dx
                ny = y + dy

                if is_valid_dig(grid, nx, ny):
                    valid_moves.append((nx, ny, (dx, dy)))

            if valid_moves:
                frontier.append((x, y, valid_moves))

    return frontier


def get_loop_candidates(grid):
    candidates = []

    for x in range(1, len(grid) - 1):
        for y in range(1, len(grid[0]) - 1):
            if is_valid_loop_cell(grid, x, y):
                candidates.append((x, y))

    return candidates


def is_connected(grid):
    cells = []

    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if grid[x][y].state:
                cells.append((x, y))

    if not cells:
        return True

    start = cells[0]
    visited = {start}
    stack = [start]

    while stack:
        x, y = stack.pop()

        for dx, dy in DIRECTIONS:
            nx = x + dx
            ny = y + dy

            if (
                is_in_grid(grid, nx, ny)
                and grid[nx][ny].state
                and (nx, ny) not in visited
            ):
                visited.add((nx, ny))
                stack.append((nx, ny))

    return len(visited) == len(cells)


def choose_directions(direction, rng, turn_probability):
    if rng.random() > turn_probability:
        other_directions = [d for d in DIRECTIONS if d != direction]
        rng.shuffle(other_directions)
        return [direction] + other_directions

    directions = [d for d in DIRECTIONS if d != direction]
    rng.shuffle(directions)
    return directions


def try_create_loop(grid, rng):
    candidates = get_loop_candidates(grid)

    if not candidates:
        return False

    x, y = rng.choice(candidates)
    grid[x][y].state = True
    return True


def dig_one_step(grid, x, y, direction, rng, turn_probability, loop_probability):
    if rng.random() < loop_probability:
        if try_create_loop(grid, rng):
            return x, y, direction, "loop"

    directions = choose_directions(direction, rng, turn_probability)

    for dx, dy in directions:
        nx = x + dx
        ny = y + dy

        if is_valid_dig(grid, nx, ny):
            grid[nx][ny].state = True
            return nx, ny, (dx, dy), "move"

    frontier = get_frontier_cells(grid)

    if not frontier:
        return x, y, direction, "blocked"

    old_x, old_y, valid_moves = rng.choice(frontier)
    nx, ny, new_direction = rng.choice(valid_moves)

    grid[nx][ny].state = True
    return nx, ny, new_direction, f"branch_from_{old_x}_{old_y}"


def generate_with_digging_agent_frames(
    n,
    m,
    steps=120,
    turn_probability=0.12,
    loop_probability=0.03,
    seed=None,
):
    rng = random.Random(seed)

    grid = create_empty_grid(n, m)

    x = n // 2
    y = m // 2
    grid[x][y].state = True

    direction = rng.choice(DIRECTIONS)

    frames = [(clone_grid(grid), f"Agent qui creuse - départ ({x}, {y})")]

    for step in range(steps):
        x, y, direction, action = dig_one_step(
            grid,
            x,
            y,
            direction,
            rng,
            turn_probability,
            loop_probability,
        )

        if action == "blocked":
            break

        if action == "loop":
            label = f"Boucle créée - étape {step + 1}"
        elif action.startswith("branch_from"):
            label = f"Nouvelle branche - étape {step + 1}"
        else:
            label = f"Agent qui creuse - étape {step + 1}"

        frames.append((clone_grid(grid), label))

    return grid, frames


def generate_with_digging_agent(
    n,
    m,
    steps=120,
    turn_probability=0.12,
    loop_probability=0.03,
    seed=None,
):
    grid, _ = generate_with_digging_agent_frames(
        n=n,
        m=m,
        steps=steps,
        turn_probability=turn_probability,
        loop_probability=loop_probability,
        seed=seed,
    )

    return grid
