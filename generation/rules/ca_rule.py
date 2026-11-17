# from generation.models.grid import get_neighbors
# from generation.rules.width_validator import respects_width_rule
# import random


# def should_become_path(grid, x, y):
#     if grid[x][y].is_path:
#         return False

#     if not respects_width_rule(grid, x, y):
#         return False

#     neighbors = get_neighbors(grid, x, y)
#     path_neighbors = [p for p in neighbors if p.is_path]
#     nb = len(path_neighbors)

#     if nb == 0:
#         return False

#     if nb == 1:
#         return True

#     if nb == 2:
#         coords = {(p.x, p.y) for p in path_neighbors}

#         vertical = {(x - 1, y), (x + 1, y)}
#         horizontal = {(x, y - 1), (x, y + 1)}

#         # ligne droite : souvent autorisée
#         if coords == vertical or coords == horizontal:
#             return True

#         # virage : rare
#         return random.random() < 0.2

#     return False
