"""
Évaluation visuelle du modèle entraîné.

Objectif :
- charger le modèle PPO entraîné ;
- voir l'agent agir dans le tunnel ;
- vérifier s'il a appris quelque chose.

À lancer après train_simple_tunnel_ppo.py.
"""

from pathlib import Path

from minigrid.wrappers import ImgObsWrapper
from stable_baselines3 import PPO

try:
    from .simple_tunnel_env import SimpleTunnelEnv
except ImportError:
    from simple_tunnel_env import SimpleTunnelEnv


MODEL_PATH = Path("reinforcement_learning/models/ppo_simple_tunnel")


def main():
    env = SimpleTunnelEnv(render_mode="human")
    env = ImgObsWrapper(env)

    model = PPO.load(str(MODEL_PATH))

    observation, info = env.reset(seed=42)

    for step in range(200):
        # deterministic=True :
        # l'agent choisit l'action qu'il pense être la meilleure,
        # plutôt qu'une action un peu aléatoire.
        action, _ = model.predict(observation, deterministic=True)

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
