from generation.config import GRID_HEIGHT, GRID_WIDTH, ITERATION
from generation.models.grid import copy_grid_state, create_empty_grid, create_grid
from generation.rules.rules import rules_update
from generation.verificator.convergence import count_grid_differences, has_converged


def create_ca_grid(n=GRID_WIDTH, m=GRID_HEIGHT, fixed_tunnels=None):
    grid = create_grid(n, m)

    if fixed_tunnels is not None:
        for x, y in fixed_tunnels:
            grid[x][y].state = True

    return grid


def grid_to_matrix(grid):
    return [[0 if cell.state else 1 for cell in row] for row in grid]


def clone_grid(grid):
    cloned_grid = create_empty_grid(len(grid), len(grid[0]))
    copy_grid_state(grid, cloned_grid)
    return cloned_grid


def apply_fixed_tunnels(grid, fixed_tunnels):
    if fixed_tunnels is None:
        return

    for x, y in fixed_tunnels:
        grid[x][y].state = True


def ca_step(grid_old, grid_new, fixed_tunnels=None):
    # Les règles CA calculent toutes les cellules normalement
    rules_update(grid_old, grid_new)

    # Puis on force les cellules imposées à rester tunnel.
    # Elles ne subissent donc jamais vraiment l'évolution CA.
    apply_fixed_tunnels(grid_new, fixed_tunnels)


def run_ca_until_convergence(
    initial_grid,
    min_iterations=ITERATION,
    on_iteration=None,
    fixed_tunnels=None,
):
    current_grid = initial_grid
    next_grid = clone_grid(initial_grid)
    iteration_count = 0

    # Les cellules fixées sont déjà tunnel dès l'état initial
    apply_fixed_tunnels(current_grid, fixed_tunnels)
    apply_fixed_tunnels(next_grid, fixed_tunnels)

    while True:
        previous_grid = current_grid

        ca_step(
            current_grid,
            next_grid,
            fixed_tunnels=fixed_tunnels,
        )

        current_grid, next_grid = next_grid, current_grid
        iteration_count += 1

        if on_iteration is not None:
            on_iteration(current_grid, iteration_count)

        difference_count = count_grid_differences(previous_grid, current_grid)

        if iteration_count >= min_iterations and has_converged(
            previous_grid,
            current_grid,
        ):
            return current_grid, {
                "iterations": iteration_count,
                "extra_iterations": max(iteration_count - min_iterations, 0),
                "difference_count": difference_count,
                "has_converged": True,
            }


def generate_tunnel_ca(
    n=GRID_WIDTH,
    m=GRID_HEIGHT,
    iterations=ITERATION,
    return_details=False,
    fixed_tunnels=None,
):
    initial_grid = create_ca_grid(
        n,
        m,
        fixed_tunnels=fixed_tunnels,
    )

    final_grid, details = run_ca_until_convergence(
        initial_grid,
        min_iterations=iterations,
        fixed_tunnels=fixed_tunnels,
    )

    if return_details:
        return final_grid, details

    return final_grid
