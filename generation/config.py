# ============================
# Configuration de la génération de tunnels
# ============================

GRID_WIDTH = 20  ## Largeur de la grille
GRID_HEIGHT = 20  ## Hauteur de la grille

WALL_PERCENTAGE = 0.75  ## Proportion de murs (0 = tout tunnel, 1 = tout mur)

GENERATION_METHOD = "agent"  # Méthode de génération : "ca" ou "agent"

# ============================
# Paramètres de l'automate cellulaire
# ============================

ITERATION = 15  ## Nombre d'itérations de l'automate

# ============================
# Visualisation et sauvegarde
# ============================

SAVE = False  ## Sauvegarde la matrice dans un CSV
VIEW = False  ## Affiche la grille avec matplotlib
ANIMATION = True  ## Affiche l'évolution étape par étape

SHOW_LONGEST_PATH = True  ## Garde le plus grand tunnel connecté

# ============================
# Paramètres de la méthode d'agents
# ============================

AGENT_STEPS = 140  ## Nombre d'étapes de l'agent
AGENT_TURN_PROBABILITY = 0.3  ## Probabilité de rotation de l'agent
