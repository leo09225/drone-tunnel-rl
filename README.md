# 🚁 Exploration de tunnels par une flotte de drones

> Projet de recherche : générer des réseaux de grottes réalistes, puis comparer des stratégies d'exploration autonome pour des drones, des algorithmes déterministes aux systèmes multi-agents, jusqu'à l'**apprentissage par renforcement**.

Projet d'Initiation à la Recherche (PIR, sujet 13 : *Proposition et évaluation de stratégies pour l'exploration de tunnels avec des drones*), 3ᵉ année Télécommunications, INSA Lyon, 2026. Projet d'équipe, dans lequel j'étais **responsable de la partie apprentissage par renforcement**.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Mesa](https://img.shields.io/badge/Mesa-multi--agent-2E7D32)
![Gymnasium](https://img.shields.io/badge/Gymnasium-RL-0081A5)
![MiniGrid](https://img.shields.io/badge/MiniGrid-2D%20grid-6f42c1)
![Stable-Baselines3](https://img.shields.io/badge/Stable--Baselines3-PPO-EE4C2C)
![PyTorch](https://img.shields.io/badge/PyTorch-CNN-EE4C2C?logo=pytorch&logoColor=white)
![CI](https://img.shields.io/badge/CI-Ruff%20%2B%20pytest-2088FF?logo=githubactions&logoColor=white)

---

## Le projet en bref

| | |
|---|---|
| **Contexte** | Mines, grottes, réseaux souterrains : des milieux sans GPS, inconnus et dangereux, où des drones doivent explorer de façon autonome. |
| **Question** | Quelle stratégie permet à un ou plusieurs drones de couvrir le plus vite possible un tunnel qu'ils ne connaissent pas ? |
| **Démarche** | ① Générer automatiquement des tunnels variés → ② les explorer avec des stratégies multi-agents → ③ apprendre une stratégie par renforcement → comparer le tout par des benchmarks. |
| **Stack** | Python, Mesa et Solara (simulation et visualisation), Gymnasium, MiniGrid, Stable-Baselines3 et PyTorch (RL), NumPy, NetworkX, Matplotlib, pytest, Ruff, GitHub Actions. |

```
 ┌───────────────────────┐     CSV      ┌──────────────────────────┐            ┌────────────────────────┐
 │ 1. Génération          │ ───────────▶ │ 2. Exploration           │ ─────────▶ │ 3. Benchmarks          │
 │  automate cellulaire   │  grilles 2D  │  multi-agent (Mesa)      │  mesures   │  couverture, temps,    │
 │  agents creuseurs      │              │  Trémaux, Pledge, …      │            │  nombre de pas         │
 └───────────────────────┘              ├──────────────────────────┤            └────────────────────────┘
                                         │ 3. Apprentissage par     │
                                         │  renforcement (PPO)      │  ← ma partie
                                         └──────────────────────────┘
```

## 1. Génération procédurale de grottes

Le module `generation/` produit des tunnels 2D (grilles 50 × 50 par défaut) connectés, fins et lisibles. Deux méthodes ont été développées :

- **Automate cellulaire**, dans l'esprit du *jeu de la vie* de Conway : on part d'une grille aléatoire (70 % de murs), puis à chaque itération l'état d'une cellule évolue selon ses 8 voisines, avec des règles de **naissance** (prolonger un tunnel droit, créer un virage avec une faible probabilité) et de **mort** (contrôle de la largeur des galeries). L'itération s'arrête à **convergence**, quand la grille ne change plus. L'utilisateur peut aussi dessiner des tunnels imposés dans une interface : l'automate les intègre dans sa croissance.
- **Agents creuseurs** : un ou plusieurs agents avancent dans la roche et creusent en gardant leur direction, tournent, créent des **boucles** et des **branches** selon des probabilités réglables (mode probabiliste) ou des règles déterministes (mode contraint).

Chaque grille est ensuite **vérifiée automatiquement** (une seule composante connexe, aucun bloc ouvert de 2 × 2) et post-traitée : on garde la plus grande composante, ou un agent creuseur **relie les composantes isolées**. Les grilles peuvent être animées pas à pas, affichées et exportées en CSV pour la simulation.

## 2. Exploration multi-agent

Le module `multi_agent/` simule une flotte de drones avec **Mesa** (modèle `Vortex`), visualisée en direct avec **Solara**. La carte des cases déjà explorées est commune à toute la flotte. Plusieurs stratégies ont été proposées et implémentées :

| Stratégie | Principe |
|---|---|
| **Aléatoire** | Choix uniforme parmi les cases libres (référence basse) |
| **Tout droit** | Avance tant que possible, choix aléatoire aux bifurcations |
| **Non exploré d'abord** | Priorité aux cases jamais visitées, puis tout droit, puis aléatoire, avec retour arrière si bloqué |
| **Choix équilibré** | Aux intersections, prend la direction la moins utilisée sur ses 20 derniers choix |
| **Trémaux** | Algorithme classique de résolution de labyrinthe : marque les passages empruntés pour ne jamais les parcourir plus de deux fois |
| **Pledge** | Garde une direction globale et contourne les obstacles en suivant le mur, avec un compteur de virages qui évite de tourner autour d'un îlot (dossier `multi_agent_pledge/`, testé sur trois labyrinthes pièges) |

Le dossier `benchmark/` compare ces stratégies sur des lots de grottes générées par les deux méthodes : **taux de couverture**, nombre de pas et temps de calcul, ainsi que l'évolution de la proportion de tunnel au fil des itérations de génération.

## 3. Apprentissage par renforcement (ma partie)

En tant que responsable du RL, j'ai formulé l'exploration comme un **processus de décision markovien** et construit toute la chaîne d'apprentissage, de l'environnement à l'évaluation de l'agent.

**Environnement `TunnelExploreEnv` (Gymnasium)** : un drone dans un tunnel en grille, dont la mission n'est pas d'atteindre une sortie mais de **couvrir toute la zone accessible**.

| Élément | Choix de conception |
|---|---|
| **Observation** | Carte globale à 4 canaux (murs, cases libres, cases visitées, position du drone), vue locale 3 × 3, taux d'exploration courant |
| **Actions** | 4 déplacements discrets |
| **Transitions** | Déplacement si la case est libre, blocage contre un mur ; fin d'épisode quand toute la zone accessible (calculée par parcours en largeur) est couverte, troncature après un nombre maximal de pas |
| **Récompense** | **−0,01** par pas (aller vite) · **+1** par nouvelle case découverte (aller vers l'inconnu) · **−0,2** par collision (apprendre la géométrie) · **+10** à l'exploration complète (finir la mission) |

**Chaîne d'expérimentation**

1. Prise en main de l'API Gymnasium sur **MiniGrid** (`reset`, `step`, observations, wrappers d'image).
2. Environnements de difficulté croissante : couloir simple, tunnel à branches, tunnel en labyrinthe.
3. Validation automatique avec `check_env` de Stable-Baselines3 et des politiques aléatoires de contrôle.
4. Entraînement **PPO** avec Stable-Baselines3 : `CnnPolicy` sur l'observation image et `MultiInputPolicy` sur l'observation composée, avec un **extracteur de caractéristiques CNN sur mesure** en PyTorch, adapté aux petites grilles.
5. Évaluation séparée des modèles sauvegardés et scripts d'inspection qui affichent, pas à pas, l'action, la récompense et le pourcentage exploré.

Le travail RL a été mené sur une branche Git dédiée, isolée du reste du projet, pour expérimenter sans casser la simulation principale. La stratégie Pledge sert de point de comparaison explicable face à l'agent appris.

## Qualité logicielle

- Intégration continue **GitHub Actions** : lint et formatage avec **Ruff**, tests unitaires **pytest** du générateur et du modèle multi-agent à chaque push
- Code modulaire : génération, exploration, RL et benchmarks sont indépendants et communiquent par des fichiers CSV
- Paramètres centralisés (`generation/config.py`) et reproductibilité par graine aléatoire

## Lancer le projet

```bash
pip install -r requirements.txt

# Générer et animer une grotte
python -m generation.main

# Simulation multi-agent avec visualisation
solara run multi_agent/app.py

# Apprentissage par renforcement
pip install -r reinforcement_learning/requirements-rl.txt
python reinforcement_learning/check_tunnel_env.py
python reinforcement_learning/train_ppo_tunnel.py
python reinforcement_learning/evaluate_simple_tunnel_ppo.py

# Baseline Pledge
python multi_agent_pledge/create_pledge_envs.py
python multi_agent_pledge/run_pledge_cli.py --env maze_pledge_02_island.csv

# Tests
pytest tests/
```

## Organisation du dépôt

```
generation/            Génération de grottes : automate cellulaire, agents creuseurs, vérification, animation
multi_agent/           Simulation Mesa et stratégies d'exploration (algo/), visualisation Solara
multi_agent_pledge/    Variante de la simulation avec l'agent Pledge et ses labyrinthes de test
reinforcement_learning/ Environnements Gymnasium, entraînement et évaluation PPO
benchmark/             Comparaison des stratégies et des méthodes de génération
tests/                 Tests unitaires (pytest)
```

## Compétences mobilisées

Apprentissage par renforcement (MDP, reward shaping, PPO) · Gymnasium, MiniGrid, Stable-Baselines3, PyTorch · systèmes multi-agents (Mesa) · algorithmique d'exploration et de labyrinthes (Trémaux, Pledge) · génération procédurale (automates cellulaires) · démarche de recherche et benchmarking · Python, Git, CI

## Références

- M. Towers *et al.*, *Gymnasium: A Standard Interface for Reinforcement Learning Environments*, arXiv:2407.17032, 2024.
- J. Schulman *et al.*, *Proximal Policy Optimization Algorithms*, arXiv:1707.06347, 2017.
- Documentation de Mesa, MiniGrid et Stable-Baselines3.

## Auteur

**Léo Le Calvé**, responsable de l'apprentissage par renforcement · élève ingénieur en Télécommunications à l'INSA Lyon · [GitHub](https://github.com/leo09225) · [LinkedIn](https://www.linkedin.com/in/l%C3%A9o-le-calv%C3%A9-b93a1b387/)

Projet réalisé en équipe dans le cadre du PIR 13 de l'INSA Lyon.
