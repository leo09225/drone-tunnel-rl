"""
Entraînement PPO sur SimpleTunnelEnv.

Objectif :
- entraîner un premier agent RL très simple ;
- utiliser notre environnement tunnel custom ;
- sauvegarder le modèle entraîné.

Important :
ce n'est pas encore l'objectif final du PIR.
C'est une première preuve que l'environnement peut être utilisé
pour de l'apprentissage par renforcement.
"""

from pathlib import Path

import torch
import torch.nn as nn
from minigrid.wrappers import ImgObsWrapper
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

try:
    from .simple_tunnel_env import SimpleTunnelEnv
except ImportError:
    from simple_tunnel_env import SimpleTunnelEnv


MODEL_DIR = Path("reinforcement_learning/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "ppo_simple_tunnel"


class MinigridFeaturesExtractor(BaseFeaturesExtractor):
    """
    Petit extracteur de caractéristiques pour les images MiniGrid.

    MiniGrid renvoie une petite image locale autour de l'agent.
    PPO ne travaille pas directement sur cette image brute :
    on utilise un petit réseau CNN pour extraire des informations utiles.

    Ce bloc transforme donc :
    image observée -> vecteur de caractéristiques -> décision de l'agent
    """

    def __init__(self, observation_space, features_dim: int = 128):
        super().__init__(observation_space, features_dim)

        # Nombre de canaux de l'image.
        # Après traitement par Stable-Baselines3, l'image est souvent au format :
        # channels x height x width
        n_input_channels = observation_space.shape[0]

        self.cnn = nn.Sequential(
            nn.Conv2d(n_input_channels, 16, kernel_size=2),
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=2),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=2),
            nn.ReLU(),
            nn.Flatten(),
        )

        # On calcule automatiquement la taille de sortie du CNN.
        # Cela évite de devoir faire le calcul à la main.
        with torch.no_grad():
            sample = torch.as_tensor(observation_space.sample()[None]).float()
            n_flatten = self.cnn(sample).shape[1]

        self.linear = nn.Sequential(
            nn.Linear(n_flatten, features_dim),
            nn.ReLU(),
        )

    def forward(self, observations):
        """
        Fonction appelée pendant l'entraînement.

        Elle transforme une observation image en vecteur utilisable par PPO.
        """
        return self.linear(self.cnn(observations))


def make_env():
    """
    Création de l'environnement d'entraînement.

    Les 4 éléments RL sont ici :

    1. États / observations :
       ImgObsWrapper garde seulement l'image observée par l'agent.

    2. Actions :
       L'environnement utilise les actions MiniGrid :
       tourner à gauche, tourner à droite, avancer.

    3. Transition :
       La transition est gérée par SimpleTunnelEnv + MiniGrid.
       Si l'agent avance vers un mur, il est bloqué.
       Si l'agent avance dans le tunnel, sa position change.

    4. Récompense :
       Définie dans SimpleTunnelEnv.step().
       Petite pénalité par étape.
       Récompense positive si l'agent atteint le but.
    """
    env = SimpleTunnelEnv(render_mode="rgb_array")

    # MiniGrid renvoie par défaut un dictionnaire.
    # ImgObsWrapper simplifie : l'agent ne voit que l'image.
    env = ImgObsWrapper(env)

    # Monitor enregistre des statistiques utiles :
    # longueur des épisodes, récompenses, etc.
    env = Monitor(env)

    return env


def main():
    env = make_env()

    policy_kwargs = dict(
        features_extractor_class=MinigridFeaturesExtractor,
        features_extractor_kwargs=dict(features_dim=128),
    )

    # PPO = algorithme classique d'apprentissage par renforcement.
    # CnnPolicy = politique adaptée aux observations sous forme d'image.
    model = PPO(
        policy="CnnPolicy",
        env=env,
        policy_kwargs=policy_kwargs,
        verbose=1,
        learning_rate=0.0003,
        n_steps=128,
        batch_size=64,
    )

    # Nombre de pas d'entraînement.
    # Tu peux commencer petit pour tester : 5_000 ou 10_000.
    # Puis augmenter si tout marche.
    model.learn(total_timesteps=20_000)

    model.save(str(MODEL_PATH))

    env.close()

    print(f"Modèle sauvegardé dans : {MODEL_PATH}.zip")


if __name__ == "__main__":
    main()
