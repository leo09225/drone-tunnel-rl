# ============================
# Configuration de la generation de tunnels
# ============================

# ============================
# Parametres generaux
# ============================

GENERATION_METHOD = "agent"  # "ca" ou "agent"

GRID_WIDTH = 50  # Largeur de la grille
GRID_HEIGHT = 50  # Hauteur de la grille

SAVE = False  # Sauvegarde la matrice dans un CSV
VIEW = False  # Affiche la grille finale
ANIMATION = True  # Affiche l'evolution etape par etape


# ============================
# Post-traitement
# ============================

POST_PROCESSING_MODE = "connect_components"
# "largest_component"  -> garde uniquement la plus grande composante
# "connect_components" -> connecte toutes les composantes avec un agent
# "none"               -> aucun post-traitement


# ============================
# Mode CA avec contraintes utilisateur
# ============================

CA_USE_FIXED_TUNNELS = True
# True  -> ouvre l'interface pour imposer des tunnels
# False -> CA classique


# ============================
# Parametres de l'automate cellulaire
# ============================

WALL_PERCENTAGE = 0.7  # Proportion initiale de murs
ITERATION = 50  # Nombre d'iterations minimales

TUNNEL_CONTINUITY_PROBA = 0.8  # Proba de prolonger un tunnel droit
BIRTH_CORNER_PROBA = 0.03  # Proba de creer un virage
DIGGER_PROBA = 0.03

# MTM    MTM
# MMM -> MTM
# MTM    MTM
ENABLE_BIRTH_CONTINUITY = True  # Active la regle de continuite

# MTM    MTM
# TMM -> TTM
# MMM    MMM
ENABLE_BIRTH_CORNER = True  # Active la regle de creation de virages

# MTM    MTM
# MMM -> MTM
# MMM    MMM
ENABLE_DIGGER = False

# T*T    T*T
# *** -> *T*
# T*T    T*T
ENABLE_DRAUGHTBOARD = False

MIN_ALIVE_NEIGHBORS = 5  # Seuil max de voisins vivants pour autoriser une naissance


# ============================
# Parametres de l'agent creusant
# ============================

AGENT_MODE = "probabilistic"  # "probabilistic" ou "constrained"

AGENT_STEPS = 200  # Nombre d'etapes de l'agent
AGENT_TURN_PROBABILITY = 0.2  # Probabilite de rotation
AGENT_LOOP_PROBABILITY = 0.03  # Probabilite de creer une boucle
AGENT_BRANCH_PROBABILITY = 0.08  # Probabilite de creer une branche

TARGET_LOOPS = 5  # Nombre de boucles souhaitees

AGENT_COUNT = 4
