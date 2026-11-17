# Génération de Tunnel

<div align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-%2300A8E8.svg?style=for-the-badge&logo=python&logoColor=white">
</div>

## Sommaire

- [Introduction](#introduction)
- [Méthodes de génération](#méthodes-de-génération)
  - [Automate cellulaire](#automate-cellulaire)
  - [Agent creusant](#agent-creusant)
- [Règles vérifiées](#règles-vérifiées)
- [Fichier `config.py`](#fichier-configpy)
- [Lancer la génération](#lancer-la-génération)
- [Animation](#animation)
- [Lancer les tests](#lancer-les-tests)
- [Structure du projet](#structure-du-projet)
- [Objectif dans le projet](#objectif-dans-le-projet)

---

## Introduction

Ce module permet de générer automatiquement des tunnels en 2D sur une grille.  
L'objectif est de produire des galeries exploitables pour la simulation, avec des tunnels connectés, fins, lisibles et sans blocs pleins de type 2x2.

La génération peut se faire avec deux méthodes différentes :

- un automate cellulaire ;
- un agent creusant qui avance dans la grille et ouvre progressivement le tunnel.

Le générateur peut ensuite afficher, animer, sauvegarder et vérifier automatiquement la grille obtenue.

---

## Méthodes de génération

### Automate cellulaire

La méthode par automate cellulaire part d'une grille initiale, puis applique plusieurs itérations de règles locales.  
À chaque itération, l'état d'une cellule dépend de ses voisines.

Cette méthode permet de générer des formes de tunnels à partir de paramètres globaux comme :

- le nombre d'itérations ;
- la taille de la grille ;
- la densité initiale de murs ;
- les règles de voisinage.

Elle est adaptée pour produire des structures variées et paramétrables.

---

### Agent creusant

La méthode par agent creusant simule un agent qui se déplace dans la grille et creuse le tunnel au fur et à mesure.

L'agent :

- démarre dans la grille ;
- avance cellule par cellule ;
- garde souvent la même direction pour favoriser les lignes droites ;
- change parfois de direction selon une probabilité définie ;
- évite de créer des carrés 2x2 ;
- maintient une structure connectée, car le tunnel est creusé progressivement.

Cette méthode donne des tunnels plus contrôlés, souvent plus linéaires, et limite les formes trop chaotiques.

---

## Règles vérifiées

Après la génération, le programme vérifie automatiquement plusieurs propriétés :

- **Connexion du tunnel** : toutes les cellules du tunnel doivent appartenir à une seule composante connectée.
- **Absence de carrés 2x2** : aucune zone pleine de 2x2 cellules ne doit être présente.
- **Validité globale** : le tunnel est considéré valide si les règles précédentes sont respectées.

Ces vérifications sont regroupées dans le module de vérification du tunnel.

---

## Fichier `config.py`

Le fichier `config.py` permet de modifier les paramètres principaux du générateur.

### Paramètres généraux

| Paramètre | Description |
|-----------|-------------|
| `GRID_WIDTH` | Largeur de la grille |
| `GRID_HEIGHT` | Hauteur de la grille |
| `GENERATION_METHOD` | Méthode utilisée par défaut (`"ca"` ou `"agent"`) |
| `SAVE` | Sauvegarde la grille générée dans un fichier `.csv` |
| `VIEW` | Affiche la grille finale |
| `ANIMATION` | Affiche l'animation de la génération |
| `SHOW_LONGEST_PATH` | Conserve ou affiche la plus grande composante connectée |

### Paramètres de l'automate cellulaire

| Paramètre | Description |
|-----------|-------------|
| `ITERATION` | Nombre d'itérations de l'automate |
| `WALL_PERCENTAGE` | Proportion initiale de murs |

### Paramètres de l'agent creusant

| Paramètre | Description |
|-----------|-------------|
| `AGENT_STEPS` | Nombre de pas de l'agent |
| `AGENT_TURN_PROBABILITY` | Probabilité de changement de direction |

---

## Lancer la génération

Depuis la racine du repository :

```bash
python -m generation.generator
```

La méthode dépend de `GENERATION_METHOD` dans `config.py`.

---

## Lancer les tests

Les tests vérifient automatiquement :

- les deux méthodes (`ca` et `agent`) ;
- la connexité du tunnel ;
- l'absence de carrés 2x2.

```bash
python -m pytest tests/test_generator.py
```

Résultat attendu :

```
tests/test_generator.py .. [100%]
```


---

## Structure du projet

```
generation/
│
├── algorithms/        # CA, agent creusant, longest path
├── models/            # grille et cellules
├── view/              # affichage + animation
├── data/              # export CSV
├── verificator/       # validation du tunnel
├── config.py          # paramètres
└── generator.py       # point d'entrée principal
```

---

## Objectif dans le projet

Ce générateur sert de base pour simuler des environnements souterrains dans le projet PIR.

Il permet :

- de générer des tunnels variés ;
- de tester des stratégies d'exploration (mono ou multi-agents) ;
- de créer des environnements réalistes sans données réelles.

Ce travail s'inscrit dans un contexte de simulation pour drones autonomes en milieux souterrains, où la génération procédurale permet de produire rapidement des environnements d'entraînement variés.