import csv
import logging
from pathlib import Path

from multi_agent.model import Vortex

MAX_STEPS = 10000
AGENT_NAMES = ["random", "straight", "tremaux", "balancedchoice", "unexplored"]


def list_map_files(base_dir=None):
    base_path = (
        Path(base_dir) if base_dir is not None else Path(__file__).parent / "50X50"
    )
    map_files = []

    for folder_name in ("CA", "agent"):
        folder_path = base_path / folder_name

        if not folder_path.exists():
            continue

        for csv_path in sorted(folder_path.glob("*.csv")):
            map_files.append((f"{folder_name}/{csv_path.name}", csv_path))

    return map_files


def get_agent_config(agent_name):
    config = {
        "n_random": 0,
        "n_straight": 0,
        "n_tremaux": 0,
        "n_balanced_choice": 0,
        "n_unexplored": 0,
    }

    if agent_name == "random":
        config["n_random"] = 1
    elif agent_name == "straight":
        config["n_straight"] = 1
    elif agent_name == "tremaux":
        config["n_tremaux"] = 1
    elif agent_name == "balancedchoice":
        config["n_balanced_choice"] = 1
    elif agent_name == "unexplored":
        config["n_unexplored"] = 1
    else:
        raise ValueError(f"Unknown agent name: {agent_name}")

    return config


def compute_explored_percent(model):
    tunnel_mask = model.env_walls == 0
    total_tunnels = int(tunnel_mask.sum())

    if total_tunnels == 0:
        return 100.0
    explored_tunnels = int((tunnel_mask & (model.explored_cells == 1)).sum())
    return round((explored_tunnels / total_tunnels) * 100, 2)


def run_benchmark_for_map(map_path, agent_name, max_steps=MAX_STEPS):
    model = Vortex(
        env_path=str(map_path),
        seed=0,
        **get_agent_config(agent_name),
    )

    for _ in range(max_steps):
        model.step()

    return compute_explored_percent(model)


def write_benchmark_csv(rows, output_path):
    output_path = Path(output_path)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["map", *AGENT_NAMES])
        writer.writerows(rows)


def run_benchmark(base_dir=None, output_path=None, max_steps=MAX_STEPS):
    if output_path is None:
        output_path = Path(__file__).parent / "benchmark_coverage.csv"

    map_files = list_map_files(base_dir=base_dir)

    previous_logger_states = {}
    for logger_name in ("model", "agent", "app"):
        logger = logging.getLogger(logger_name)
        previous_logger_states[logger_name] = logger.disabled
        logger.disabled = True

    try:
        rows = []
        total_maps = len(map_files)

        print(
            f"Benchmark start: {total_maps} map(s), {len(AGENT_NAMES)} algo(s), "
            f"max_steps={max_steps}"
        )

        for map_index, (map_name, map_path) in enumerate(map_files, start=1):
            print(f"[{map_index}/{total_maps}] {map_name}")
            row = [map_name]

            for agent_name in AGENT_NAMES:
                result = run_benchmark_for_map(
                    map_path, agent_name, max_steps=max_steps
                )
                row.append(result)
                print(f"  - {agent_name}: {result}%")

            rows.append(row)

        write_benchmark_csv(rows, output_path)
        print(f"Benchmark saved to {output_path}")
        return rows

    finally:
        for logger_name, disabled in previous_logger_states.items():
            logging.getLogger(logger_name).disabled = disabled


if __name__ == "__main__":
    run_benchmark()
