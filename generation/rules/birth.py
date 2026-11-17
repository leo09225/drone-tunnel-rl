import random


def is_alive(grid, x, y):
    """
    Retourne True si la cellule (x, y) existe et est active.
    Les coordonnées hors grille sont traitées comme des murs.
    """
    height = len(grid)
    width = len(grid[0])

    if x < 0 or y < 0 or x >= height or y >= width:
        return False

    return grid[x][y].state


def creates_square(grid, x, y):
    """
    Vérifie si activer la cellule (x, y) créerait un carré 2x2
    """

    squares = [
        [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)],
        [(x, y), (x - 1, y), (x, y + 1), (x - 1, y + 1)],
        [(x, y), (x + 1, y), (x, y - 1), (x + 1, y - 1)],
        [(x, y), (x - 1, y), (x, y - 1), (x - 1, y - 1)],
    ]

    height = len(grid)
    width = len(grid[0])

    for square in squares:
        valid = True

        for i, j in square:
            if i < 0 or j < 0 or i >= height or j >= width:
                valid = False
                break

            if (i, j) == (x, y):
                continue

            if not grid[i][j].state:
                valid = False
                break

        if valid:
            return True

    return False


def tunnel_continuity(x, y, grid):
    """
    Vérifie si la case morte (x, y) prolonge naturellement un tunnel.
    Les motifs sont évalués de manière sûre sur toute la grille, y compris au bord.
    """
    if is_alive(grid, x, y):
        return False

    up = is_alive(grid, x - 1, y)
    up2 = is_alive(grid, x - 2, y)
    down = is_alive(grid, x + 1, y)
    down2 = is_alive(grid, x + 2, y)
    left = is_alive(grid, x, y - 1)
    left2 = is_alive(grid, x, y - 2)
    right = is_alive(grid, x, y + 1)
    right2 = is_alive(grid, x, y + 2)

    straight_vertical = up and down
    straight_horizontal = left and right
    extended_vertical = (up2 and down) or (up and down2)
    extended_horizontal = (left2 and right) or (left and right2)

    return (
        straight_vertical
        or straight_horizontal
        or extended_vertical
        or extended_horizontal
    )


def birth_corner(grid, x, y):
    """
    Retourne True si la case (x, y) peut devenir un tunnel
    grâce à deux tunnels en angle autour d'elle.

    Motifs détectés :
    - haut + gauche
    - gauche + bas
    - droite + haut
    - droite + bas
    """
    if is_alive(grid, x, y):
        return False

    up = is_alive(grid, x - 1, y)
    down = is_alive(grid, x + 1, y)
    left = is_alive(grid, x, y - 1)
    right = is_alive(grid, x, y + 1)

    return (up and left) or (left and down) or (down and right) or (right and up)


def has_six_or_more_alive_neighbors(grid, x, y):
    """
    Vérifie si la cellule (x, y) a 6 voisins ou plus qui sont vivants.
    """
    alive_neighbors = sum(
        [
            is_alive(grid, x - 1, y),  # haut
            is_alive(grid, x + 1, y),  # bas
            is_alive(grid, x, y - 1),  # gauche
            is_alive(grid, x, y + 1),  # droite
            is_alive(grid, x - 1, y - 1),  # haut gauche
            is_alive(grid, x - 1, y + 1),  # haut droite
            is_alive(grid, x + 1, y - 1),  # bas gauche
            is_alive(grid, x + 1, y + 1),  # bas droite
        ]
    )

    return alive_neighbors >= 6  # Retourne True si 6 ou plus de voisins sont vivants


def should_birth(grid, x, y):
    if is_alive(grid, x, y):
        return False

    if creates_square(grid, x, y):
        return False

    if has_six_or_more_alive_neighbors(grid, x, y):
        return False

    # priorité aux lignes droites
    if tunnel_continuity(x, y, grid):
        return True

    # virages rares
    if birth_corner(grid, x, y):
        return random.random() < 0.3

    return False


def update_birth(grid_old, grid_new):
    """
    Mise à jour de la grille avec la règle de naissance pour chaque cellule :
    - une cellule morte devient active si un motif de continuité de tunnel est trouvé autour d'elle
    """
    height = len(grid_old)
    width = len(grid_old[0])

    for x in range(height):
        old_row = grid_old[x]
        new_row = grid_new[x]
        for y in range(width):
            if not old_row[y].state and should_birth(grid_old, x, y):
                new_row[y].state = True
