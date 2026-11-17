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
    from .agents import (
        Drones,
        EnvExit,
        EnvStart,
        LeftHandDrone,
        PledgeDrone,
        RandomDrone,
        StraightDrone,
    )
except ImportError:
    from agents import (
        Drones,
        EnvExit,
        EnvStart,
        LeftHandDrone,
        PledgeDrone,
        RandomDrone,
        StraightDrone,
    )

if TYPE_CHECKING:
    from mesa.discrete_space import Cell


logger = logging.getLogger("model")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
formatter = logging.Formatter("(%(name)s)[%(levelname)s]: %(message)s")
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)


PLEDGE_MAZES = {
    1: "maze_pledge_01_wall.csv",
    2: "maze_pledge_02_island.csv",
    3: "maze_pledge_03_trap.csv",
    4: "maze_pledge_04_wrong_direction.csv",
}
DEFAULT_MAZES = PLEDGE_MAZES


class Vortex(Model):
    def __init__(
        self,
        n_agents: int | None = None,
        n_random: int = 0,
        n_straight: int = 0,
        n_pledge: int = 1,
        n_left_hand: int = 0,
        maze_id: int = 2,
        env_name: str | None = None,
        env_filename: str | None = None,
        preferred_direction: str = "E",
        preferred_direction_id: int | None = None,
        max_steps: int = 1000,
        seed: int | None = None,
    ) -> None:
        """
        Modele Mesa pour la simulation.
        """
        super().__init__(seed=seed)

        if n_agents is not None and not any(
            [n_random, n_straight, n_pledge, n_left_hand]
        ):
            n_random = n_agents

        self.n_random = n_random
        self.n_straight = n_straight
        self.n_pledge = n_pledge
        self.n_left_hand = n_left_hand

        self.maze_id = maze_id
        self.max_steps = max_steps
        self.step_count = 0
        self.finished = False

        if preferred_direction_id is not None:
            directions = ["N", "E", "S", "W"]
            preferred_direction = directions[preferred_direction_id]

        self.preferred_direction = preferred_direction

        if env_name is None and env_filename is not None:
            env_name = env_filename

        if env_name is None:
            env_name = DEFAULT_MAZES.get(maze_id, DEFAULT_MAZES[2])

        self.env_name = env_name
        self.env_path = os.path.join(os.path.dirname(__file__), "envs", env_name)

        self.start_cell: Cell
        self.exit_cell: Cell | None = None

        self._load_environment()

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
        if self.exit_cell is not None:
            EnvExit(self, cell=self.exit_cell)

    def _parse_header_ints(self, header: list[str]) -> list[int]:
        values: list[int] = []

        for value in header:
            value = value.strip()
            if value == "":
                continue
            values.append(int(value))

        return values

    def _load_environment(self) -> None:
        with open(self.env_path, "r", newline="") as handle:
            reader = list(csv.reader(handle))

        if len(reader) < 2:
            raise ValueError(f"Le fichier {self.env_path} ne contient pas de labyrinthe.")

        header = reader[0]
        exit_x: int | None = None
        exit_y: int | None = None

        if header and header[0].strip().lower() == "start":
            if len(header) < 3:
                raise ValueError(f"En-tete start invalide dans {self.env_path}: {header}")

            start_x = int(header[1])
            start_y = int(header[2])

            map_start_index = 1
            if len(reader) >= 2:
                exit_header = reader[1]
                if exit_header and exit_header[0].strip().lower() == "exit":
                    if len(exit_header) < 3:
                        raise ValueError(
                            f"En-tete exit invalide dans {self.env_path}: {exit_header}"
                        )
                    exit_x = int(exit_header[1])
                    exit_y = int(exit_header[2])
                    map_start_index = 2

            map_rows = reader[map_start_index:]
        else:
            header_values = self._parse_header_ints(header)
            if len(header_values) < 2:
                raise ValueError(
                    "La premiere ligne du CSV doit contenir au moins start_x,start_y."
                )

            start_x, start_y = header_values[0], header_values[1]
            if len(header_values) >= 4:
                exit_x, exit_y = header_values[2], header_values[3]

            map_rows = reader[1:]

        self.height = len(map_rows)
        self.width = len(map_rows[0])

        self.grid: OrthogonalVonNeumannGrid = OrthogonalVonNeumannGrid(
            (self.width, self.height),
            torus=False,
            random=self.random,
        )

        self.env_walls: npt.NDArray[np.float64] = np.zeros(
            [self.height, self.width]
        )

        for y, row in enumerate(reversed(map_rows)):
            if len(row) != self.width:
                raise ValueError(
                    f"Ligne de taille incorrecte dans {self.env_path}: {row}"
                )

            self.env_walls[y] = [float(value) for value in row]

        self.start_cell = self.grid[(start_x, start_y)]

        if exit_x is not None and exit_y is not None:
            self.exit_cell = self.grid[(exit_x, exit_y)]
        else:
            self.exit_cell = self._find_exit_on_border()

    def _find_exit_on_border(self) -> Cell | None:
        start_coord = self.start_cell.coordinate
        border_coordinates: list[tuple[int, int]] = []

        for x in range(self.width):
            border_coordinates.append((x, 0))
            border_coordinates.append((x, self.height - 1))

        for y in range(self.height):
            border_coordinates.append((0, y))
            border_coordinates.append((self.width - 1, y))

        for x, y in border_coordinates:
            if (x, y) == start_coord:
                continue

            if self.env_walls[y, x] == 0:
                return self.grid[(x, y)]

        return None

    def add_to_explored_cells(self) -> None:
        for y, x in np.argwhere(self.explored_cells == 0):
            if any(isinstance(agent, Drones) for agent in self.grid[x, y].agents):
                self.explored_cells[y, x] = 1
                self.new_explored_cell = self.grid[x, y]

    def check_exit_reached(self) -> None:
        if self.exit_cell is None:
            return

        drone_on_exit = any(
            isinstance(agent, Drones)
            for agent in self.exit_cell.agents
        )

        if drone_on_exit:
            self.finished = True
            self.agents_by_type[EnvStart][0].flagger()

    def step(self) -> None:
        self.step_count += 1

        if self.step_count >= self.max_steps:
            logger.info("Nombre maximal d'etapes atteint.")
            self.running = False
            return

        if self.agents_by_type[EnvStart][0].flag:
            logger.info("Sortie atteinte. Simulation terminee.")
            self.running = False
            return

        if RandomDrone in self.agents_by_type:
            self.agents_by_type[RandomDrone].do("step")

        if StraightDrone in self.agents_by_type:
            self.agents_by_type[StraightDrone].do("step")

        if PledgeDrone in self.agents_by_type:
            self.agents_by_type[PledgeDrone].do("step")

        if LeftHandDrone in self.agents_by_type:
            self.agents_by_type[LeftHandDrone].do("step")

        self.agents_by_type[EnvStart].do("step")
        self.check_exit_reached()
        self.add_to_explored_cells()
        self.grid.set_property("Explored Cells", self.explored_cells.T)
