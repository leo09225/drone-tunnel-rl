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

La méthode par agent creusant simule un ou plusieurs agents qui se déplacent dans la grille et creusent le tunnel au fur et à mesure.

Chaque agent :

- démarre dans la grille ;
- avance cellule par cellule ;
- garde souvent la même direction pour favoriser les lignes droites ;
- change parfois de direction selon une probabilité définie ;
- peut créer des boucles avec une probabilité configurable ;
- peut créer des branches pour générer des tunnels secondaires ;
- évite de créer des carrés 2x2 ;
- maintient une structure connectée, car le tunnel est creusé progressivement.

Cette méthode dispose de deux modes :
- **Probabilistic** : les décisions du tunnel (virage, boucle, branche) sont basées sur des probabilités.
- **Constrained** : les mouvements sont plus contraints selon des règles déterministes.

Cette méthode donne des tunnels plus contrôlés, souvent plus linéaires, et limite les formes trop chaotiques.

---

## Règles vérifiées

Après la génération, le programme vérifie automatiquement plusieurs propriétés :

- **Connexion du tunnel** : toutes les cellules du tunnel doivent appartenir à une seule composante connectée.
- **Absence de carrés 2x2** : aucune zone pleine de 2x2 cellules ne doit être présente.
- **Validité globale** : le tunnel est considéré valide si les règles précédentes sont respectées.

Ces vérifications sont regroupées dans le module de vérification du tunnel.

---

## Post-traitement

Après la génération, le programme peut appliquer un post-traitement selon le mode configuré :

- **largest_component** : conserve uniquement la plus grande composante connectée et supprime les tunnels isolés.
- **connect_components** : connecte automatiquement toutes les composantes disconnectées en utilisant un agent creusant.
- **none** : aucun post-traitement, la grille générée est conservée tel quel.

Le post-traitement se configure via le paramètre `POST_PROCESSING_MODE` dans `config.py`.

---

## Automate cellulaire avec contraintes utilisateur

Il est possible de forcer l'automate cellulaire à préserver certains tunnels imposés manuellement.

Lorsque `CA_USE_FIXED_TUNNELS` est `True`, une interface interactive s'ouvre permettant de dessiner des tunnels avant de lancer la génération. L'automate cellulaire respectera ces tunnels imposés et les intégrera dans sa croissance.

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

### Paramètres de post-traitement

| Paramètre | Description |
|-----------|-------------|
| `POST_PROCESSING_MODE` | Mode de post-traitement : `"largest_component"` (garde la plus grande composante), `"connect_components"` (connecte toutes les composantes avec un agent) ou `"none"` (aucun) |
| `CA_USE_FIXED_TUNNELS` | `True` : ouvre une interface pour imposer des tunnels manuels avant la génération ; `False` : génération classique |

### Paramètres de l'automate cellulaire

| Paramètre | Description |
|-----------|-------------|
| `ITERATION` | Nombre d'itérations minimales de l'automate |
| `WALL_PERCENTAGE` | Proportion initiale de murs (0 à 1) |
| `TUNNEL_CONTINUITY_PROBA` | Probabilité de prolonger un tunnel droit |
| `BIRTH_CORNER_PROBA` | Probabilité de créer un virage |
| `DIGGER_PROBA` | Probabilité de générer une cellule tunnel isolée |
| `ENABLE_BIRTH_CONTINUITY` | Active la règle de continuité des tunnels |
| `ENABLE_BIRTH_CORNER` | Active la règle de création de virages |
| `ENABLE_DIGGER` | Active la règle de digger |
| `ENABLE_DRAUGHTBOARD` | Active la règle d'échiquier (damier) |
| `MIN_ALIVE_NEIGHBORS` | Seuil maximum de voisins vivants pour autoriser une naissance |

### Paramètres de l'agent creusant

| Paramètre | Description |
|-----------|-------------|
| `AGENT_MODE` | Mode de l'agent : `"probabilistic"` (décisions aléatoires) ou `"constrained"` (mouvements contraints) |
| `AGENT_STEPS` | Nombre d'étapes de l'agent creusant |
| `AGENT_TURN_PROBABILITY` | Probabilité de changement de direction |
| `AGENT_LOOP_PROBABILITY` | Probabilité de créer une boucle |
| `AGENT_BRANCH_PROBABILITY` | Probabilité de créer une branche |
| `TARGET_LOOPS` | Nombre de boucles souhaitées dans le tunnel |
| `AGENT_COUNT` | Nombre d'agents creusants à déployer |

---

## Lancer la génération

Depuis la racine du repository :

```bash
python -m generation.main
```

La méthode dépend de `GENERATION_METHOD` dans `config.py`.

---

## Animation

L'animation de la génération peut être activée en mettant `ANIMATION = True` dans `config.py`.

- **Automate cellulaire** : affiche chaque itération de l'automate cellulaire en temps réel avec les transitions d'état.
- **Agent creusant** : visualise le déplacement de l'agent (ou des agents) et la progression du creusage tunnel par tunnel.

Les animations sont affichées dans une fenêtre matplotlib et permettent de comprendre le processus de génération étape par étape.

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