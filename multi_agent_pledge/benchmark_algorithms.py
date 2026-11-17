from __future__ import annotations

import argparse
import csv
from pathlib import Path

try:
    from .agents import LeftHandDrone, PledgeDrone, RandomDrone, StraightDrone
    from .model import PLEDGE_MAZES, Vortex
except ImportError:
    from agents import LeftHandDrone, PledgeDrone, RandomDrone, StraightDrone
    from model import PLEDGE_MAZES, Vortex


ALGORITHM_CONFIG = {
    "pledge": ("n_pledge", PledgeDrone),
    "left_hand": ("n_left_hand", LeftHandDrone),
    "random": ("n_random", RandomDrone),
    "straight": ("n_straight", StraightDrone),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark maze-solving algorithms on the multi_agent Pledge mazes."
        )
    )
    parser.add_argument(
        "--algorithms",
        nargs="+",
        choices=sorted(ALGORITHM_CONFIG),
        default=["pledge", "left_hand", "random", "straight"],
        help="Algorithms to benchmark.",
    )
    parser.add_argument(
        "--agent-counts",
        nargs="+",
        type=int,
        default=[1],
        help="Number of agents of the same algorithm to spawn at once.",
    )
    parser.add_argument(
        "--mazes",
        nargs="+",
        default=["all"],
        help=(
            "Maze filenames to benchmark, or 'all' for every generated Pledge maze."
        ),
    )
    parser.add_argument(
        "--direction",
        default="E",
        choices=["N", "E", "S", "W"],
        help="Preferred direction used by the deterministic algorithms.",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=1000,
        help="Maximum number of simulation steps per run.",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=1,
        help="Number of independent runs per configuration.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Base random seed. Trial i uses seed + i.",
    )
    parser.add_argument(
        "--csv-out",
        type=str,
        default=None,
        help="Optional CSV file to store the aggregated results.",
    )
    return parser.parse_args()


def resolve_mazes(raw_mazes: list[str]) -> list[str]:
    if raw_mazes == ["all"]:
        return list(PLEDGE_MAZES.values())
    return raw_mazes


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def format_metric(value: float | None, precision: int = 2) -> str:
    if value is None:
        return "-"
    return f"{value:.{precision}f}"


def run_single_benchmark(
    algorithm: str,
    agent_count: int,
    maze_filename: str,
    preferred_direction: str,
    max_steps: int,
    seed: int,
) -> dict[str, float | int | str]:
    agent_field, agent_class = ALGORITHM_CONFIG[algorithm]

    model_kwargs = {
        "n_pledge": 0,
        "n_left_hand": 0,
        "n_random": 0,
        "n_straight": 0,
        "env_filename": maze_filename,
        "preferred_direction": preferred_direction,
        "max_steps": max_steps,
        "seed": seed,
    }
    model_kwargs[agent_field] = agent_count

    model = Vortex(**model_kwargs)

    while model.running:
        model.step()

    agents = list(model.agents_by_type.get(agent_class, []))
    successes = [agent for agent in agents if agent.reached_exit]

    free_cells = int((model.env_walls == 0).sum())
    global_explored_cells = int(model.explored_cells.sum())

    success_steps = [agent.steps_taken for agent in successes]
    success_exit_steps = [
        agent.exit_step for agent in successes if agent.exit_step is not None
    ]
    all_steps = [agent.steps_taken for agent in agents]
    success_visited = [len(agent.visited_cells) for agent in successes]
    all_visited = [len(agent.visited_cells) for agent in agents]

    return {
        "algorithm": algorithm,
        "maze": maze_filename,
        "agent_count": agent_count,
        "trial_seed": seed,
        "success_count": len(successes),
        "success_rate_pct": 100 * len(successes) / agent_count if agent_count else 0.0,
        "mean_steps_success": mean(success_steps),
        "mean_exit_step_success": mean(success_exit_steps),
        "mean_steps_all": mean(all_steps),
        "mean_visited_cells_success": mean(success_visited),
        "mean_visited_cells_all": mean(all_visited),
        "global_explored_cells": global_explored_cells,
        "global_explored_pct": 100 * global_explored_cells / free_cells
        if free_cells
        else 0.0,
        "free_cells": free_cells,
        "model_steps": model.step_count,
        "at_least_one_exit": int(model.finished),
    }


