"""
Inspection script for the custom MiniGrid tunnel environment.

Goal:
show, on our own environment, the 4 elements we want to explain in a report:
1. observations
2. actions
3. transition
4. reward

This script is the natural next step after inspect_empty_env.py:
we now inspect a custom environment instead of the default EmptyEnv.
"""

from __future__ import annotations

from minigrid.wrappers import ImgObsWrapper

try:
    from .simple_tunnel_env import (
        ACTION_FORWARD,
        ACTION_LEFT,
        ACTION_RIGHT,
        SimpleTunnelEnv,
    )
except ImportError:
    from simple_tunnel_env import (
        ACTION_FORWARD,
        ACTION_LEFT,
        ACTION_RIGHT,
        SimpleTunnelEnv,
    )


def inspect_raw_observation() -> None:
    """
    Inspect the default MiniGrid observation dictionary.

    This is the easiest way to explain what the environment exposes before
    applying any wrapper.
    """
    env = SimpleTunnelEnv()
    observation, info = env.reset(seed=42)

    print("===== SIMPLE TUNNEL: RAW OBSERVATION =====")
    print("Observation space:", env.observation_space)
    print("Action space:", env.action_space)
    print("Observation type:", type(observation))
    print("Available keys:", observation.keys())
    print("Direction:", observation["direction"])
    print("Mission:", observation["mission"])
    print("Image shape:", observation["image"].shape)
    print()

    print("Actions used in this custom environment:")
    print(f"{ACTION_LEFT} : turn left")
    print(f"{ACTION_RIGHT} : turn right")
    print(f"{ACTION_FORWARD} : move forward")
    print()

    env.close()


def inspect_wrapped_observation() -> None:
    """
    Inspect the image-only observation used for CNN training.

    ImgObsWrapper removes the dictionary and keeps only the image tensor.
    That is usually the most convenient representation for deep RL.
    """
    env = SimpleTunnelEnv()
    env = ImgObsWrapper(env)
    observation, info = env.reset(seed=42)

    print("===== SIMPLE TUNNEL: WRAPPED OBSERVATION =====")
    print("Observation space:", env.observation_space)
    print("Observation type:", type(observation))
    print("Image-only observation shape:", observation.shape)
    print()

    env.close()


def inspect_transitions_and_rewards() -> None:
    """
    Run a short hand-crafted action sequence.

    The idea is to show that:
    - turning changes orientation,
    - moving forward changes position only if the next cell is free,
    - the reward gets a small negative step penalty,
    - the episode ends when the goal is reached.
    """
    env = SimpleTunnelEnv()
    observation, info = env.reset(seed=42)

    # This sequence follows the tunnel for a few steps:
    # go forward along the corridor, turn left to follow the bend,
    # then continue forward.
    actions_to_test = [
        ACTION_FORWARD,
        ACTION_FORWARD,
        ACTION_FORWARD,
        ACTION_LEFT,
        ACTION_FORWARD,
        ACTION_FORWARD,
    ]

    print("===== SIMPLE TUNNEL: TRANSITIONS =====")
    print("Initial direction:", observation["direction"])
    print("Initial mission:", observation["mission"])
    print()

    for step_index, action in enumerate(actions_to_test):
        old_direction = observation["direction"]

        observation, reward, terminated, truncated, info = env.step(action)

        print(f"Step {step_index}")
        print("Action:", action)
        print("Old direction:", old_direction)
        print("New direction:", observation["direction"])
        print("Reward:", reward)
        print("Terminated:", terminated)
        print("Truncated:", truncated)
        print("---")

        if terminated or truncated:
            break

    env.close()


def main() -> None:
    inspect_raw_observation()
    inspect_wrapped_observation()
    inspect_transitions_and_rewards()


if __name__ == "__main__":
    main()
