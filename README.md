# 🚁 Exploration de tunnels par drones — Reinforcement Learning

> Comment un drone peut-il explorer seul un tunnel inconnu ? Ce projet de recherche compare des stratégies d'exploration classiques (algorithmes déterministes, systèmes multi-agents) à une approche par **apprentissage par renforcement**, pour laquelle j'ai conçu l'environnement d'apprentissage et le **système de récompense** du drone.

Projet d'Initiation à la Recherche (PIR, sujet 13 : *Proposition et évaluation de stratégies pour l'exploration de tunnels avec des drones*), 3ᵉ année Télécommunications, INSA Lyon, 2026. Projet d'équipe ; je pilotais la partie reinforcement learning.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Gymnasium](https://img.shields.io/badge/Gymnasium-RL%20env-0081A5)
![Stable-Baselines3](https://img.shields.io/badge/Stable--Baselines3-PPO-EE4C2C)
![MiniGrid](https://img.shields.io/badge/MiniGrid-2D%20grid-6f42c1)
![Mesa](https://img.shields.io/badge/Mesa-multi--agent-2E7D32)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)

---

## Le projet en bref

| | |
|---|---|
| **Contexte** | Tunnels, mines, réseaux souterrains : des lieux sans GPS, mal cartographiés et dangereux pour l'humain, où des drones autonomes doivent explorer seuls. |
| **Question de recherche** | Quelle stratégie permet à un drone (ou une flotte) de couvrir un tunnel inconnu le plus efficacement possible ? |
| **Démarche** | 1) Génération procédurale de tunnels, 2) exploration par systèmes multi-agents (Mesa), 3) apprentissage d'une stratégie par reinforcement learning, comparée aux approches classiques. |
| **Ma partie** | Modéliser l'exploration comme un problème de RL : observations, actions, transitions et **fonction de récompense**, puis la boucle complète création → vérification → entraînement PPO → évaluation. |

## Ma contribution : formuler l'exploration comme un problème de RL

J'ai développé un environnement **Gymnasium** sur mesure, `TunnelExploreEnv`, où un drone évolue dans un tunnel 2D représenté par une grille. L'objectif n'est pas d'atteindre une sortie, mais de **couvrir toutes les zones accessibles**, ce qui rend la conception de la récompense centrale.

### Les 4 éléments du problème

| Élément | Choix de conception |
|---|---|
| **Observation** | Dictionnaire combinant une carte globale à 4 canaux (murs, cases libres, cases déjà visitées, position du drone), une vue locale 3×3 autour du drone et le taux d'exploration courant |
| **Actions** | 4 déplacements discrets (haut, droite, bas, gauche) |
| **Transitions** | Le drone avance si la case est libre, reste bloqué face à un mur ; chaque nouvelle case est marquée comme explorée. L'épisode se termine quand toute la zone accessible est couverte, ou est tronqué après un nombre maximal de pas |
| **Récompense** | Voir ci-dessous |

### Le système de récompense

| Événement | Récompense | Comportement encouragé |
|---|---:|---|
| Chaque pas de temps | **−0,01** | Explorer vite, ne pas tourner en rond |
| Découverte d'une nouvelle case | **+1,0** | Aller vers l'inconnu plutôt que repasser au même endroit |
| Collision avec un mur ou le bord | **−0,2** | Apprendre la géométrie du tunnel, éviter les chocs |
| Exploration complète de la zone | **+10,0** | Aller jusqu'au bout de la mission |

L'équilibre entre ces termes est le cœur du travail : une pénalité par pas trop forte pousse le drone à s'arrêter tôt, une récompense de découverte trop faible ne suffit pas à le faire sortir des zones déjà connues.

### La chaîne d'expérimentation

```
 MiniGrid EmptyEnv      →   SimpleTunnelEnv      →   check_env (SB3)   →   PPO.learn()   →   évaluation
 (prise en main de          (grille + but +          (compatibilité         (premier           (visualiser le
  l'API Gymnasium)           agent, obs. image)       vérifiée)              modèle)            comportement)
```

- Prise en main de l'API Gymnasium (`reset()`, `step()`, observations) sur MiniGrid
- Environnements custom validés automatiquement (`check_env` de Stable-Baselines3 + tests avec politique aléatoire)
- Entraînement **PPO** (Stable-Baselines3, politiques `CnnPolicy` et `MultiInputPolicy`), sauvegarde et évaluation séparée des modèles
- Scripts d'inspection et de rapport qui affichent les observations, les récompenses et le taux d'exploration pas à pas

### Une baseline déterministe : l'algorithme de Pledge

Pour disposer d'un point de comparaison explicable, j'ai aussi intégré à la simulation multi-agent (Mesa) un agent `PledgeDrone` : il garde une direction globale préférée et contourne les obstacles en suivant les murs, avec un compteur de virages qui l'empêche de tourner indéfiniment autour d'un îlot. Il est testé sur trois labyrinthes conçus pour piéger les stratégies naïves (mur isolé, îlot central, obstacles disjoints) et comparé visuellement aux stratégies aléatoire et « tout droit » dans une interface Solara.

## Architecture du projet d'équipe

```
generation/              Génération procédurale de tunnels (algorithmes, règles, vérification)
multi_agent/             Simulation multi-agent Mesa, agents (dont PledgeDrone), benchmark, interface Solara
reinforcement_learning/  Environnements Gymnasium, entraînement et évaluation PPO  ← ma partie
tests/                   Tests unitaires (générateur, modèle), exécutés en intégration continue
```

Le travail expérimental a été mené sur une branche Git dédiée, testé sans casser la branche principale, puis intégré une fois validé.

## Lancer le projet

```bash
pip install -r requirements.txt
pip install -r reinforcement_learning/requirements-rl.txt

# Environnement RL
python reinforcement_learning/check_tunnel_env.py       # vérifie l'environnement
python reinforcement_learning/random_policy_demo.py     # démo pas à pas
python reinforcement_learning/train_ppo_tunnel.py       # entraînement PPO
python reinforcement_learning/evaluate_simple_tunnel_ppo.py

# Baseline Pledge
python multi_agent/create_pledge_envs.py
python multi_agent/run_pledge_cli.py --env maze_pledge_02_island.csv
solara run multi_agent/app.py                           # visualisation
```

## Compétences mobilisées

Reinforcement learning (formulation MDP, reward shaping, PPO) · Gymnasium · Stable-Baselines3 · simulation multi-agent (Mesa) · algorithmique d'exploration · démarche de recherche (état de l'art, expérimentation, comparaison) · Python · Git et intégration continue

## Références

- M. Towers *et al.*, *Gymnasium: A Standard Interface for Reinforcement Learning Environments*, arXiv:2407.17032, 2024.
- Stable-Baselines3, MiniGrid, Mesa (documentation officielle).

## Auteur

**Léo Le Calvé** — élève ingénieur en Télécommunications à l'INSA Lyon · [GitHub](https://github.com/leo09225) · [LinkedIn](https://www.linkedin.com/in/l%C3%A9o-le-calv%C3%A9-b93a1b387/)

Projet réalisé en équipe dans le cadre du PIR (dépôt principal de l'équipe : `leopoldcst/projet_PTIR_13`).
