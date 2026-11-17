# Exploration multi/mono agents

## Installation

Pour installer les dépendances nécessaires :

```bash
pip install "mesa[viz]" numpy python-statemachine networkx pydot
```

## Exécution

Pour lancer solara :

```bash
solara run multi_agent/app.py
```

## Structure

- `app.py` : Définit la visualisation avec Solara ;
- `model.py` : Définit le modèle de simulation ;
- `agents.py` : Définit le socle commun des agents ;
- `algo/` : Contient les stratégies d'exploration (`random.py`, `straight.py`, `tremaux.py`) ;
- `envs/` : Contient les fichiers CSV décrivant les tunnels.
