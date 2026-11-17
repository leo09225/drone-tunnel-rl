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
    from model import Vortex


class Unexplored(Drones):
    """
    A drone that prioritizes unexplored cells, then forward cells, then random cells, and backtracks if no other option is available.
    """

    def __init__(self, model: Vortex, cell: Cell) -> None:
        super().__init__(model, cell)
        self.path_stack: list[Cell] = [cell]

    def get_unvisited_moves(self, possible_moves: list[Cell]) -> list[Cell]:
        """
        Filters unexplored cells from the list of possible moves.
        """

        explored = getattr(self.model.grid, "Explored Cells")
        return [c for c in possible_moves if explored.data[c.coordinate] == 0]

    def step(self) -> None:
        possible_moves = self.get_possible_moves()
        forward = self.get_forward_cell()
        unvisited = self.get_unvisited_moves(possible_moves)
        unvisited_forward = (
            forward if (forward is not None and forward in unvisited) else None
        )

        if len(unvisited) >= 3:
            new_cell = self.model.random.choice(unvisited)
        elif unvisited_forward is not None:
            new_cell = unvisited_forward
        elif len(unvisited) > 0:
            new_cell = self.model.random.choice(unvisited)
        else:
            if len(self.path_stack) > 1:
                self.path_stack.pop()
                new_cell = self.path_stack[-1]
            elif possible_moves:
                new_cell = self.model.random.choice(possible_moves)
            else:
                return
        if unvisited and new_cell in unvisited:
            self.path_stack.append(new_cell)

        self.change_cell_and_direction(new_cell)
