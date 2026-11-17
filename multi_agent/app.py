from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import solara

try:
    from .benchmark_algorithms import format_metric, run_benchmark_suite
    from .agents import (
        Drones,
        EnvExit,
        EnvStart,
        LeftHandDrone,
        PledgeDrone,
        RandomDrone,
        StraightDrone,
    )
    from .model import Vortex
except ImportError:
    from benchmark_algorithms import format_metric, run_benchmark_suite
    from agents import (
        Drones,
        EnvExit,
        EnvStart,
        LeftHandDrone,
        PledgeDrone,
        RandomDrone,
        StraightDrone,
    )
    from model import Vortex


MAZE_OPTIONS = {
    "1 - Wall": (1, "maze_pledge_01_wall.csv"),
    "2 - Island": (2, "maze_pledge_02_island.csv"),
    "3 - Trap": (3, "maze_pledge_03_trap.csv"),
    "4 - Wrong Direction Spiral": (4, "maze_pledge_04_wrong_direction.csv"),
}
MAZE_LABELS = list(MAZE_OPTIONS.keys())


maze_label = solara.reactive("2 - Island")
preferred_direction_id = solara.reactive(1)  # 0=N, 1=E, 2=S, 3=W
n_pledge = solara.reactive(1)
n_left_hand = solara.reactive(0)
n_random = solara.reactive(0)
n_straight = solara.reactive(0)
max_steps = solara.reactive(1000)
model_state = solara.reactive(None)
render_tick = solara.reactive(0)
benchmark_agent_count = solara.reactive(50)
benchmark_trials = solara.reactive(5)
benchmark_max_steps = solara.reactive(300)
benchmark_seed = solara.reactive(42)
benchmark_results_state = solara.reactive([])
benchmark_maze_labels = solara.reactive(MAZE_LABELS.copy())
benchmark_scope_label = solara.reactive("No benchmark launched yet.")

DIRECTIONS = ["N", "E", "S", "W"]


def current_maze_id() -> int:
    return MAZE_OPTIONS[maze_label.value][0]


def current_maze_filename() -> str:
    return MAZE_OPTIONS[maze_label.value][1]


def create_model() -> Vortex:
    return Vortex(
        n_random=n_random.value,
        n_straight=n_straight.value,
        n_pledge=n_pledge.value,
        n_left_hand=n_left_hand.value,
        maze_id=current_maze_id(),
        preferred_direction=DIRECTIONS[preferred_direction_id.value],
        max_steps=max_steps.value,
        seed=42,
    )


def reset_model() -> None:
    model_state.value = create_model()
    render_tick.value += 1


def step_model() -> None:
    if model_state.value is None:
        reset_model()

    if model_state.value is not None and model_state.value.running:
        model_state.value.step()
        render_tick.value += 1


def run_many_steps(n: int = 50) -> None:
    if model_state.value is None:
        reset_model()

    if model_state.value is None:
        return

    for _ in range(n):
        if not model_state.value.running:
            break
        model_state.value.step()

    render_tick.value += 1


def run_benchmark(use_current_maze_only: bool) -> None:
    if use_current_maze_only:
        mazes = [current_maze_filename()]
        benchmark_scope_label.value = f"Running benchmark on current maze: {maze_label.value}..."
    else:
        selected_labels = benchmark_maze_labels.value or MAZE_LABELS
        mazes = [MAZE_OPTIONS[label][1] for label in selected_labels]
        benchmark_scope_label.value = (
            "Running benchmark on selected mazes: "
            + ", ".join(selected_labels)
            + "..."
        )

    benchmark_results_state.value = run_benchmark_suite(
        algorithms=["pledge", "left_hand", "random", "straight"],
        agent_counts=[benchmark_agent_count.value],
        mazes=mazes,
        preferred_direction=DIRECTIONS[preferred_direction_id.value],
        max_steps=benchmark_max_steps.value,
        trials=benchmark_trials.value,
        seed=benchmark_seed.value,
    )

    benchmark_scope_label.value = (
        f"Benchmark finished on current maze: {maze_label.value}."
        if use_current_maze_only
        else "Benchmark finished on selected mazes: "
        + ", ".join(benchmark_maze_labels.value or MAZE_LABELS)
        + "."
    )


