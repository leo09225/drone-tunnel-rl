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


DIRECTIONS = ["N", "E", "S", "W"]
DELTA: dict[str, tuple[int, int]] = {
    "N": (0, 1),
    "E": (1, 0),
    "S": (0, -1),
    "W": (-1, 0),
}


def turn_left(direction: str) -> str:
    return DIRECTIONS[(DIRECTIONS.index(direction) - 1) % 4]


def turn_right(direction: str) -> str:
    return DIRECTIONS[(DIRECTIONS.index(direction) + 1) % 4]


def turn_around(direction: str) -> str:
    return DIRECTIONS[(DIRECTIONS.index(direction) + 2) % 4]


class TremauxDrone(Drones):
    def __init__(self, model: Vortex, cell: Cell) -> None:
        super().__init__(model, cell)
        self.state: str = "EXPLORING"
        self.front = "N"
        self.marks: dict[tuple[tuple[int, int], tuple[int, int]], int] = {}
        self.path_stack: list[tuple[int, int]] = []
        self.came_from: tuple[int, int] | None = None
        self.start_coord = cell.coordinate

    def _edge(
        self, a: tuple[int, int], b: tuple[int, int]
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        return (min(a, b), max(a, b))

    def _mark_count(self, a: tuple[int, int], b: tuple[int, int]) -> int:
        return self.marks.get(self._edge(a, b), 0)

    def _add_mark(self, a: tuple[int, int], b: tuple[int, int]) -> None:
        key = self._edge(a, b)
        self.marks[key] = self.marks.get(key, 0) + 1

    def _is_map_fully_explored(self) -> bool:
        tunnel_mask = self.model.env_walls == 0
        explored_tunnels = (tunnel_mask & (self.model.explored_cells == 1)).sum()
        total_tunnels = tunnel_mask.sum()
        return int(explored_tunnels) == int(total_tunnels)

    def _free_neighbors(self) -> dict[str, tuple[int, int]]:
        result: dict[str, tuple[int, int]] = {}
        for direction in DIRECTIONS:
            dx, dy = DELTA[direction]
            nx = self.cell.coordinate[0] + dx
            ny = self.cell.coordinate[1] + dy
            if 0 <= nx < self.model.width and 0 <= ny < self.model.height:
                if self.model.env_walls[ny, nx] == 0:
                    result[direction] = (nx, ny)
        return result

    def _priority_directions(self) -> list[str]:
        return [
            turn_left(self.front),
            self.front,
            turn_right(self.front),
            turn_around(self.front),
        ]

    def _move_to_coord(self, coord: tuple[int, int]) -> None:
        target = self.model.grid[coord[0], coord[1]]
        dx = coord[0] - self.cell.coordinate[0]
        dy = coord[1] - self.cell.coordinate[1]

        for direction, (delta_x, delta_y) in DELTA.items():
            if delta_x == dx and delta_y == dy:
                self.front = direction
                break

        self.move_to(target)

    def step(self) -> None:
        if self.state != "EXPLORING":
            return

        position = self.cell.coordinate

        neighbors = self._free_neighbors()
        ordered_neighbors = [
            (direction, neighbors[direction])
            for direction in self._priority_directions()
            if direction in neighbors
        ]

        unvisited = [
            (direction, coord)
            for direction, coord in ordered_neighbors
            if self._mark_count(position, coord) == 0
        ]

        if unvisited:
            _, next_coord = unvisited[0]

            self._add_mark(position, next_coord)
            self.path_stack.append(position)
            self.came_from = position
            self._move_to_coord(next_coord)
            return

        if self.path_stack:
            previous_coord = self.path_stack.pop()
            self._add_mark(position, previous_coord)
            self.came_from = position
            self._move_to_coord(previous_coord)
            return

        if position == self.start_coord and len(self.marks) > 0:
            if self._is_map_fully_explored():
                self.came_from = None
                self.state = "RETURNING_HOME"
                return

            if ordered_neighbors:
                min_marks = min(
                    self._mark_count(position, coord) for _, coord in ordered_neighbors
                )
                _, next_coord = next(
                    (direction, coord)
                    for direction, coord in ordered_neighbors
                    if self._mark_count(position, coord) == min_marks
                )
                self._add_mark(position, next_coord)
                self.path_stack.append(position)
                self.came_from = position
                self._move_to_coord(next_coord)
                return

        self.came_from = None
