from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from mesa.discrete_space import FixedAgent, Grid2DMovingAgent

if TYPE_CHECKING:
    from mesa.discrete_space import Cell

    try:
        from .model import Vortex
    except ImportError:
        from model import Vortex


logger = logging.getLogger("agent")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
formatter = logging.Formatter("(%(name)s)[%(levelname)s]: %(message)s")
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)


# Directions possibles du drone.
DIRECTIONS = ["N", "E", "S", "W"]

# Deplacement associe a chaque direction.
DIRECTION_DELTAS = {
    "N": (0, 1),
    "E": (1, 0),
    "S": (0, -1),
    "W": (-1, 0),
}


class EnvStart(FixedAgent):
    """
    Case de depart des agents.
    """

    def __init__(self, model: Vortex, cell: Cell | None = None) -> None:
        super().__init__(model)
        self.cell = cell
        self.flag = False

    def flagger(self) -> None:
        """
        Marque la simulation comme terminee.
        """
        self.flag = True

    def spawner(self) -> None:
        """
        Fait apparaitre les agents au point de depart.
        """
        if self.cell is None:
            return

        n_random_current = len(self.model.agents_by_type.get(RandomDrone, []))
        n_straight_current = len(self.model.agents_by_type.get(StraightDrone, []))
        n_pledge_current = len(self.model.agents_by_type.get(PledgeDrone, []))
        n_left_hand_current = len(self.model.agents_by_type.get(LeftHandDrone, []))

        if n_random_current < self.model.n_random:
            RandomDrone(self.model, cell=self.cell)
        elif n_straight_current < self.model.n_straight:
            StraightDrone(self.model, cell=self.cell)
        elif n_pledge_current < self.model.n_pledge:
            PledgeDrone(
                self.model,
                cell=self.cell,
                preferred_direction=self.model.preferred_direction,
            )
        elif n_left_hand_current < self.model.n_left_hand:
            LeftHandDrone(
                self.model,
                cell=self.cell,
                preferred_direction=self.model.preferred_direction,
            )

    def step(self) -> None:
        """
        A chaque etape, si la case de depart est libre,
        on peut faire apparaitre un nouvel agent.
        """
        n_current = (
            len(self.model.agents_by_type.get(RandomDrone, []))
            + len(self.model.agents_by_type.get(StraightDrone, []))
            + len(self.model.agents_by_type.get(PledgeDrone, []))
            + len(self.model.agents_by_type.get(LeftHandDrone, []))
        )

        n_target = (
            self.model.n_random
            + self.model.n_straight
            + self.model.n_pledge
            + self.model.n_left_hand
        )

        # len(self.cell.agents) == 1 signifie :
        # il n'y a que EnvStart sur la case, donc aucun drone n'occupe le depart.
        if self.cell is not None and len(self.cell.agents) == 1 and n_current < n_target:
            self.spawner()


class EnvExit(FixedAgent):
    """
    Case de sortie du labyrinthe.
    """

    def __init__(self, model: Vortex, cell: Cell | None = None) -> None:
        super().__init__(model)
        self.cell = cell


class Drones(Grid2DMovingAgent):
    """
    Classe de base pour tous les drones.
    """

    def __init__(self, model: Vortex, cell: Cell) -> None:
        super().__init__(model)

        self.model: Vortex = model
        self.cell: Cell = cell
        self.front: str = "E"
        self.reached_exit = False
        self.exit_step: int | None = None
        self.steps_taken = 0
        self.visited_cells: set[tuple[int, int]] = {cell.coordinate}

    def start_step(self) -> None:
        """
        Met a jour les statistiques de l'agent au debut de son tour.
        """
        self.steps_taken += 1
        self.visited_cells.add(self.cell.coordinate)
        self.update_exit_state()

    def update_exit_state(self) -> None:
        """
        Enregistre si l'agent a atteint la sortie.
        """
        if self.reached_exit or self.model.exit_cell is None:
            return

        if self.cell.coordinate == self.model.exit_cell.coordinate:
            self.reached_exit = True
            self.exit_step = self.steps_taken

    def is_cell_free(self, cell: Cell | None) -> bool:
        """
        Verifie qu'une case existe et qu'elle n'est pas un mur.
        """
        if cell is None:
            return False

        return self.model.grid.Walls.data[cell.coordinate] == 0

    def get_possible_moves(self) -> list[Cell]:
        """
        Renvoie toutes les cases voisines accessibles.
        """
        possible_moves: list[Cell] = []

        for neighbor in self.cell.neighborhood:
            if self.is_cell_free(neighbor):
                possible_moves.append(neighbor)

        return possible_moves

    def get_cell_in_direction(self, direction: str) -> Cell | None:
        """
        Renvoie la case situee dans une direction donnee.
        """
        x, y = self.cell.coordinate
        dx, dy = DIRECTION_DELTAS[direction]

        target_x = x + dx
        target_y = y + dy

        if target_x < 0 or target_x >= self.model.width:
            return None

        if target_y < 0 or target_y >= self.model.height:
            return None

        return self.model.grid[(target_x, target_y)]

    def get_forward_cell(self) -> Cell | None:
        """
        Renvoie la case devant le drone.
        """
        return self.get_cell_in_direction(self.front)

    def change_cell_and_direction(self, new_cell: Cell) -> None:
        """
        Deplace le drone vers une nouvelle cellule
        et met a jour sa direction pour l'affichage.
        """
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

        self.move_to(new_cell)
        self.visited_cells.add(new_cell.coordinate)
        self.update_exit_state()

    def turn_left(self) -> None:
        """
        Tourne le drone a gauche sans avancer.
        """
        current_index = DIRECTIONS.index(self.front)
        self.front = DIRECTIONS[(current_index - 1) % 4]

    def turn_right(self) -> None:
        """
        Tourne le drone a droite sans avancer.
        """
        current_index = DIRECTIONS.index(self.front)
        self.front = DIRECTIONS[(current_index + 1) % 4]

    def step(self) -> None:
        """
        Methode redefinie dans les drones specialises.
        """
        pass