def draw_model(model: Vortex):
    fig, ax = plt.subplots(figsize=(9, 6))

    walls = model.env_walls
    height, width = walls.shape
    image = np.ones((height, width, 3))

    image[walls == 1] = [0.0, 0.0, 0.0]

    explored_mask = (model.explored_cells == 1) & (walls == 0)
    image[explored_mask] = [0.65, 1.0, 0.65]

    ax.imshow(
        image,
        origin="lower",
        extent=(-0.5, width - 0.5, -0.5, height - 0.5),
    )

    ax.set_xticks(np.arange(-0.5, width, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, height, 1), minor=True)
    ax.grid(which="minor", color="lightgray", linewidth=0.5)

    for agent in model.agents:
        if not hasattr(agent, "cell") or agent.cell is None:
            continue

        x, y = agent.cell.coordinate

        if isinstance(agent, EnvStart):
            ax.scatter(x, y, marker="s", s=180, color="blue", edgecolors="black")
            ax.text(x, y + 0.35, "Start", ha="center", fontsize=8)

        elif isinstance(agent, EnvExit):
            ax.scatter(x, y, marker="*", s=250, color="lime", edgecolors="black")
            ax.text(x, y + 0.35, "Exit", ha="center", fontsize=8)

        elif isinstance(agent, PledgeDrone):
            marker = {
                "N": "^",
                "E": ">",
                "S": "v",
                "W": "<",
            }.get(agent.front, "o")

            ax.scatter(
                x,
                y,
                marker=marker,
                s=180,
                color="purple",
                edgecolors="black",
            )
            ax.text(
                x,
                y - 0.45,
                f"Pledge\n{agent.mode}\nturn={agent.turn_counter}",
                ha="center",
                va="top",
                fontsize=7,
                color="purple",
            )

        elif isinstance(agent, LeftHandDrone):
            marker = {
                "N": "^",
                "E": ">",
                "S": "v",
                "W": "<",
            }.get(agent.front, "o")

            ax.scatter(
                x,
                y,
                marker=marker,
                s=180,
                color="teal",
                edgecolors="black",
            )
            ax.text(
                x,
                y - 0.45,
                f"Left hand\n{agent.mode}",
                ha="center",
                va="top",
                fontsize=7,
                color="teal",
            )

        elif isinstance(agent, RandomDrone):
            ax.scatter(x, y, marker="o", s=120, color="red", edgecolors="black")

        elif isinstance(agent, StraightDrone):
            ax.scatter(x, y, marker="o", s=120, color="orange", edgecolors="black")

        elif isinstance(agent, Drones):
            ax.scatter(x, y, marker="o", s=120, color="gray", edgecolors="black")

    ax.set_title(
        f"Pledge vs left-hand rule - maze {model.maze_id} | "
        f"steps={model.step_count} | "
        f"direction={model.preferred_direction} | "
        f"exit reached={model.finished}"
    )

    ax.set_xlim(-0.5, width - 0.5)
    ax.set_ylim(-0.5, height - 0.5)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

    return fig


def count_agents(model: Vortex, agent_class: type[Drones]) -> tuple[int, int]:
    agents = list(model.agents_by_type.get(agent_class, []))
    reached_exit = sum(1 for agent in agents if agent.reached_exit)
    return len(agents), reached_exit


def benchmark_results_to_markdown(
    benchmark_results: list[dict[str, float | int | str]],
) -> str:
    if not benchmark_results:
        return "_No benchmark results yet._"

    headers = [
        "algorithm",
        "maze",
        "agents",
        "trials",
        "success %",
        "avg steps(exit)",
        "avg steps(all)",
        "avg cells(all)",
        "global explored %",
    ]

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]

    for result in benchmark_results:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(result["algorithm"]),
                    str(result["maze"]),
                    str(result["agent_count"]),
                    str(result["trials"]),
                    format_metric(result["success_rate_pct"]),
                    format_metric(result["mean_steps_success"]),
                    format_metric(result["mean_steps_all"]),
                    format_metric(result["mean_visited_cells_all"]),
                    format_metric(result["global_explored_pct"]),
                ]
            )
            + " |"
        )

    return "\n".join(lines)


