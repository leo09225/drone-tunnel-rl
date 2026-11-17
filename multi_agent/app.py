from __future__ import annotations

import logging
from typing import TYPE_CHECKING

try:
    from multi_agent.agents import Drones, EnvStart
    from multi_agent.algo import (
        BalancedChoiceDrone,
        RandomDrone,
        StraightDrone,
        TremauxDrone,
        Unexplored,
    )
    from multi_agent.model import Vortex
    from multi_agent.rendering import compute_render_settings
except ModuleNotFoundError as exc:
    if exc.name != "multi_agent":
        raise
    from agents import Drones, EnvStart
    from algo import (
        BalancedChoiceDrone,
        RandomDrone,
        StraightDrone,
        TremauxDrone,
        Unexplored,
    )
    from model import Vortex
    from rendering import compute_render_settings

from mesa.visualization import (
    SolaraViz,
    SpaceRenderer,
)
from mesa.visualization.components import AgentPortrayalStyle, PropertyLayerStyle

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from mesa.agent import Agent
    from mesa.discrete_space import PropertyLayer

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()

formatter = logging.Formatter("(%(name)s)[%(levelname)s]: %(message)s")

console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

model = Vortex()
render_settings = compute_render_settings(model.width, model.height)


def propertylayer_portrayal(layer: PropertyLayer) -> PropertyLayerStyle | None:
    if layer.name == "Walls":
        return PropertyLayerStyle(
            color="black", colorbar=False, alpha=1, vmin=0, vmax=1
        )
    if layer.name == "Explored Cells":
        return PropertyLayerStyle(
            color="green", colorbar=False, alpha=0.5, vmin=0, vmax=1
        )
    return None


def agent_color(agent: Agent) -> str:
    """
    function to dynamically specify the agent color
    """
    if isinstance(agent, EnvStart):
        return "blue"
    if isinstance(agent, TremauxDrone):
        return "purple"
    if isinstance(agent, RandomDrone):
        return "red"
    if isinstance(agent, Unexplored):
        return "orange"
    if isinstance(agent, BalancedChoiceDrone):
        return "gold"
    if isinstance(agent, StraightDrone):
        return "cyan"
    if isinstance(agent, Drones):
        return "red"
    return "gray"


def agent_shape(agent: Agent) -> str:
    """
    function to dynamically specify the agent shape
    """
    if isinstance(agent, EnvStart):
        return "s"
    if isinstance(agent, Drones):
        if agent.front == "E":
            return ">"
        if agent.front == "N":
            return "^"
        if agent.front == "W":
            return "<"
        if agent.front == "S":
            return "v"
    return "o"


def agent_portrayal(agent: Agent) -> AgentPortrayalStyle:
    settings = compute_render_settings(agent.model.width, agent.model.height)
    color = agent_color(agent)
    marker = agent_shape(agent)
    if isinstance(agent, EnvStart):
        return AgentPortrayalStyle(
            color=color,
            marker=marker,
            size=settings.start_size,
            zorder=0,  # ordre de dessin (plus haut = devant)
            alpha=0.5,  # opacité
            edgecolors="black",
            linewidths=1.0,
        )
    if isinstance(agent, Drones):
        return AgentPortrayalStyle(
            color=color,
            marker=marker,
            size=settings.drone_size,
            zorder=1,  # ordre de dessin (plus haut = devant)
            alpha=1.0,  # opacité
            edgecolors="black",
            linewidths=1.0,
        )
    return AgentPortrayalStyle(color=color, marker=marker)


def post_process_space(ax: Axes) -> None:
    width = int(round(ax.get_xlim()[1] - ax.get_xlim()[0]))
    height = int(round(ax.get_ylim()[1] - ax.get_ylim()[0]))
    settings = compute_render_settings(width, height)

    ax.figure.set_dpi(settings.dpi)
    ax.figure.set_size_inches(settings.figure_inches, settings.figure_inches)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

    for line in ax.lines:
        line.set_linewidth(settings.grid_linewidth)
        line.set_alpha(settings.grid_alpha)


renderer: SpaceRenderer = SpaceRenderer(model, backend="matplotlib")
renderer.setup_structure(
    figsize=(render_settings.figure_inches, render_settings.figure_inches),
    dpi=render_settings.dpi,
)

renderer.draw_structure()

renderer.setup_propertylayer(propertylayer_portrayal)
renderer.draw_propertylayer()

renderer.setup_agents(agent_portrayal)
renderer.draw_agents()

renderer.post_process = post_process_space

model_params = {
    "n_random": {
        "type": "SliderInt",
        "value": 1,
        "label": "Agents aléatoires",
        "min": 0,
        "max": 10,
        "step": 1,
    },
    "n_unexplored": {
        "type": "SliderInt",
        "value": 0,
        "label": "Agents non explorés",
        "min": 0,
        "max": 10,
        "step": 1,
    },
    "n_tremaux": {
        "type": "SliderInt",
        "value": 0,
        "label": "Agents Trémaux",
        "min": 0,
        "max": 10,
        "step": 1,
    },
    "n_balanced_choice": {
        "type": "SliderInt",
        "value": 0,
        "label": "Agents choix équilibré",
        "min": 0,
        "max": 10,
        "step": 1,
    },
    "n_straight": {
        "type": "SliderInt",
        "value": 0,
        "label": "Agents droits",
        "min": 0,
        "max": 10,
        "step": 1,
    },
}

page = SolaraViz(
    model,
    renderer,
    name="Vortex sim",
    model_params=model_params,
    play_interval=1,
    render_interval=1,
    width="100%",
    height="90vh",
)
