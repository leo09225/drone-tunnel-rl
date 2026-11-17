"""
Automatic report generator for the 4 RL elements.

Goal:
produce a short, copyable summary for:
1. MiniGrid-Empty-5x5-v0
2. SimpleTunnelEnv

The report is meant to help with a student write-up. It mixes:
- information observed directly from the environments,
- a small amount of explanation taken from our own custom code.

Usage:
    python reinforcement_learning/report_rl_elements.py

Optional:
    python reinforcement_learning/report_rl_elements.py --output report.md
"""

from __future__ import annotations

import argparse
from pathlib import Path

import gymnasium as gym
import minigrid  # needed so MiniGrid environments are registered
from minigrid.wrappers import ImgObsWrapper

try:
    from .simple_tunnel_env import (
        ACTION_FORWARD,
        ACTION_LEFT,
        ACTION_RIGHT,
        SimpleTunnelEnv,
    )
except ImportError:
    from simple_tunnel_env import (
        ACTION_FORWARD,
        ACTION_LEFT,
        ACTION_RIGHT,
        SimpleTunnelEnv,
    )


def summarize_empty_env() -> dict[str, object]:
    """
    Inspect the default MiniGrid Empty environment.

    We intentionally read the environment directly instead of hardcoding
    everything so the report stays aligned with what the code actually runs.
    """
    env = gym.make("MiniGrid-Empty-5x5-v0")
    observation, info = env.reset(seed=42)

    summary = {
        "observation_space": str(env.observation_space),
        "action_space": str(env.action_space),
        "observation_keys": list(observation.keys()),
        "direction": observation["direction"],
        "mission": observation["mission"],
        "image_shape": tuple(observation["image"].shape),
    }

    env.close()
    return summary


def summarize_simple_tunnel_env() -> dict[str, object]:
    """
    Inspect the custom tunnel environment in both raw and wrapped forms.
    """
    raw_env = SimpleTunnelEnv()
    raw_observation, info = raw_env.reset(seed=42)

    wrapped_env = ImgObsWrapper(SimpleTunnelEnv())
    wrapped_observation, info = wrapped_env.reset(seed=42)

    # We run one simple forward action to show the per-step penalty in practice.
    next_observation, reward, terminated, truncated, info = raw_env.step(ACTION_FORWARD)

    summary = {
        "raw_observation_space": str(raw_env.observation_space),
        "wrapped_observation_space": str(wrapped_env.observation_space),
        "action_space": str(raw_env.action_space),
        "raw_observation_keys": list(raw_observation.keys()),
        "raw_image_shape": tuple(raw_observation["image"].shape),
        "wrapped_image_shape": tuple(wrapped_observation.shape),
        "mission": raw_observation["mission"],
        "action_mapping": {
            ACTION_LEFT: "turn left",
            ACTION_RIGHT: "turn right",
            ACTION_FORWARD: "move forward",
        },
        "sample_forward_reward": reward,
        "sample_forward_terminated": terminated,
        "sample_forward_truncated": truncated,
    }

    raw_env.close()
    wrapped_env.close()
    return summary


