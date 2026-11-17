from __future__ import annotations

import argparse

from agents import PledgeDrone
from model import Vortex


def run_simulation(env_name: str, max_steps: int, direction: str) -> None:
    """
    Lance une simulation Pledge en terminal.

    Ce fichier sert uniquement à tester rapidement l'algorithme
    sans ouvrir l'interface Mesa/Solara.
    """

    model = Vortex(
        n_random=0,
        n_straight=0,
        n_pledge=1,
        env_name=env_name,
        preferred_direction=direction,
        max_steps=max_steps,
        seed=42,
    )

    while model.running:
        model.step()

    pledge_agents = list(model.agents_by_type.get(PledgeDrone, []))

    if pledge_agents:
        final_position = pledge_agents[0].cell.coordinate
    else:
        final_position = None

    print("===== Résultat simulation Pledge =====")
    print(f"Labyrinthe : {env_name}")
    print(f"Direction préférée : {direction}")
    print(f"Sortie atteinte : {model.finished}")
    print(f"Nombre de steps : {model.step_count}")
    print(f"Position finale : {final_position}")

    if model.exit_cell is not None:
        print(f"Position sortie : {model.exit_cell.coordinate}")


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--env",
        type=str,
        default="maze_pledge_02_island.csv",
        help="Nom du fichier CSV dans multi_agent/envs/",
    )

    parser.add_argument(
        "--max-steps",
        type=int,
        default=1000,
        help="Nombre maximal d'étapes avant arrêt.",
    )

    parser.add_argument(
        "--direction",
        type=str,
        default="E",
        choices=["N", "E", "S", "W"],
        help="Direction préférée de Pledge : N, E, S ou W.",
    )

    args = parser.parse_args()

    run_simulation(
        env_name=args.env,
        max_steps=args.max_steps,
        direction=args.direction,
    )


if __name__ == "__main__":
    main()