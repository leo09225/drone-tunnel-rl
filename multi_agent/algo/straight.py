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


class StraightDrone(Drones):
    """
    A drone that moves straight and chooses randomly at bifurcations.
    """

    def __init__(self, model: Vortex, cell: Cell) -> None:
        super().__init__(model, cell)

    def step(self) -> None:
        possible_moves = self.get_possible_moves()
        forward = self.get_forward_cell()

        if forward in possible_moves:
            new_cell = forward
        elif possible_moves:
            new_cell = self.model.random.choice(possible_moves)
        else:
            return

        self.change_cell_and_direction(new_cell)