def build_report(empty_summary: dict[str, object], tunnel_summary: dict[str, object]) -> str:
    """
    Build a markdown report ready to paste into a write-up.
    """
    action_mapping = tunnel_summary["action_mapping"]
    tunnel_actions = ", ".join(
        f"{action_id} = {label}" for action_id, label in action_mapping.items()
    )

    return f"""# Resume des 4 elements RL

## 1. MiniGrid EmptyEnv

### Etats / observations
`MiniGrid-Empty-5x5-v0` renvoie une observation sous forme de dictionnaire avec les cles
`{empty_summary["observation_keys"]}`.
Cette observation contient :
- `image` : la vue locale de l'agent
- `direction` : l'orientation de l'agent
- `mission` : la consigne textuelle de l'episode

Pour le reset inspecte, l'image a pour taille `{empty_summary["image_shape"]}` et
la mission initiale est :
`{empty_summary["mission"]}`

Espace d'observation :
`{empty_summary["observation_space"]}`

### Actions
L'espace d'action est :
`{empty_summary["action_space"]}`

En pratique, les actions les plus importantes dans EmptyEnv sont :
- `0`: turn left
- `1`: turn right
- `2`: move forward

Les autres actions existent dans l'API MiniGrid, mais elles ne sont pas
centrales dans cette tache de salle vide.

### Transition
La transition est geree par `env.step(action)`.
A chaque etape :
- tourner change l'orientation,
- avancer change la position seulement si la case suivante est libre,
- atteindre le goal termine l'episode avec `terminated=True`,
- depasser la limite de temps termine l'episode avec `truncated=True`.

### Recompense
La recompense est sparse :
- l'agent recoit une recompense positive lorsqu'il atteint le goal,
- pendant les pas ordinaires, il n'y a pas de signal dense intermediaire,
- la recompense de succes par defaut de MiniGrid favorise les trajectoires courtes.

## 2. SimpleTunnelEnv

### Etats / observations
`SimpleTunnelEnv` conserve le format d'observation MiniGrid par defaut, donc
l'observation brute reste un dictionnaire avec :
`{tunnel_summary["raw_observation_keys"]}`

La taille de l'image brute est :
`{tunnel_summary["raw_image_shape"]}`

La mission est :
`{tunnel_summary["mission"]}`

Espace d'observation brut :
`{tunnel_summary["raw_observation_space"]}`

Si on applique `ImgObsWrapper`, on ne garde que l'image. Dans ce cas,
l'observation transformee devient :
`{tunnel_summary["wrapped_image_shape"]}`

Espace d'observation avec wrapper :
`{tunnel_summary["wrapped_observation_space"]}`

### Actions
L'environnement custom reduit volontairement l'espace d'action a :
`{tunnel_summary["action_space"]}`

Correspondance des actions dans le code :
- {tunnel_actions}

Cet environnement ne garde donc que les 3 actions utiles :
- tourner a gauche
- tourner a droite
- avancer

Il n'y a pas d'action `backward` explicite dans l'implementation actuelle.

### Transition
La transition est toujours geree par MiniGrid, mais dans une carte custom :
- l'interieur de la grille est d'abord rempli de murs,
- seules les cases du tunnel sont ouvertes,
- l'agent commence au debut du tunnel,
- le goal est place a la fin du tunnel.

Cela signifie :
- avancer dans une case libre change la position,
- avancer contre un mur laisse l'agent bloque,
- atteindre le goal termine l'episode.

### Recompense
`SimpleTunnelEnv` reutilise la transition et la recompense de succes de MiniGrid,
puis ajoute une petite penalite negative a chaque pas.

Dans l'execution inspectee, un pas en avant produit :
- reward = `{tunnel_summary["sample_forward_reward"]}`
- terminated = `{tunnel_summary["sample_forward_terminated"]}`
- truncated = `{tunnel_summary["sample_forward_truncated"]}`

Le schema de recompense est donc :
- recompense positive si le goal est atteint,
- petite penalite par etape (`-0.01`) pour encourager les chemins courts.

## 3. Construction de l'environnement custom

L'environnement custom suit le schema habituel de MiniGrid :
1. heriter de `MiniGridEnv`
2. definir un `MissionSpace`
3. implementer `_gen_grid(...)`
4. placer les murs, l'agent et le goal
5. redefinir eventuellement `step(...)` pour ajuster la recompense

Dans notre code, `_gen_grid(...)` cree les murs exterieurs, remplit l'interieur
avec des murs, creuse un tunnel unique, place le goal sur la derniere case du
chemin, puis place l'agent au debut du tunnel.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a markdown summary of the 4 RL elements."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional markdown file to write the report to.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    empty_summary = summarize_empty_env()
    tunnel_summary = summarize_simple_tunnel_env()
    report = build_report(empty_summary, tunnel_summary)

    if args.output is not None:
        args.output.write_text(report, encoding="utf-8")
        print(f"Report written to: {args.output}")
        return

    print(report)


if __name__ == "__main__":
    main()
