from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


ENV_DIR = Path(__file__).with_name("envs")


def make_blank_maze(width: int = 15, height: int = 11) -> np.ndarray:
    maze = np.zeros((height, width), dtype=int)
    maze[0, :] = 1
    maze[-1, :] = 1
    maze[:, 0] = 1
    maze[:, -1] = 1
    return maze


def build_wall_maze() -> tuple[np.ndarray, tuple[int, int], tuple[int, int]]:
    maze = make_blank_maze()
    maze[3:9, 6] = 1
    # Start directly next to the central wall, not next to the outer boundary.
    return maze, (5, 5), (13, 5)


def build_island_maze() -> tuple[np.ndarray, tuple[int, int], tuple[int, int]]:
    maze = make_blank_maze()
    maze[3:8, 5:10] = 1
    # Start glued to the western face of the central island.
    return maze, (4, 5), (13, 5)


def build_trap_maze() -> tuple[np.ndarray, tuple[int, int], tuple[int, int]]:
    maze = make_blank_maze()
    maze[8, 6:11] = 1
    maze[4, 6:11] = 1
    maze[4:9, 10] = 1
    # Start next to the central vertical wall of the trap.
    return maze, (9, 5), (13, 5)


def build_wrong_direction_maze() -> tuple[np.ndarray, tuple[int, int], tuple[int, int]]:
    """
    Maze designed to highlight a bad preferred direction for Pledge.

    The exit is immediately to the east of the start, but the maze offers a
    very long spiral corridor toward the west. With preferred_direction="W",
    Pledge commits to that western spiral and does not reach the exit within a
    standard budget of 1000 steps. With preferred_direction="E", the exit is
    found immediately.
    """
    width = 361
    height = 161
    maze = np.ones((height, width), dtype=int)

    start = (width - 3, 2)
    exit_position = (width - 2, 2)

    # Build a large inward spiral. Starting from the east entrance and heading
    # west means the agent spends a long time following the spiral before it
    # can possibly return to the eastern exit branch.
    left = 2
    right = width - 3
    bottom = 2
    top = height - 3

    spiral_cells: list[tuple[int, int]] = []

    while left <= right and bottom <= top:
        for x in range(right, left - 1, -1):
            spiral_cells.append((x, bottom))

        bottom += 1
        if bottom > top:
            break

        for y in range(bottom, top + 1):
            spiral_cells.append((left, y))

        left += 1
        if left > right:
            break

        for x in range(left, right + 1):
            spiral_cells.append((x, top))

        top -= 1
        if bottom > top:
            break

        for y in range(top, bottom - 1, -1):
            spiral_cells.append((right, y))

        right -= 1

    spiral_cells.append(exit_position)

    for x, y in spiral_cells:
        maze[y, x] = 0

    return maze, start, exit_position


def write_maze_csv(
    path: Path,
    maze: np.ndarray,
    start: tuple[int, int],
    exit_position: tuple[int, int],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["start", start[0], start[1]])
        writer.writerow(["exit", exit_position[0], exit_position[1]])

        for row in reversed(maze):
            writer.writerow(row.tolist())


def ensure_pledge_envs(env_dir: Path | None = None) -> list[Path]:
    target_dir = env_dir or ENV_DIR

    definitions = [
        ("maze_pledge_01_wall.csv", build_wall_maze),
        ("maze_pledge_02_island.csv", build_island_maze),
        ("maze_pledge_03_trap.csv", build_trap_maze),
        ("maze_pledge_04_wrong_direction.csv", build_wrong_direction_maze),
    ]

    written_paths: list[Path] = []
    for filename, builder in definitions:
        maze, start, exit_position = builder()
        output_path = target_dir / filename
        write_maze_csv(output_path, maze, start, exit_position)
        written_paths.append(output_path)

    return written_paths


def main() -> None:
    written_paths = ensure_pledge_envs()

    print("Pledge environments created:")
    for path in written_paths:
        print(f"- {path.name}")


if __name__ == "__main__":
    main()
