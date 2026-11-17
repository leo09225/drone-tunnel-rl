import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap

from generation.algorithms.ca import run_ca_until_convergence
from generation.algorithms.digging_agent import generate_with_digging_agent_frames
from generation.algorithms.longest_path import keep_largest_connected_component
from generation.models.grid import copy_grid_state, create_empty_grid


def grid_to_matrix(grid):
    matrix = []

    for row in grid:
        matrix_row = []
        for cell in row:
            if cell.state:
                matrix_row.append(0)
            else:
                matrix_row.append(1)
        matrix.append(matrix_row)

    return np.array(matrix)


def clone_grid(grid):
    cloned_grid = create_empty_grid(len(grid), len(grid[0]))
    copy_grid_state(grid, cloned_grid)
    return cloned_grid


def unpack_frame(frame):
    if len(frame) == 2:
        grid, label = frame
        return grid, label, []

    grid, second, third = frame

    if isinstance(second, str):
        return grid, second, third

    return grid, third, second


def add_agent_overlay(matrix, agent_positions):
    matrix_with_agents = matrix.copy()

    for x, y in agent_positions:
        if (
            0 <= x < matrix_with_agents.shape[0]
            and 0 <= y < matrix_with_agents.shape[1]
        ):
            matrix_with_agents[x, y] = 2

    return matrix_with_agents


def add_fixed_tunnels_overlay(matrix, fixed_tunnels):
    if fixed_tunnels is None:
        return matrix

    matrix_with_fixed = matrix.copy()

    for x, y in fixed_tunnels:
        if (
            0 <= x < matrix_with_fixed.shape[0]
            and 0 <= y < matrix_with_fixed.shape[1]
            and matrix_with_fixed[x, y] == 0
        ):
            matrix_with_fixed[x, y] = 3

    return matrix_with_fixed


def animate_frames(frames, interval=120, fixed_tunnels=None):
    matrix_frames = []

    for frame in frames:
        grid, label, agent_positions = unpack_frame(frame)
        matrix = grid_to_matrix(grid)
        matrix = add_agent_overlay(matrix, agent_positions)
        matrix = add_fixed_tunnels_overlay(matrix, fixed_tunnels)
        matrix_frames.append((matrix.copy(), label))

    cmap = ListedColormap(
        ["#00CC66", "#222222", "#FF3333", "#FF0000"]
    )  # vert tunnel, noir mur, rouge 1 agents, rouge 2 tunnels imposés

    fig, ax = plt.subplots(figsize=(6, 6))
    image = ax.imshow(
        matrix_frames[0][0],
        cmap=cmap,
        vmin=0,
        vmax=3,
        interpolation="nearest",
    )

    title = ax.set_title(matrix_frames[0][1])
    ax.axis("off")

    def update(frame_index):
        matrix, label = matrix_frames[frame_index]
        image.set_data(matrix)
        title.set_text(label)
        return image, title

    animation = FuncAnimation(
        fig,
        update,
        frames=len(matrix_frames),
        interval=interval,
        blit=False,
        repeat=False,
    )

    fig._animation = animation
    plt.show()


def animate_automaton(
    grid,
    iterations=200,
    interval=200,
    post_processing_mode="largest_component",
    fixed_tunnels=None,
):
    frames = [(clone_grid(grid), "Automate cellulaire - iteration 0")]

    def record_frame(current_grid, iteration_count):
        frames.append(
            (
                clone_grid(current_grid),
                f"Automate cellulaire - iteration {iteration_count}",
            )
        )

    current_grid, details = run_ca_until_convergence(
        grid,
        min_iterations=iterations,
        on_iteration=record_frame,
        fixed_tunnels=fixed_tunnels,
    )

    if post_processing_mode == "largest_component":
        final_grid = clone_grid(current_grid)
        keep_largest_connected_component(final_grid)

        frames.append(
            (
                final_grid,
                "Post-traitement - plus grande composante connectee",
            )
        )

    elif post_processing_mode == "connect_components":
        from generation.algorithms.connect_components import connect_all_components

        final_grid = clone_grid(current_grid)
        connect_all_components(final_grid)

        frames.append(
            (
                final_grid,
                "Post-traitement - connexion des composantes",
            )
        )

    elif post_processing_mode == "none":
        final_grid = current_grid

    else:
        raise ValueError(
            f"Unknown post_processing_mode: {post_processing_mode}. "
            "Use 'largest_component', 'connect_components' or 'none'."
        )

    animate_frames(frames, interval=interval, fixed_tunnels=fixed_tunnels)

    return final_grid, details


def animate_digging_agent(
    n,
    m,
    steps=120,
    turn_probability=0.12,
    loop_probability=0.03,
    branch_probability=0.0,
    mode="probabilistic",
    target_loops=0,
    agent_count=1,
    seed=None,
    interval=120,
    show_post_processing=True,
):
    grid, frames = generate_with_digging_agent_frames(
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

    if show_post_processing:
        final_grid = clone_grid(grid)
        keep_largest_connected_component(final_grid)
        frames.append((final_grid, "Plus grand chemin connecte"))

    animate_frames(frames, interval=interval)

    return grid
