# Exploration multi/mono agents

## Installation

Pour installer les dependances necessaires :

```bash
pip install "mesa[viz]" numpy python-statemachine networkx pydot
```

## Execution

Pour lancer Solara depuis la racine du projet :

```bash
SOLARA_HOME=.solara_local python -m solara run multi_agent/app.py
```

Ou en utilisant directement le Python du venv :

```powershell
$env:SOLARA_HOME = "$PWD\\.solara_local"
.\.venv\Scripts\python.exe -m solara run multi_agent/app.py
```

Ou en se placant dans le dossier `multi_agent` :

```bash
cd multi_agent
python -m solara run app.py
```

Sous Windows / PowerShell, si l'activation de `.venv` est bloquee par la
policy d'execution, ou si le dossier `C:\Users\...\ .solara` reste verrouille,
le plus simple est d'utiliser le lanceur fourni :

```powershell
.\multi_agent\start_solara.cmd
```

## Structure

- `app.py` : definit la visualisation avec Solara ;
- `model.py` : definit le modele de simulation ;
- `agents.py` : definit les agents ;
- `envs/` : contient les fichiers CSV decrivant les tunnels.
