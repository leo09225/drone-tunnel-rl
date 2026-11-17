import random

from generation.models.grid import create_empty_grid, is_in_grid, copy_grid_state


DIRECTIONS = [
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
]


def is_alive(grid, x, y):
    """
    Retourne True si la cellule (x, y) existe et est active.
    Les coordonnées hors grille sont traitées comme des murs.
    """
    height = len(grid)
    width = len(grid[0])

    if x < 0 or y < 0 or x >= height or y >= width:
        return False

    return grid[x][y].state


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

    if count_neighbors_4(grid, x, y) != 2:
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


def count_tunnel_cells(grid):
    count = 0

    for row in grid:
        for cell in row:
            if cell.state:
                count += 1

    return count


def count_edges(grid):
    edges = 0

    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if not grid[x][y].state:
                continue

            for dx, dy in [(1, 0), (0, 1)]:
                nx = x + dx
                ny = y + dy

                if is_in_grid(grid, nx, ny) and grid[nx][ny].state:
                    edges += 1

    return edges


def count_loops(grid):
    if not is_connected(grid):
        return 0

    vertices = count_tunnel_cells(grid)
    edges = count_edges(grid)

    return max(0, edges - vertices + 1)


def would_exceed_target_loops(grid, x, y, target_loops):
    loops_before = count_loops(grid)

    grid[x][y].state = True
    loops_after = count_loops(grid)
    grid[x][y].state = False

    return loops_before <= target_loops and loops_after > target_loops


def choose_directions(direction, rng, turn_probability):
    if rng.random() > turn_probability:
        other_directions = [d for d in DIRECTIONS if d != direction]
        rng.shuffle(other_directions)
        return [direction] + other_directions

    directions = [d for d in DIRECTIONS if d != direction]
    rng.shuffle(directions)
    return directions


def try_create_loop(grid, rng, target_loops=None):
    if target_loops is not None and count_loops(grid) >= target_loops:
        return False

    candidates = get_loop_candidates(grid)

    if not candidates:
        return False

    rng.shuffle(candidates)

    for x, y in candidates:
        if target_loops is not None and would_exceed_target_loops(
            grid, x, y, target_loops
        ):
            continue

        grid[x][y].state = True
        return True

    return False


def try_create_branch(grid, rng, target_loops=None):
    frontier = get_frontier_cells(grid)

    if not frontier:
        return None

    rng.shuffle(frontier)

    for old_x, old_y, valid_moves in frontier:
        rng.shuffle(valid_moves)

        for nx, ny, new_direction in valid_moves:
            if target_loops is not None and would_exceed_target_loops(
                grid, nx, ny, target_loops
            ):
                continue

            grid[nx][ny].state = True
            return nx, ny, new_direction, f"branch_from_{old_x}_{old_y}"

    return None


def dig_one_step(
    grid,
    x,
    y,
    direction,
    rng,
    turn_probability,
    loop_probability,
    branch_probability=0.0,
    target_loops=None,
):
    if rng.random() < loop_probability:
        if try_create_loop(grid, rng, target_loops):
            return x, y, direction, "loop"

    if rng.random() < branch_probability:
        branch = try_create_branch(grid, rng, target_loops)

        if branch is not None:
            return branch

    directions = choose_directions(direction, rng, turn_probability)

    for dx, dy in directions:
        nx = x + dx
        ny = y + dy

        if not is_valid_dig(grid, nx, ny):
            continue

        if target_loops is not None and would_exceed_target_loops(
            grid, nx, ny, target_loops
        ):
            continue

        grid[nx][ny].state = True
        return nx, ny, (dx, dy), "move"

    branch = try_create_branch(grid, rng, target_loops)

    if branch is not None:
        return branch

    return x, y, direction, "blocked"


def create_agents(grid, n, m, agent_count, rng):
    agents = []

    center_x = n // 2
    center_y = m // 2

    grid[center_x][center_y].state = True

    agents.append(
        {
            "x": center_x,
            "y": center_y,
            "direction": rng.choice(DIRECTIONS),
        }
    )

    frontier = get_frontier_cells(grid)

    while len(agents) < agent_count and frontier:
        old_x, old_y, valid_moves = rng.choice(frontier)
        nx, ny, direction = rng.choice(valid_moves)

        grid[nx][ny].state = True

        agents.append(
            {
                "x": nx,
                "y": ny,
                "direction": direction,
            }
        )

        frontier = get_frontier_cells(grid)

    return agents


def generate_with_digging_agent_frames(
    n,
    m,
    steps=120,
    turn_probability=0.12,
    loop_probability=0.03,
    branch_probability=0.0,
    seed=None,
    mode="probabilistic",
    target_loops=0,
    agent_count=1,
):
    rng = random.Random(seed)

    grid = create_empty_grid(n, m)

    agents = create_agents(grid, n, m, agent_count, rng)
    agent_positions = [(agent["x"], agent["y"]) for agent in agents]

    frames = [
        (
            clone_grid(grid),
            f"{agent_count} agent(s) qui creusent - départ",
            agent_positions,
        )
    ]

    for step in range(steps):
        loop_limit = target_loops if mode == "constrained" else None
        actions = []

        active_agents = 0

        for agent_index, agent in enumerate(agents):
            x, y, direction, action = dig_one_step(
                grid,
                agent["x"],
                agent["y"],
                agent["direction"],
                rng,
                turn_probability,
                loop_probability,
                branch_probability,
                loop_limit,
            )

            if action != "blocked":
                active_agents += 1
                actions.append(action)

            agent["x"] = x
            agent["y"] = y
            agent["direction"] = direction

        if active_agents == 0:
            break

        loops = count_loops(grid)

        if "loop" in actions:
            label = (
                f"{agent_count} agents - étape {step + 1} | "
                f"boucle créée | loops={loops}"
            )
        elif any(action.startswith("branch_from") for action in actions):
            label = (
                f"{agent_count} agents - étape {step + 1} | "
                f"branche créée | loops={loops}"
            )
        else:
            label = f"{agent_count} agents - étape {step + 1} | loops={loops}"

        agent_positions = [(agent["x"], agent["y"]) for agent in agents]
        frames.append((clone_grid(grid), label, agent_positions))

    return grid, frames


def generate_with_digging_agent(
    n,
    m,
    steps=120,
    turn_probability=0.12,
    loop_probability=0.03,
    branch_probability=0.0,
    seed=None,
    mode="probabilistic",
    target_loops=0,
    agent_count=1,
):
    grid, _ = generate_with_digging_agent_frames(
        n=n,
        m=m,
        steps=steps,
        turn_probability=turn_probability,
        loop_probability=loop_probability,
        branch_probability=branch_probability,
        seed=seed,
        mode=mode,
        target_loops=target_loops,
        agent_count=agent_count,
    )

    return grid
