from generation.config import (
    GRID_HEIGHT,
    GRID_WIDTH,
    SAVE,
    ITERATION,
    VIEW,
    ANIMATION,
    SHOW_LONGEST_PATH,
    GENERATION_METHOD,
    AGENT_STEPS,
    AGENT_TURN_PROBABILITY,
)
from generation.data.save import save_matrix_to_csv
from generation.verificator.tunnel_verificator import get_verification_report
from generation.algorithms.ca import (
    ca_step,
    clone_grid,
    create_ca_grid,
    generate_tunnel_ca,
    grid_to_matrix,
)
from generation.algorithms.longest_path import keep_largest_connected_component
from generation.algorithms.digging_agent import generate_with_digging_agent


def print_matrix(matrix):
    for row in matrix:
        print(" ".join(str(value) for value in row))


def prepare_output_grid(grid):
    output_grid = clone_grid(grid)

    if SHOW_LONGEST_PATH:
        keep_largest_connected_component(output_grid)

    return output_grid


def generate_tunnel_agent():
    return generate_with_digging_agent(
        n=GRID_WIDTH,
        m=GRID_HEIGHT,
        steps=AGENT_STEPS,
        turn_probability=AGENT_TURN_PROBABILITY,
    )


def run_ca_generation(animation):
    if animation:
        try:
            from generation.view.animation import animate_automaton
        except ModuleNotFoundError as exc:
            print(f"Animation unavailable: {exc}")
            return generate_tunnel_ca()

        return animate_automaton(
            create_ca_grid(GRID_WIDTH, GRID_HEIGHT),
            GRID_WIDTH,
            GRID_HEIGHT,
            ca_step,
            iterations=ITERATION,
            interval=2000,
            show_longest_path=SHOW_LONGEST_PATH,
        )

    return generate_tunnel_ca()


def run_agent_generation(animation):
    if animation:
        from generation.view.animation import animate_digging_agent

        return animate_digging_agent(
            n=GRID_WIDTH,
            m=GRID_HEIGHT,
            steps=AGENT_STEPS,
            turn_probability=AGENT_TURN_PROBABILITY,
            seed=None,
            interval=120,
            show_post_processing=True,
        )

    return generate_tunnel_agent()


def generation_tunnel(
    method=None, view=VIEW, save=SAVE, verbose=True, animation=ANIMATION
):
    if method is None:
        method = GENERATION_METHOD

    if method == "ca":
        grid = run_ca_generation(animation)

    elif method == "agent":
        grid = run_agent_generation(animation)

    else:
        raise ValueError(f"Unknown generation method: {method}. Use 'ca' or 'agent'.")

    output_grid = prepare_output_grid(grid)
    matrix = grid_to_matrix(output_grid)

    if verbose:
        print_matrix(matrix)

    if save:
        save_matrix_to_csv(matrix, GRID_WIDTH, GRID_HEIGHT)

    if view and not animation:
        try:
            from generation.view.plot import plot
        except ModuleNotFoundError as exc:
            if verbose:
                print(f"Plot unavailable: {exc}")
        else:
            plot(matrix)

    verif = get_verification_report(output_grid)

    if verbose:
        print("")
        print(f"The connection of all the cave : {verif['is_connected_4']}")
        print(f"The square rule is respected : {verif['has_width_one']}")
        print(f"The cave is good : {verif['is_valid']}")
        print(f"Positions of full 2x2 squares : {verif['full_2x2_positions']}")

    return output_grid
