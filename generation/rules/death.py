from generation.models.grid import is_in_grid


def get_alive_neighbors_positions(x, y, grid):
    directions = {
        "N": (x - 1, y),
        "S": (x + 1, y),
        "W": (x, y - 1),
        "E": (x, y + 1),
        "NE": (x - 1, y + 1),
        "NW": (x - 1, y - 1),
        "SE": (x + 1, y + 1),
        "SW": (x + 1, y - 1),
    }

    alive = set()

    for name, (nx, ny) in directions.items():
        if is_in_grid(grid, nx, ny) and grid[nx][ny].state:
            alive.add(name)

    return alive


def find_cells_to_kill(grid, x, y):
    """
    Vérifie si la cellule (x, y) fait partie d'un carré 2x2
    constitué des cellules (x, y), (x+1, y), (x, y+1), (x+1, y+1),
    et si c'est le cas, retourne True.
    """
    height = len(grid)
    width = len(grid[0])

    if not grid[x][y].state:
        return False

    if x + 1 < height and y + 1 < width:
        if grid[x + 1][y].state and grid[x][y + 1].state and grid[x + 1][y + 1].state:
            return True

    return False


def update_width_validator(grid_old, grid_new):
    """
    Mise à jour de l'automate :
    - une case active reste active
    - une case inactive peut naître selon la règle de continuité
    """
    height = len(grid_old)
    width = len(grid_old[0])

    for x in range(height - 1):
        for y in range(width - 1):
            if find_cells_to_kill(grid_old, x, y):
                grid_new[x][y].state = False


def check_death(x, y, grid):
    """
    Une cellule vivante meurt si :
    - elle n'a aucun voisin vivant
    - ou elle a uniquement un voisin diagonal vivant
    - ou elle a uniquement deux voisins diagonaux opposés
    - ou elle a 6 voisins ou plus vivants
    """
    alive = get_alive_neighbors_positions(x, y, grid)

    # Aucun voisin vivant
    if len(alive) == 0:
        return True

    if len(alive) >= 6:
        return True

    diagonal_neighbors = {"NE", "NW", "SE", "SW"}

    # Un seul voisin vivant, et il est diagonal
    if len(alive) == 1 and alive.issubset(diagonal_neighbors):
        return True

    # Deux voisins vivants diagonaux opposés
    if alive == {"NE", "SW"} or alive == {"NW", "SE"}:
        return True

    return False


def update_death(grid_old, grid_new):
    """
    Mise à jour de la grille avec la règle de mort :
    - une cellule vivante devient morte si elle est entourée uniquement de cellules mortes.
    """
    height = len(grid_old)
    width = len(grid_old[0])

    for x in range(height):
        old_row = grid_old[x]
        new_row = grid_new[x]
        for y in range(width):
            if old_row[y].state and check_death(x, y, grid_old):
                new_row[y].state = False
