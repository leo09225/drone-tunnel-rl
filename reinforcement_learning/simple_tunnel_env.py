"""
Custom MiniGrid environment: SimpleTunnelEnv.

Goal:
build a very small environment that looks like a tunnel.

This file is meant to make the 4 core RL elements explicit:

1. States / observations
   The agent receives MiniGrid's local partial observation.
   By default that observation contains:
   - image: local view around the agent
   - direction: agent orientation
   - mission: text description of the goal

2. Actions
   We keep only the 3 useful MiniGrid actions:
   0: turn left
   1: turn right
   2: move forward

3. Transition
   MiniGrid handles the dynamics:
   - moving into a free cell changes the position
   - moving into a wall leaves the agent blocked
   - reaching the goal ends the episode

4. Reward
   We keep MiniGrid's success reward and add a small step penalty
   to encourage shorter trajectories.

This is not a full training pipeline yet.
It is a first custom environment we can inspect and explain.
"""

from __future__ import annotations

from gymnasium import spaces
from minigrid.core.grid import Grid
from minigrid.core.mission import MissionSpace
from minigrid.core.world_object import Goal, Wall
from minigrid.minigrid_env import MiniGridEnv


ACTION_LEFT = 0
ACTION_RIGHT = 1
ACTION_FORWARD = 2

# The tunnel is carved cell by cell so the path is easy to explain.
TUNNEL_PATH: list[tuple[int, int]] = [
    (1, 1),
    (2, 1),
    (3, 1),
    (4, 1),
    (4, 2),
    (4, 3),
    (5, 3),
    (6, 3),
    (6, 4),
    (6, 5),
    (7, 5),
    (7, 6),
    (7, 7),
]


class SimpleTunnelEnv(MiniGridEnv):
    """
    Small tunnel environment built on top of MiniGridEnv.

    The grid is first filled with walls, then a single valid path is carved.
    The agent starts at the beginning of the tunnel and the goal is placed
    at the end of the tunnel.
    """

    def __init__(
        self,
        size: int = 9,
        agent_start_pos: tuple[int, int] = (1, 1),
        agent_start_dir: int = 0,
        max_steps: int | None = None,
        **kwargs,
    ):
        # Initial position of the agent in grid coordinates.
        self.agent_start_pos = agent_start_pos

        # Initial direction of the agent.
        # In MiniGrid, 0 usually means "facing east / right".
        self.agent_start_dir = agent_start_dir

        # The mission is a text instruction exposed by MiniGrid.
        mission_space = MissionSpace(mission_func=self._gen_mission)

        # If the caller does not provide a step budget, we choose a simple one.
        # This avoids episodes running forever when the agent gets stuck.
        if max_steps is None:
            max_steps = 4 * size**2

        super().__init__(
            mission_space=mission_space,
            grid_size=size,
            max_steps=max_steps,
            see_through_walls=True,
            **kwargs,
        )

        # We deliberately reduce the action space to the 3 actions that matter
        # in this simple tunnel setting.
        self.action_space = spaces.Discrete(3)

    @staticmethod
    def _gen_mission() -> str:
        """
        Mission text shown in the observation.
        """
        return "reach the end of the tunnel"

    def _fill_inner_area_with_walls(self, width: int, height: int) -> None:
        """
        Fill the inside of the map with walls.

        We do this first, then we carve only the cells that belong to the
        tunnel path. This makes the environment structure very explicit.
        """
        for x in range(1, width - 1):
            for y in range(1, height - 1):
                self.grid.set(x, y, Wall())

    def _carve_tunnel_path(self) -> None:
        """
        Open the cells listed in TUNNEL_PATH.

        In MiniGrid, assigning None to a cell means the cell is empty.
        """
        for x, y in TUNNEL_PATH:
            self.grid.set(x, y, None)

    def _gen_grid(self, width: int, height: int) -> None:
        """
        Build the grid layout.

        This method is called automatically by MiniGrid during env.reset().
        Following the official tutorial, we:
        1. create an empty Grid object,
        2. add outer walls,
        3. create the world layout,
        4. place the goal,
        5. place the agent.
        """
        # Step 1: create the grid object.
        self.grid = Grid(width, height)

        # Step 2: create the external border walls.
        self.grid.wall_rect(0, 0, width, height)

        # Step 3: create the internal world.
        self._fill_inner_area_with_walls(width, height)
        self._carve_tunnel_path()

        # Step 4: place the goal at the end of the tunnel.
        goal_position = TUNNEL_PATH[-1]
        self.put_obj(Goal(), goal_position[0], goal_position[1])

        # Step 5: place the agent at the beginning of the tunnel.
        self.agent_pos = self.agent_start_pos
        self.agent_dir = self.agent_start_dir

        # MiniGrid expects the mission string to be available on the env.
        self.mission = self._gen_mission()

    def step(self, action: int):
        """
        Apply an action to the environment.

        We first reuse MiniGrid's default transition logic, then slightly adapt
        the reward with a small negative step cost.
        """
        observation, reward, terminated, truncated, info = super().step(action)

        # Small penalty at every step.
        # The goal is to prefer shorter solutions over long wandering paths.
        reward -= 0.01

        return observation, reward, terminated, truncated, info


def main():
    """
    Manual smoke test with random actions.

    This is useful to check that the environment opens, runs, and terminates
    correctly before thinking about RL training.
    """
    env = SimpleTunnelEnv(render_mode="human")
    observation, info = env.reset(seed=42)

    for step in range(100):
        action = env.action_space.sample()
        observation, reward, terminated, truncated, info = env.step(action)

        print(
            f"Step={step}, action={action}, reward={reward:.2f}, "
            f"terminated={terminated}, truncated={truncated}"
        )

        if terminated or truncated:
            observation, info = env.reset()

    env.close()


if __name__ == "__main__":
    main()
