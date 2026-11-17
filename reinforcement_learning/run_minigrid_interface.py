"""
Lanceur unique pour l'interface MiniGrid.

Objectif :
- ouvrir rapidement une fenetre MiniGrid ;
- utiliser le modele PPO entraine si disponible ;
- retomber sur un agent aleatoire si le modele ou SB3 manquent.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import gymnasium as gym
import minigrid  # necessaire pour enregistrer les environnements MiniGrid
from minigrid.wrappers import ImgObsWrapper

try:
    from stable_baselines3 import PPO
except ImportError:
    PPO = None

try:
    from .simple_tunnel_env import SimpleTunnelEnv
except ImportError:
    from simple_tunnel_env import SimpleTunnelEnv


MODEL_PATH = Path("reinforcement_learning/models/ppo_simple_tunnel")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the MiniGrid RL interface."
    )
    parser.add_argument(
        "--mode",
        choices=("trained", "random", "empty"),
        default="trained",
        help="trained loads the PPO model, random uses SimpleTunnelEnv, empty uses MiniGrid-Empty-5x5-v0.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=200,
        help="Number of environment steps to display.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed used for the first reset.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.1,
        help="Seconds to wait between steps so the interface stays readable.",
    )
    return parser.parse_args()


def get_effective_mode(requested_mode: str) -> str:
    if requested_mode != "trained":
        return requested_mode

    if PPO is None:
        print("Stable-Baselines3 absent : bascule automatique vers le mode random.")
        return "random"

    if not MODEL_PATH.with_suffix(".zip").exists():
        print(f"Modele introuvable : {MODEL_PATH}.zip")
        print("Bascule automatique vers le mode random.")
        return "random"

    return "trained"


def build_env(mode: str):
    if mode == "trained":
        return ImgObsWrapper(SimpleTunnelEnv(render_mode="human"))

    if mode == "empty":
        return gym.make("MiniGrid-Empty-5x5-v0", render_mode="human")

    return SimpleTunnelEnv(render_mode="human")


def run_trained_interface(args) -> None:
    env = build_env("trained")
    model = PPO.load(str(MODEL_PATH))
    observation, info = env.reset(seed=args.seed)

    try:
        for step in range(args.steps):
            action, _ = model.predict(observation, deterministic=True)
            observation, reward, terminated, truncated, info = env.step(action)

            print(
                f"Step={step}, action={int(action)}, reward={reward:.2f}, "
                f"terminated={terminated}, truncated={truncated}"
            )

            if args.delay > 0:
                time.sleep(args.delay)

            if terminated or truncated:
                print("Episode finished, resetting the environment.")
                observation, info = env.reset()
    finally:
        env.close()


def run_random_interface(mode: str, args) -> None:
    env = build_env(mode)
    observation, info = env.reset(seed=args.seed)

    try:
        for step in range(args.steps):
            action = env.action_space.sample()
            observation, reward, terminated, truncated, info = env.step(action)

            print(
                f"Step={step}, action={int(action)}, reward={reward:.2f}, "
                f"terminated={terminated}, truncated={truncated}"
            )

            if args.delay > 0:
                time.sleep(args.delay)

            if terminated or truncated:
                print("Episode finished, resetting the environment.")
                observation, info = env.reset()
    finally:
        env.close()


def main():
    args = parse_args()
    mode = get_effective_mode(args.mode)

    if mode == "trained":
        run_trained_interface(args)
        return

    run_random_interface(mode, args)


if __name__ == "__main__":
    main()