@solara.component
def Page():
    _ = render_tick.value

    if model_state.value is None:
        reset_model()

    model = model_state.value

    solara.Markdown("# Demo Mesa - Pledge vs Left-Hand Rule")

    solara.Markdown(
        """
This demo tests the **Pledge** algorithm on three different mazes.

The agent tries to keep a preferred direction, by default **East**.
When it meets an obstacle, it follows the wall while counting its turns.
It leaves the wall when the turn counter returns to zero and it faces
its preferred direction again.

You can also add a **left-hand rule** agent to compare the behaviors.
In mazes with an island or a trap, that agent can keep following the wall
without escaping, while Pledge is able to leave the obstacle.
"""
    )

    with solara.Sidebar():
        solara.Markdown("## Parameters")

        solara.Select("Simulation maze", value=maze_label, values=MAZE_LABELS)

        solara.SliderInt(
            "Preferred direction: 0=N, 1=E, 2=S, 3=W",
            value=preferred_direction_id,
            min=0,
            max=3,
            step=1,
        )

        solara.SliderInt(
            "Pledge agents",
            value=n_pledge,
            min=0,
            max=3,
            step=1,
        )

        solara.SliderInt(
            "Left-hand agents",
            value=n_left_hand,
            min=0,
            max=3,
            step=1,
        )

        solara.SliderInt(
            "Random agents",
            value=n_random,
            min=0,
            max=10,
            step=1,
        )

        solara.SliderInt(
            "Straight agents",
            value=n_straight,
            min=0,
            max=10,
            step=1,
        )

        solara.SliderInt(
            "Max steps",
            value=max_steps,
            min=100,
            max=3000,
            step=100,
        )

        solara.Button("Reset simulation", on_click=reset_model)
        solara.Button("Step", on_click=step_model)
        solara.Button("Run 50 steps", on_click=lambda: run_many_steps(50))
        solara.Button("Run 200 steps", on_click=lambda: run_many_steps(200))

        solara.Markdown("## Benchmark")

        solara.SliderInt(
            "Benchmark agents",
            value=benchmark_agent_count,
            min=1,
            max=100,
            step=1,
        )

        solara.SliderInt(
            "Benchmark trials",
            value=benchmark_trials,
            min=1,
            max=20,
            step=1,
        )

        solara.SliderInt(
            "Benchmark max steps",
            value=benchmark_max_steps,
            min=50,
            max=3000,
            step=50,
        )

        solara.SliderInt(
            "Benchmark seed",
            value=benchmark_seed,
            min=0,
            max=999,
            step=1,
        )

        solara.SelectMultiple(
            "Benchmark mazes",
            benchmark_maze_labels,
            MAZE_LABELS,
        )

        solara.Button(
            "Benchmark current maze",
            on_click=lambda: run_benchmark(use_current_maze_only=True),
        )
        solara.Button(
            "Benchmark selected mazes",
            on_click=lambda: run_benchmark(use_current_maze_only=False),
        )

    if model is not None:
        pledge_total, pledge_finished = count_agents(model, PledgeDrone)
        left_total, left_finished = count_agents(model, LeftHandDrone)
        random_total, random_finished = count_agents(model, RandomDrone)
        straight_total, straight_finished = count_agents(model, StraightDrone)

        solara.Markdown(
            f"""
**Current state:**

- Maze: `{maze_label.value}`
- Preferred direction: `{model.preferred_direction}`
- Step: `{model.step_count}`
- At least one exit reached: `{model.finished}`
- Simulation active: `{model.running}`
- Pledge: `{pledge_finished}/{pledge_total}` reached the exit
- Left-hand rule: `{left_finished}/{left_total}` reached the exit
- Random: `{random_finished}/{random_total}` reached the exit
- Straight: `{straight_finished}/{straight_total}` reached the exit
"""
        )

        fig = draw_model(model)
        solara.FigureMatplotlib(fig)
        plt.close(fig)

    solara.Markdown("## Benchmark results")
    solara.Markdown(
        f"""
- Scope: `{benchmark_scope_label.value}`
- Algorithms benchmarked: `pledge`, `left_hand`, `random`, `straight`
- Direction used: `{DIRECTIONS[preferred_direction_id.value]}`
- Agents per algorithm: `{benchmark_agent_count.value}`
- Trials: `{benchmark_trials.value}`
- Max steps: `{benchmark_max_steps.value}`
- Benchmark maze selection: `{", ".join(benchmark_maze_labels.value or MAZE_LABELS)}`
"""
    )
    solara.Markdown(benchmark_results_to_markdown(benchmark_results_state.value))
