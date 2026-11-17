from __future__ import annotations

import csv
import logging
import os
from typing import TYPE_CHECKING, Any

import numpy as np
import numpy.typing as npt
from mesa import Model
from mesa.discrete_space import OrthogonalVonNeumannGrid, PropertyLayer

try:
    from multi_agent.agents import Drones, EnvStart
    from multi_agent.algo import EXPLORATION_DRONES
except ModuleNotFoundError as exc:
    if exc.name != "multi_agent":
        raise
    from agents import Drones, EnvStart
    from algo import EXPLORATION_DRONES

if TYPE_CHECKING:
    from mesa.discrete_space import Cell

logger = logging.getLogger("model")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()

formatter = logging.Formatter("(%(name)s)[%(levelname)s]: %(message)s")

console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def resolve_env_path() -> str:
    env_dir = os.path.join(os.path.dirname(__file__), "envs")
    candidates = ("50x50_matrix.csv", "100x100_matrix.csv", "env_cross.csv")

    for filename in candidates:
        candidate = os.path.join(env_dir, filename)
        if os.path.exists(candidate):
            return candidate

    raise FileNotFoundError(f"No environment CSV found in {env_dir}")


DEFAULT_ENV_PATH = resolve_env_path()


class Vortex(Model):
    def __init__(
        self,
        n_random: int = 1,
        n_unexplored: int = 0,
        n_tremaux: int = 0,
        n_balanced_choice: int = 0,
        n_balanced_choice_50: int = 0,
        n_straight: int = 0,
        n_agents: int = 5,
        seed: int | None = None,
        env_path: str | None = None,
    ) -> None:

        super().__init__(seed=seed)
        self.n_random = n_random
        self.n_unexplored = n_unexplored
        self.n_agents = n_agents
        self.n_tremaux = n_tremaux
        self.n_balanced_choice = n_balanced_choice
        self.n_balanced_choice_50 = n_balanced_choice_50
        self.n_straight = n_straight
        self.env_path = env_path or DEFAULT_ENV_PATH

        with open(self.env_path, "r", newline="") as f:
            reader = list(csv.reader(f))

            self.height: int = len(reader) - 1
            self.width: int = len(reader[0])

            self.grid: OrthogonalVonNeumannGrid = OrthogonalVonNeumannGrid(
                (self.width, self.height), torus=False, random=self.random
            )

            self.env_walls: npt.NDArray[np.float64] = np.zeros(
                [self.height, self.width]
            )

            for i, ligne in enumerate(reversed(reader)):
                if i < self.height:
                    self.env_walls[i] = [float(x) for x in ligne]
                else:
                    start_x = int(ligne[0])
                    start_y = self.height - 1 - int(ligne[1])
                    self.start_cell = self.grid[(start_x, start_y)]

        self.explored_cells: npt.NDArray[np.float64] = np.zeros(
            [self.height, self.width]
        )
        self.explored_cells[
            self.start_cell.coordinate[1], self.start_cell.coordinate[0]
        ] = 1

        self.new_explored_cell: Cell = self.start_cell

        self.grid.add_property_layer(PropertyLayer.from_data("Walls", self.env_walls.T))
        self.grid.add_property_layer(
            PropertyLayer.from_data("Explored Cells", self.explored_cells.T)
        )

        self.occupation_list: list[Any] = []

        EnvStart(self, cell=self.start_cell)

    def add_to_explored_cells(self) -> None:
        """
        Keep info of newly explored cell
        """
        for y, x in np.argwhere(self.explored_cells == 0):
            if any(isinstance(a, Drones) for a in self.grid[x, y].agents):
                self.explored_cells[y, x] = 1
                self.new_explored_cell = self.grid[x, y]

    def step(self) -> None:
        """
        Model step function
        """

        # Condition to end simulation
        if self.agents_by_type[EnvStart][0].flag:
            logger.info("Exploration finished!")
            self.running = False
        else:
            for drone_class in EXPLORATION_DRONES:
                if drone_class in self.agents_by_type:
                    self.agents_by_type[drone_class].do("step")
            self.agents_by_type[EnvStart].do("step")

        # Make new explored cells green in the simulation renderer
        self.add_to_explored_cells()
        self.grid.set_property("Explored Cells", self.explored_cells.T)
