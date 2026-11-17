from generation.models.grid import copy_grid_state
from .birth import update_birth
from .death import update_width_validator, update_death


def rules_update(grid_old, grid_new):
    """
    Applique toutes les règles (naissance et mort) à la grille.
    """
    copy_grid_state(grid_old, grid_new)

    update_birth(grid_old, grid_new)

    update_death(grid_old, grid_new)

    update_width_validator(grid_old, grid_new)
