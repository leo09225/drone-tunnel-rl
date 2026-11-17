"""
Custom Gymnasium environment for tunnel exploration.

Project goal:
train a drone to explore a 2D tunnel represented as a grid.

This environment is deliberately simple and highly commented because it is meant
to be readable by a student discovering reinforcement learning.

Grid convention:
- 0 = free cell
- 1 = wall

High-level RL definition:
- the drone starts on a free cell,
- the drone must explore every accessible free cell,
- the episode ends when all accessible free cells have been visited,
- the agent receives a reward for discovering new cells.
"""

from __future__ import annotations

from collections import deque
from typing import Iterable

import gymnasium as gym
import numpy as np
from gymnasium import spaces


# Action identifiers used by spaces.Discrete(4).
ACTION_UP = 0
ACTION_RIGHT = 1
ACTION_DOWN = 2
ACTION_LEFT = 3

ACTION_TO_DELTA = {
    ACTION_UP: (-1, 0),
    ACTION_RIGHT: (0, 1),
    ACTION_DOWN: (1, 0),
    ACTION_LEFT: (0, -1),
}

ACTION_NAMES = {
    ACTION_UP: "up",
    ACTION_RIGHT: "right",
    ACTION_DOWN: "down",
    ACTION_LEFT: "left",
}


