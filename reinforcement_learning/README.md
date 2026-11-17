# Reinforcement Learning - Tunnel Exploration

Ce dossier contient une partie RL isolee du reste du projet PIR.

L'objectif ici n'est pas de remplacer la partie `multi_agent/`, mais de
prototyper proprement un environnement de reinforcement learning pour un drone
qui explore un tunnel 2D represente par une grille.

Le code est volontairement simple, tres commente, et lanceable depuis la
racine du projet.

## Installation

Depuis la racine du projet :

```bash
pip install -r reinforcement_learning/requirements-rl.txt
```

Sous Windows avec Python 3.14, le script suivant reste une option robuste
si l'installation de MiniGrid / pygame pose probleme :

```powershell
powershell -ExecutionPolicy Bypass -File reinforcement_learning/setup_rl_windows.ps1
```

## Test de MiniGrid

Ce test sert uniquement a verifier que MiniGrid fonctionne correctement avant
de passer a l'environnement custom.

```bash
python reinforcement_learning/test_minigrid_empty.py
```

## Environnement custom

Le fichier principal est :

```bash
reinforcement_learning/tunnel_explore_env.py
```

Il definit une classe :

```python
TunnelExploreEnv(gymnasium.Env)
```

Le drone evolue dans une grille 2D avec la convention :

- `0` = case libre
- `1` = mur

Le but n'est pas d'atteindre une sortie unique, mais d'explorer toutes les
cases libres accessibles depuis la position de depart.

## Verification de l'environnement custom

Pour verifier que l'environnement ne plante pas :

```bash
python reinforcement_learning/check_tunnel_env.py
```

Ce script :

- utilise `stable_baselines3.common.env_checker.check_env` si SB3 est installe ;
- sinon, ou en plus, lance un test manuel avec 100 actions aleatoires ;
- affiche les rewards et le pourcentage explore.

## Demo avec politique aleatoire

Pour lancer une politique aleatoire pas a pas :

```bash
python reinforcement_learning/random_policy_demo.py
```

Le script affiche :

- l'action choisie ;
- la position du drone ;
- la recompense ;
- le pourcentage explore ;
- `terminated` / `truncated` ;
- un rendu texte simple de la grille.

## Entrainement PPO minimal

Le fichier suivant est optionnel et sert seulement de premier test :

```bash
python reinforcement_learning/train_ppo_tunnel.py
```

Il utilise :

- `stable-baselines3`
- `PPO`
- `MultiInputPolicy`

Le modele est sauvegarde dans :

```bash
reinforcement_learning/models/
```

## Les 4 elements RL de l'environnement

### Etats / observations

L'observation est un `gymnasium.spaces.Dict` avec :

- `global_map` : `Box` de shape `(4, height, width)`
  - canal 0 : murs
  - canal 1 : cases libres
  - canal 2 : cases deja visitees
  - canal 3 : position du drone
- `local_view` : `Box` de shape `(3, 3, 3)`
  - vue locale 3x3 autour du drone
  - indique murs / libres / visitees
- `explored_ratio` : `Box` de shape `(1,)`
  - valeur entre `0` et `1`
  - pourcentage de cases libres accessibles deja explorees

### Actions

L'espace d'action est :

```python
spaces.Discrete(4)
```

avec la convention :

- `0` = haut
- `1` = droite
- `2` = bas
- `3` = gauche

### Transition

Dans `step(action)` :

- on calcule la case cible a partir de l'action ;
- si la case cible est libre, le drone se deplace ;
- si la case cible est un mur ou sort de la carte, le drone reste en place ;
- si le drone arrive sur une case libre jamais visitee, elle est marquee comme exploree ;
- l'episode se termine quand toutes les cases libres accessibles sont explorees ;
- l'episode est tronque si `max_steps` est atteint.

### Recompense

La logique de recompense est volontairement simple :

- `-0.01` a chaque step ;
- `+1.0` si une nouvelle case est exploree ;
- `-0.2` si le drone percute un mur ou le bord de la carte ;
- `+10.0` si toute la zone libre accessible est exploree.

## Fichiers principaux

- `requirements-rl.txt` : dependances RL isolees du projet principal
- `test_minigrid_empty.py` : test d'installation MiniGrid
- `tunnel_explore_env.py` : environnement Gymnasium custom
- `check_tunnel_env.py` : verification de l'environnement
- `random_policy_demo.py` : demo avec politique aleatoire
- `train_ppo_tunnel.py` : premier test PPO optionnel

## Remarques Git

Les artefacts generes par les experiences RL ne doivent pas etre commit :

- `reinforcement_learning/models/`
- `reinforcement_learning/logs/`
- `reinforcement_learning/runs/`
- `reinforcement_learning/videos/`
