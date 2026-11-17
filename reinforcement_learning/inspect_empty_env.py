"""
Inspection de EmptyEnv.

Objectif :
comprendre les 4 éléments importants avant l'entraînement :
1. États / observations
2. Actions
3. Transition
4. Récompense

On ne cherche pas encore à entraîner un agent.
On observe simplement ce que MiniGrid renvoie.
"""

import gymnasium as gym
import minigrid  # nécessaire pour enregistrer les environnements MiniGrid


def main():
    env = gym.make("MiniGrid-Empty-5x5-v0")

    observation, info = env.reset(seed=42)

    print("===== ESPACE D'OBSERVATION =====")
    print(env.observation_space)
    print()

    print("===== OBSERVATION INITIALE =====")
    print("Type de l'observation :", type(observation))
    print("Clés disponibles :", observation.keys())
    print("Direction de l'agent :", observation["direction"])
    print("Mission :", observation["mission"])
    print("Taille de l'image observée :", observation["image"].shape)
    print()

    print("===== ESPACE D'ACTIONS =====")
    print(env.action_space)
    print()

    print("Actions MiniGrid principales :")
    print("0 : tourner à gauche")
    print("1 : tourner à droite")
    print("2 : avancer")
    print("3 : ramasser un objet")
    print("4 : déposer un objet")
    print("5 : interagir avec un objet")
    print("6 : terminer")
    print()

    # On teste quelques actions manuellement.
    actions_to_test = [2, 1, 2, 2]

    print("===== TEST DE TRANSITIONS =====")

    for action in actions_to_test:
        old_direction = observation["direction"]

        observation, reward, terminated, truncated, info = env.step(action)

        print(f"Action jouée : {action}")
        print(f"Ancienne direction : {old_direction}")
        print(f"Nouvelle direction : {observation['direction']}")
        print(f"Récompense : {reward}")
        print(f"Terminé ? {terminated}")
        print(f"Timeout ? {truncated}")
        print("---")

        if terminated or truncated:
            break

    env.close()


if __name__ == "__main__":
    main()
