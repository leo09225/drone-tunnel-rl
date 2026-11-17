from __future__ import annotations

from collections import Counter, deque
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


class BalancedChoiceDrone(Drones):
    """
    Drone qui avance tout droit tant qu'il n'est pas à une intersection.
    Lorsqu'il arrive à une intersection, il choisit la direction relative
    la moins utilisée dans ses 20 derniers choix.

    Les choix sont enregistrés uniquement aux intersections.

    """

    RELATIVE_CHOICES = ("LEFT", "FRONT", "RIGHT", "BACK")

    def __init__(self, model: Vortex, cell: Cell) -> None:
        super().__init__(model, cell)
        self.last_choices: deque[str] = deque(maxlen=20)

    def get_cell_in_direction(self, direction: str) -> Cell | None:
        x, y = self.cell.coordinate

        direction_map = {
            "N": (x, y + 1),
            "S": (x, y - 1),
            "E": (x + 1, y),
            "W": (x - 1, y),
        }

        target = direction_map[direction]

        for neighbor in self.cell.neighborhood:
            if neighbor.coordinate == target:
                if self.model.grid.Walls.data[neighbor.coordinate] == 0:
                    return neighbor

        return None

    def get_left_direction(self) -> str:
        directions = ("N", "E", "S", "W")
        index = directions.index(self.front)
        return directions[(index - 1) % 4]

    def get_right_direction(self) -> str:
        directions = ("N", "E", "S", "W")
        index = directions.index(self.front)
        return directions[(index + 1) % 4]

    def get_backward_direction(self) -> str:
        directions = ("N", "E", "S", "W")
        index = directions.index(self.front)
        return directions[(index + 2) % 4]

    def get_relative_choice(self, cell: Cell) -> str:
        forward = self.get_forward_cell()
        left = self.get_cell_in_direction(self.get_left_direction())
        right = self.get_cell_in_direction(self.get_right_direction())
        back = self.get_cell_in_direction(self.get_backward_direction())

        if cell == left:
            return "LEFT"
        if cell == forward:
            return "FRONT"
        if cell == right:
            return "RIGHT"
        if cell == back:
            return "BACK"

        return "FRONT"

    def get_choice_counts(self) -> dict[str, int]:
        counter = Counter(self.last_choices)

        return {choice: counter.get(choice, 0) for choice in self.RELATIVE_CHOICES}

    def choose_least_used(self, cells: list[Cell]) -> Cell:
        counts = self.get_choice_counts()

        min_count = min(counts[self.get_relative_choice(cell)] for cell in cells)

        best_cells = [
            cell
            for cell in cells
            if counts[self.get_relative_choice(cell)] == min_count
        ]

        chosen_cell = self.model.random.choice(best_cells)
        chosen_choice = self.get_relative_choice(chosen_cell)

        self.last_choices.append(chosen_choice)

        return chosen_cell

    def step(self) -> None:
        possible_moves = self.get_possible_moves()

        if not possible_moves:
            return

        forward = self.get_forward_cell()
        back = self.get_cell_in_direction(self.get_backward_direction())

        is_intersection = len(possible_moves) >= 3

        # Cas 1 : couloir simple, le drone avance tout droit sans prendre de décision
        if forward is not None and not is_intersection:
            new_cell = forward

        # Cas 2 : vraie intersection, le drone choisit avec l'algo équilibré
        elif is_intersection:
            new_cell = self.choose_least_used(possible_moves)

        # Cas 3 : pas une intersection, mais le drone est forcé de tourner ou de revenir
        else:
            non_back_moves = [cell for cell in possible_moves if cell != back]

            if non_back_moves:
                new_cell = non_back_moves[0]
            else:
                new_cell = possible_moves[0]

        self.change_cell_and_direction(new_cell)
