"""
Small smoke test for the MiniGrid installation.

Goal:
- verify that MiniGrid is correctly installed,
- open a standard environment from the library,
- run a few random actions,
- inspect the values returned by Gymnasium.

This file does not train anything.
It is only used to validate the tooling before creating a custom RL environment.
"""

from __future__ import annotations

import gymnasium as gym
import minigrid  # Important: importing minigrid registers MiniGrid environments.


def main() -> None:
    # We use a very small built-in environment:
    # - empty room
    # - one goal square
    # - simple enough to inspect manually
    env = gym.make("MiniGrid-Empty-5x5-v0")

    # reset() starts a new episode and returns:
    # - observation: what the agent perceives
    # - info: additional metadata
    observation, info = env.reset(seed=42)

    print("===== INITIAL OBSERVATION =====")
    print(observation)
    print()
    print("Observation keys:", observation.keys())
    print("Action space:", env.action_space)
    print()

    # We only run a few random steps because the goal here is inspection.
    for step_index in range(10):
        action = env.action_space.sample()
        observation, reward, terminated, truncated, info = env.step(action)

        print(f"Step {step_index}")
        print("observation:", observation)
        print("action:", action)
        print("reward:", reward)
        print("terminated:", terminated)
        print("truncated:", truncated)
        print("---")

        if terminated or truncated:
            print("Episode finished, resetting the environment.")
            observation, info = env.reset()

    env.close()


if __name__ == "__main__":
    main()
