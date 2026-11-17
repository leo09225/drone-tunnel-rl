from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from mesa.discrete_space import FixedAgent, Grid2DMovingAgent

if TYPE_CHECKING:
    from mesa.discrete_space import Cell
    from model import Vortex

logger = logging.getLogger("agent")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()

formatter = logging.Formatter("(%(name)s)[%(levelname)s]: %(message)s")

console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class EnvStart(FixedAgent):
    """
    The cell where agents start the exploration.
    """

    def __init__(self, model: Vortex, cell: Cell | None = None) -> None:
        super().__init__(model)
        self.cell = cell
        self.flag = False

    def flagger(self) -> None:
        self.flag = True

    def spawner(self) -> None:
        if self.cell is None:
            return

        try:
            from multi_agent.algo import (
                BalancedChoiceDrone,
                RandomDrone,
                StraightDrone,
                TremauxDrone,
                Unexplored,
            )
        except ModuleNotFoundError:
            from algo import (
                BalancedChoiceDrone,
                RandomDrone,
                StraightDrone,
                TremauxDrone,
                Unexplored,
            )

        n_random_current = len(self.model.agents_by_type.get(RandomDrone, []))
        n_unexplored_current = len(self.model.agents_by_type.get(Unexplored, []))
        n_tremaux_current = len(self.model.agents_by_type.get(TremauxDrone, []))
        n_straight_current = len(self.model.agents_by_type.get(StraightDrone, []))
        n_balanced_choice_current = len(
            self.model.agents_by_type.get(BalancedChoiceDrone, [])
        )

        if n_random_current < self.model.n_random:
            RandomDrone(self.model, cell=self.cell)
        elif n_unexplored_current < self.model.n_unexplored:
            Unexplored(self.model, cell=self.cell)
        elif n_tremaux_current < self.model.n_tremaux:
            TremauxDrone(self.model, cell=self.cell)
        elif n_balanced_choice_current < self.model.n_balanced_choice:
            BalancedChoiceDrone(self.model, cell=self.cell)
        elif n_straight_current < self.model.n_straight:
            StraightDrone(self.model, cell=self.cell)

    def step(self) -> None:
        try:
            from multi_agent.algo import (
                BalancedChoiceDrone,
                RandomDrone,
                StraightDrone,
                TremauxDrone,
                Unexplored,
            )
        except ModuleNotFoundError:
            from algo import (
                BalancedChoiceDrone,
                RandomDrone,
                StraightDrone,
                TremauxDrone,
                Unexplored,
            )

        n_current = (
            len(self.model.agents_by_type.get(RandomDrone, []))
            + len(self.model.agents_by_type.get(Unexplored, []))
            + len(self.model.agents_by_type.get(TremauxDrone, []))
            + len(self.model.agents_by_type.get(BalancedChoiceDrone, []))
            + len(self.model.agents_by_type.get(StraightDrone, []))
        )

        if (
            self.cell is not None
            and len(self.cell.agents) == 1
            and n_current
            < (
                self.model.n_random
                + self.model.n_unexplored
                + self.model.n_tremaux
                + self.model.n_balanced_choice
                + self.model.n_straight
            )
        ):
            self.spawner()


class Drones(Grid2DMovingAgent):
    """
    The base class for the drones.
    """

    def __init__(self, model: Vortex, cell: Cell) -> None:
        super().__init__(model)
        self.model: Vortex = model
        self.cell: Cell = cell
        self.front: str = "E"

    def get_possible_moves(self) -> list[Cell]:
        """
        Returns a list of possible adjacent cells that are not walls.
        """
        possible_moves: list[Cell] = []
        for neighbor in self.cell.neighborhood:
            if self.model.grid.Walls.data[neighbor.coordinate] == 0:
                possible_moves.append(neighbor)
        return possible_moves

    def change_cell_and_direction(self, new_cell: Cell) -> None:
        """
        Changes the direction the drone is facing based on the new cell.
        """
        # Update direction (front) for visualization
        old_x, old_y = self.cell.coordinate
        new_x, new_y = new_cell.coordinate

        if new_x > old_x:
            self.front = "E"
        elif new_x < old_x:
            self.front = "W"
        elif new_y > old_y:
            self.front = "N"
        elif new_y < old_y:
            self.front = "S"

        # Move the agent to the new cell
        self.move_to(new_cell)

    def get_forward_cell(self) -> Cell | None:

        x, y = self.cell.coordinate

        direction_map = {
            "N": (x, y + 1),
            "S": (x, y - 1),
            "E": (x + 1, y),
            "W": (x - 1, y),
        }

        target = direction_map[self.front]
        for neighbor in self.cell.neighborhood:
            if neighbor.coordinate == target:
                if self.model.grid.Walls.data[neighbor.coordinate] == 0:
                    return neighbor
        return None

    def step(self) -> None:
        """
        The function to specify the agents behavior.
        """
        pass