def create_simple_tunnel_map() -> np.ndarray:
    """
    Create a small hand-made tunnel.

    The layout is intentionally tiny so it is easy to understand by eye.
    The first accessible free cell, at row 1 / col 1, will be used as the
    default starting position.
    """
    return np.array(
        [
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        dtype=np.int8,
    )


def create_branching_tunnel_map() -> np.ndarray:
    """
    Create a tunnel with side branches.

    This is a better test than a straight corridor because the agent can no
    longer solve the task by just moving in a single direction.
    """
    return np.array(
        [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        dtype=np.int8,
    )


def create_maze_like_tunnel_map() -> np.ndarray:
    """
    Create a more complex tunnel map.

    It still follows the same wall/free-cell convention, but contains more
    turns and branches to make exploration harder.
    """
    return np.array(
        [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        dtype=np.int8,
    )


class TunnelExploreEnv(gym.Env):
    """
    Custom Gymnasium environment for tunnel exploration.

    Observation design:
    - global_map: full map with 4 channels
    - local_view: 3x3 neighborhood around the drone
    - explored_ratio: percentage of accessible free cells already visited

    Action design:
    - Discrete(4): up, right, down, left
    """

    metadata = {"render_modes": ["human", "ansi"], "render_fps": 4}

    def __init__(
        self,
        grid_map: np.ndarray | None = None,
        start_position: tuple[int, int] | None = None,
        max_steps: int = 200,
        render_mode: str | None = None,
    ) -> None:
        super().__init__()

        # If no map is provided, we start with the simplest hand-made tunnel.
        if grid_map is None:
            grid_map = create_simple_tunnel_map()

        self.grid_map = np.array(grid_map, dtype=np.int8)
        self._validate_map(self.grid_map)

        self.height, self.width = self.grid_map.shape
        self.render_mode = render_mode
        self.max_steps = max_steps

        # The drone starts on a free cell. If no explicit start is given, we
        # choose the first free cell found while scanning the grid.
        self.start_position = (
            start_position if start_position is not None else self._find_first_free_cell()
        )
        self._validate_start_position(self.start_position)

        # Precompute masks that do not change during the episode.
        self.wall_mask = self.grid_map == 1
        self.free_mask = self.grid_map == 0

        # The agent only needs to explore cells that are reachable from the
        # start position. We compute this once with a simple BFS.
        self.accessible_free_mask = self._compute_accessible_free_mask()
        self.total_accessible_free_cells = int(self.accessible_free_mask.sum())

        # Four movement actions: up, right, down, left.
        self.action_space = spaces.Discrete(4)

        # global_map uses 4 channels:
        # 0 = walls
        # 1 = free cells
        # 2 = visited cells
        # 3 = drone position
        #
        # We keep float values in [0, 1] because it is simple and works well
        # with Gymnasium and Stable-Baselines3.
        self.observation_space = spaces.Dict(
            {
                "global_map": spaces.Box(
                    low=0.0,
                    high=1.0,
                    shape=(4, self.height, self.width),
                    dtype=np.float32,
                ),
                # local_view is a 3x3 neighborhood around the drone.
                # We use 3 channels:
                # 0 = wall
                # 1 = free cell
                # 2 = visited
                #
                # Shape convention here is (height, width, channels), which is
                # easy to read when inspecting arrays manually.
                "local_view": spaces.Box(
                    low=0.0,
                    high=1.0,
                    shape=(3, 3, 3),
                    dtype=np.float32,
                ),
                "explored_ratio": spaces.Box(
                    low=0.0,
                    high=1.0,
                    shape=(1,),
                    dtype=np.float32,
                ),
            }
        )

        # Episode state variables are initialized in reset().
        self.agent_position: tuple[int, int]
        self.visited_mask: np.ndarray
        self.step_count: int
        self.last_action: int | None
        self.last_reward: float
        self.last_collision: bool
        self.last_new_cell: bool

    def _validate_map(self, grid_map: np.ndarray) -> None:
        """
        Check that the map follows the expected format.
        """
        if grid_map.ndim != 2:
            raise ValueError("grid_map must be a 2D array.")

        unique_values = set(np.unique(grid_map).tolist())
        if not unique_values.issubset({0, 1}):
            raise ValueError("grid_map must only contain 0 for free cells and 1 for walls.")

    def _find_first_free_cell(self) -> tuple[int, int]:
        """
        Return the first free cell found in row-major order.
        """
        free_positions = np.argwhere(self.grid_map == 0)
        if len(free_positions) == 0:
            raise ValueError("The map does not contain any free cell.")

        first_row, first_col = free_positions[0]
        return int(first_row), int(first_col)

    def _validate_start_position(self, start_position: tuple[int, int]) -> None:
        """
        Ensure the chosen start position is inside the grid and free.
        """
        row, col = start_position

        if not (0 <= row < self.height and 0 <= col < self.width):
            raise ValueError("start_position must be inside the grid.")

        if self.grid_map[row, col] != 0:
            raise ValueError("start_position must be placed on a free cell.")

    def _iter_valid_neighbors(self, row: int, col: int) -> Iterable[tuple[int, int]]:
        """
        Yield the four cardinal neighbors that stay inside the grid.
        """
        for delta_row, delta_col in ACTION_TO_DELTA.values():
            next_row = row + delta_row
            next_col = col + delta_col

            if 0 <= next_row < self.height and 0 <= next_col < self.width:
                yield next_row, next_col

    def _compute_accessible_free_mask(self) -> np.ndarray:
        """
        Compute which free cells are reachable from the start position.

        This is important because the drone should not be punished for failing
        to visit free cells that are completely disconnected from the start.
        """
        accessible_mask = np.zeros_like(self.free_mask, dtype=bool)
        queue: deque[tuple[int, int]] = deque([self.start_position])
        accessible_mask[self.start_position] = True

        while queue:
            row, col = queue.popleft()

            for next_row, next_col in self._iter_valid_neighbors(row, col):
                if accessible_mask[next_row, next_col]:
                    continue

                if not self.free_mask[next_row, next_col]:
                    continue

                accessible_mask[next_row, next_col] = True
                queue.append((next_row, next_col))

        return accessible_mask

    def _compute_explored_ratio(self) -> float:
        """
        Return the percentage of accessible free cells already visited.
        """
        visited_accessible = self.visited_mask & self.accessible_free_mask
        return float(visited_accessible.sum() / self.total_accessible_free_cells)

    def _extract_local_view(self) -> np.ndarray:
        """
        Build a 3x3 local view centered on the drone.

        Channel meaning:
        - channel 0: wall
        - channel 1: free cell
        - channel 2: visited cell
        """
        local_view = np.zeros((3, 3, 3), dtype=np.float32)
        center_row, center_col = self.agent_position

        for local_row, delta_row in enumerate([-1, 0, 1]):
            for local_col, delta_col in enumerate([-1, 0, 1]):
                world_row = center_row + delta_row
                world_col = center_col + delta_col

                # Outside the grid is treated as a wall.
                if not (0 <= world_row < self.height and 0 <= world_col < self.width):
                    local_view[local_row, local_col, 0] = 1.0
                    continue

                if self.wall_mask[world_row, world_col]:
                    local_view[local_row, local_col, 0] = 1.0
                else:
                    local_view[local_row, local_col, 1] = 1.0
                    if self.visited_mask[world_row, world_col]:
                        local_view[local_row, local_col, 2] = 1.0

        return local_view

    def _get_obs(self) -> dict[str, np.ndarray]:
        """
        Build the observation dictionary expected by the agent.
        """
        global_map = np.zeros((4, self.height, self.width), dtype=np.float32)

        # Channel 0: walls
        global_map[0] = self.wall_mask.astype(np.float32)

        # Channel 1: free cells
        global_map[1] = self.free_mask.astype(np.float32)

        # Channel 2: visited cells
        global_map[2] = self.visited_mask.astype(np.float32)

        # Channel 3: current drone position
        agent_row, agent_col = self.agent_position
        global_map[3, agent_row, agent_col] = 1.0

        explored_ratio = np.array([self._compute_explored_ratio()], dtype=np.float32)

        return {
            "global_map": global_map,
            "local_view": self._extract_local_view(),
            "explored_ratio": explored_ratio,
        }

    def _get_info(self) -> dict[str, object]:
        """
        Return debug information that is useful during testing.
        """
        visited_accessible = int((self.visited_mask & self.accessible_free_mask).sum())
        explored_ratio = self._compute_explored_ratio()

        return {
            "position": self.agent_position,
            "steps": self.step_count,
            "visited_accessible_cells": visited_accessible,
            "total_accessible_cells": self.total_accessible_free_cells,
            "explored_ratio": explored_ratio,
            "collision": self.last_collision,
            "new_cell_explored": self.last_new_cell,
        }

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict | None = None,
    ) -> tuple[dict[str, np.ndarray], dict[str, object]]:
        """
        Start a new episode.

        Gymnasium recommends calling super().reset(seed=seed) so the base class
        can manage the RNG state correctly.
        """
        super().reset(seed=seed)

        self.agent_position = self.start_position
        self.visited_mask = np.zeros((self.height, self.width), dtype=bool)
        self.visited_mask[self.agent_position] = True

        self.step_count = 0
        self.last_action = None
        self.last_reward = 0.0
        self.last_collision = False
        self.last_new_cell = True

        return self._get_obs(), self._get_info()

    def step(
        self, action: int
    ) -> tuple[dict[str, np.ndarray], float, bool, bool, dict[str, object]]:
        """
        Apply one action and update the environment state.

        Reward logic requested in the specification:
        - -0.01 at every step
        - +1.0 when a new free cell is explored
        - -0.2 on collision with a wall or outside the grid
        - +10.0 when the full accessible area has been explored
        """
        if not self.action_space.contains(action):
            raise ValueError(f"Invalid action: {action}")

        self.step_count += 1
        self.last_action = action
        self.last_collision = False
        self.last_new_cell = False

        # Base step penalty applied at every step.
        reward = -0.01

        delta_row, delta_col = ACTION_TO_DELTA[action]
        row, col = self.agent_position
        target_row = row + delta_row
        target_col = col + delta_col

        # If the target cell is outside the grid, we count it as a collision.
        outside_grid = not (0 <= target_row < self.height and 0 <= target_col < self.width)
        hits_wall = False

        if outside_grid:
            self.last_collision = True
            reward -= 0.2
        else:
            hits_wall = bool(self.wall_mask[target_row, target_col])

            if hits_wall:
                self.last_collision = True
                reward -= 0.2
            else:
                # Valid move: the drone enters the free target cell.
                self.agent_position = (target_row, target_col)

                # Discovering a never-visited free cell gives a positive reward.
                if not self.visited_mask[target_row, target_col]:
                    self.visited_mask[target_row, target_col] = True
                    self.last_new_cell = True
                    reward += 1.0

        fully_explored = bool(
            (self.visited_mask & self.accessible_free_mask).sum()
            == self.total_accessible_free_cells
        )
        terminated = fully_explored
        truncated = self.step_count >= self.max_steps and not terminated

        if terminated:
            reward += 10.0

        self.last_reward = float(reward)
        observation = self._get_obs()
        info = self._get_info()

        return observation, float(reward), terminated, truncated, info

    def _build_ascii_render(self) -> str:
        """
        Convert the current state into a small text map.

        Rendering legend:
        - # = wall
        - . = free but not yet visited
        - v = visited free cell
        - D = drone
        """
        lines = []
        explored_ratio = self._compute_explored_ratio()
        lines.append(
            "TunnelExploreEnv | "
            f"step={self.step_count}/{self.max_steps} | "
            f"explored={explored_ratio:.1%} | "
            f"last_reward={self.last_reward:.2f}"
        )

        for row in range(self.height):
            chars = []
            for col in range(self.width):
                position = (row, col)

                if position == self.agent_position:
                    chars.append("D")
                elif self.wall_mask[row, col]:
                    chars.append("#")
                elif self.visited_mask[row, col]:
                    chars.append("v")
                else:
                    chars.append(".")

            lines.append("".join(chars))

        return "\n".join(lines)

    def render(self) -> str | None:
        """
        Render the environment.

        - render_mode="ansi" returns a text string
        - render_mode="human" prints the same string directly
        """
        ascii_frame = self._build_ascii_render()

        if self.render_mode == "ansi":
            return ascii_frame

        if self.render_mode == "human":
            print(ascii_frame)
            return None

        # If no render mode is set, we still return the text version because it
        # is convenient for debugging from scripts.
        return ascii_frame

    def close(self) -> None:
        """
        No external resources are held, so close() is a no-op.
        """
        return None