class RandomDrone(Drones):
    """
    Drone qui choisit une direction accessible au hasard.
    """

    def step(self) -> None:
        self.start_step()
        possible_moves = self.get_possible_moves()

        if possible_moves:
            new_cell = self.random.choice(possible_moves)
            self.change_cell_and_direction(new_cell)


class StraightDrone(Drones):
    """
    Drone qui essaie d'aller tout droit.
    S'il ne peut pas, il choisit une direction possible.
    """

    def step(self) -> None:
        self.start_step()
        possible_moves = self.get_possible_moves()
        forward = self.get_forward_cell()

        if len(possible_moves) >= 3:
            new_cell = self.random.choice(possible_moves)
        elif forward is not None and self.is_cell_free(forward):
            new_cell = forward
        elif possible_moves:
            new_cell = self.random.choice(possible_moves)
        else:
            return

        self.change_cell_and_direction(new_cell)


class LeftHandDrone(Drones):
    """
    Drone qui suit le mur avec la main gauche.
    """

    def __init__(
        self,
        model: Vortex,
        cell: Cell,
        preferred_direction: str = "E",
    ) -> None:
        super().__init__(model, cell)
        self.front = preferred_direction
        self.mode = "FOLLOW_LEFT_WALL"

    def step(self) -> None:
        self.start_step()

        old_direction = self.front
        self.turn_left()
        left_cell = self.get_forward_cell()
        self.front = old_direction

        if self.is_cell_free(left_cell):
            self.turn_left()
            self.change_cell_and_direction(left_cell)
            return

        forward = self.get_forward_cell()
        if self.is_cell_free(forward):
            self.change_cell_and_direction(forward)
            return

        old_direction = self.front
        self.turn_right()
        right_cell = self.get_forward_cell()
        self.front = old_direction

        if self.is_cell_free(right_cell):
            self.turn_right()
            self.change_cell_and_direction(right_cell)
            return

        self.turn_right()
        self.turn_right()
        backward = self.get_forward_cell()
        if self.is_cell_free(backward):
            self.change_cell_and_direction(backward)


class PledgeDrone(Drones):
    """
    Drone utilisant l'algorithme de Pledge.
    """

    def __init__(
        self,
        model: Vortex,
        cell: Cell,
        preferred_direction: str = "E",
    ) -> None:
        super().__init__(model, cell)

        self.preferred_direction = preferred_direction
        self.front = preferred_direction
        self.mode = "GO_TO_PREFERRED_DIRECTION"
        self.turn_counter = 0

    def counted_turn_left(self) -> None:
        self.turn_left()
        self.turn_counter += 1

    def counted_turn_right(self) -> None:
        self.turn_right()
        self.turn_counter -= 1

    def counted_turn_around_right(self) -> None:
        self.counted_turn_right()
        self.counted_turn_right()

    def can_leave_wall(self) -> bool:
        forward = self.get_forward_cell()

        return (
            self.turn_counter == 0
            and self.front == self.preferred_direction
            and self.is_cell_free(forward)
        )

    def go_to_preferred_direction(self) -> None:
        self.front = self.preferred_direction
        forward = self.get_forward_cell()

        if self.is_cell_free(forward):
            self.change_cell_and_direction(forward)
            return

        self.mode = "FOLLOW_WALL"
        self.counted_turn_left()

        forward_after_turn = self.get_forward_cell()
        if self.is_cell_free(forward_after_turn):
            self.change_cell_and_direction(forward_after_turn)

    def follow_wall(self) -> None:
        if self.can_leave_wall():
            self.mode = "GO_TO_PREFERRED_DIRECTION"

            forward = self.get_forward_cell()
            if self.is_cell_free(forward):
                self.change_cell_and_direction(forward)
            return

        old_direction = self.front
        self.turn_right()
        right_cell = self.get_forward_cell()
        self.front = old_direction

        if self.is_cell_free(right_cell):
            self.counted_turn_right()
            self.change_cell_and_direction(right_cell)
            return

        forward = self.get_forward_cell()
        if self.is_cell_free(forward):
            self.change_cell_and_direction(forward)
            return

        old_direction = self.front
        self.turn_left()
        left_cell = self.get_forward_cell()
        self.front = old_direction

        if self.is_cell_free(left_cell):
            self.counted_turn_left()
            self.change_cell_and_direction(left_cell)
            return

        self.counted_turn_around_right()

        forward_after_turn = self.get_forward_cell()
        if self.is_cell_free(forward_after_turn):
            self.change_cell_and_direction(forward_after_turn)

    def step(self) -> None:
        self.start_step()

        if self.mode == "GO_TO_PREFERRED_DIRECTION":
            self.go_to_preferred_direction()
        elif self.mode == "FOLLOW_WALL":
            self.follow_wall()
