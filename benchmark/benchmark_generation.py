import csv
import random
from contextlib import contextmanager
from pathlib import Path

import generation.config as generation_config
import generation.models.grid as grid_model
import generation.rules.birth as birth_rules
from generation.algorithms.ca import ca_step, clone_grid, create_ca_grid
from generation.algorithms.digging_agent import generate_with_digging_agent_frames


SCENARIO_ORDER = [
    "ca_continuity_corner_wp07",
    "ca_digger_wp07",
    "agent_solo",
    "agent_4_agents",
]

DEFAULT_WIDTH = 50
DEFAULT_HEIGHT = 50
DEFAULT_TOTAL_STEPS = 10000
DEFAULT_WALL_PERCENTAGE = 0.7
DEFAULT_SEED = 0
DEFAULT_NUM_RUNS = 1


def compute_tunnel_percentage(grid):
    total_cells = sum(len(row) for row in grid)
    tunnel_cells = sum(cell.state for row in grid for cell in row)
    return round((tunnel_cells / total_cells) * 100, 6)


def repeat_last_value(history, target_length):
    if not history:
        raise ValueError("History must contain at least one value.")

    padded_history = list(history)

    while len(padded_history) < target_length:
        padded_history.append(padded_history[-1])

    return padded_history[:target_length]


def average_histories(histories):
    if not histories:
        raise ValueError("Histories must contain at least one run.")

    history_length = len(histories[0])

    if history_length == 0:
        raise ValueError("Histories must contain at least one step.")

    for history in histories[1:]:
        if len(history) != history_length:
            raise ValueError("All histories must have the same length.")

    averaged_history = []

    for step in range(history_length):
        step_average = sum(history[step] for history in histories) / len(histories)
        averaged_history.append(round(step_average, 6))

    return averaged_history


def build_wide_rows(histories, total_steps=DEFAULT_TOTAL_STEPS):
    target_length = total_steps + 1
    padded_histories = {
        scenario: repeat_last_value(histories[scenario], target_length)
        for scenario in SCENARIO_ORDER
    }

    rows = []

    for step in range(target_length):
        row = {"step": step}

        for scenario in SCENARIO_ORDER:
            row[scenario] = padded_histories[scenario][step]

        rows.append(row)

    return rows


def write_wide_csv(rows, output_path):
    output_path = Path(output_path)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["step", *SCENARIO_ORDER])
        writer.writeheader()
        writer.writerows(rows)


@contextmanager
def temporary_random_seed(seed):
    state = random.getstate()
    random.seed(seed)

    try:
        yield
    finally:
        random.setstate(state)


@contextmanager
def temporary_module_values(module_overrides):
    originals = []

    for module, overrides in module_overrides.items():
        for attribute_name, new_value in overrides.items():
            originals.append((module, attribute_name, getattr(module, attribute_name)))
            setattr(module, attribute_name, new_value)

    try:
        yield
    finally:
        for module, attribute_name, original_value in reversed(originals):
            setattr(module, attribute_name, original_value)


def run_ca_scenario(
    *,
    width,
    height,
    total_steps,
    seed,
    wall_percentage,
    enable_birth_continuity,
    enable_birth_corner,
    enable_digger,
):
    overrides = {
        generation_config: {
            "WALL_PERCENTAGE": wall_percentage,
            "ENABLE_BIRTH_CONTINUITY": enable_birth_continuity,
            "ENABLE_BIRTH_CORNER": enable_birth_corner,
            "ENABLE_DIGGER": enable_digger,
        },
        grid_model: {
            "WALL_PERCENTAGE": wall_percentage,
        },
        birth_rules: {
            "ENABLE_BIRTH_CONTINUITY": enable_birth_continuity,
            "ENABLE_BIRTH_CORNER": enable_birth_corner,
            "ENABLE_DIGGER": enable_digger,
        },
    }

    with temporary_module_values(overrides), temporary_random_seed(seed):
        current_grid = create_ca_grid(width, height, fixed_tunnels=None)
        next_grid = clone_grid(current_grid)
        history = [compute_tunnel_percentage(current_grid)]

        for _ in range(total_steps):
            ca_step(current_grid, next_grid, fixed_tunnels=None)
            current_grid, next_grid = next_grid, current_grid
            history.append(compute_tunnel_percentage(current_grid))

    return history


def run_agent_scenario(*, width, height, total_steps, seed, agent_count):
    _, frames = generate_with_digging_agent_frames(
        n=width,
        m=height,
        steps=total_steps,
        turn_probability=generation_config.AGENT_TURN_PROBABILITY,
        loop_probability=generation_config.AGENT_LOOP_PROBABILITY,
        branch_probability=generation_config.AGENT_BRANCH_PROBABILITY,
        seed=seed,
        mode=generation_config.AGENT_MODE,
        target_loops=generation_config.TARGET_LOOPS,
        agent_count=agent_count,
    )

    history = [compute_tunnel_percentage(frame_grid) for frame_grid, _, _ in frames]
    return repeat_last_value(history, total_steps + 1)


def run_benchmark(
    output_path=None,
    width=DEFAULT_WIDTH,
    height=DEFAULT_HEIGHT,
    total_steps=DEFAULT_TOTAL_STEPS,
    seed=DEFAULT_SEED,
    num_runs=DEFAULT_NUM_RUNS,
):
    histories = {}

    ca_continuity_corner_runs = []
    ca_digger_runs = []
    agent_solo_runs = []
    agent_4_agents_runs = []

    for run_index in range(num_runs):
        run_seed = seed + run_index

        ca_continuity_corner_runs.append(
            run_ca_scenario(
                width=width,
                height=height,
                total_steps=total_steps,
                seed=run_seed,
                wall_percentage=DEFAULT_WALL_PERCENTAGE,
                enable_birth_continuity=True,
                enable_birth_corner=True,
                enable_digger=False,
            )
        )

        ca_digger_runs.append(
            run_ca_scenario(
                width=width,
                height=height,
                total_steps=total_steps,
                seed=run_seed,
                wall_percentage=DEFAULT_WALL_PERCENTAGE,
                enable_birth_continuity=False,
                enable_birth_corner=False,
                enable_digger=True,
            )
        )

        agent_solo_runs.append(
            run_agent_scenario(
                width=width,
                height=height,
                total_steps=total_steps,
                seed=run_seed,
                agent_count=1,
            )
        )

        agent_4_agents_runs.append(
            run_agent_scenario(
                width=width,
                height=height,
                total_steps=total_steps,
                seed=run_seed,
                agent_count=4,
            )
        )

    histories["ca_continuity_corner_wp07"] = average_histories(
        ca_continuity_corner_runs
    )
    histories["ca_digger_wp07"] = average_histories(ca_digger_runs)
    histories["agent_solo"] = average_histories(agent_solo_runs)
    histories["agent_4_agents"] = average_histories(agent_4_agents_runs)

    rows = build_wide_rows(histories, total_steps=total_steps)

    if output_path is None:
        output_path = Path(__file__).with_name("benchmark_generation.csv")

    write_wide_csv(rows, output_path)
    return rows


if __name__ == "__main__":
    csv_path = Path(__file__).with_name("try.csv")
    run_benchmark(output_path=csv_path)
    print(f"Benchmark saved to {csv_path}")
