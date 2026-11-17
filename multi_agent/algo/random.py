from __future__ import annotations

from typing import TYPE_CHECKING

try:
    from multi_agent.agents import Drones
except ModuleNotFoundError as exc:
    if exc.name != "multi_agent":
        raise

    from agents import Drones

if TYPE_CHECKING:
    from mesa.discrete_space import Cell
    from multi_agent.model import Vortex


class RandomDrone(Drones):
    """
    A drone that moves randomly.
    """

    def __init__(self, model: Vortex, cell: Cell) -> None:
        super().__init__(model, cell)

    def step(self) -> None:
        possible_moves = self.get_possible_moves()
        if possible_moves:
            new_cell = self.random.choice(possible_moves)
            self.change_cell_and_direction(new_cell)