def aggregate_runs(run_results: list[dict[str, float | int | str]]) -> dict[str, float | int | str]:
    sample = run_results[0]

    def collect_numeric(key: str) -> list[float]:
        values: list[float] = []
        for result in run_results:
            value = result[key]
            if isinstance(value, (int, float)):
                values.append(float(value))
        return values

    return {
        "algorithm": sample["algorithm"],
        "maze": sample["maze"],
        "agent_count": sample["agent_count"],
        "trials": len(run_results),
        "success_rate_pct": mean(collect_numeric("success_rate_pct")),
        "mean_steps_success": mean(
            [
                value
                for value in (result["mean_steps_success"] for result in run_results)
                if isinstance(value, (int, float))
            ]
        ),
        "mean_exit_step_success": mean(
            [
                value
                for value in (result["mean_exit_step_success"] for result in run_results)
                if isinstance(value, (int, float))
            ]
        ),
        "mean_steps_all": mean(collect_numeric("mean_steps_all")),
        "mean_visited_cells_success": mean(
            [
                value
                for value in (
                    result["mean_visited_cells_success"] for result in run_results
                )
                if isinstance(value, (int, float))
            ]
        ),
        "mean_visited_cells_all": mean(collect_numeric("mean_visited_cells_all")),
        "global_explored_cells": mean(collect_numeric("global_explored_cells")),
        "global_explored_pct": mean(collect_numeric("global_explored_pct")),
        "model_steps": mean(collect_numeric("model_steps")),
        "at_least_one_exit_rate_pct": mean(collect_numeric("at_least_one_exit")) * 100,
    }


def run_benchmark_suite(
    algorithms: list[str],
    agent_counts: list[int],
    mazes: list[str],
    preferred_direction: str,
    max_steps: int,
    trials: int,
    seed: int,
) -> list[dict[str, float | int | str]]:
    aggregated_results: list[dict[str, float | int | str]] = []

    for maze in mazes:
        for algorithm in algorithms:
            for agent_count in agent_counts:
                run_results = [
                    run_single_benchmark(
                        algorithm=algorithm,
                        agent_count=agent_count,
                        maze_filename=maze,
                        preferred_direction=preferred_direction,
                        max_steps=max_steps,
                        seed=seed + trial_index,
                    )
                    for trial_index in range(trials)
                ]
                aggregated_results.append(aggregate_runs(run_results))

    return aggregated_results


def print_results(aggregated_results: list[dict[str, float | int | str]]) -> None:
    headers = [
        "algorithm",
        "maze",
        "agents",
        "trials",
        "success %",
        "avg steps(exit)",
        "avg exit step",
        "avg steps(all)",
        "avg cells(exit)",
        "avg cells(all)",
        "global cells",
        "global explored %",
        "any exit %",
    ]

    rows: list[list[str]] = []
    for result in aggregated_results:
        rows.append(
            [
                str(result["algorithm"]),
                str(result["maze"]),
                str(result["agent_count"]),
                str(result["trials"]),
                format_metric(result["success_rate_pct"]),
                format_metric(result["mean_steps_success"]),
                format_metric(result["mean_exit_step_success"]),
                format_metric(result["mean_steps_all"]),
                format_metric(result["mean_visited_cells_success"]),
                format_metric(result["mean_visited_cells_all"]),
                format_metric(result["global_explored_cells"]),
                format_metric(result["global_explored_pct"]),
                format_metric(result["at_least_one_exit_rate_pct"]),
            ]
        )

    widths = [
        max(len(header), *(len(row[index]) for row in rows))
        for index, header in enumerate(headers)
    ]

    header_line = " | ".join(
        header.ljust(widths[index]) for index, header in enumerate(headers)
    )
    separator = "-+-".join("-" * width for width in widths)

    print(header_line)
    print(separator)
    for row in rows:
        print(
            " | ".join(
                value.ljust(widths[index]) for index, value in enumerate(row)
            )
        )


def write_csv(path: Path, aggregated_results: list[dict[str, float | int | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(aggregated_results[0].keys())

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(aggregated_results)


def main() -> None:
    args = parse_args()
    mazes = resolve_mazes(args.mazes)
    aggregated_results = run_benchmark_suite(
        algorithms=args.algorithms,
        agent_counts=args.agent_counts,
        mazes=mazes,
        preferred_direction=args.direction,
        max_steps=args.max_steps,
        trials=args.trials,
        seed=args.seed,
    )

    print_results(aggregated_results)

    if args.csv_out:
        output_path = Path(args.csv_out)
        write_csv(output_path, aggregated_results)
        print(f"\nCSV saved to: {output_path}")


if __name__ == "__main__":
    main()
