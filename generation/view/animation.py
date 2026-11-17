import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap

from generation.models.grid import copy_grid_state, create_grid, create_empty_grid
from generation.algorithms.longest_path import keep_largest_connected_component
from generation.algorithms.digging_agent import generate_with_digging_agent_frames


def grid_to_matrix(grid):
    return np.array([[1 if cell.state else 0 for cell in row] for row in grid])


def clone_grid(grid):
    cloned_grid = create_empty_grid(len(grid), len(grid[0]))
    copy_grid_state(grid, cloned_grid)
    return cloned_grid


def animate_frames(frames, interval=120):
    matrix_frames = [(grid_to_matrix(grid).copy(), label) for grid, label in frames]

    cmap = ListedColormap(["#222222", "#00CC66"])

    fig, ax = plt.subplots(figsize=(6, 6))
    image = ax.imshow(
        matrix_frames[0][0],
        cmap=cmap,
        vmin=0,
        vmax=1,
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
    grid, n, m, ca_step, iterations=200, interval=200, show_longest_path=True
):
    current_grid = grid
    next_grid = create_grid(n, m)
    copy_grid_state(current_grid, next_grid)

    frames = []
    frames.append((clone_grid(current_grid), "Automate cellulaire - iteration 0"))

    for i in range(iterations):
        ca_step(current_grid, next_grid)
        current_grid, next_grid = next_grid, current_grid

        frames.append(
            (
                clone_grid(current_grid),
                f"Automate cellulaire - iteration {i + 1}",
            )
        )

    if show_longest_path:
        longest_path_grid = clone_grid(current_grid)
        keep_largest_connected_component(longest_path_grid)

        frames.append(
            (
                longest_path_grid,
                "Plus grand chemin connecte",
            )
        )

    animate_frames(frames, interval=interval)

    return current_grid


def animate_digging_agent(
    n,
    m,
    steps=120,
    turn_probability=0.12,
    seed=None,
    interval=120,
    show_post_processing=True,
):
    grid, frames = generate_with_digging_agent_frames(
        n=n,
        m=m,
        steps=steps,
        turn_probability=turn_probability,
        seed=seed,
    )

    animate_frames(frames, interval=interval)

    return grid
