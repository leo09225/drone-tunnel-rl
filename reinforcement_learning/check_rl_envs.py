"""
Verification des environnements RL.

Objectif :
- verifier que MiniGrid fonctionne ;
- verifier que notre environnement custom SimpleTunnelEnv est compatible ;
- ne pas encore entrainer d'agent.

Stable-Baselines3 recommande d'utiliser check_env pour verifier qu'un
environnement custom respecte bien l'interface Gymnasium.
"""

import gymnasium as gym
import minigrid  # necessaire pour enregistrer les environnements MiniGrid
from minigrid.wrappers import ImgObsWrapper

try:
    from stable_baselines3.common.env_checker import check_env
except ImportError:
    check_env = None

try:
    from .simple_tunnel_env import SimpleTunnelEnv
except ImportError:
    from simple_tunnel_env import SimpleTunnelEnv


def maybe_check_env(env):
    """
    Lance la verification SB3 si la dependance est disponible.

    Cela permet de garder un check MiniGrid utile meme avant
    l'installation de Stable-Baselines3.
    """
    if check_env is None:
        print("Stable-Baselines3 absent : verification SB3 ignoree.")
        return

    check_env(env, warn=True)


def check_empty_env():
    """
    Verifie l'environnement MiniGrid de base.

    ImgObsWrapper transforme l'observation MiniGrid :
    avant  : dict avec image, direction, mission
    apres : seulement l'image

    C'est plus simple pour entrainer une politique CNN.
    """
    env = gym.make("MiniGrid-Empty-5x5-v0")
    env = ImgObsWrapper(env)

    print("Verification de MiniGrid-Empty-5x5-v0...")
    maybe_check_env(env)

    obs, info = env.reset(seed=42)
    print("Observation shape :", obs.shape)
    print("Action space :", env.action_space)

    env.close()
    print("MiniGrid-Empty OK\n")


def check_simple_tunnel_env():
    """
    Verifie notre environnement tunnel custom.
    """
    env = SimpleTunnelEnv()
    env = ImgObsWrapper(env)

    print("Verification de SimpleTunnelEnv...")
    maybe_check_env(env)

    obs, info = env.reset(seed=42)
    print("Observation shape :", obs.shape)
    print("Action space :", env.action_space)

    env.close()
    print("SimpleTunnelEnv OK\n")


if __name__ == "__main__":
    check_empty_env()
    check_simple_tunnel_env()
