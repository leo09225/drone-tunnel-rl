"""
Premier test MiniGrid : lancement de EmptyEnv.

Objectif :
- vérifier que l'installation fonctionne ;
- lancer un environnement MiniGrid de base ;
- faire bouger l'agent avec des actions aléatoires.

Cet environnement n'entraîne rien pour l'instant.
Il sert uniquement à manipuler l'API Gymnasium/MiniGrid.
"""

import gymnasium as gym
import minigrid  # important : permet d'enregistrer les environnements MiniGrid


def main():
    # Création de l'environnement EmptyEnv.
    # render_mode="human" affiche une fenêtre graphique.
    #
    # MiniGrid-Empty-5x5-v0 :
    # - petite grille 5x5
    # - objectif : atteindre la case verte
    env = gym.make("MiniGrid-Empty-5x5-v0", render_mode="human")

    # reset() initialise un nouvel épisode.
    # observation contient l'état observé par l'agent.
    # info contient des informations complémentaires.
    observation, info = env.reset(seed=42)

    # On fait 100 actions aléatoires maximum.
    for step in range(100):
        # action_space.sample() choisit une action au hasard.
        # Ici, ce n'est PAS encore de l'apprentissage.
        action = env.action_space.sample()

        # step(action) applique l'action dans l'environnement.
        # Gymnasium renvoie :
        # - observation : nouvelle observation après l'action
        # - reward : récompense obtenue
        # - terminated : True si l'objectif est atteint
        # - truncated : True si l'épisode s'arrête à cause d'une limite de temps
        # - info : infos complémentaires
        observation, reward, terminated, truncated, info = env.step(action)

        print(
            f"Step={step}, action={action}, reward={reward}, "
            f"terminated={terminated}, truncated={truncated}"
        )

        # Si l'épisode est terminé, on le réinitialise.
        if terminated or truncated:
            observation, info = env.reset()

    env.close()


if __name__ == "__main__":
    main()
